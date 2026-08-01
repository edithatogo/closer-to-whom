#!/usr/bin/env python3
"""Build a self-contained Static Space from reviewed national aggregate reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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

TEMPLATE = r"""<!doctype html>
<html lang="en-NZ">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Closer to whom? - national aggregate analysis</title>
  <style>
    :root{font-family:system-ui,sans-serif;color:#102a43;background:#f5f7fa}
    body{max-width:1100px;margin:auto;padding:1rem 1.5rem;line-height:1.5}
    header,section{background:white;border:1px solid #d9e2ec;border-radius:.75rem;padding:1rem;margin:1rem 0}
    h1,h2{color:#0b7285}.warning{border-left:.35rem solid #d9480f;padding-left:.75rem}
    .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(12rem,1fr));gap:.75rem}
    .card{border:1px solid #bcccdc;border-radius:.5rem;padding:.75rem}.metric{font-size:1.5rem;font-weight:700}
    table{border-collapse:collapse;width:100%;font-size:.9rem}th,td{padding:.5rem;border-bottom:1px solid #d9e2ec;text-align:right}
    th:first-child,td:first-child{text-align:left}.bar{height:.8rem;background:#0b7285;border-radius:.2rem}
    .muted{color:#52667a}code{overflow-wrap:anywhere}:focus{outline:3px solid #005a9c;outline-offset:2px}
  </style>
</head>
<body><a href="#main">Skip to main content</a><main id="main">
  <header>
    <h1>Closer to whom?</h1>
    <p class="warning"><strong>Boundary:</strong> Public aggregate planning scenarios - not confirmed anti-HER2 services, observed capacity, operational feasibility, clinical guidance, or a policy recommendation.</p>
  <p>This free static site serves nine precomputed, hash-receipted reports. No patient records, individual locations, raw source payloads, live APIs, or paid compute are used.</p>
  </header>
  <noscript><section><h2>No-JavaScript summary</h2><p>The table below is rendered into the page at build time; interactive enhancements are not required.</p><div style="overflow:auto"><table><caption>Travel and access summary without JavaScript</caption><thead><tr><th scope="col">Configuration</th><th scope="col">Sites</th><th scope="col">Mean minutes</th><th scope="col">P95 minutes</th><th scope="col">Within 60 min</th></tr></thead><tbody>__NOSCRIPT_ROWS__</tbody></table></div></section></noscript>
  <section><h2>Candidate-network comparison</h2><div class="cards" id="cards"></div><div style="overflow:auto"><table><caption>Travel and access summary</caption><thead><tr><th scope="col">Configuration</th><th scope="col">Sites</th><th scope="col">Mean minutes</th><th scope="col">P95 minutes</th><th scope="col">Within 60 min</th></tr></thead><tbody id="scenarios"></tbody></table></div></section>
  <section><h2>Normative viewpoints</h2><p class="muted">Clinical eligibility and safety are hard gates and are never traded off here.</p><div id="viewpoints"></div></section>
  <section><h2>Decision uncertainty</h2><p id="voi"></p></section>
  <section><h2>Uncertainty and provenance</h2><p>Spatial, temporal-demand, vehicle-rate, and normative-weight uncertainty remain separate. Probabilistic clinical intervals and monetary ENBS are not estimated without source-backed distributions.</p><p>Source revision: <code>__REVISION__</code>. National analysis workflow: <a href="https://github.com/edithatogo/closer-to-whom/actions/runs/30243407303">30243407303</a>. <a href="aggregate-reports.json">Download the deterministic aggregate report bundle</a>.</p></section>
  <section><h2>Additional reviewed outputs</h2><ul><li>Distributional equity: aggregate access summaries by deprivation, rurality, vehicle access, and overlapping ethnicity total-response groups; ecological only, with unknowns retained.</li><li>Capacity and cost: implied aggregate course envelopes and private-vehicle resource costs; observed staffing, capacity, treatment cost, and omitted components are not estimated.</li><li>Resilience: hypothetical single-candidate-site routing sensitivity; this is not an observed outage or resilience guarantee.</li><li>Optimisation comparison: exact p-median, p-centre, and 60-minute maximal-coverage results for p=1,3,5 only; larger configurations remain heuristic.</li></ul></section>
  <script type="application/json" id="analysis-data">__DATA__</script>
  <script>
    const DATA=JSON.parse(document.querySelector('#analysis-data').textContent);
    const fmt=(value,digits=1)=>Number(value).toFixed(digits);
    const configs=DATA.scenario_summary.configurations;
    document.querySelector('#cards').innerHTML=configs.map(x=>`<div class="card"><strong>${x.configuration_id}</strong><div class="metric">${fmt(x.weighted_mean_one_way_minutes)} min</div><div class="muted">weighted mean one-way</div><div class="bar" style="width:${100*x.share_expected_courses_within_60_minutes}%"></div></div>`).join('');
    document.querySelector('#scenarios').innerHTML=configs.map(x=>`<tr><td>${x.configuration_id}</td><td>${x.candidate_site_count}</td><td>${fmt(x.weighted_mean_one_way_minutes)}</td><td>${fmt(x.weighted_p95_one_way_minutes)}</td><td>${fmt(100*x.share_expected_courses_within_60_minutes)}%</td></tr>`).join('');
    document.querySelector('#viewpoints').innerHTML=Object.entries(DATA.mcda_outputs.viewpoints).map(([name,value])=>`<p><strong>${name.replaceAll('_',' ')}</strong>: highest-ranked ${value.ranking[0]} <span class="muted">(weights ${value.weights.map(x=>fmt(x,2)).join(', ')})</span></p>`).join('');
    const voi=DATA.voi_outputs;
    document.querySelector('#voi').textContent=`Under broad normative-weight uncertainty, ${voi.current_best_under_mean_weights} is best at mean weights. EVPI is ${fmt(voi.evpi_per_policy_decision,3)} unitless utility per policy decision. Next information priority: ${voi.next_information_priority}.`;
  </script>
</main></body></html>
"""


def load_reports(analysis: Path) -> dict[str, dict[str, Any]]:
    """Load exactly the five CTW-050 output contracts and enforce publication boundaries."""
    payload = {
        name: json.loads((analysis / f"{name}.json").read_text(encoding="utf-8"))
        for name in REPORT_NAMES
    }
    if any(item.get("operational_recommendation") is not False for item in payload.values()):
        raise ValueError("National Space payload crossed the operational claim boundary")
    return payload


def build(analysis: Path, output: Path, *, revision: str) -> Path:
    """Build one static HTML file with no runtime data or network dependency."""
    payload = load_reports(analysis)
    encoded = json.dumps(payload, separators=(",", ":")).replace("<", "\\u003c")
    fallback_rows = "".join(
        "<tr>"
        f"<th scope='row'>{row['configuration_id']}</th>"
        f"<td>{row['candidate_site_count']}</td>"
        f"<td>{row['weighted_mean_one_way_minutes']:.1f}</td>"
        f"<td>{row['weighted_p95_one_way_minutes']:.1f}</td>"
        f"<td>{row['share_expected_courses_within_60_minutes']:.1%}</td>"
        "</tr>"
        for row in payload["scenario_summary"]["configurations"]
    )
    output.mkdir(parents=True, exist_ok=True)
    target = output / "index.html"
    target.write_text(
        TEMPLATE.replace("__DATA__", encoded)
        .replace("__REVISION__", revision)
        .replace("__NOSCRIPT_ROWS__", fallback_rows),
        encoding="utf-8",
    )
    (output / "aggregate-reports.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "artifact": "reviewed-national-aggregate-reports",
                "source_revision": revision,
                "claim_boundary": payload["scenario_summary"].get(
                    "claim_boundary",
                    "Reviewed aggregate scenarios only; no operational recommendation or clinical claim.",
                ),
                "reports": payload,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", type=Path, default=Path("reports/national-analysis"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    print(build(args.analysis, args.output, revision=args.revision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
