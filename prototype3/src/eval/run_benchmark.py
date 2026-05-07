from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from dataclasses import dataclass
import os
from pathlib import Path
import re
import sys

from src.brain.foundry_planner import FoundryPlanner
from src.brain.model_client import ModelClient, ModelRequest
from src.brain.uncertainty import assess_uncertainty
from src.eval.benchmark_loader import load_benchmark
from src.eval.metrics_logger import write_run_record
from src.eval.run_metadata import collect_run_metadata
from src.eval.scoring import score_semantics
from src.schema.action_schema import validate_action_plan
from src.brain.safety import validate_safety


def _parse_raw_json(raw_text: str) -> tuple[object | None, bool]:
    """Return (parsed_object, parse_ok)."""
    try:
        return json.loads(raw_text), True
    except json.JSONDecodeError:
        return None, False


@dataclass
class RunnerPlanResult:
    success: bool
    parsed_output: object | None
    raw_output: str | None
    error: str | None
    planning_latency_ms: int


@dataclass
class PreExecutionDecision:
    rejected: bool
    rejection_reasons: list[str]
    execution_eligible: bool


def _is_uncertain_or_low_confidence(uncertainty_result) -> bool:
    return bool(
        uncertainty_result.uncertain or uncertainty_result.score > 0.0
    )


def _decide_pre_execution(
    *,
    schema_valid: bool,
    semantic_passed: bool,
    uncertainty_result,
    safety_valid: bool,
) -> PreExecutionDecision:
    if not schema_valid:
        return PreExecutionDecision(
            rejected=True,
            rejection_reasons=["schema_invalid"],
            execution_eligible=False,
        )

    if not semantic_passed:
        return PreExecutionDecision(
            rejected=True,
            rejection_reasons=["semantic_mismatch"],
            execution_eligible=False,
        )

    if _is_uncertain_or_low_confidence(uncertainty_result):
        return PreExecutionDecision(
            rejected=True,
            rejection_reasons=["uncertain_or_low_confidence"],
            execution_eligible=False,
        )

    if not safety_valid:
        return PreExecutionDecision(
            rejected=True,
            rejection_reasons=["safety_violation"],
            execution_eligible=False,
        )

    return PreExecutionDecision(
        rejected=False,
        rejection_reasons=[],
        execution_eligible=True,
    )


class _FakePlanner:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._client = ModelClient()

    def plan(self, command: str, scene_state: dict | None = None) -> RunnerPlanResult:
        del scene_state
        request = ModelRequest(command=command, model_name=self._model_name)
        response = self._client.generate_plan(request)

        parsed_output, parse_ok = _parse_raw_json(response.raw_text)
        return RunnerPlanResult(
            success=response.success,
            parsed_output=parsed_output if parse_ok else None,
            raw_output=response.raw_text,
            error=response.error if response.error else (None if parse_ok else "parse_error"),
            planning_latency_ms=int(response.latency_ms),
        )


def _parse_foundry_model_spec(model_name: str) -> tuple[str, str] | None:
    parts = model_name.split(":")
    if len(parts) != 3 or parts[0] != "foundry":
        return None
    return parts[1], parts[2]


def _build_planner(model_name: str):
    if model_name in {"fake_slm", "fake_llm"}:
        return _FakePlanner(model_name)

    foundry_spec = _parse_foundry_model_spec(model_name)
    if foundry_spec is not None:
        alias, device = foundry_spec
        return FoundryPlanner(model_alias=alias, device=device)

    raise ValueError(f"Unsupported model backend: {model_name}")


