"""Validate the explicit service capability matrix and unknown/absent boundary."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data/public/service-census-capabilities.yaml"
RECORDS = ROOT / "data/public/service-census-records.yaml"
REVIEW = ROOT / "data/public/service-census-review.yaml"
CLAIMS = {
    "facility_existence",
    "oncology_presence",
    "solid_tumour_sact",
    "iv_trastuzumab",
    "trastuzumab_sc",
    "phesgo_sc",
    "outreach",
    "consultation_only",
}
STATES = {"confirmed", "plausible", "unknown", "absent"}


def validate(
    matrix_path: Path = MATRIX,
    records_path: Path = RECORDS,
    review_path: Path = REVIEW,
) -> list[str]:
    matrix = yaml.safe_load(matrix_path.read_text(encoding="utf-8")) or {}
    records = yaml.safe_load(records_path.read_text(encoding="utf-8")) or {}
    review = yaml.safe_load(review_path.read_text(encoding="utf-8")) or {}
    failures: list[str] = []
    expected = {str(row.get("facility_id")) for row in records.get("records", [])}
    source_ids = {
        str(source_id)
        for row in (records.get("records") or [])
        if isinstance(row, dict)
        for source_id in (row.get("source_ids") or [])
    }
    reviewed_source_ids = {
        str(row.get("source_id"))
        for row in (review.get("review_records") or [])
        if isinstance(row, dict)
    }
    if source_ids != reviewed_source_ids - {
        "source.healthnz-hospital-finder",
        "source.licence-healthnz-copyright",
    }:
        failures.append("review queue must cover every census source exactly once")
    if review.get("status") != "pending_sole_developer_clinician_attestation":
        failures.append(
            "review queue must remain explicitly pending until sole-developer attestations exist"
        )
    governance = review.get("governance_model") or {}
    if governance.get("code_harness") != "sole_developer":
        failures.append("review queue must declare the sole-developer code harness")
    if governance.get("second_reviewer_required") is not False:
        failures.append("review queue must declare that a second reviewer is not required")
    if (review.get("licence_adjudication") or {}).get("status") != "adjudicated_for_site_text_only":
        failures.append("licence boundary must remain explicit and site-text-only")
    required_receipt_fields = {
        "role",
        "reviewer_name_or_organisation",
        "reviewed_on",
        "scope",
        "decision",
        "receipt_ref",
        "unresolved_questions",
    }
    raw_receipt_fields = (review.get("receipt_requirements") or {}).get("required_fields")
    declared_receipt_fields = (
        set(raw_receipt_fields) if isinstance(raw_receipt_fields, list) else set()
    )
    if declared_receipt_fields != required_receipt_fields:
        failures.append("review queue must declare the complete attestation receipt contract")
    actual_rows = matrix.get("records", [])
    actual = {str(row.get("facility_id")) for row in actual_rows}
    if expected != actual:
        failures.append("capability matrix facility IDs must match service census records")
    for row in actual_rows:
        facility_id = str(row.get("facility_id", ""))
        claims = row.get("claims")
        if not isinstance(claims, dict) or set(claims) != CLAIMS:
            failures.append(f"{facility_id}: capability claim keys are incomplete")
            continue
        if row.get("review_state") != "pending_sole_developer_review":
            failures.append(f"{facility_id}: review state must remain explicit")
        for claim, state in claims.items():
            if state not in STATES:
                failures.append(f"{facility_id}/{claim}: invalid capability state {state!r}")
        for claim in ("iv_trastuzumab", "trastuzumab_sc", "phesgo_sc"):
            if claims.get(claim) == "confirmed":
                failures.append(
                    f"{facility_id}/{claim}: drug-specific confirmation needs review receipt"
                )
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Service capability matrix failures:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("Validated explicit service capability states; unknown remains distinct from absent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
