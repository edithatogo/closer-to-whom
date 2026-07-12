#!/usr/bin/env python3
"""Audit pathway safety invariants and report the clinical-review blocker explicitly."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from closer_to_whom.pathways import default_synthetic_pathways

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports/clinical-pathway-freeze.json"


def audit(output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    pathways = default_synthetic_pathways()
    errors: list[str] = []
    for pathway in pathways:
        for visit in pathway.visits:
            if visit.may_be_home and visit.requires_hospital:
                errors.append(
                    f"Home visit requires hospital: {pathway.pathway_id}/{visit.visit_type_id}"
                )
            if visit.requires_resuscitation and not visit.requires_hospital:
                errors.append(
                    f"Resuscitation-capable visit lacks hospital setting: {pathway.pathway_id}/{visit.visit_type_id}"
                )
    clinically_reviewed = sum(pathway.clinically_reviewed for pathway in pathways)
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "pathway_count": len(pathways),
        "clinically_reviewed_count": clinically_reviewed,
        "status": "blocked_pending_clinical_review"
        if clinically_reviewed < len(pathways)
        else "ready_for_review_receipt",
        "safety_errors": errors,
        "pathway_ids": [pathway.pathway_id for pathway in pathways],
        "claim_boundary": "Synthetic pathway contracts demonstrate software behaviour and are not clinical guidance or evidence of funding/eligibility.",
    }
    if errors:
        raise ValueError(json.dumps(report, sort_keys=True))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(audit(args.output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
