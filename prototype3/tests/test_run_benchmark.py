from contextlib import contextmanager
import json
from pathlib import Path
import shutil
from unittest.mock import patch
from uuid import uuid4

import pytest

from src.brain.uncertainty import UncertaintyResult
from src.eval.run_benchmark import RunnerPlanResult, _parse_raw_json, run_benchmark
from src.eval.scoring import SemanticScore
from src.schema.action_schema import validate_action_plan
from src.brain.safety import validate_safety


@contextmanager
def _local_output_path(test_name: str):
    root = Path("tests") / ".tmp_run_benchmark" / f"{test_name}_{uuid4().hex}"
    root.mkdir(parents=True, exist_ok=True)
    try:
        yield root / "benchmark.jsonl"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _load_entries(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").strip().splitlines()
    ]


class _StubPlanner:
    def __init__(
        self,
        *,
        parsed_output: object | None,
        error: str | None = None,
        raw_output: str | None = None,
    ) -> None:
        self._parsed_output = parsed_output
        self._error = error
        self._raw_output = raw_output

    def plan(self, command: str, scene_state: dict | None = None) -> RunnerPlanResult:
        del command, scene_state
        raw_output = self._raw_output
        if raw_output is None and self._parsed_output is not None:
            raw_output = json.dumps(self._parsed_output)
        return RunnerPlanResult(
            success=self._error is None,
            parsed_output=self._parsed_output,
            raw_output=raw_output,
            error=self._error,
            planning_latency_ms=1,
        )


def test_run_benchmark_generates_records_for_both_models() -> None:
    with _local_output_path("all_models") as output_path:
        count = run_benchmark(
            dataset_path="datasets/benchmark_v1.json",
            output_path=str(output_path),
            models=["fake_slm", "fake_llm"],
        )

        assert count == 60
        assert output_path.exists()

        lines = output_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 60

        entries = [json.loads(line) for line in lines]
        models_seen = {entry["model"] for entry in entries}
        assert models_seen == {"fake_slm", "fake_llm"}

        command_ids = {entry["command_id"] for entry in entries}
        assert len(command_ids) == 30

        for entry in entries:
            assert "schema_errors" in entry
            assert isinstance(entry["schema_errors"], list)
            assert "planning_latency_ms" in entry
            assert isinstance(entry["planning_latency_ms"], int)
            assert "rejected" in entry
            assert "rejection_reasons" in entry
            assert "execution_eligible" in entry

        assert isinstance(entries[0]["semantic_score"], float)
        assert "run_id" in entries[0]


def test_c01_fake_slm_schema_valid_and_score_1() -> None:
    with _local_output_path("c01_exact") as output_path:
        run_benchmark(
            dataset_path="datasets/benchmark_v1.json",
            output_path=str(output_path),
            models=["fake_slm"],
            command_ids=["C01"],
        )

        entries = _load_entries(output_path)
        c01 = entries[0]
        assert c01["schema_valid"] is True
        assert c01["schema_errors"] == []
        assert c01["semantic_score"] == 1.0
        assert c01["rejected"] is False
        assert c01["rejection_reasons"] == []
        assert c01["execution_eligible"] is True
        assert c01["executed"] is False
        assert c01["failure_mode"] is None


def test_malformed_raw_response_schema_invalid() -> None:

    # Inject a malformed raw response via _parse_raw_json helper directly.
    parsed, ok = _parse_raw_json("not valid json {{{{")
    assert ok is False

    # Also validate that schema validator handles garbage lists.
    result = validate_action_plan([{"action": "unknown_xyz"}])
    assert result.valid is False
    assert any("unknown_action" in e for e in result.errors)


def test_schema_errors_present_when_invalid() -> None:
    result = validate_action_plan([{"action": "pick"}])
    assert result.valid is False
    assert result.errors != []


# ---------------------------------------------------------------------------
# Phase 3.3 — safety_valid and safety_violations are real, not hardcoded
# ---------------------------------------------------------------------------

def test_all_records_have_safety_fields() -> None:
    with _local_output_path("safety_fields") as output_path:
        run_benchmark(
            dataset_path="datasets/benchmark_v1.json",
            output_path=str(output_path),
            models=["fake_slm"],
        )
        entries = _load_entries(output_path)
        for entry in entries:
            assert "safety_valid" in entry
            assert "safety_violations" in entry
            assert isinstance(entry["safety_violations"], list)


def test_c01_fake_slm_safety_valid() -> None:
    with _local_output_path("c01_safety") as output_path:
        run_benchmark(
            dataset_path="datasets/benchmark_v1.json",
            output_path=str(output_path),
            models=["fake_slm"],
            command_ids=["C01"],
        )
        entries = _load_entries(output_path)
        c01 = entries[0]
        assert c01["safety_valid"] is True
        assert c01["safety_violations"] == []


def test_safety_validator_rejects_unknown_object_directly() -> None:
    result = validate_safety([{"action": "pick", "object": "scalpel"}])
    assert result.safe is False
    assert any("unsafe_object" in v for v in result.violations)


def test_safety_validator_rejects_out_of_bounds_coordinates() -> None:
    result = validate_safety([{"action": "moveee", "target_xyz": [999.9, 0.0, 0.0]}])
    assert result.safe is False
    assert any("out_of_bounds" in v for v in result.violations)


def test_safety_validator_safe_actions_not_none_on_valid_plan() -> None:
    result = validate_safety([{"action": "pick", "object": "medicine_cup"}])
    assert result.safe is True
    assert result.safe_actions is not None


# ---------------------------------------------------------------------------
# Phase 3.4 — model selection, command filters, and latency logging
# ---------------------------------------------------------------------------

