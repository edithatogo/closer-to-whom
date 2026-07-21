#!/usr/bin/env python3
"""Validate the CTW-050 national-analysis evidence gate."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data" / "public" / "national-analysis-receipt.yaml"
REQUIRED_OUTPUTS = {
    "scenario_summary",
    "optimisation_frontier",
    "uncertainty_analysis",
    "mcda_outputs",
    "voi_outputs",
}
REQUIRED_PREREQUISITES = {
    "service_census",
    "public_input_freeze",
    "clinical_pathway_review",
    "route_costs",
    "governance_review",
}


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def validate(path: Path = RECEIPT) -> list[str]:
    payload = _load(path)
    failures: list[str] = []
    status = str(payload.get("status", "")).lower()
    if status not in {"blocked_on_prerequisites", "ready_for_review", "completed"}:
        failures.append(f"unsupported national analysis status: {status or '<blank>'}")

    prerequisites = payload.get("prerequisites")
    if (
        not isinstance(prerequisites, dict)
        or set(map(str, prerequisites)) != REQUIRED_PREREQUISITES
    ):
        failures.append("prerequisites must enumerate all five CTW-050 gates")
        prerequisites = {}
    outputs = payload.get("required_outputs", [])
    if set(map(str, outputs)) != REQUIRED_OUTPUTS:
        failures.append("required_outputs must enumerate the five national-analysis outputs")
    receipts = payload.get("analysis_receipts", [])
    if not isinstance(receipts, list):
        failures.append("analysis_receipts must be a list")
        receipts = []

    if status in {"ready_for_review", "completed"}:
        if any(str(value).lower() != "complete" for value in prerequisites.values()):
            failures.append("reviewable analysis requires every prerequisite to be complete")
        if len(receipts) < len(REQUIRED_OUTPUTS):
            failures.append("reviewable analysis requires one receipt per required output")

    boundary = str(payload.get("claim_boundary", "")).lower()
    for term in ("blocked", "synthetic", "observed capacity", "clinical", "operational"):
        if term not in boundary:
            failures.append(f"claim_boundary must preserve the {term} boundary")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("National analysis receipt failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated national analysis receipt; publication remains gated by declared status.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
