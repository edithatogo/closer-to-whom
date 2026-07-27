"""Materialise the source-backed travel-cost parameter freeze."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSUMPTIONS = ROOT / "assumptions/assumptions.yaml"
DEFAULT_OUTPUT = ROOT / "reports/travel-cost-parameters.json"

_CATEGORIES: dict[str, dict[str, object]] = {
    "car": {
        "status": "source_backed_scenario",
        "parameter_ids": ["K01"],
        "source_ids": ["candidate.ird-kilometre-rates"],
        "applicability": "private_vehicle_resource_cost_scenario",
    },
    "public_transport": {
        "status": "route_specific_actual_cost_pending",
        "parameter_ids": [],
        "source_ids": ["candidate.healthnz-nta"],
        "applicability": "mode_specific_sensitivity_only",
    },
    "ferry": {
        "status": "route_specific_actual_cost_pending",
        "parameter_ids": [],
        "source_ids": ["candidate.healthnz-nta"],
        "applicability": "mode_specific_sensitivity_only",
    },
    "walking_waiting_transfer": {
        "status": "duration_and_valuation_pending",
        "parameter_ids": ["K03"],
        "source_ids": ["synthetic.parameter-fixture"],
        "applicability": "report_time_separately_until_source_backed",
    },
    "parking": {
        "status": "location_specific_rate_pending",
        "parameter_ids": [],
        "source_ids": [],
        "applicability": "exclude_from_primary_monetary_result",
    },
    "fares": {
        "status": "route_specific_actual_cost_pending",
        "parameter_ids": [],
        "source_ids": ["candidate.healthnz-nta"],
        "applicability": "exclude_from_primary_monetary_result",
    },
    "accommodation": {
        "status": "source_backed_reimbursement_cap",
        "parameter_ids": ["K04", "K05"],
        "source_ids": ["candidate.healthnz-nta"],
        "applicability": "eligibility_scenario_not_observed_cost",
    },
    "provider_travel": {
        "status": "resource_rates_pending",
        "parameter_ids": [],
        "source_ids": [],
        "applicability": "exclude_until_service_model_requires_provider_travel",
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def materialize(
    assumptions_path: Path = DEFAULT_ASSUMPTIONS,
    output_path: Path = DEFAULT_OUTPUT,
) -> dict[str, object]:
    """Write deterministic parameter and category evidence without filling unknown rates."""
    assumptions_document = yaml.safe_load(assumptions_path.read_text(encoding="utf-8"))
    selected_ids = {"K01", "K02", "K03", "K04", "K05"}
    parameters = [
        assumption
        for assumption in assumptions_document["assumptions"]
        if assumption["id"] in selected_ids
    ]
    present_ids = {parameter["id"] for parameter in parameters}
    if present_ids != selected_ids:
        missing = sorted(selected_ids - present_ids)
        raise ValueError(f"Missing required cost assumptions: {missing}")

    payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "status": "source_backed_partial_cost_parameter_freeze",
        "currency": "NZD",
        "assumptions_sha256": _sha256(assumptions_path),
        "parameters": sorted(parameters, key=lambda parameter: parameter["id"]),
        "categories": _CATEGORIES,
        "primary_analysis_rule": (
            "Report distance, duration, and each monetary component separately. Use K01 only as "
            "a private-vehicle resource-cost scenario and K02/K04/K05 only as reimbursement "
            "scenarios. K03 remains illustrative and is excluded from primary monetised results."
        ),
        "unknown_rule": (
            "A missing route-, facility-, or provider-specific rate remains unknown and is not "
            "replaced with zero, a national average, or a synthetic value."
        ),
        "claim_boundary": (
            "These are transparent policy scenarios and reimbursement caps, not observed patient "
            "costs, eligibility, uptake, travel mode, accommodation use, or provider expenditure."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assumptions", type=Path, default=DEFAULT_ASSUMPTIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(materialize(args.assumptions, args.output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
