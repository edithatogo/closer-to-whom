#!/usr/bin/env python3
"""Materialize evidence-bounded treatment and delivery-setting scenario definitions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from closer_to_whom.pathways import default_synthetic_pathways, pathway_summary


def _resource_profiles() -> dict[str, dict[str, Any]]:
    profiles = {}
    for pathway in default_synthetic_pathways():
        summary = pathway_summary(pathway)
        profiles[str(summary["formulation"])] = {
            "pathway_id": summary["pathway_id"],
            "expected_administrations": summary["expected_administrations"],
            "course_on_site_minutes": summary["course_on_site_minutes"],
            "hospital_required_visits": summary["hospital_required_visits"],
            "home_eligible_visits": summary["home_eligible_visits"],
            "profile_status": "synthetic_clinical_fixture_only",
        }
    return profiles


def materialize(catalogue: Path, output: Path) -> None:
    payload = yaml.safe_load(catalogue.read_text(encoding="utf-8"))
    resource_profiles = _resource_profiles()
    scenarios: list[dict[str, Any]] = []
    for source in payload.get("scenarios", []):
        kind = str(source["kind"])
        if kind == "current_documented":
            status = "definition_only_current_documented_evidence"
        elif kind in {"commissioning_counterfactual", "infrastructure_exploratory"}:
            status = "definition_only_not_estimated_counterfactual"
        else:
            status = "definition_only_evidence_pending"
        scenarios.append(
            {
                "scenario_id": source["scenario_id"],
                "name": source["name"],
                "kind": kind,
                "status": status,
                "allowed_delivery_modes": source["allowed_delivery_modes"],
                "allowed_formulations": source["allowed_formulations"],
                "evidence_grade_threshold": source["evidence_grade_threshold"],
                "candidate_site_count": source["candidate_site_count"],
                "capacity_envelope": source["capacity_envelope"],
                "capability_state": "unknown",
                "clinical_eligibility_state": "not_estimated",
                "resource_profiles": [
                    resource_profiles[formulation]
                    for formulation in source["allowed_formulations"]
                    if formulation in resource_profiles
                ],
                "patient_travel_status": "not_estimated",
                "provider_travel_status": "not_estimated",
            }
        )
    result = {
        "schema_version": "1.0.0",
        "generated_at": "derived_from_scenario_catalogue",
        "status": "materialized_evidence_bounded_scenario_register",
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "resource_profile_scope": "Synthetic pathway profiles only; no national treatment mix or capability is inferred.",
        "claim_boundary": (
            "Scenario definitions are aggregate policy-model inputs. They do not establish funding, "
            "clinical eligibility, service capability, observed capacity, or operational feasibility."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, default=Path("scenarios/scenario-catalogue.yaml"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/national-analysis/treatment-delivery-scenarios.json"),
    )
    args = parser.parse_args()
    materialize(args.catalogue, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
