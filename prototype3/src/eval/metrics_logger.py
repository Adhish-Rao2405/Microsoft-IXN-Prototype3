from __future__ import annotations

import csv
import json
from pathlib import Path

from src.eval.comparison import aggregate_model_metrics


def write_run_record(path: str, record: dict) -> None:
    if not isinstance(record, dict):
        raise ValueError("Metrics record must be a dictionary")

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        encoded = json.dumps(record, ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise ValueError("Metrics record must be valid JSON serializable data") from exc

    with destination.open("a", encoding="utf-8") as handle:
        handle.write(encoded + "\n")


def write_summary_csv(jsonl_path: str, csv_path: str) -> int:
    """Read a JSONL run record file and write a flat CSV summary.

    Returns the number of data rows written. Raises ValueError if the JSONL
    file does not exist.
    """
    import csv

    source = Path(jsonl_path)
    if not source.exists():
        raise ValueError(f"JSONL file does not exist: {jsonl_path}")

    COLUMNS = [
        "run_id", "command_id", "command_text", "category", "difficulty",
        "gold_label", "model", "schema_valid", "semantic_score",
        "semantic_failure_mode", "rejected", "execution_eligible",
        "failure_mode", "latency_ms",
    ]

    rows = []
    for line in source.read_text(encoding="utf-8").strip().splitlines():
        record = json.loads(line)
        rows.append({col: record.get(col, "") for col in COLUMNS})

    destination = Path(csv_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def write_comparison_csv(jsonl_path: str, csv_path: str) -> int:
    """Aggregate per-record JSONL into a per-model comparison CSV.

    Returns the number of model rows written. Raises ValueError if the JSONL
    file does not exist.
    """
    COLUMNS = [
        "model", "total_records", "schema_valid_count", "schema_valid_rate",
        "execution_eligible_count", "execution_eligible_rate",
        "false_accept_count", "false_reject_count", "correct_reject_count",
        "mean_latency_ms",
    ]

    rows = aggregate_model_metrics(jsonl_path)

    destination = Path(csv_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)
