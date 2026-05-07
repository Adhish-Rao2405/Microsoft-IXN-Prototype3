import json

import pytest

from src.eval.metrics_logger import write_run_record, write_summary_csv


def test_write_run_record_appends_jsonl(tmp_path) -> None:
    out_path = tmp_path / "logs" / "runs.jsonl"

    first = {"run_id": "r1", "semantic_score": 1.0}
    second = {"run_id": "r2", "semantic_score": 0.0}

    write_run_record(str(out_path), first)
    write_run_record(str(out_path), second)

    lines = out_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["run_id"] == "r1"
    assert json.loads(lines[1])["run_id"] == "r2"


def test_write_run_record_requires_dict(tmp_path) -> None:
    with pytest.raises(ValueError, match="dictionary"):
        write_run_record(str(tmp_path / "x.jsonl"), ["not", "a", "dict"])


def test_write_run_record_requires_json_serializable(tmp_path) -> None:
    bad = {"run_id": "r1", "non_serializable": {1, 2, 3}}
    with pytest.raises(ValueError, match="JSON serializable"):
        write_run_record(str(tmp_path / "x.jsonl"), bad)


_EXPECTED_CSV_COLUMNS = [
    "run_id", "command_id", "command_text", "category", "difficulty",
    "gold_label", "model", "schema_valid", "semantic_score",
    "semantic_failure_mode", "rejected", "execution_eligible",
    "failure_mode", "latency_ms",
]


def test_write_summary_csv_produces_correct_columns(tmp_path) -> None:
    jsonl_path = tmp_path / "runs.jsonl"
    record = {
        "run_id": "r1",
        "command_id": "C01",
        "command_text": "pick medicine cup",
        "category": "object_manipulation",
        "difficulty": "easy",
        "gold_label": "EXECUTE_EXACT",
        "model": "fake_slm",
        "schema_valid": True,
        "semantic_score": 1.0,
        "semantic_failure_mode": "exact_match",
        "rejected": False,
        "execution_eligible": True,
        "failure_mode": None,
        "latency_ms": 5,
    }
    jsonl_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    csv_path = tmp_path / "summary.csv"
    row_count = write_summary_csv(str(jsonl_path), str(csv_path))

    assert row_count == 1
    assert csv_path.exists()

    import csv
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert list(reader.fieldnames) == _EXPECTED_CSV_COLUMNS
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["run_id"] == "r1"
    assert rows[0]["category"] == "object_manipulation"


def test_write_summary_csv_missing_file_raises(tmp_path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        write_summary_csv(str(tmp_path / "nonexistent.jsonl"), str(tmp_path / "out.csv"))


def test_write_summary_csv_row_count_matches_jsonl(tmp_path) -> None:
    from src.eval.run_benchmark import run_benchmark

    jsonl_path = tmp_path / "runs.jsonl"
    run_benchmark(
        dataset_path="datasets/benchmark_v1.json",
        output_path=str(jsonl_path),
        models=["fake_slm"],
    )

    csv_path = tmp_path / "summary.csv"
    row_count = write_summary_csv(str(jsonl_path), str(csv_path))

    assert row_count == 30

    import csv as csv_mod
    with csv_path.open(encoding="utf-8") as f:
        reader = csv_mod.DictReader(f)
        rows = list(reader)
    assert len(rows) == 30


def test_write_comparison_csv_column_order(tmp_path) -> None:
    import csv as csv_mod
    from src.eval.metrics_logger import write_comparison_csv

    jsonl_path = tmp_path / "runs.jsonl"
    records = [
        {
            "model": "model_a", "schema_valid": True, "execution_eligible": True,
            "semantic_failure_mode": "exact_match", "latency_ms": 10,
        },
        {
            "model": "model_b", "schema_valid": False, "execution_eligible": False,
            "semantic_failure_mode": "false_accept", "latency_ms": 20,
        },
    ]
    import json as _json
    jsonl_path.write_text(
        "\n".join(_json.dumps(r) for r in records) + "\n", encoding="utf-8"
    )

    csv_path = tmp_path / "comparison.csv"
    write_comparison_csv(str(jsonl_path), str(csv_path))

    with csv_path.open(encoding="utf-8") as f:
        reader = csv_mod.DictReader(f)
        assert list(reader.fieldnames) == [
            "model", "total_records", "schema_valid_count", "schema_valid_rate",
            "execution_eligible_count", "execution_eligible_rate",
            "false_accept_count", "false_reject_count", "correct_reject_count",
            "mean_latency_ms",
        ]


def test_write_comparison_csv_missing_file_raises(tmp_path) -> None:
    from src.eval.metrics_logger import write_comparison_csv
    with pytest.raises(ValueError, match="does not exist"):
        write_comparison_csv(
            str(tmp_path / "nonexistent.jsonl"), str(tmp_path / "out.csv")
        )