def run_benchmark(
    dataset_path: str = "datasets/benchmark_v1.json",
    output_path: str = "results/runs/benchmark.jsonl",
    models: list[str] | None = None,
    command_ids: list[str] | None = None,
) -> int:
    items = load_benchmark(dataset_path)
    if command_ids:
        wanted = {cid.strip() for cid in command_ids if cid.strip()}
        items = [item for item in items if item["id"] in wanted]

    selected_models = models or ["fake_slm", "fake_llm"]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    records_written = 0
    for model in selected_models:
        planner = _build_planner(model)
        safe_model = re.sub(r'[^\w.\-]', '_', model)
        metadata = collect_run_metadata(
            dataset_path=dataset_path,
            model=model,
            timestamp=timestamp,
            foundry_endpoint=None if model in {"fake_slm", "fake_llm"} else os.getenv("FOUNDRY_LOCAL_BASE_URL", "http://127.0.0.1:8080"),
            planner_temperature=None if model in {"fake_slm", "fake_llm"} else 0.0,
            planner_max_tokens=None if model in {"fake_slm", "fake_llm"} else 256,
            planner_timeout_s=None if model in {"fake_slm", "fake_llm"} else 30.0,
        )
        metadata_path = Path(output_path).parent / f"run_metadata_{timestamp}_{safe_model}.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=True, indent=2), encoding="utf-8"
        )
        for item in items:
            command = item["command"]

            plan_result = planner.plan(command=command, scene_state={})
            parsed_json = plan_result.parsed_output
            parse_ok = parsed_json is not None

            safety_valid: bool = False
            safety_violations: list[str] = []

            # Planner-level failures are explicit and win failure_mode precedence.
            planner_failure = plan_result.error

            if planner_failure in {
                "foundry_connection_error",
                "foundry_timeout",
                "foundry_response_error",
                "unknown_model_error",
            }:
                schema_valid = False
                schema_errors = [planner_failure]
                planned_actions = None
                pre_schema_failure = planner_failure
            else:
                if not parse_ok:
                    schema_valid = False
                    schema_errors = ["json_parse_error"]
                    planned_actions = None
                    pre_schema_failure = "parse_error"
                else:
                    # --- Schema validation ---
                    schema_result = validate_action_plan(parsed_json)
                    schema_valid = schema_result.valid
                    schema_errors = schema_result.errors
                    planned_actions = schema_result.normalized_actions if schema_valid else None
                    pre_schema_failure = None if schema_valid else "schema_error"

            uncertainty = assess_uncertainty(command)
            semantic = score_semantics(
                benchmark_item=item,
                planned_actions=planned_actions,
                uncertainty_result=uncertainty,
            )

            if (
                schema_valid
                and planned_actions is not None
                and semantic.passed
                and not _is_uncertain_or_low_confidence(uncertainty)
            ):
                # --- Safety validation ---
                safety_result = validate_safety(planned_actions)
                safety_valid = safety_result.safe
                safety_violations = safety_result.violations
                planned_actions = safety_result.safe_actions if safety_valid else None
            else:
                safety_valid = False

            decision = _decide_pre_execution(
                schema_valid=schema_valid,
                semantic_passed=semantic.passed,
                uncertainty_result=uncertainty,
                safety_valid=safety_valid,
            )

            if pre_schema_failure is not None:
                effective_failure = pre_schema_failure
            elif decision.rejected and decision.rejection_reasons:
                effective_failure = decision.rejection_reasons[0]
            else:
                effective_failure = None

            record = {
                "run_id": f"{timestamp}_{item['id']}_{model}",
                "command_id": item["id"],
                "command_text": command,
                "difficulty": item["difficulty"],
                "gold_label": item["gold_label"],
                "category": item.get("category", ""),
                "model": model,
                "latency_ms": plan_result.planning_latency_ms,
                "planning_latency_ms": plan_result.planning_latency_ms,
                "raw_response": plan_result.raw_output or "",
                "schema_valid": schema_valid,
                "schema_errors": schema_errors,
                "safety_valid": safety_valid,
                "safety_violations": safety_violations,
                "uncertainty_flag": uncertainty.uncertain,
                "uncertainty_reasons": uncertainty.reasons,
                "uncertainty_score": uncertainty.score,
                "semantic_score": semantic.score,
                "semantic_failure_mode": semantic.failure_mode,
                "rejected": decision.rejected,
                "rejection_reasons": decision.rejection_reasons,
                "execution_eligible": decision.execution_eligible,
                "executed": False,
                "execution_success": False,
                "failure_mode": effective_failure,
                "run_metadata_path": str(metadata_path),
            }
            write_run_record(output_path, record)
            records_written += 1

    return records_written


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Prototype 3 benchmark")
    parser.add_argument("--model", default=None, help="Single model backend to run")
    parser.add_argument(
        "--commands",
        default=None,
        help="Comma-separated command IDs (e.g., C01,C02,C03)",
    )
    parser.add_argument(
        "--output",
        default="results/runs/benchmark.jsonl",
        help="Output JSONL path",
    )
    args = parser.parse_args()

    models = [args.model] if args.model else None
    commands = args.commands.split(",") if args.commands else None

    count = run_benchmark(output_path=args.output, models=models, command_ids=commands)
    print(f"Benchmark run complete. Records written: {count}")

    # Auto CSV export - write to results/summaries/ alongside JSONL
    output_file = Path(args.output)
    if count > 0 and output_file.exists():
        summary_dir = output_file.parent.parent / "summaries"
        summary_dir.mkdir(parents=True, exist_ok=True)
        csv_path = summary_dir / output_file.with_suffix(".csv").name
        from src.eval.metrics_logger import write_summary_csv

        csv_rows = write_summary_csv(str(output_file), str(csv_path))
        print(f"CSV summary written: {csv_path} ({csv_rows} rows)")

        # Brief metrics summary
        records = [
            json.loads(line)
            for line in output_file.read_text(encoding="utf-8").strip().splitlines()
        ]
        schema_valid = sum(1 for r in records if r.get("schema_valid"))
        eligible = sum(1 for r in records if r.get("execution_eligible"))
        conn_errors = sum(
            1
            for r in records
            if r.get("failure_mode") == "foundry_connection_error"
        )
        print(f"Schema valid:        {schema_valid} / {count}")
        print(f"Execution eligible:  {eligible} / {count}")
        if conn_errors:
            print(
                f"Connection errors:   {conn_errors} / {count}  "
                "<- Foundry Local not running?"
            )

    sys.stdout.flush()


if __name__ == "__main__":
    main()
