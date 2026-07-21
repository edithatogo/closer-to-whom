from pathlib import Path
from runpy import run_path

validate = run_path(
    Path(__file__).parents[2] / "scripts" / "check_clinical_review_receipt.py",
    run_name="clinical_review_receipt_test",
)["validate"]


def test_pending_sole_developer_attestation_is_valid(tmp_path: Path) -> None:
    path = tmp_path / "review.yaml"
    path.write_text(
        """status: pending_sole_developer_clinician_attestation
required_attestation_scopes: [medical_oncology]
attestation_receipts: []
decisions: []
claim_boundary: Synthetic pathway fixtures remain unreviewed.
""",
        encoding="utf-8",
    )
    assert validate(path) == []


def test_reviewed_receipt_requires_all_roles(tmp_path: Path) -> None:
    path = tmp_path / "review.yaml"
    path.write_text(
        """status: reviewed
required_reviewers: [medical_oncology, nursing]
reviewers:
  - role: medical_oncology
    receipt_ref: review-1
    reviewed_on: 2026-07-13
decisions: [retain_safety_constraints]
claim_boundary: Synthetic pathway fixtures remain unreviewed.
""",
        encoding="utf-8",
    )
    failures = validate(path)
    assert any("nursing" in failure for failure in failures)
