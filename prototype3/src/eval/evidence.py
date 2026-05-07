from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path

from src.eval.comparison import aggregate_model_metrics


def _aggregate_by_dim(records: list[dict], dim_field: str) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for record in records:
        dim_value = str(record.get(dim_field, ""))
        model = str(record.get("model", ""))
        key = (dim_value, model)
        grouped.setdefault(key, []).append(record)

    rows: list[dict] = []
    for dim_value, model in sorted(grouped):
        bucket = grouped[(dim_value, model)]
        total = len(bucket)
        schema_valid_count = sum(1 for r in bucket if r.get("schema_valid"))
        eligible_count = sum(1 for r in bucket if r.get("execution_eligible"))
        false_accept_count = sum(
            1 for r in bucket if r.get("semantic_failure_mode") == "false_accept"
        )
        false_reject_count = sum(
            1 for r in bucket if r.get("semantic_failure_mode") == "false_reject"
        )
        correct_reject_count = sum(
            1 for r in bucket if r.get("semantic_failure_mode") == "correct_reject"
        )
        mean_latency_ms = round(
            sum(float(r.get("latency_ms", 0.0)) for r in bucket) / total,
            1,
        ) if total else 0.0

        rows.append(
            {
                dim_field: dim_value,
                "model": model,
                "total_records": total,
                "schema_valid_count": schema_valid_count,
                "schema_valid_rate": round(schema_valid_count / total, 4)
                if total
                else 0.0,
                "execution_eligible_count": eligible_count,
                "execution_eligible_rate": round(eligible_count / total, 4)
                if total
                else 0.0,
                "false_accept_count": false_accept_count,
                "false_reject_count": false_reject_count,
                "correct_reject_count": correct_reject_count,
                "mean_latency_ms": mean_latency_ms,
            }
        )

    return rows


def generate_evidence_pack(jsonl_path: str, output_dir: str) -> dict:
    source = Path(jsonl_path)
    if not source.exists():
        raise ValueError(f"JSONL file does not exist: {jsonl_path}")

    lines = source.read_text(encoding="utf-8").strip().splitlines()
    records = [json.loads(line) for line in lines] if lines else []

    per_model = aggregate_model_metrics(jsonl_path)
    by_difficulty = _aggregate_by_dim(records, "difficulty")
    by_category = _aggregate_by_dim(records, "category")

    rq4_summary: dict[str, dict[str, float]] = {}
    for row in per_model:
        total = int(row["total_records"])
        false_accept_rate = round(int(row["false_accept_count"]) / total, 4) if total else 0.0
        false_reject_rate = round(int(row["false_reject_count"]) / total, 4) if total else 0.0
        correct_reject_rate = round(int(row["correct_reject_count"]) / total, 4) if total else 0.0
        rq4_summary[str(row["model"])] = {
            "false_accept_rate": false_accept_rate,
            "false_reject_rate": false_reject_rate,
            "correct_reject_rate": correct_reject_rate,
        }

    pack = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_jsonl": str(source),
        "total_records": len(records),
        "per_model": per_model,
        "by_difficulty": by_difficulty,
        "by_category": by_category,
        "rq4_summary": rq4_summary,
    }

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    (destination / "evidence_pack.json").write_text(
        json.dumps(pack, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )

    difficulty_columns = [
        "difficulty",
        "model",
        "total_records",
        "schema_valid_count",
        "schema_valid_rate",
        "execution_eligible_count",
        "execution_eligible_rate",
        "false_accept_count",
        "false_reject_count",
        "correct_reject_count",
        "mean_latency_ms",
    ]
    with (destination / "evidence_by_difficulty.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=difficulty_columns)
        writer.writeheader()
        writer.writerows(by_difficulty)

    category_columns = [
        "category",
        "model",
        "total_records",
        "schema_valid_count",
        "schema_valid_rate",
        "execution_eligible_count",
        "execution_eligible_rate",
        "false_accept_count",
        "false_reject_count",
        "correct_reject_count",
        "mean_latency_ms",
    ]
    with (destination / "evidence_by_category.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=category_columns)
        writer.writeheader()
        writer.writerows(by_category)

    return pack