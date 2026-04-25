from __future__ import annotations

import json
from pathlib import Path


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
