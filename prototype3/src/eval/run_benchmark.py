from __future__ import annotations

from datetime import datetime, timezone
import json

from src.brain.model_client import ModelClient, ModelRequest
from src.brain.uncertainty import assess_uncertainty
from src.eval.benchmark_loader import load_benchmark
from src.eval.metrics_logger import write_run_record
from src.eval.scoring import score_semantics


def parse_planned_actions(raw_text: str) -> list[dict] | None:
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict) and "actions" in parsed:
            actions = parsed["actions"]
            return actions if isinstance(actions, list) else None
        return None
    except json.JSONDecodeError:
        return None


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

            planned_actions = parse_planned_actions(response.raw_text)

            uncertainty = assess_uncertainty(command)
            semantic = score_semantics(
                benchmark_item=item,
                planned_actions=planned_actions,
                uncertainty_result=uncertainty,
            )

            record = {
                "run_id": f"{timestamp}_{item['id']}_{model}",
                "command_id": item["id"],
                "command_text": command,
                "difficulty": item["difficulty"],
                "gold_label": item["gold_label"],
                "model": model,
                "latency_ms": response.latency_ms,
                "raw_response": response.raw_text,
                "schema_valid": True,
                "safety_valid": True,
                "uncertainty_flag": uncertainty.uncertain,
                "uncertainty_reasons": uncertainty.reasons,
                "uncertainty_score": uncertainty.score,
                "semantic_score": semantic.score,
                "executed": False,
                "execution_success": False,
                "failure_mode": None
                if semantic.failure_mode in (None, "none")
                else semantic.failure_mode,
            }
            write_run_record(output_path, record)
            records_written += 1

    return records_written


def main() -> None:
    count = run_benchmark()
    print(f"Benchmark run complete. Records written: {count}")


if __name__ == "__main__":
    main()
