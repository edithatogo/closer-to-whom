#!/usr/bin/env python3
"""Validate the fail-closed CTW-060 publication and release gate."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "data" / "public" / "publication-gate.yaml"
REQUIRED_ARTIFACTS = {
    "release/verification-receipt.json",
    "release/publication-readiness.json",
    "release/source-manifest.json",
}
REQUIRED_PROHIBITIONS = {
    "individual health data",
    "confidential health-service data",
    "live Healthpoint payloads",
    "row-level clinical records",
}
REQUIRED_EVIDENCE = {
    "national_analysis_receipt",
    "source_and_licence_receipts",
    "clinical_review_receipt",
    "governance_review_receipt",
    "aggregate_artifact_review",
    "space_credential",
    "promotion_receipt",
}


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def validate(path: Path = GATE) -> list[str]:
    payload = _load(path)
    failures: list[str] = []
    status = str(payload.get("status", "")).lower()
    if status not in {"blocked_on_national_analysis", "ready_for_review", "published"}:
        failures.append(f"unsupported publication gate status: {status or '<blank>'}")
    evidence = payload.get("required_evidence")
    if not isinstance(evidence, dict) or set(map(str, evidence)) != REQUIRED_EVIDENCE:
        failures.append("required_evidence must enumerate all seven publication gates")
        evidence = {}
    artifacts = payload.get("required_artifacts", [])
    if set(map(str, artifacts)) != REQUIRED_ARTIFACTS:
        failures.append("required_artifacts must enumerate the three release receipts")
    prohibited = payload.get("prohibited_content", [])
    if set(map(str, prohibited)) != REQUIRED_PROHIBITIONS:
        failures.append("prohibited_content must enumerate all four protected-data boundaries")
    if status in {"ready_for_review", "published"}:
        if str(evidence.get("national_analysis_receipt", "")).lower() != "completed":
            failures.append("reviewable publication requires a completed national analysis receipt")
        if any(
            str(value).lower()
            not in {"complete", "reviewed", "determined", "configured", "verified"}
            for value in evidence.values()
        ):
            failures.append("reviewable publication requires every evidence receipt to be complete")
    boundary = str(payload.get("claim_boundary", "")).lower()
    for term in ("blocked", "aggregate", "synthetic", "service capability", "authorisation"):
        if term not in boundary:
            failures.append(f"claim_boundary must preserve the {term} boundary")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Publication gate failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Validated publication gate; release remains bounded by declared evidence status.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
