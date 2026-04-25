import json

import pytest

from src.eval.metrics_logger import write_run_record


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
