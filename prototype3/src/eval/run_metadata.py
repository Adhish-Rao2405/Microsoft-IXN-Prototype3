from __future__ import annotations

import os
import platform
import subprocess


def collect_run_metadata(
    *,
    dataset_path: str,
    model: str,
    timestamp: str,
    foundry_endpoint: str | None = None,
    planner_temperature: float | None = None,
    planner_max_tokens: int | None = None,
    planner_timeout_s: float | None = None,
) -> dict:
    """Collect reproducibility metadata for a benchmark run.

    Every collection step is wrapped in try/except so a missing binary,
    unavailable psutil, or restricted subprocess call never crashes the runner.
    All values are JSON-serializable (str, int, float, or None).
    """
    git_commit_hash: str
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        git_commit_hash = result.stdout.strip() or "unavailable"
    except Exception:
        git_commit_hash = "unavailable"

    try:
        python_version: str = platform.python_version()
    except Exception:
        python_version = "unavailable"

    try:
        os_name: str = platform.system()
    except Exception:
        os_name = "unavailable"

    try:
        os_version: str = platform.version()
    except Exception:
        os_version = "unavailable"

    try:
        cpu_info_raw = platform.processor()
        cpu_info: str = cpu_info_raw if cpu_info_raw else "unavailable"
    except Exception:
        cpu_info = "unavailable"

    try:
        cpu_count: int | None = os.cpu_count()
    except Exception:
        cpu_count = None

    ram_gb: float | None
    try:
        import psutil  # type: ignore[import]
        ram_gb = round(psutil.virtual_memory().total / 1e9, 1)
    except Exception:
        ram_gb = None

    return {
        "timestamp_utc": timestamp,
        "git_commit_hash": git_commit_hash,
        "dataset_path": dataset_path,
        "model": model,
        "python_version": python_version,
        "os_name": os_name,
        "os_version": os_version,
        "cpu_info": cpu_info,
        "cpu_count": cpu_count,
        "ram_gb": ram_gb,
        "planner_temperature": planner_temperature,
        "planner_max_tokens": planner_max_tokens,
        "planner_timeout_s": planner_timeout_s,
        "foundry_endpoint": foundry_endpoint,
    }
