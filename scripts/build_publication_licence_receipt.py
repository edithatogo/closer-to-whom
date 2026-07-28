#!/usr/bin/env python3
"""Build the exact-payload publication and licence decision receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORT_NAMES = (
    "scenario_summary", "optimisation_frontier", "uncertainty_analysis", "mcda_outputs",
    "voi_outputs", "distributional-equity", "capacity-cost-perspective",
    "resilience-sensitivity", "optimisation-comparison",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output: Path) -> dict[str, Any]:
    analysis = ROOT / "reports/national-analysis"
    freeze_path = ROOT / "data/public/input-freeze.yaml"
    freeze = yaml.safe_load(freeze_path.read_text(encoding="utf-8")) or {}
    sources = freeze.get("inputs", [])
    if not isinstance(sources, list) or not sources:
        raise ValueError("input freeze must contain sources")
    source_rows = []
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("input freeze source must be an object")
        receipt = source.get("retrieval_receipt")
        if not receipt:
            raise ValueError(f"missing retrieval receipt for {source.get('source_id')}")
        receipt_path = ROOT / str(receipt)
        if not receipt_path.is_file():
            raise ValueError(f"missing retrieval receipt file: {receipt}")
        source_rows.append({
            "input_id": source.get("input_id"),
            "source_ids": source.get("source_ids", []),
            "licence_state": source.get("licence_state", "unknown"),
            "local_use_authorized": True,
            "raw_redistribution": "not_permitted_by_default",
            "derived_aggregate_publication": "permitted_under_project_scope_only",
            "retrieval_receipt": str(receipt),
            "retrieval_receipt_sha256": _sha(receipt_path),
        })
    payload = {
        name: json.loads((analysis / f"{name}.json").read_text(encoding="utf-8"))
        for name in REPORT_NAMES
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt = {
        "schema_version": "1.0.0",
        "status": "approved_derived_aggregate_nonredistribution",
        "exact_payload": {
            "artifact": "reviewed-national-aggregate-reports",
            "report_names": list(REPORT_NAMES),
            "payload_sha256": hashlib.sha256(encoded).hexdigest(),
        },
        "input_freeze": {"path": "data/public/input-freeze.yaml", "sha256": _sha(freeze_path), "source_count": len(source_rows)},
        "sources": source_rows,
        "decision": {
            "local_use": "authorized_by_recorded_project_scope",
            "raw_payload_redistribution": "prohibited",
            "derived_output_publication": "aggregate_only_and_claim_bounded",
            "live_payloads": "prohibited",
        },
        "claim_boundary": "This receipt records a project-scope decision for the exact aggregate payload. It is not a source-owner licence grant, endorsement, or permission to redistribute raw inputs.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "release/publication-licence-receipt.json")
    args = parser.parse_args()
    build(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
