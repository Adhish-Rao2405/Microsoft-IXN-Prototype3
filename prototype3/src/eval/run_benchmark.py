from __future__ import annotations

from datetime import datetime, timezone
import json

from src.brain.model_client import ModelClient, ModelRequest
from src.brain.uncertainty import assess_uncertainty
from src.eval.benchmark_loader import load_benchmark
from src.eval.metrics_logger import write_run_record
from src.eval.scoring import score_semantics
from src.schema.action_schema import validate_action_plan
from src.brain.safety import validate_safety


def _parse_raw_json(raw_text: str) -> tuple[object | None, bool]:
    """Return (parsed_object, parse_ok)."""
    try:
        return json.loads(raw_text), True
    except json.JSONDecodeError:
        return None, False


def run_benchmark(
    dataset_path: str = "datasets/benchmark_v1.json",
    output_path: str = "results/runs/benchmark.jsonl",
    models: list[str] | None = None,
) -> int:
    items = load_benchmark(dataset_path)
    selected_models = models or ["fake_slm", "fake_llm"]

    client = ModelClient()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    records_written = 0
    for model in selected_models:
        for item in items:
            command = item["command"]

            request = ModelRequest(
                command=command,
                model_name=model,
            )
            response = client.generate_plan(request)

            # --- Parse raw JSON ---
            parsed_json, parse_ok = _parse_raw_json(response.raw_text)
            safety_valid: bool = False
            safety_violations: list[str] = []
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
                if not schema_valid:
                    planned_actions = None
                    pre_schema_failure = "schema_error"
                    safety_valid = False
                    safety_violations: list[str] = []
                else:
                    # --- Safety validation ---
                    safety_result = validate_safety(schema_result.normalized_actions)
                    safety_valid = safety_result.safe
                    safety_violations = safety_result.violations
                    planned_actions = safety_result.safe_actions if safety_valid else None
                    pre_schema_failure = None if safety_valid else "safety_error"

            uncertainty = assess_uncertainty(command)
            semantic = score_semantics(
                benchmark_item=item,
                planned_actions=planned_actions,
                uncertainty_result=uncertainty,
            )

            # Prefer semantic scoring failure mode when schema already passed;
            # otherwise keep the earlier parse/schema error.
            if pre_schema_failure is not None:
                effective_failure = pre_schema_failure
            elif semantic.failure_mode in (None, "none"):
                effective_failure = None
            else:
                effective_failure = semantic.failure_mode

            record = {
                "run_id": f"{timestamp}_{item['id']}_{model}",
                "command_id": item["id"],
                "command_text": command,
                "difficulty": item["difficulty"],
                "gold_label": item["gold_label"],
                "model": model,
                "latency_ms": response.latency_ms,
                "raw_response": response.raw_text,
                "schema_valid": schema_valid,
                "schema_errors": schema_errors,
                "safety_valid": safety_valid,
                "safety_violations": safety_violations,
                "uncertainty_flag": uncertainty.uncertain,
                "uncertainty_reasons": uncertainty.reasons,
                "uncertainty_score": uncertainty.score,
                "semantic_score": semantic.score,
                "executed": False,
                "execution_success": False,
                "failure_mode": effective_failure,
            }
            write_run_record(output_path, record)
            records_written += 1

    return records_written


def main() -> None:
    count = run_benchmark()
    print(f"Benchmark run complete. Records written: {count}")


if __name__ == "__main__":
    main()
