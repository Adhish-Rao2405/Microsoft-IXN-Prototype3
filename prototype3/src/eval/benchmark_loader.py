from __future__ import annotations

import json
from pathlib import Path

ALLOWED_LABELS = {
    "EXECUTE_EXACT",
    "EXECUTE_FLEXIBLE",
    "REJECT_UNCERTAIN",
    "REJECT_UNSUPPORTED",
}
ALLOWED_DIFFICULTIES = {"clear", "moderate", "high"}
REQUIRED_FIELDS = {
    "id",
    "command",
    "difficulty",
    "category",
    "gold_label",
    "gold_intent",
    "uncertainty_expected",
    "allowed_behavior",
    "semantic_pass_rule",
    "notes",
}


def load_benchmark(path: str) -> list[dict]:
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"Benchmark file does not exist: {path}")

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid benchmark JSON: {path}") from exc

    if not isinstance(payload, list):
        raise ValueError("Benchmark must be a JSON array of items")

    if len(payload) != 30:
        raise ValueError(f"Benchmark must contain exactly 30 items, found {len(payload)}")

    seen_ids: set[str] = set()
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Each benchmark item must be a JSON object")

        missing = REQUIRED_FIELDS - set(item.keys())
        if missing:
            raise ValueError(
                f"Benchmark item missing required fields: {sorted(missing)}"
            )

        item_id = item["id"]
        if item_id in seen_ids:
            raise ValueError(f"Duplicate benchmark id: {item_id}")
        seen_ids.add(item_id)

        if item["gold_label"] not in ALLOWED_LABELS:
            raise ValueError(f"Invalid gold_label '{item['gold_label']}' in {item_id}")

        if item["difficulty"] not in ALLOWED_DIFFICULTIES:
            raise ValueError(
                f"Invalid difficulty '{item['difficulty']}' in {item_id}"
            )

    return payload
