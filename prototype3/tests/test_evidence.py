from __future__ import annotations

import pytest

from src.eval.evidence import generate_evidence_pack
from src.eval.run_benchmark import run_benchmark


def test_generate_evidence_pack_returns_required_keys(tmp_path) -> None:
    jsonl_path = tmp_path / "runs.jsonl"
    out_dir = tmp_path / "summaries"
    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(jsonl_path),
        models=["fake_slm", "fake_llm"],
    )

    pack = generate_evidence_pack(str(jsonl_path), str(out_dir))
    assert set(pack.keys()) == {
        "generated_at",
        "source_jsonl",
        "total_records",
        "per_model",
        "by_difficulty",
        "by_category",
        "rq4_summary",
    }


def test_generate_evidence_pack_creates_output_files(tmp_path) -> None:
    jsonl_path = tmp_path / "runs.jsonl"
    out_dir = tmp_path / "summaries"
    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(jsonl_path),
        models=["fake_slm", "fake_llm"],
    )

    generate_evidence_pack(str(jsonl_path), str(out_dir))
    assert (out_dir / "evidence_pack.json").exists()
    assert (out_dir / "evidence_by_difficulty.csv").exists()
    assert (out_dir / "evidence_by_category.csv").exists()


def test_generate_evidence_pack_rq4_rates_in_bounds(tmp_path) -> None:
    jsonl_path = tmp_path / "runs.jsonl"
    out_dir = tmp_path / "summaries"
    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(jsonl_path),
        models=["fake_slm", "fake_llm"],
    )

    pack = generate_evidence_pack(str(jsonl_path), str(out_dir))
    for _, rates in pack["rq4_summary"].items():
        assert 0.0 <= rates["false_accept_rate"] <= 1.0
        assert 0.0 <= rates["false_reject_rate"] <= 1.0
        assert 0.0 <= rates["correct_reject_rate"] <= 1.0


def test_generate_evidence_pack_missing_file_raises(tmp_path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        generate_evidence_pack(
            str(tmp_path / "nonexistent.jsonl"),
            str(tmp_path / "summaries"),
        )
