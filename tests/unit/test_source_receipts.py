from pathlib import Path
from runpy import run_path

validate = run_path(
    Path(__file__).parents[2] / "scripts" / "check_source_receipts.py",
    run_name="source_receipts_test",
)["validate"]


def _registry(tmp_path: Path, extra: str = "") -> Path:
    path = tmp_path / "source-registry.yaml"
    path.write_text(
        """sources:
  - source_id: source.example
    title: Example source
    publisher: Example publisher
    url: https://example.com/data.csv
    retrieved_on: 2026-07-13
    licence_state: open
    redistribution_allowed: false
    status: candidate_requires_capture
"""
        + extra,
        encoding="utf-8",
    )
    return path


def test_pending_candidate_does_not_claim_a_receipt(tmp_path: Path) -> None:
    assert validate(_registry(tmp_path)) == []


def test_captured_source_requires_receipt_and_evidence_grade(tmp_path: Path) -> None:
    registry = _registry(
        tmp_path,
        """    status: captured
    receipt_path: missing-receipt.json
""",
    )
    failures = validate(registry)
    assert any("receipt does not exist" in failure for failure in failures)
    assert any("evidence_grade" in failure for failure in failures)


def test_receipt_must_match_registry(tmp_path: Path) -> None:
    receipt = tmp_path / "receipt.json"
    receipt.write_text(
        """{
  "source_id": "other",
  "url": "https://example.net/other.csv",
  "retrieved_unix_seconds": 1783728000,
  "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "bytes": 12,
  "content_type": "text/csv",
  "output_path": "data/raw/source.example/data.csv"
}
""",
        encoding="utf-8",
    )
    registry = _registry(
        tmp_path,
        f"""    status: captured
    evidence_grade: 2
    receipt_path: {receipt.name}
""",
    )
    failures = validate(registry)
    assert any("source_id" in failure for failure in failures)
    assert any("URL" in failure for failure in failures)
