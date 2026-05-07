from __future__ import annotations

import json
from pathlib import Path


def aggregate_model_metrics(jsonl_path: str) -> list[dict]:
    """Aggregate per-record JSONL into one summary row per model.

    Returns a list of dicts (one per model) sorted ascending by model name.
    Raises ValueError if the JSONL file does not exist.
    """
    source = Path(jsonl_path)
    if not source.exists():
        raise ValueError(f"JSONL file does not exist: {jsonl_path}")

    groups: dict[str, list[dict]] = {}
    for line in source.read_text(encoding="utf-8").strip().splitlines():
        record = json.loads(line)
        model = record.get("model", "")
        groups.setdefault(model, []).append(record)

    rows = []
    for model in sorted(groups):
        records = groups[model]
        total = len(records)
        schema_valid_count = sum(1 for r in records if r.get("schema_valid"))
        eligible_count = sum(1 for r in records if r.get("execution_eligible"))
        false_accept = sum(
            1 for r in records if r.get("semantic_failure_mode") == "false_accept"
        )
        false_reject = sum(
            1 for r in records if r.get("semantic_failure_mode") == "false_reject"
        )
        correct_reject = sum(
            1 for r in records if r.get("semantic_failure_mode") == "correct_reject"
        )
        latencies = [r.get("latency_ms", 0) for r in records]
        mean_lat = round(sum(latencies) / total, 1) if total else 0.0

        rows.append({
            "model": model,
            "total_records": total,
            "schema_valid_count": schema_valid_count,
            "schema_valid_rate": round(schema_valid_count / total, 4) if total else 0.0,
            "execution_eligible_count": eligible_count,
            "execution_eligible_rate": round(eligible_count / total, 4) if total else 0.0,
            "false_accept_count": false_accept,
            "false_reject_count": false_reject,
            "correct_reject_count": correct_reject,
            "mean_latency_ms": mean_lat,
        })

    return rows
