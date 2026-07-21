from pathlib import Path
from runpy import run_path

validate = run_path(
    str(Path(__file__).parents[2] / "scripts" / "check_publication_gate.py"),
    run_name="publication_gate_test",
)["validate"]


def test_publication_gate_is_blocked_by_default(tmp_path: Path) -> None:
    path = tmp_path / "publication.yaml"
    path.write_text(
        """status: blocked_on_national_analysis
required_evidence:
  national_analysis_receipt: blocked_on_prerequisites
  source_and_licence_receipts: pending
  clinical_review_receipt: pending_external_review
  governance_review_receipt: pending_external_review
  aggregate_artifact_review: pending
  space_credential: not_configured
  promotion_receipt: not_promoted
required_artifacts: [release/verification-receipt.json, release/publication-readiness.json, release/source-manifest.json]
prohibited_content: [individual health data, confidential health-service data, live Healthpoint payloads, row-level clinical records]
claim_boundary: blocked; aggregate synthetic harness only; no service capability or authorisation.
""",
        encoding="utf-8",
    )
    assert validate(path) == []


def test_publication_gate_requires_completed_evidence(tmp_path: Path) -> None:
    path = tmp_path / "publication.yaml"
    path.write_text(
        """status: ready_for_review
required_evidence:
  national_analysis_receipt: completed
  source_and_licence_receipts: complete
  clinical_review_receipt: pending_external_review
  governance_review_receipt: pending_external_review
  aggregate_artifact_review: pending
  space_credential: not_configured
  promotion_receipt: not_promoted
required_artifacts: [release/verification-receipt.json, release/publication-readiness.json, release/source-manifest.json]
prohibited_content: [individual health data, confidential health-service data, live Healthpoint payloads, row-level clinical records]
claim_boundary: blocked; aggregate synthetic harness only; no service capability or authorisation.
""",
        encoding="utf-8",
    )
    assert any("every evidence receipt" in failure for failure in validate(path))
