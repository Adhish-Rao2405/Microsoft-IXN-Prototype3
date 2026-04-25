import json

import pytest

from src.eval.benchmark_loader import load_benchmark


def test_load_benchmark_success() -> None:
    items = load_benchmark("datasets/benchmark_v1.json")
    assert len(items) == 30
    ids = {item["id"] for item in items}
    assert len(ids) == 30


def test_load_benchmark_missing_file() -> None:
    with pytest.raises(ValueError, match="does not exist"):
        load_benchmark("datasets/does_not_exist.json")


def test_load_benchmark_invalid_count(tmp_path) -> None:
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(json.dumps([{"id": "C01"}]), encoding="utf-8")

    with pytest.raises(ValueError, match="exactly 30"):
        load_benchmark(str(bad_file))


def test_load_benchmark_duplicate_id(tmp_path) -> None:
    item = {
        "id": "C01",
        "command": "Pick up the medicine cup",
        "difficulty": "clear",
        "category": "object_manipulation",
        "gold_label": "EXECUTE_EXACT",
        "gold_intent": {"actions": []},
        "uncertainty_expected": False,
        "allowed_behavior": "execute_if_schema_and_safety_valid",
        "semantic_pass_rule": "rule",
        "notes": "note",
    }
    bad_file = tmp_path / "dup.json"
    bad_file.write_text(json.dumps([item] * 30), encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate benchmark id"):
        load_benchmark(str(bad_file))
