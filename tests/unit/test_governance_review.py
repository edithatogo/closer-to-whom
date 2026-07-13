from pathlib import Path
from runpy import run_path

validate = run_path(
    Path(__file__).parents[2] / "scripts" / "check_governance_review.py",
    run_name="governance_review_test",
)["validate"]


def test_pending_governance_review_is_explicit(tmp_path: Path) -> None:
    path = tmp_path / "governance.yaml"
    path.write_text(
        """status: pending_external_review
review_scope: public_aggregate_policy_evaluation
required_outputs:
  - maori_equity_review_receipt
  - ethics_hdec_scope_determination
  - unresolved_equity_risks
  - culturally_safe_interpretation_constraints
review_receipts: []
unresolved_equity_risks: []
interpretation_constraints: []
ethics_hdec_determination: null
claim_boundary: Pending governance review; no endorsement, ethical approval, or future microdata authorisation.
""",
        encoding="utf-8",
    )
    assert validate(path) == []


def test_completed_governance_review_requires_evidence(tmp_path: Path) -> None:
    path = tmp_path / "governance.yaml"
    path.write_text(
        """status: reviewed
required_outputs: [maori_equity_review_receipt, ethics_hdec_scope_determination, unresolved_equity_risks, culturally_safe_interpretation_constraints]
review_receipts: [one]
unresolved_equity_risks: []
interpretation_constraints: []
ethics_hdec_determination: null
claim_boundary: Pending governance review; no endorsement, ethical approval, or future microdata authorisation.
""",
        encoding="utf-8",
    )
    failures = validate(path)
    assert any("both review receipts" in failure for failure in failures)
    assert any("unresolved equity risks" in failure for failure in failures)
