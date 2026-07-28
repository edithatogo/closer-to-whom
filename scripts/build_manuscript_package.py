#!/usr/bin/env python3
"""Build an evidence-linked, claim-bounded aggregate manuscript package."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = (
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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output: Path) -> dict[str, object]:
    analysis = ROOT / "reports/national-analysis"
    payload = {
        name: json.loads((analysis / f"{name}.json").read_text(encoding="utf-8"))
        for name in REPORTS
    }
    summary = payload["scenario_summary"]
    rows = summary["configurations"]
    report_hashes = {name: sha(analysis / f"{name}.json") for name in REPORTS}
    report = (
        f"""# Closer to whom? — evidence-linked national aggregate analysis

## Methods

We used frozen public aggregate inputs and deterministic travel-routing outputs to compare
candidate-network scenarios across Aotearoa New Zealand. Expected courses are aggregate model
cells, not patients or observed service use. The analysis does not add individual, confidential,
or row-level health data. Clinical eligibility and service capability remain hard unknown gates.

The package contains nine canonical reports: scenario summary, optimisation frontier, uncertainty,
MCDA, VOI, distributional equity, capacity/cost, resilience sensitivity, and exact optimisation
comparison. Exact optimisation is limited to the declared finite p=1,3,5 enumeration scope.

## Results

The deterministic candidate-network comparison contains **{len(rows)}** configurations. The
weighted mean one-way travel results are:

| Configuration | Candidate sites | Weighted mean minutes | Expected courses within 60 minutes |
|---|---:|---:|---:|
"""
        + "\n".join(
            f"| {row['configuration_id']} | {row['candidate_site_count']} | {row['weighted_mean_one_way_minutes']:.1f} | {row['share_expected_courses_within_60_minutes']:.1%} |"
            for row in rows
        )
        + """\n
Distributional outputs retain unknown groups and are ecological summaries. Capacity outputs are
arithmetic workload envelopes and a private-vehicle resource-cost scenario; observed staffing,
capacity, treatment mix, and omitted cost components are not estimated. Resilience results are
hypothetical candidate-site removal routing sensitivities, not observed outage performance.

## Limitations and bounded conclusions

The outputs support reproducible comparison of modelled aggregate access scenarios. They do not
support clinical guidance, service-capability claims, operational deployment, patient-level
inference, policy recommendation, or cost-effectiveness conclusions. Unsupported delivery settings,
provider travel, patient travel, and national treatment mix remain unknown or not estimated.

## Reproducibility and data statement

The exact report hashes, source/licence decision, release receipts, assumptions, and code revision
are recorded in the repository. Raw or licensed source payloads are not redistributed. The public
Space contains only precomputed aggregate outputs and provenance.

## Author and submission boundary

This is a prepared manuscript package, not journal submission or acceptance. Author disclosures,
funding, conflicts, AI disclosure, journal selection, and authenticated submission remain human-
controlled actions.
"""
    )
    output.mkdir(parents=True, exist_ok=True)
    (output / "national-aggregate-analysis.md").write_text(report, encoding="utf-8")
    receipt = {
        "schema_version": "1.0.0",
        "status": "prepared_evidence_linked_aggregate_manuscript",
        "generated_at": datetime.now(UTC).isoformat(),
        "report_names": list(REPORTS),
        "report_sha256": report_hashes,
        "claim_boundary": "Prepared package only; no journal submission, acceptance, endorsement, clinical guidance, or policy recommendation.",
        "author_controlled_actions": [
            "funding_disclosure",
            "conflict_disclosure",
            "ai_disclosure",
            "journal_submission",
        ],
    }
    (output / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "release/manuscript")
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
