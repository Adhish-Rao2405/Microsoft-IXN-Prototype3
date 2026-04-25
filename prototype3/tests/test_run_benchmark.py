import json
from pathlib import Path

from src.eval.run_benchmark import run_benchmark


def test_run_benchmark_generates_records_for_both_models(tmp_path) -> None:
    output_path = tmp_path / "runs" / "benchmark.jsonl"

    count = run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(output_path),
        models=["fake_slm", "fake_llm"],
    )

    assert count == 60
    assert output_path.exists()

    lines = output_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 60

    entries = [json.loads(line) for line in lines]
    models = {entry["model"] for entry in entries}
    assert models == {"fake_slm", "fake_llm"}

    command_ids = {entry["command_id"] for entry in entries}
    assert len(command_ids) == 30

    # Ensure at least one key field is present and typed as expected.
    assert isinstance(entries[0]["semantic_score"], float)
    assert "run_id" in entries[0]
