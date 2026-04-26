from __future__ import annotations

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
OUTPUT_PATH = Path("results/full/full_benchmark.jsonl")


def main() -> None:
    count = run_benchmark(
        output_path=str(OUTPUT_PATH),
        models=FULL_MODELS,
    )
    print(f"Full benchmark complete. Records written: {count}")
    print("Expected records: 60")


if __name__ == "__main__":
    main()
