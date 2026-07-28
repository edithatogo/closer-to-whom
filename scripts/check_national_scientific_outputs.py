#!/usr/bin/env python3
"""Validate the cross-report scientific contract for national outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports/national-analysis"
REPORTS = (
    "scenario_summary",
    "optimisation_frontier",
    "uncertainty_analysis",
    "mcda_outputs",
    "voi_outputs",
    "distributional-equity",
    "capacity-cost-perspective",
    "resilience-sensitivity",
)


def _load(name: str) -> dict[str, Any]:
    path = REPORT_DIR / f"{name}.json"
    if not path.exists():
        raise ValueError(f"Missing national report: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"National report is not an object: {name}")
    return payload


def validate() -> dict[str, Any]:
    reports = {name: _load(name) for name in REPORTS}
    for name, payload in reports.items():
        if payload.get("operational_recommendation") is not False:
            raise ValueError(f"{name} crosses the operational recommendation boundary")
        if not payload.get("claim_boundary"):
            raise ValueError(f"{name} lacks a claim boundary")
        if payload.get("analysis_population") != "aggregate_expected_course_cells":
            raise ValueError(f"{name} lacks the aggregate analysis population contract")
    equity = reports["distributional-equity"]
    if set(equity.get("dimensions", [])) != {"deprivation_quintile", "rurality"}:
        raise ValueError("Distributional report must cover deprivation and rurality")
    if "unknown" not in {row.get("group") for row in equity.get("rows", [])}:
        raise ValueError("Distributional report must retain explicit unknown groups")
    if "ecological" not in str(equity.get("claim_boundary", "")).lower():
        raise ValueError("Distributional report lacks its ecological claim boundary")
    capacity = reports["capacity-cost-perspective"]
    if capacity.get("capacity_status") != "not_estimable_observed_capacity_and_staffing_unknown":
        raise ValueError("Capacity report must keep observed capacity and staffing unknown")
    if capacity.get("operational_recommendation") is not False:
        raise ValueError("Capacity report crosses the operational recommendation boundary")
    resilience = reports["resilience-sensitivity"]
    if resilience.get("outage_scenario_type") != "counterfactual_candidate_site_removal":
        raise ValueError("Resilience report must declare its counterfactual scenario type")
    if "hypothetical" not in str(resilience.get("claim_boundary", "")).lower():
        raise ValueError("Resilience report lacks its hypothetical claim boundary")
    summary_ids = {row["configuration_id"] for row in reports["scenario_summary"]["configurations"]}
    frontier_ids = {row["configuration_id"] for row in reports["optimisation_frontier"]["points"]}
    if summary_ids != frontier_ids:
        raise ValueError("Scenario and optimisation configuration IDs differ")
    uncertainty_types = {row["uncertainty_type"] for row in reports["uncertainty_analysis"]["rows"]}
    required_types = {"spatial_structural", "temporal_scenario", "deterministic_cost_scenario"}
    if not required_types <= uncertainty_types:
        raise ValueError(f"Uncertainty types missing: {sorted(required_types - uncertainty_types)}")
    if reports["optimisation_frontier"].get("optimality_claimed") is not False:
        raise ValueError("Frontier must not claim optimality without an exact-solver receipt")
    return {
        "schema_version": "1.0.0",
        "status": "passed",
        "report_names": list(REPORTS),
        "configuration_count": len(summary_ids),
        "uncertainty_types": sorted(uncertainty_types),
        "report_sha256": {
            name: hashlib.sha256((REPORT_DIR / f"{name}.json").read_bytes()).hexdigest()
            for name in REPORTS
        },
        "claim_boundary": "Scientific contract validation only; outputs remain aggregate policy simulations, not clinical or operational evidence.",
    }


def main() -> None:
    print(json.dumps(validate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
