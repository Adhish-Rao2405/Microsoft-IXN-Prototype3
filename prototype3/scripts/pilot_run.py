from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.eval.run_benchmark import run_benchmark


PILOT_MODELS = [
    "foundry:qwen2.5-coder-0.5b:cpu",
    "foundry:qwen2.5-coder-7b:cpu",
]
PILOT_COMMANDS = [
    "C01",
    "C02",
    "C03",
    "C04",
    "C05",
    "C06",
    "C07",
    "C08",
    "C09",
    "C10",
]
OUTPUT_PATH = Path("results/pilot/pilot.jsonl")


def _load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return []
    return [json.loads(line) for line in lines]


def main() -> None:
    count = run_benchmark(
        output_path=str(OUTPUT_PATH),
        models=PILOT_MODELS,
        command_ids=PILOT_COMMANDS,
    )

    records = _load_records(OUTPUT_PATH)
    parse_or_schema_failures = sum(
        1
        for r in records
        if (r.get("failure_mode") in {"parse_error", "schema_error"})
        or (r.get("schema_valid") is False)
    )
    reached_safety = sum(1 for r in records if r.get("schema_valid") is True)

    print(f"Pilot run complete. Records written: {count}")
    print("Expected records: 20")
    print(f"Actual records: {len(records)}")
    print(f"Parse/schema failures: {parse_or_schema_failures}/{len(records) if records else 0}")
    print(f"Reached safety validation: {reached_safety}/{len(records) if records else 0}")
    print("Manual inspection required before Stage 2 full benchmark.")


if __name__ == "__main__":
    main()
