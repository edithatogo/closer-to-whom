#!/usr/bin/env python3
"""Validate the fail-closed CTW-070 microdata and VOI decision boundary."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "data" / "public" / "microdata-voi-decision.yaml"
REQUIRED_OUTPUTS = {
    "voi_summary",
    "research_design_comparison",
    "governance_burden_assessment",
    "ethics_scope_boundary",
}


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def validate(path: Path = DECISION) -> list[str]:
    payload = _load(path)
    failures: list[str] = []
    status = str(payload.get("status", "")).lower()
    if status not in {"blocked_on_ctw050", "pending_external_decision", "determined"}:
        failures.append(f"unsupported microdata decision status: {status or '<blank>'}")
    if payload.get("microdata_build_dependency") is not False:
        failures.append("microdata_build_dependency must remain false")
    outputs = payload.get("required_outputs", [])
    if set(map(str, outputs)) != REQUIRED_OUTPUTS:
        failures.append("required_outputs must enumerate the four CTW-070 outputs")
    contracts = payload.get("output_contracts")
    if not isinstance(contracts, dict) or set(map(str, contracts)) != REQUIRED_OUTPUTS:
        failures.append("output_contracts must enumerate the four CTW-070 output contracts")
    elif status in {"blocked_on_ctw050", "pending_external_decision"} and any(
        str(value).lower() != "blocked_pending_governance_decision" for value in contracts.values()
    ):
        failures.append("undetermined outputs must remain blocked_pending_governance_decision")
    receipts = payload.get("decision_receipts", [])
    if not isinstance(receipts, list):
        failures.append("decision_receipts must be a list")
        receipts = []
    if status == "determined" and len(receipts) < len(REQUIRED_OUTPUTS):
        failures.append("determined decision requires one receipt per required output")
    if status == "determined" and any(
        str(value).lower() == "blocked_pending_governance_decision" for value in contracts.values()
    ):
        failures.append("determined decision cannot retain blocked output contracts")

    boundary = str(payload.get("claim_boundary", "")).lower()
    for term in ("individual", "confidential", "row-level", "separate protocol", "ethics/hdec"):
        if term not in boundary:
            failures.append(f"claim_boundary must preserve the {term} boundary")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Microdata VOI decision failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated microdata VOI decision; microdata remains outside the build dependency graph.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
