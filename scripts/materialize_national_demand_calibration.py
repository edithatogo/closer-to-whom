"""Materialise a source-backed national aggregate anti-HER2 demand scenario."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSUMPTIONS = ROOT / "assumptions/assumptions.yaml"
DEFAULT_REPORT = ROOT / "reports/national-demand-calibration.json"
REQUIRED_IDS = ("D03", "D04", "D05", "D06")


def _assumptions(path: Path) -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    records = payload.get("assumptions", [])
    if not isinstance(records, list):
        raise TypeError("assumptions must be a list")
    indexed = {
        str(record["id"]): record
        for record in records
        if isinstance(record, dict) and record.get("id")
    }
    missing = [identifier for identifier in REQUIRED_IDS if identifier not in indexed]
    if missing:
        raise ValueError(f"missing calibration assumptions: {missing}")
    return indexed


def _proportion(record: dict[str, Any]) -> float:
    value = float(record["value"])
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{record['id']} must be a proportion")
    return value


def materialize(
    assumptions_path: Path = DEFAULT_ASSUMPTIONS,
    report_path: Path = DEFAULT_REPORT,
) -> dict[str, Any]:
    """Write a deterministic, national-only calibration receipt."""
    records = _assumptions(assumptions_path)
    incidence = float(records["D06"]["value"])
    if incidence <= 0:
        raise ValueError("D06 must be positive")
    her2_probability = _proportion(records["D03"])
    stage_probability = _proportion(records["D05"])
    treatment_uptake = _proportion(records["D04"])
    annual_courses = incidence * her2_probability * stage_probability * treatment_uptake
    source_ids = sorted(
        {
            source_id
            for identifier in REQUIRED_IDS
            for source_id in records[identifier].get("source_ids", [])
        }
    )
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "materialized_national_scenario_not_spatially_allocated",
        "calibration_years": {
            "incidence": 2022,
            "treatment_uptake": "2020-2021",
        },
        "inputs": {
            "annual_female_breast_cancer_registrations": incidence,
            "her2_positive_probability": her2_probability,
            "stage_i_iii_probability": stage_probability,
            "treatment_uptake": treatment_uptake,
        },
        "formula": "registrations * her2_positive_probability * stage_i_iii_probability * treatment_uptake",
        "annual_expected_courses": round(annual_courses, 6),
        "source_ids": source_ids,
        "uncertainty": {
            "parameter": "source point estimates are retained without invented confidence intervals",
            "temporal": "incidence and uptake refer to different observation periods",
            "structural": "national rates are not assumed to be spatially homogeneous",
            "decision": "clinical eligibility and service feasibility remain hard constraints",
        },
        "claim_boundary": (
            "This is a public aggregate national planning scenario, not observed current demand, "
            "an SA2 estimate, a patient count, or evidence of facility capability."
        ),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assumptions", type=Path, default=DEFAULT_ASSUMPTIONS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(json.dumps(materialize(args.assumptions, args.report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
