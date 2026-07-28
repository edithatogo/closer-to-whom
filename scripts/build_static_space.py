#!/usr/bin/env python3
"""Build a deterministic, no-JavaScript public aggregate summary page."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _read(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "reports" / "national-analysis" / name).read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output: Path) -> None:
    summary = _read("scenario_summary.json")
    frontier = _read("optimisation_frontier.json")
    mcda = _read("mcda_outputs.json")
    voi = _read("voi_outputs.json")
    equity = _read("distributional-equity.json")
    capacity = _read("capacity-cost-perspective.json")
    resilience = _read("resilience-sensitivity.json")
    rows = []
    for row in summary["configurations"]:
        rows.append(
            "<tr>"
            f"<th scope='row'>{html.escape(row['configuration_id'])}</th>"
            f"<td>{row['candidate_site_count']}</td>"
            f"<td>{row['weighted_mean_one_way_minutes']:.1f}</td>"
            f"<td>{row['share_expected_courses_within_60_minutes']:.1%}</td>"
            f"<td>{row['vehicle_resource_cost_nzd']:,.0f}</td>"
            "</tr>"
        )
    links = "".join(
        f"<li><a href='https://github.com/edithatogo/closer-to-whom/blob/main/reports/national-analysis/{name}'>{label}</a></li>"
        for name, label in (
            ("scenario_summary.json", "Scenario summary"),
            ("optimisation_frontier.json", "Optimisation frontier"),
            ("uncertainty_analysis.json", "Separated uncertainty"),
            ("mcda_outputs.json", "MCDA outputs"),
            ("voi_outputs.json", "VOI outputs"),
            ("distributional-equity.json", "Distributional equity"),
            ("capacity-cost-perspective.json", "Capacity and cost perspective"),
            ("resilience-sensitivity.json", "Resilience sensitivity"),
        )
    )
    report_names = (
        "scenario_summary.json",
        "optimisation_frontier.json",
        "uncertainty_analysis.json",
        "mcda_outputs.json",
        "voi_outputs.json",
        "distributional-equity.json",
        "capacity-cost-perspective.json",
        "resilience-sensitivity.json",
    )
    bundle = {
        "schema_version": "1.0.0",
        "artifact": "reviewed-national-aggregate-reports",
        "claim_boundary": summary["claim_boundary"],
        "generated_at": summary["generated_at"],
        "reports": {name.removesuffix(".json"): _read(name) for name in report_names},
    }
    page = f"""<!doctype html>
<html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Closer to whom? — reviewed aggregate results</title>
<style>body{{font:1rem/1.5 system-ui,sans-serif;max-width:70rem;margin:auto;padding:1rem;color:#17202a}}:focus{{outline:3px solid #005a9c;outline-offset:2px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #777;padding:.4rem;text-align:left}}caption{{font-weight:700;text-align:left;margin:.5rem 0}}.notice{{border-left:.4rem solid #005a9c;padding:.5rem 1rem;background:#eef6fb}}</style></head>
<body><a href="#main">Skip to main content</a><main id="main"><h1>Closer to whom?</h1>
<p class="notice"><strong>Research boundary:</strong> This is a public-data aggregate policy simulation. Candidate sites are plausible locations, not confirmed anti-HER2 services. Capacity, eligibility, operational feasibility, patient outcomes, and policy preference are not estimated.</p>
<h2>Reviewed candidate-network comparison</h2><p>Values are expected aggregate courses, not people or observed service use.</p>
<table><caption>Travel and vehicle-resource results</caption><thead><tr><th scope="col">Configuration</th><th scope="col">Candidate sites</th><th scope="col">Weighted mean one-way minutes</th><th scope="col">Expected courses within 60 minutes</th><th scope="col">Vehicle resource cost (NZD)</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<h2>Evidence and interpretation</h2><ul><li>Optimisation frontier: {html.escape(frontier["status"])}; optimality claimed: {str(frontier["optimality_claimed"]).lower()}.</li><li>Uncertainty is separated into spatial, temporal-demand, and deterministic cost scenarios; probabilistic intervals are not estimated.</li><li>MCDA and VOI outputs are exploratory research artifacts and do not recommend a policy.</li></ul>
<p>Distributional equity is ecological and retains unknown groups. Capacity and cost report implied aggregate workload and a private-vehicle resource scenario only. Resilience is hypothetical candidate-site routing sensitivity, not an observed outage or guarantee.</p>
<h2>Auditable downloads and source records</h2><p><a href='aggregate-reports.json'>Download the deterministic aggregate report bundle</a>.</p><ul>{links}</ul><p>Generated from report revision {html.escape(summary["generated_at"])}. The repository's assumptions, source registry, model card, and release receipts remain the authoritative provenance records.</p>
<p>MCDA status: {html.escape(str(mcda.get("status", "not declared")))}. VOI status: {html.escape(str(voi.get("status", "not declared")))}. Equity status: {html.escape(str(equity.get("status", "not declared")))}. Capacity/cost status: {html.escape(str(capacity.get("status", "not declared")))}. Resilience status: {html.escape(str(resilience.get("status", "not declared")))}.</p></main></body></html>\n"""
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.html").write_text(page, encoding="utf-8")
    (output / "aggregate-reports.json").write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = {
        "schema_version": "1.0.0",
        "artifact": "static-space-summary",
        "claim_boundary": summary["claim_boundary"],
        "generated_at": summary["generated_at"],
        "source_reports": {
            name: {"sha256": _digest(ROOT / "reports" / "national-analysis" / name)}
            for name in (
                "scenario_summary.json",
                "optimisation_frontier.json",
                "uncertainty_analysis.json",
                "mcda_outputs.json",
                "voi_outputs.json",
                "distributional-equity.json",
                "capacity-cost-perspective.json",
                "resilience-sensitivity.json",
            )
        },
        "javascript_required": False,
        "aggregate_only": True,
    }
    (output / "provenance.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "spaces" / "static")
    build(parser.parse_args().output)


if __name__ == "__main__":
    main()
