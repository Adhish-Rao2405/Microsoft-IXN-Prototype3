from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.eval.run_benchmark import run_benchmark


FULL_MODELS = [
    "foundry:qwen2.5-coder-0.5b:cpu",
    "foundry:qwen2.5-coder-7b:cpu",
]
PILOT_PATH = Path("results/pilot/pilot.jsonl")
OUTPUT_PATH = Path("results/full/full_benchmark.jsonl")


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines()]


def _pilot_gate_check(records: list[dict]) -> tuple[bool, list[str]]:
    failures: list[str] = []

    if len(records) != 20:
        failures.append(f"pilot record count must be 20, got {len(records)}")

    missing_latency = sum(
        1
        for record in records
        if "planning_latency_ms" not in record or record.get("planning_latency_ms") is None
    )
    if missing_latency > 0:
        failures.append(f"planning_latency_ms missing in {missing_latency} pilot records")

    total = len(records)
    if total > 0:
        parse_or_schema_failures = sum(
            1
            for record in records
            if record.get("failure_mode") in {"parse_error", "schema_error"}
            or (record.get("schema_valid") is False)
        )
        failure_rate = parse_or_schema_failures / total
        if failure_rate >= 0.5:
            failures.append(
                "parse/schema failure rate must be below 50% "
                f"(got {parse_or_schema_failures}/{total} = {failure_rate:.1%})"
            )

        reached_safety = sum(1 for record in records if record.get("schema_valid") is True)
        safety_rate = reached_safety / total
        if safety_rate < 0.5:
            failures.append(
                "at least 50% of pilot records must reach safety validation "
                f"(got {reached_safety}/{total} = {safety_rate:.1%})"
            )
    else:
        failures.append("pilot file is empty")

    return len(failures) == 0, failures


def main() -> None:
    pilot_records = _load_jsonl(PILOT_PATH)
    gate_passed, gate_failures = _pilot_gate_check(pilot_records)

    if not gate_passed:
        print("Pilot gate failed. Do not run full benchmark until Foundry Local is reachable and pilot quality thresholds pass.")
        print("Pilot gate summary:")
        for failure in gate_failures:
            print(f"- {failure}")
        sys.exit(1)

    count = run_benchmark(
        output_path=str(OUTPUT_PATH),
        models=FULL_MODELS,
    )
    print(f"Full benchmark complete. Records written: {count}")
    print("Expected records: 60")


if __name__ == "__main__":
    main()
