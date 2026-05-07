from __future__ import annotations

import pytest

from src.eval.comparison import aggregate_model_metrics
from src.eval.run_benchmark import run_benchmark

_REQUIRED_COLUMNS = [
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


def test_aggregate_returns_one_row_per_model(tmp_path) -> None:
    jsonl_path = tmp_path / "runs.jsonl"
    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(jsonl_path),
        models=["fake_slm", "fake_llm"],
    )
    rows = aggregate_model_metrics(str(jsonl_path))
    assert len(rows) == 2
    assert {r["model"] for r in rows} == {"fake_slm", "fake_llm"}


def test_aggregate_required_columns(tmp_path) -> None:
    jsonl_path = tmp_path / "runs.jsonl"
    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(jsonl_path),
        models=["fake_slm", "fake_llm"],
    )
    rows = aggregate_model_metrics(str(jsonl_path))
    for row in rows:
        assert list(row.keys()) == _REQUIRED_COLUMNS


def test_aggregate_rates_are_valid_floats(tmp_path) -> None:
    jsonl_path = tmp_path / "runs.jsonl"
    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(jsonl_path),
        models=["fake_slm", "fake_llm"],
    )
    rows = aggregate_model_metrics(str(jsonl_path))
    for row in rows:
        assert 0.0 <= row["schema_valid_rate"] <= 1.0
        assert 0.0 <= row["execution_eligible_rate"] <= 1.0


def test_aggregate_missing_file_raises(tmp_path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        aggregate_model_metrics(str(tmp_path / "nonexistent.jsonl"))