def test_commands_filter_limits_dataset() -> None:
    with _local_output_path("commands_filter") as output_path:
        count = run_benchmark(
            dataset_path="datasets/benchmark_v1.json",
            output_path=str(output_path),
            models=["fake_slm"],
            command_ids=["C01", "C02", "C03"],
        )

        assert count == 3
        entries = _load_entries(output_path)
        assert {e["command_id"] for e in entries} == {"C01", "C02", "C03"}
        assert {e["model"] for e in entries} == {"fake_slm"}


def test_model_selection_runs_one_model_only() -> None:
    with _local_output_path("single_model") as output_path:
        count = run_benchmark(
            dataset_path="datasets/benchmark_v1.json",
            output_path=str(output_path),
            models=["fake_llm"],
        )

        assert count == 30
        entries = _load_entries(output_path)
        assert {e["model"] for e in entries} == {"fake_llm"}


def test_unknown_model_raises_controlled_error() -> None:
    with _local_output_path("unknown_model") as output_path:
        with pytest.raises(ValueError, match="Unsupported model backend"):
            run_benchmark(
                dataset_path="datasets/benchmark_v1.json",
                output_path=str(output_path),
                models=["totally_unknown_model"],
            )


def test_schema_invalid_plan_is_rejected_and_not_execution_eligible() -> None:
    with _local_output_path("schema_invalid") as output_path:
        run_benchmark(
            dataset_path="datasets/benchmark_v1.json",
            output_path=str(output_path),
            models=["fake_llm"],
            command_ids=["C01"],
        )

        entry = _load_entries(output_path)[0]
        assert entry["schema_valid"] is False
        assert entry["rejected"] is True
        assert entry["rejection_reasons"] == ["schema_invalid"]
        assert entry["execution_eligible"] is False
        assert entry["executed"] is False


def test_semantic_mismatch_is_rejected_and_not_execution_eligible() -> None:
    with _local_output_path("semantic_reject") as output_path:
        run_benchmark(
            dataset_path="datasets/benchmark_v1.json",
            output_path=str(output_path),
            models=["fake_slm"],
            command_ids=["C02"],
        )

        entry = _load_entries(output_path)[0]
        assert entry["schema_valid"] is True
        assert entry["rejected"] is True
        assert entry["rejection_reasons"] == ["semantic_mismatch"]
        assert entry["execution_eligible"] is False
        assert entry["executed"] is False


def test_uncertain_plan_is_rejected_and_not_execution_eligible() -> None:
    stub_planner = _StubPlanner(
        parsed_output={"actions": [{"action": "pick", "object": "medicine_cup"}]}
    )
    forced_semantics = SemanticScore(
        score=1.0,
        passed=True,
        failure_mode="none",
        notes="forced semantic pass",
    )
    forced_uncertainty = UncertaintyResult(
        uncertain=True,
        reasons=["ambiguous_reference"],
        score=0.4,
    )

    with _local_output_path("uncertain_reject") as output_path:
        with patch("src.eval.run_benchmark._build_planner", return_value=stub_planner):
            with patch(
                "src.eval.run_benchmark.score_semantics",
                return_value=forced_semantics,
            ):
                with patch(
                    "src.eval.run_benchmark.assess_uncertainty",
                    return_value=forced_uncertainty,
                ):
                    run_benchmark(
                        dataset_path="datasets/benchmark_v1.json",
                        output_path=str(output_path),
                        models=["patched_model"],
                        command_ids=["C01"],
                    )

        entry = _load_entries(output_path)[0]
        assert entry["rejected"] is True
        assert entry["rejection_reasons"] == ["uncertain_or_low_confidence"]
        assert entry["execution_eligible"] is False
        assert entry["executed"] is False


def test_unsafe_plan_is_rejected_and_not_execution_eligible() -> None:
    stub_planner = _StubPlanner(
        parsed_output={"actions": [{"action": "pick", "object": "scalpel"}]}
    )
    forced_semantics = SemanticScore(
        score=1.0,
        passed=True,
        failure_mode="none",
        notes="forced semantic pass",
    )
    forced_uncertainty = UncertaintyResult(
        uncertain=False,
        reasons=[],
        score=0.0,
    )

    with _local_output_path("unsafe_reject") as output_path:
        with patch("src.eval.run_benchmark._build_planner", return_value=stub_planner):
            with patch(
                "src.eval.run_benchmark.score_semantics",
                return_value=forced_semantics,
            ):
                with patch(
                    "src.eval.run_benchmark.assess_uncertainty",
                    return_value=forced_uncertainty,
                ):
                    run_benchmark(
                        dataset_path="datasets/benchmark_v1.json",
                        output_path=str(output_path),
                        models=["patched_model"],
                        command_ids=["C01"],
                    )

        entry = _load_entries(output_path)[0]
        assert entry["schema_valid"] is True
        assert entry["safety_valid"] is False
        assert entry["rejected"] is True
        assert entry["rejection_reasons"] == ["safety_violation"]
        assert entry["execution_eligible"] is False
        assert entry["executed"] is False


def test_all_pass_plan_is_eligible_but_not_executed() -> None:
    with _local_output_path("all_pass") as output_path:
        run_benchmark(
            dataset_path="datasets/benchmark_v1.json",
            output_path=str(output_path),
            models=["fake_slm"],
            command_ids=["C01"],
        )

        entry = _load_entries(output_path)[0]
        assert entry["rejected"] is False
        assert entry["rejection_reasons"] == []
        assert entry["execution_eligible"] is True
        assert entry["executed"] is False
        assert entry["execution_success"] is False
