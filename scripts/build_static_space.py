#!/usr/bin/env python3
"""Build a self-contained static Space from aggregate demo outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import polars as pl

TEMPLATE = r"""<!doctype html>
<html lang="en-NZ">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Closer to whom?</title>
  <style>
    :root{font-family:system-ui,sans-serif;color:#102a43;background:#f7fafc}
    body{max-width:1100px;margin:auto;padding:1rem 1.5rem;line-height:1.5}
    header,section{background:white;border:1px solid #d9e2ec;border-radius:.75rem;padding:1rem;margin:1rem 0}
    h1{margin-top:0;color:#0b7285}.warning{border-left:.35rem solid #d9480f;padding-left:.75rem}
    label{font-weight:700}select{font:inherit;padding:.4rem;margin-left:.5rem}
    .bars{display:grid;gap:.5rem}.bar-row{display:grid;grid-template-columns:minmax(10rem,20rem) 1fr 5rem;gap:.5rem;align-items:center}
    .bar{height:1.4rem;background:#0b7285;border-radius:.25rem;min-width:2px}.bar-row span:last-child{text-align:right}
    table{border-collapse:collapse;width:100%;font-size:.9rem}th,td{padding:.4rem;border-bottom:1px solid #d9e2ec;text-align:left}
    code{overflow-wrap:anywhere}
  </style>
</head>
<body>
  <header><h1>Closer to whom?</h1><p class="warning"><strong>Boundary:</strong> Public-data policy simulation. Not a forecast of individual care, actual service use, capacity, waiting time, or clinical outcomes.</p><p>All displayed values are precomputed from aggregate or synthetic development inputs. No individual locations or patient records are served.</p></header>
  <section><label for="scenario">Scenario</label><select id="scenario"></select><h2>Expected course travel minutes</h2><div id="travel" class="bars"></div><h2>Area-level equity stratification</h2><div id="equity" class="bars"></div></section>
  <section><h2>Aggregate scenario rows</h2><div style="overflow:auto"><table><thead><tr><th>Pathway</th><th>Mean travel minutes</th><th>Expected demand</th></tr></thead><tbody id="rows"></tbody></table></div></section>
  <section><h2>Provenance</h2><p>Manifest: <code id="manifest"></code></p><p>Static site generated from the repository's demo artifact. Healthpoint and other licensed/private payloads are excluded.</p></section>
  <script>
    const DATA = __DATA__;
    const scenario = document.querySelector('#scenario');
    const max = values => Math.max(...values, 1);
    const bars = (target, entries, colour) => { const scale=max(entries.map(x=>x.value)); target.innerHTML=entries.map(x=>`<div class="bar-row"><span>${x.label}</span><div class="bar" style="width:${Math.max(2,100*x.value/scale)}%;background:${colour}"></div><span>${Number(x.value).toFixed(1)}</span></div>`).join(''); };
    function render(){
      const id=scenario.value, rows=DATA.summary.filter(x=>x.scenario_id===id), equity=DATA.equity.filter(x=>x.scenario_id===id);
      bars(document.querySelector('#travel'), rows.map(x=>({label:x.pathway_id,value:x.mean_course_travel_minutes})), '#0b7285');
      bars(document.querySelector('#equity'), equity.map(x=>({label:`${x.pathway_id} / ${x.ethnicity}`,value:x.mean_course_travel_minutes})), '#6741d9');
      document.querySelector('#rows').innerHTML=rows.map(x=>`<tr><td>${x.pathway_id}</td><td>${Number(x.mean_course_travel_minutes).toFixed(1)}</td><td>${x.expected_demand ?? '—'}</td></tr>`).join('');
    }
    [...new Set(DATA.summary.map(x=>x.scenario_id))].forEach(id=>scenario.add(new Option(id,id))); scenario.addEventListener('change',render); document.querySelector('#manifest').textContent=DATA.manifest; render();
  </script>
</body></html>
"""


def build(results: Path, output: Path) -> Path:
    summary = pl.read_parquet(results / "scenario-summary.parquet").to_dicts()
    equity = pl.read_parquet(results / "equity-ethnicity.parquet").to_dicts()
    manifest = json.loads((results / "manifest.json").read_text(encoding="utf-8"))
    manifest_id = str(manifest.get("manifest_id", "unavailable"))
    payload: dict[str, Any] = {"summary": summary, "equity": equity, "manifest": manifest_id}
    output.mkdir(parents=True, exist_ok=True)
    target = output / "index.html"
    target.write_text(TEMPLATE.replace("__DATA__", json.dumps(payload, separators=(",", ":"))), encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=Path("artifacts/demo"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(build(args.results, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
