#!/usr/bin/env python3
"""Derive public aggregate publication readiness from current evidence receipts."""

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
    """Derive readiness without treating unused synthetic demo assumptions as blockers."""
    sources = _load_yaml(root / "data/public/source-registry.yaml")
    assumptions = _load_yaml(root / "assumptions/assumptions.yaml")
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
    legacy_non_publication = [
        item["id"]
        for item in assumptions["assumptions"]
        if item["status"] in {"illustrative", "synthetic_fixture"}
    ]
    unresolved_publication = [
        item["id"]
        for item in assumptions["assumptions"]
        if item["status"]
        in {
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
    analysis_status = str(national_analysis.get("status", ""))
    input_authorized = input_freeze.get("status") == "frozen" and bool(
        input_freeze.get("approval_receipt")
    )
    blockers = {
        "service_census_frozen": bool(service_records.get("freeze_date"))
        and str(service_review.get("status", "")).startswith("attested_"),
        "clinical_pathways_reviewed": clinical_review.get("status") == "reviewed",
        "public_inputs_licence_checked": (
            "approved_derived_aggregate_nonredistribution" if input_authorized else False
        ),
        "national_network_routing_complete": route_status == "complete",
        "aggregate_calibration_complete": calibration_status.startswith("complete_"),
        "national_analysis_complete": analysis_status == "completed",
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
        "unresolved_publication_assumption_ids": unresolved_publication,
        "legacy_non_publication_assumption_ids": legacy_non_publication,
    }
    required = (
        blockers["service_census_frozen"],
        blockers["clinical_pathways_reviewed"],
        blockers["public_inputs_licence_checked"],
        blockers["national_network_routing_complete"],
        blockers["aggregate_calibration_complete"],
        blockers["national_analysis_complete"],
        blockers["maori_equity_governance_review_complete"],
        blockers["ethics_scope_determination_archived"],
        not unresolved_publication,
    )
    return {
        "publication_ready": all(bool(item) for item in required),
        "software_handover_ready": (root / "release/verification-receipt.json").exists(),
        "blockers": blockers,
        "claim_boundary": (
            "Readiness covers the reviewed five-report public aggregate static payload only. "
            "Legacy synthetic demonstrations remain outside publication and do not establish "
            "service capability, observed capacity, clinical guidance, or policy preference."
        ),
    }


def main() -> None:
    payload = build_payload()
    output = ROOT / "release/publication-readiness.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
