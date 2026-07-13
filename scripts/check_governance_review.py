#!/usr/bin/env python3
"""Validate Māori/equity and ethics-scope review receipts without overclaiming approval."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data" / "public" / "governance-review.yaml"
REQUIRED = {
    "maori_equity_review_receipt",
    "ethics_hdec_scope_determination",
    "unresolved_equity_risks",
    "culturally_safe_interpretation_constraints",
}
COMPLETED = {"reviewed", "determined"}


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def validate(path: Path = REVIEW) -> list[str]:
    payload = _load(path)
    failures: list[str] = []
    status = str(payload.get("status", "")).lower()
    outputs = payload.get("required_outputs", [])
    if set(map(str, outputs)) != REQUIRED:
        failures.append("required_outputs must enumerate the four governance outputs")
    receipts = payload.get("review_receipts", [])
    risks = payload.get("unresolved_equity_risks", [])
    constraints = payload.get("interpretation_constraints", [])
    if not isinstance(receipts, list):
        failures.append("review_receipts must be a list")
        receipts = []
    if not isinstance(risks, list):
        failures.append("unresolved_equity_risks must be a list")
        risks = []
    if not isinstance(constraints, list):
        failures.append("interpretation_constraints must be a list")
        constraints = []
    if status in COMPLETED:
        if len(receipts) < 2:
            failures.append("completed governance review requires both review receipts")
        if not risks:
            failures.append("completed governance review must record unresolved equity risks")
        if not constraints:
            failures.append("completed governance review must record interpretation constraints")
        determination = payload.get("ethics_hdec_determination")
        if not isinstance(determination, dict) or not determination.get("status"):
            failures.append("completed governance review requires ethics_hdec_scope_determination")
    elif status != "pending_external_review":
        failures.append(f"unsupported governance review status: {status or '<blank>'}")
    boundary = str(payload.get("claim_boundary", "")).lower()
    for term, variants in (
        ("pending", ("pending",)),
        ("endorsement", ("endorsement",)),
        ("ethical approval", ("ethical approval",)),
        ("authorisation", ("authoris", "authoriz")),
    ):
        if not any(variant in boundary for variant in variants):
            failures.append(f"claim_boundary must preserve the {term} boundary")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Governance review failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated governance review receipt; external review remains pending where declared.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
