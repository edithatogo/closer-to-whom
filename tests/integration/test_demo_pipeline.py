from __future__ import annotations

import json
from pathlib import Path

import polars as pl

from closer_to_whom.pipeline import compare_manifests, run_demo


def test_demo_pipeline_and_reproducibility(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    manifest = run_demo(left, seed=7)
    run_demo(right, seed=7)
    assert manifest["validation_passed"]
    assert compare_manifests(left / "manifest.json", right / "manifest.json")
    results = pl.read_parquet(left / "results.parquet")
    assert results.height == manifest["row_counts"]["results"]
    optimisation = json.loads((left / "optimisation.json").read_text())
    assert optimisation["p_median"]["selected_facility_ids"]
    assert (left / "mcda.json").exists()
    assert (left / "voi.json").exists()
