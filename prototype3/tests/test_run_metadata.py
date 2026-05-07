from __future__ import annotations

import json
import re

from src.eval.run_metadata import collect_run_metadata

_REQUIRED_KEYS = {
    "timestamp_utc", "git_commit_hash", "dataset_path", "model",
    "python_version", "os_name", "os_version", "cpu_info", "cpu_count",
    "ram_gb", "planner_temperature", "planner_max_tokens",
    "planner_timeout_s", "foundry_endpoint",
}


def _sample_metadata() -> dict:
    return collect_run_metadata(
        dataset_path="datasets/benchmark_v1.json",
        model="fake_slm",
        timestamp="20260101T000000Z",
    )


def test_collect_run_metadata_returns_required_keys() -> None:
    meta = _sample_metadata()
    assert _REQUIRED_KEYS == set(meta.keys())


def test_collect_run_metadata_is_json_serializable() -> None:
    meta = _sample_metadata()
    encoded = json.dumps(meta)
    assert isinstance(encoded, str)


def test_collect_run_metadata_python_version_format() -> None:
    meta = _sample_metadata()
    assert re.match(r"^\d+\.\d+\.\d+$", meta["python_version"])


def test_collect_run_metadata_git_commit_is_hex_or_unavailable() -> None:
    meta = _sample_metadata()
    commit = meta["git_commit_hash"]
    assert commit == "unavailable" or re.match(r"^[0-9a-f]{40}$", commit)
