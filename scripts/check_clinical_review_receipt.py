#!/usr/bin/env python3
"""Validate the clinical pathway review receipt without treating fixtures as evidence."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data" / "public" / "clinical-pathway-review.yaml"
REVIEWED = {"reviewed", "accepted"}


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def validate(path: Path = REVIEW) -> list[str]:
    payload = _load(path)
    failures: list[str] = []
    required = payload.get("required_attestation_scopes", payload.get("required_reviewers", []))
    reviewers = payload.get("attestation_receipts", payload.get("reviewers", []))
    decisions = payload.get("decisions", [])
    if not isinstance(required, list) or not required:
        failures.append("required_reviewers must be a non-empty list")
        required = []
    scope_contracts = payload.get("scope_contracts")
    required_scopes = set(map(str, required))
    if not isinstance(scope_contracts, dict) or set(map(str, scope_contracts)) != required_scopes:
        failures.append("scope_contracts must enumerate every required attestation scope")
    elif str(payload.get("status", "")).lower() in {
        "pending_external_review",
        "pending_sole_developer_clinician_attestation",
    } and any(str(value).lower() != "pending" for value in scope_contracts.values()):
        failures.append("pending clinical scopes must remain pending")
    if not isinstance(reviewers, list):
        failures.append("reviewers must be a list")
        reviewers = []
    if not isinstance(decisions, list):
        failures.append("decisions must be a list")
        decisions = []
    status = str(payload.get("status", "")).lower()
    roles: set[str] = set()
    for index, reviewer in enumerate(reviewers):
        if not isinstance(reviewer, dict):
            failures.append(f"reviewer {index}: expected a mapping")
            continue
        role = str(reviewer.get("role", "")).strip()
        if not role:
            failures.append(f"reviewer {index}: role is required")
            continue
        roles.add(role)
        receipt_ref = reviewer.get("receipt_ref")
        reviewed_on = reviewer.get("reviewed_on")
        if not receipt_ref:
            failures.append(f"{role}: receipt_ref is required")
        if not reviewed_on:
            failures.append(f"{role}: reviewed_on is required")
        else:
            try:
                date.fromisoformat(str(reviewed_on))
            except ValueError:
                failures.append(f"{role}: reviewed_on must be an ISO date")
    if status in REVIEWED:
        missing = set(map(str, required)) - roles
        if missing:
            failures.append(f"reviewed clinical receipt missing roles: {sorted(missing)}")
        if not decisions:
            failures.append("reviewed clinical receipt requires decisions")
        if any(str(value).lower() == "pending" for value in scope_contracts.values()):
            failures.append("reviewed clinical receipt cannot retain pending scopes")
    elif status not in {
        "pending_external_review",
        "pending_sole_developer_clinician_attestation",
    }:
        failures.append(f"unsupported clinical review status: {status or '<blank>'}")
    if "synthetic" not in str(payload.get("claim_boundary", "")).lower():
        failures.append("claim_boundary must preserve the synthetic-fixture boundary")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Clinical review receipt failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated clinical review receipt; external review remains pending where declared.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
