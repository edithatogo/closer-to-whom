#!/usr/bin/env python3
"""Report external and evidentiary blockers that software tests cannot satisfy."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    sources = yaml.safe_load(
        (ROOT / "data/public/source-registry.yaml").read_text(encoding="utf-8")
    )
    assumptions = yaml.safe_load(
        (ROOT / "assumptions/assumptions.yaml").read_text(encoding="utf-8")
    )
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
    blockers = {
        "service_census_frozen": False,
        "clinical_pathways_reviewed": False,
        "public_inputs_licence_checked": False,
        "national_network_routing_complete": False,
        "aggregate_calibration_complete": False,
        "maori_equity_governance_review_complete": False,
        "ethics_scope_determination_archived": False,
        "candidate_source_ids": candidate_sources,
        "non_frozen_assumption_ids": non_frozen,
    }
    payload = {
        "publication_ready": False,
        "software_handover_ready": (ROOT / "release/verification-receipt.json").exists(),
        "blockers": blockers,
    }
    output = ROOT / "release/publication-readiness.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
