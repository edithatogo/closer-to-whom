#!/usr/bin/env python3
"""Package aggregate workload and source-backed travel-resource perspectives."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

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
    return {
        "schema_version": "1.0.0",
        "status": "materialized_implied_workload_and_partial_travel_resource_perspective",
        "analysis_population": "aggregate_expected_course_cells",
        "configurations": configurations,
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
        },
        "claim_boundary": (
            "Expected courses are aggregate model cells, not patients or observed workload. "
            "Per-site values are arithmetic workload envelopes, not staffing requirements or capacity. "
            "Vehicle costs are a source-backed private-vehicle resource scenario; omitted cost components "
            "remain unpriced and no operational or policy recommendation is made."
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
