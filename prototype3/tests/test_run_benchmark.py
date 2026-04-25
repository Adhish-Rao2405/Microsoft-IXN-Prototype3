import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.eval.run_benchmark import _parse_raw_json, run_benchmark
from src.schema.action_schema import validate_action_plan
from src.brain.safety import validate_safety


def test_run_benchmark_generates_records_for_both_models(tmp_path) -> None:
    output_path = tmp_path / "runs" / "benchmark.jsonl"

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

    # All records have schema_errors field.
    for entry in entries:
        assert "schema_errors" in entry
        assert isinstance(entry["schema_errors"], list)

    assert isinstance(entries[0]["semantic_score"], float)
    assert "run_id" in entries[0]


def test_c01_fake_slm_schema_valid_and_score_1(tmp_path) -> None:
    output_path = tmp_path / "runs" / "benchmark.jsonl"

    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(output_path),
        models=["fake_slm"],
    )

    entries = [
        json.loads(line)
        for line in output_path.read_text(encoding="utf-8").strip().splitlines()
    ]
    c01 = next(e for e in entries if e["command_id"] == "C01" and e["model"] == "fake_slm")
    assert c01["schema_valid"] is True
    assert c01["schema_errors"] == []
    assert c01["semantic_score"] == 1.0
    assert c01["failure_mode"] is None


def test_malformed_raw_response_schema_invalid(tmp_path) -> None:
    output_path = tmp_path / "runs" / "benchmark.jsonl"

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

def test_all_records_have_safety_fields(tmp_path) -> None:
    output_path = tmp_path / "runs" / "benchmark.jsonl"
    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(output_path),
        models=["fake_slm"],
    )
    entries = [
        json.loads(line)
        for line in output_path.read_text(encoding="utf-8").strip().splitlines()
    ]
    for entry in entries:
        assert "safety_valid" in entry
        assert "safety_violations" in entry
        assert isinstance(entry["safety_violations"], list)


def test_c01_fake_slm_safety_valid(tmp_path) -> None:
    output_path = tmp_path / "runs" / "benchmark.jsonl"
    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(output_path),
        models=["fake_slm"],
    )
    entries = [
        json.loads(line)
        for line in output_path.read_text(encoding="utf-8").strip().splitlines()
    ]
    c01 = next(e for e in entries if e["command_id"] == "C01")
    # fake_slm returns a valid pick — must pass safety too.
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
