#!/usr/bin/env python3
"""Fail closed when Conductor graph, state, track files, or test count drift."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> None:
    state = _load(ROOT / "conductor/state.yaml")
    graph = json.loads((ROOT / "conductor/task-graph.json").read_text(encoding="utf-8"))
    ids = {str(node["id"]): str(node["status"]) for node in graph["nodes"]}
    track_root = ROOT / "conductor/tracks"
    missing = [
        node_id
        for node_id in ids
        if not (
            (track_root / f"{node_id}.yaml").exists()
            or (track_root / node_id).is_dir()
            or (ROOT / "conductor/receipts" / f"{node_id}.json").exists()
        )
    ]
    if missing:
        raise SystemExit(f"Conductor nodes without track files: {sorted(missing)}")
    active = state.get("active_track")
    if active and ids.get(active) != "active":
        raise SystemExit(f"Active track is not active in graph: {active}")
    result = subprocess.run(
        ["pytest", "--collect-only", "-q", "--no-cov"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("Unable to collect tests for Conductor test-count coherence")
    output = f"{result.stdout}\n{result.stderr}"
    lines = [line for line in output.splitlines() if "tests collected" in line]
    if not lines:
        raise SystemExit("Pytest collection did not report a test count")
    collected = int(lines[-1].split()[0])
    recorded = int(state["verification_status"]["tests"])
    if recorded != collected:
        raise SystemExit(f"Conductor test count {recorded} != collected tests {collected}")
    print(f"Conductor coherence passed: {len(ids)} nodes, {collected} collected tests.")


if __name__ == "__main__":
    main()
