#!/usr/bin/env python3
"""Report external and evidentiary blockers that software tests cannot satisfy."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def build_payload(root: Path = ROOT) -> dict:
    """Derive readiness from current evidence files rather than fixed booleans."""
    sources = yaml.safe_load(
        (root / "data/public/source-registry.yaml").read_text(encoding="utf-8")
    )
    assumptions = yaml.safe_load(
        (root / "assumptions/assumptions.yaml").read_text(encoding="utf-8")
    )
    service_records = _load_yaml(root / "data/public/service-census-records.yaml")
    service_review = _load_yaml(root / "data/public/service-census-review.yaml")
    clinical_review = _load_yaml(root / "data/public/clinical-pathway-review.yaml")
    input_freeze = _load_yaml(root / "data/public/input-freeze.yaml")
    governance = _load_yaml(root / "data/public/governance-review.yaml")
    national_analysis = _load_yaml(root / "data/public/national-analysis-receipt.yaml")
    candidate_sources = [
        item["source_id"]
        for item in sources["sources"]
        if str(item["status"]).startswith("candidate")
    ]
    non_frozen = [
        item["id"]
        for item in assumptions["assumptions"]
        if item["status"]
        in {
            "illustrative",
            "synthetic_fixture",
            "placeholder_requires_source_freeze",
            "planned_public_input",
            "planned_method",
            "temporary_rate_requires_date_check",
            "requires_analysis_date_refresh",
        }
    ]
    governance_status = str(governance.get("status", ""))
    route_status = str(national_analysis.get("prerequisites", {}).get("route_costs", ""))
    calibration_status = str(national_analysis.get("calibration_status", ""))
    blockers = {
        "service_census_frozen": bool(service_records.get("freeze_date"))
        and str(service_review.get("status", "")).startswith("attested_"),
        "clinical_pathways_reviewed": clinical_review.get("status") == "reviewed",
        "public_inputs_licence_checked": (
            "approved_for_local_use_source_licence_gaps_remain"
            if input_freeze.get("status") == "frozen" and input_freeze.get("approval_receipt")
            else False
        ),
        "national_network_routing_complete": route_status == "complete",
        "aggregate_calibration_complete": calibration_status.startswith("complete_"),
        "maori_equity_governance_review_complete": (
            "not_required_for_scope"
            if governance_status == "out_of_scope_for_public_aggregate_harness"
            else governance_status == "complete"
        ),
        "ethics_scope_determination_archived": (
            "not_required_for_scope"
            if governance_status == "out_of_scope_for_public_aggregate_harness"
            else bool(governance.get("ethics_hdec_determination"))
        ),
        "candidate_source_ids": candidate_sources,
        "non_frozen_assumption_ids": non_frozen,
    }
    return {
        "publication_ready": False,
        "software_handover_ready": (root / "release/verification-receipt.json").exists(),
        "blockers": blockers,
    }


def main() -> None:
    payload = build_payload()
    output = ROOT / "release/publication-readiness.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
