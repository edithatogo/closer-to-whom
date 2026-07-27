from __future__ import annotations

import json
from pathlib import Path
from runpy import run_path

import pytest
import yaml

module = run_path("scripts/check_contracts.py", run_name="conductor_contract_test")
check_conductor = module["check_conductor"]


def write_context(
    root: Path, *, active_track: str | None, status: str, next_tracks: list[str]
) -> None:
    conductor = root / "conductor"
    conductor.mkdir(parents=True)
    (conductor / "project.yaml").write_text(
        yaml.safe_dump({"project_id": "example"}), encoding="utf-8"
    )
    (conductor / "state.yaml").write_text(
        yaml.safe_dump(
            {
                "project_id": "example",
                "active_track": active_track,
                "next_tracks": next_tracks,
            }
        ),
        encoding="utf-8",
    )
    (conductor / "task-graph.json").write_text(
        json.dumps({"nodes": [{"id": "track-1", "status": status}], "edges": []}),
        encoding="utf-8",
    )


def test_conductor_allows_completed_graph_without_active_track(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_context(tmp_path, active_track=None, status="completed", next_tracks=[])
    monkeypatch.setitem(check_conductor.__globals__, "ROOT", tmp_path)
    check_conductor()


def test_conductor_rejects_incomplete_graph_without_active_track(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_context(tmp_path, active_track=None, status="active", next_tracks=["track-1"])
    monkeypatch.setitem(check_conductor.__globals__, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="completed graph"):
        check_conductor()


def test_conductor_requires_active_node_to_match_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_context(tmp_path, active_track="track-1", status="completed", next_tracks=[])
    monkeypatch.setitem(check_conductor.__globals__, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="node is not active"):
        check_conductor()
