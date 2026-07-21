"""Validate the explicit service capability matrix and unknown/absent boundary."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data/public/service-census-capabilities.yaml"
RECORDS = ROOT / "data/public/service-census-records.yaml"
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


def validate(matrix_path: Path = MATRIX, records_path: Path = RECORDS) -> list[str]:
    matrix = yaml.safe_load(matrix_path.read_text(encoding="utf-8")) or {}
    records = yaml.safe_load(records_path.read_text(encoding="utf-8")) or {}
    failures: list[str] = []
    expected = {str(row.get("facility_id")) for row in records.get("records", [])}
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
        if row.get("review_state") != "pending_external_review":
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
