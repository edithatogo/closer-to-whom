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
