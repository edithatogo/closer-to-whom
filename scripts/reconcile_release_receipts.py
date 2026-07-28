#!/usr/bin/env python3
"""Compare historical deployment evidence with the current repository payload."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_NAMES = (
    "scenario_summary",
    "optimisation_frontier",
    "uncertainty_analysis",
    "mcda_outputs",
    "voi_outputs",
    "distributional-equity",
    "capacity-cost-perspective",
    "resilience-sensitivity",
    "optimisation-comparison",
)
RECEIPT_ONLY_PATHS = {
    "conductor/state.yaml",
    "release/receipt-reconciliation.json",
    "release/recovery-drill-receipt.json",
    "release/space-deployment-receipt.json",
    "release/space-monitor-receipt.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _receipt_only_descendant(historical_revision: str, current_revision: str) -> bool:
    """Allow receipt registration commits, but never source or report drift."""
    if not historical_revision or historical_revision == current_revision:
        return historical_revision == current_revision
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", historical_revision, current_revision],
        cwd=ROOT,
        check=False,
    )
    if ancestor.returncode != 0:
        return False
    changed = subprocess.run(
        ["git", "diff", "--name-only", f"{historical_revision}..{current_revision}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return bool(changed) and set(changed).issubset(RECEIPT_ONLY_PATHS)


def build(output: Path) -> dict[str, Any]:
    historical_path = ROOT / "release/space-deployment-receipt.json"
    historical = json.loads(historical_path.read_text(encoding="utf-8"))
    analysis = ROOT / "reports/national-analysis"
    payload = {
        name: json.loads((analysis / f"{name}.json").read_text(encoding="utf-8"))
        for name in REPORT_NAMES
    }
    payload_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    historical_reports = str(historical.get("published_payload", ""))
    current_revision = _revision()
    historical_revision = str(historical.get("source_revision", ""))
    source_matches = _receipt_only_descendant(historical_revision, current_revision)
    drift = {
        "source_revision": {
            "historical": historical_revision,
            "current": current_revision,
            "matches": source_matches,
            "mode": "exact"
            if historical_revision == current_revision
            else "receipt_only_descendant",
        },
        "report_scope": {
            "historical": historical_reports,
            "current_report_count": len(REPORT_NAMES),
            "current_report_names": list(REPORT_NAMES),
            "matches": "nine" in historical_reports.lower(),
        },
        "current_payload_sha256": payload_hash,
        "historical_receipt_sha256": _sha(historical_path),
    }
    matches = all(item["matches"] for item in (drift["source_revision"], drift["report_scope"]))
    receipt = {
        "schema_version": "1.0.0",
        "status": "historical_space_receipt_matches"
        if matches
        else "historical_space_receipt_stale",
        "historical_receipt": "release/space-deployment-receipt.json",
        "drift": drift,
        "required_next_evidence": []
        if matches
        else [
            "fresh deployment receipt from the publish workflow",
            "live Space revision and content hash probe",
            "approved source revision matching current main",
        ],
        "claim_boundary": "This is a reconciliation of repository and historical receipt metadata; it does not establish current Space availability or deployment.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "release/receipt-reconciliation.json")
    args = parser.parse_args()
    receipt = build(args.output)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
