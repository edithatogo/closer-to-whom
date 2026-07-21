from __future__ import annotations

import polars as pl
import pytest

from closer_to_whom.capacity import CapacityAssumptions, implied_capacity
from closer_to_whom.equity import equity_gap, equity_summary, worst_served_share
from closer_to_whom.metrics import (
    better_worse_summary,
    compare_to_baseline,
    scenario_summary,
    weighted_quantile,
)
from closer_to_whom.resilience import evaluate_facility_outages
from closer_to_whom.simulation import simulate_all, simulate_scenario_pathway


def _results(bundle: dict[str, object]) -> pl.DataFrame:
    return simulate_all(
        demand_cells=bundle["demand"],  # type: ignore[arg-type]
        facilities=bundle["facilities"],  # type: ignore[arg-type]
        pathways=bundle["pathways"],  # type: ignore[arg-type]
        scenarios=bundle["scenarios"],  # type: ignore[arg-type]
        cost_rates=bundle["cost_rates"],  # type: ignore[arg-type]
        assumptions_fingerprint="test",
    )


def test_simulate_all_and_home_shift(bundle: dict[str, object]) -> None:
    results = _results(bundle)
    assert results.height > 0
    assert results.select(pl.col("scenario_id").n_unique()).item() >= 5
    home = results.filter(pl.col("scenario_id") == "s5_home_sc")
    assert home.select(pl.col("provider_home_visits").max()).item() > 0
    assert home.select(pl.col("provider_cost_nzd").sum()).item() > 0


def test_incompatible_pathway_returns_empty(bundle: dict[str, object]) -> None:
    frame = simulate_scenario_pathway(
        demand_cells=bundle["demand"],  # type: ignore[arg-type]
        facilities=bundle["facilities"],  # type: ignore[arg-type]
        pathway=bundle["pathways"][0],  # type: ignore[index]
        scenario=bundle["scenarios"][3],  # type: ignore[index]
        cost_rates=bundle["cost_rates"],  # type: ignore[arg-type]
        assumptions_fingerprint="test",
    )
    assert frame.is_empty()


def test_summaries_and_comparison(bundle: dict[str, object]) -> None:
    results = _results(bundle)
    summary = scenario_summary(results)
    assert summary.height > 0
    compared = compare_to_baseline(results, baseline_scenario_id="s0_auckland_only_iv")
    assert set(compared.get_column("direction").unique()) <= {"better", "similar", "worse"}
    better_worse = better_worse_summary(compared)
    shares = better_worse.group_by("scenario_id", "pathway_id").agg(pl.col("share").sum())
    assert all(value == pytest.approx(1.0) for value in shares.get_column("share"))
    with pytest.raises(ValueError, match="Baseline"):
        compare_to_baseline(results, baseline_scenario_id="missing")


def test_weighted_quantile() -> None:
    frame = pl.DataFrame({"value": [1.0, 2.0, 10.0], "expected_courses": [1.0, 8.0, 1.0]})
    assert weighted_quantile(frame, "value", 0.5) == 2.0
    with pytest.raises(ValueError):
        weighted_quantile(frame, "value", 2.0)
    with pytest.raises(ValueError):
        weighted_quantile(frame.with_columns(pl.lit(0.0).alias("expected_courses")), "value", 0.5)


def test_equity_and_capacity(bundle: dict[str, object]) -> None:
    results = _results(bundle)
    summary = equity_summary(results, group_column="ethnicity")
    assert summary.height > 0
    gap = equity_gap(
        summary,
        group_column="ethnicity",
        reference_group="European/Other",
        comparison_group="Māori",
        mean_column="mean_course_travel_minutes",
    )
    assert {"absolute_gap", "relative_ratio"}.issubset(gap.columns)
    assert worst_served_share(results).height > 0
    with pytest.raises(ValueError):
        worst_served_share(results, top_fraction=0)
    capacity = implied_capacity(results, assumptions=CapacityAssumptions())
    assert capacity.select(pl.col("annual_expected_courses").min()).item() > 0
    with pytest.raises(ValueError):
        CapacityAssumptions(chair_utilisation_target=1.2)


def test_resilience_on_simulated_assignments(bundle: dict[str, object]) -> None:
    results = _results(bundle)
    facility_id = str(results.get_column("facility_id").head(1).item())
    resilience = evaluate_facility_outages(results, {"single-site": [facility_id]})
    assert resilience.height > 0
    assert resilience.select(pl.col("affected_share").max()).item() <= 1.0
