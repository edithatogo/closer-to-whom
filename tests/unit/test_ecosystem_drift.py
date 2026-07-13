from pathlib import Path
from runpy import run_path

build_report = run_path(
    str(Path(__file__).parents[2] / "scripts" / "check_ecosystem_drift.py"),
    run_name="ecosystem_drift_test",
)["build_report"]


def test_ecosystem_drift_reports_metadata_changes_without_mutating_registry(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        """repositories:
  - repository: https://github.com/example/project
    default_branch: main
    archived: false
    fork: false
    license_spdx: MIT
    updated_at: 2026-07-01T00:00:00Z
""",
        encoding="utf-8",
    )
    snapshot = tmp_path / "snapshot.yaml"
    snapshot.write_text("snapshot_date: '2026-07-01'\n", encoding="utf-8")

    def fetcher(path: str) -> dict[str, object]:
        assert path == "example/project"
        return {
            "default_branch": "trunk",
            "archived": False,
            "fork": False,
            "license": {"spdx_id": "MIT"},
            "updated_at": "2026-07-02T00:00:00Z",
        }

    report = build_report(registry, snapshot, fetcher=fetcher)
    assert report["snapshot_date"] == "2026-07-01"
    assert report["changes"][0]["repository"] == "example/project"  # type: ignore[index]
    assert registry.read_text(encoding="utf-8").count("trunk") == 0


def test_ecosystem_drift_records_unavailable_repository(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        "repositories: [{repository: https://github.com/example/project}]\n", encoding="utf-8"
    )
    snapshot = tmp_path / "snapshot.yaml"
    snapshot.write_text("snapshot_date: '2026-07-01'\n", encoding="utf-8")

    def fetcher(path: str) -> dict[str, object]:
        raise OSError(f"offline: {path}")

    report = build_report(registry, snapshot, fetcher=fetcher)
    assert report["changes"] == []
    assert report["unavailable"][0]["repository"] == "example/project"  # type: ignore[index]
