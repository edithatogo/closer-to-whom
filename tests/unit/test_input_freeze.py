from pathlib import Path
from runpy import run_path

validate = run_path(
    Path(__file__).parents[2] / "scripts" / "check_input_freeze.py",
    run_name="input_freeze_test",
)["validate"]


def _registry(tmp_path: Path) -> Path:
    path = tmp_path / "source-registry.yaml"
    path.write_text(
        """sources:
  - source_id: source.example
    title: Example
""",
        encoding="utf-8",
    )
    return path


def test_pending_manifest_is_explicitly_valid(tmp_path: Path) -> None:
    manifest = tmp_path / "input-freeze.yaml"
    manifest.write_text(
        """status: pending
inputs:
  - input_id: geography
    title: Geography
    source_ids: [source.example]
    version: null
    licence_state: unknown
    evidence_grade: pending
    status: pending
""",
        encoding="utf-8",
    )
    assert validate(manifest, _registry(tmp_path)) == []


def test_frozen_manifest_requires_evidence_and_receipt(tmp_path: Path) -> None:
    manifest = tmp_path / "input-freeze.yaml"
    manifest.write_text(
        """status: frozen
freeze_date: 2026-07-13
inputs:
  - input_id: geography
    title: Geography
    source_ids: [source.example]
    version: null
    licence_state: unknown
    evidence_grade: pending
    status: frozen
""",
        encoding="utf-8",
    )
    failures = validate(manifest, _registry(tmp_path))
    assert any("version" in failure for failure in failures)
    assert any("retrieval_receipt" in failure for failure in failures)
    assert any("evidence_grade" in failure for failure in failures)
