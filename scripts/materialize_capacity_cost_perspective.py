#!/usr/bin/env python3
"""Package aggregate workload and source-backed travel-resource perspectives."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from closer_to_whom.pathways import default_synthetic_pathways, pathway_summary

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected JSON object: {path}")
    return value


def build_report(scenario_path: Path, demand_path: Path, costs_path: Path) -> dict[str, Any]:
    scenario = _load(scenario_path)
    demand = _load(demand_path)
    _load(costs_path)
    total_courses = float(demand["materialized_expected_courses"])
    capacity_assumptions = {
        "working_days_per_year": 240.0,
        "productive_hours_per_fte_year": 1500.0,
        "active_nursing_fraction_of_on_site_time": 0.45,
        "chair_utilisation_target": 0.80,
        "peak_to_mean_factor": 1.25,
    }
    treatment_envelopes = []
    for pathway in default_synthetic_pathways():
        profile = pathway_summary(pathway)
        annual_administrations = total_courses * float(profile["expected_administrations"])
        annual_patient_visits = annual_administrations
        annual_on_site_minutes = total_courses * float(profile["course_on_site_minutes"])
        annual_chair_hours = annual_on_site_minutes / 60.0
        annual_nursing_hours = (
            annual_chair_hours * capacity_assumptions["active_nursing_fraction_of_on_site_time"]
        )
        mean_visits_per_day = annual_patient_visits / capacity_assumptions["working_days_per_year"]
        treatment_envelopes.append(
            {
                "pathway_id": profile["pathway_id"],
                "formulation": profile["formulation"],
                "annual_expected_courses": total_courses,
                "annual_administrations": annual_administrations,
                "annual_patient_visits": annual_patient_visits,
                "annual_on_site_minutes": annual_on_site_minutes,
                "annual_chair_hours": annual_chair_hours,
                "annual_active_nursing_hours": annual_nursing_hours,
                "implied_chair_fte_equivalent": annual_chair_hours
                / (
                    capacity_assumptions["productive_hours_per_fte_year"]
                    * capacity_assumptions["chair_utilisation_target"]
                ),
                "implied_nursing_fte": annual_nursing_hours
                / capacity_assumptions["productive_hours_per_fte_year"],
                "peak_equivalent_visits_per_day": mean_visits_per_day
                * capacity_assumptions["peak_to_mean_factor"],
                "profile_status": "synthetic_clinical_fixture_envelope_only",
            }
        )
    configurations = []
    for row in scenario["configurations"]:
        configurations.append(
            {
                "configuration_id": row["configuration_id"],
                "candidate_site_count": row["candidate_site_count"],
                "expected_annual_courses": total_courses,
                "expected_courses_per_candidate_site": total_courses / row["candidate_site_count"],
                "expected_annual_round_trip_km": row["expected_annual_round_trip_km"],
                "vehicle_resource_cost_nzd": row["vehicle_resource_cost_nzd"],
            }
        )
    cost_ledgers = {
        "patient_direct": {
            "status": "not_estimated",
            "components": ["treatment_drug_and_administration_cost", "patient_out_of_pocket_cost"],
            "reason": "No national treatment mix or tariff receipt is available in the frozen public inputs.",
        },
        "whanau_time": {
            "status": "not_estimated",
            "components": ["whanau_travel_time", "caregiving_time"],
            "reason": "No source-backed national time valuation has been selected.",
        },
        "provider": {
            "status": "not_estimated",
            "components": ["provider_travel", "provider_time"],
            "reason": "Provider capability, staffing, and travel are unknown.",
        },
        "facility": {
            "status": "not_estimated",
            "components": ["facility_overhead", "chair_capacity"],
            "reason": "Observed capacity and facility cost data are unavailable.",
        },
        "patient_vehicle_resource": {
            "status": "source_backed_scenario",
            "components": ["private_vehicle_distance_resource_cost"],
            "basis": "travel_cost_parameters.json",
        },
        "patient_other_transport": {
            "status": "not_estimated",
            "components": ["public_transport_fares", "parking"],
            "reason": "No national mode split or fare/parking receipt is available.",
        },
    }
    return {
        "schema_version": "1.0.0",
        "status": "materialized_implied_workload_and_partial_travel_resource_perspective",
        "analysis_population": "aggregate_expected_course_cells",
        "configurations": configurations,
        "treatment_pathway_envelopes": treatment_envelopes,
        "capacity_assumptions": capacity_assumptions,
        "cost_ledgers": cost_ledgers,
        "capacity_status": "not_estimable_observed_capacity_and_staffing_unknown",
        "unpriced_cost_components": [
            "treatment_drug_and_administration_cost",
            "facility_overhead",
            "provider_travel",
            "public_transport_fares",
            "parking",
        ],
        "cost_scope": "private_vehicle_resource_cost_scenario_only",
        "source_inputs": {
            "scenario_summary": scenario_path.as_posix(),
            "national_demand_cells": demand_path.as_posix(),
            "travel_cost_parameters": costs_path.as_posix(),
            "scenario_summary_sha256": hashlib.sha256(scenario_path.read_bytes()).hexdigest(),
            "national_demand_cells_sha256": hashlib.sha256(demand_path.read_bytes()).hexdigest(),
            "travel_cost_parameters_sha256": hashlib.sha256(costs_path.read_bytes()).hexdigest(),
            "pathway_source_id": "synthetic.clinical-fixture",
        },
        "claim_boundary": (
            "Expected courses are aggregate model cells, not patients or observed workload. "
            "Per-site values are arithmetic workload envelopes, not staffing requirements or capacity. "
            "Vehicle costs are a source-backed private-vehicle resource scenario; omitted cost components "
            "remain unpriced and no operational or policy recommendation is made."
            " Treatment pathway envelopes use synthetic clinical fixtures and are not estimates of "
            "actual treatment mix, staffing, capacity, or service workload."
        ),
        "observed_capacity": "unknown",
        "operational_recommendation": False,
        "generated_at": "derived_from_frozen_national_inputs",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario", type=Path, default=ROOT / "reports/national-analysis/scenario_summary.json"
    )
    parser.add_argument("--demand", type=Path, default=ROOT / "reports/national-demand-cells.json")
    parser.add_argument("--costs", type=Path, default=ROOT / "reports/travel-cost-parameters.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports/national-analysis/capacity-cost-perspective.json",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_report(args.scenario, args.demand, args.costs), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()
