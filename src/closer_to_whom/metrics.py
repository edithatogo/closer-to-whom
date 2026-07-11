"""Distributional and comparator metrics for aggregate result cubes."""

from __future__ import annotations

import polars as pl


def weighted_mean(value: str, weight: str = "expected_courses") -> pl.Expr:
    """Return a reusable weighted-mean Polars expression."""
    return ((pl.col(value) * pl.col(weight)).sum() / pl.col(weight).sum()).alias(f"mean_{value}")


def weighted_quantile(
    frame: pl.DataFrame,
    value: str,
    quantile: float,
    *,
    weight: str = "expected_courses",
) -> float:
    """Calculate an exact weighted quantile for non-negative aggregate weights."""
    if not 0.0 <= quantile <= 1.0:
        raise ValueError("Quantile must be between zero and one")
    ordered = frame.select(value, weight).sort(value)
    total = float(ordered.select(pl.col(weight).sum()).item())
    if total <= 0:
        raise ValueError("Total weight must be positive")
    threshold = total * quantile
    cumulative = ordered.with_columns(pl.col(weight).cum_sum().alias("_cum"))
    selected = cumulative.filter(pl.col("_cum") >= threshold)
    return float(selected.select(value).head(1).item())


def scenario_summary(results: pl.DataFrame) -> pl.DataFrame:
    """Summarise each scenario and pathway while retaining distributional tails."""
    group_columns = ["scenario_id", "scenario_name", "scenario_kind", "pathway_id", "formulation"]
    means = results.group_by(group_columns).agg(
        pl.col("expected_courses").sum().alias("expected_courses"),
        weighted_mean("course_travel_km"),
        weighted_mean("course_travel_minutes"),
        weighted_mean("patient_direct_cost_nzd"),
        weighted_mean("patient_whanau_cost_nzd"),
        weighted_mean("provider_cost_nzd"),
        weighted_mean("societal_cost_nzd"),
        pl.col("route_is_approximation").any().alias("contains_approximate_routes"),
    )
    tails: list[dict[str, str | float]] = []
    for key, group in results.group_by(group_columns, maintain_order=True):
        key_tuple = key if isinstance(key, tuple) else (key,)
        row: dict[str, str | float] = {
            column: str(value) for column, value in zip(group_columns, key_tuple, strict=True)
        }
        row.update(
            {
                "p50_course_travel_minutes": weighted_quantile(group, "course_travel_minutes", 0.50),
                "p90_course_travel_minutes": weighted_quantile(group, "course_travel_minutes", 0.90),
                "p95_course_travel_minutes": weighted_quantile(group, "course_travel_minutes", 0.95),
            }
        )
        tails.append(row)
    return means.join(pl.DataFrame(tails), on=group_columns, how="left").sort(group_columns)


def compare_to_baseline(
    results: pl.DataFrame,
    *,
    baseline_scenario_id: str,
    outcome: str = "course_travel_minutes",
    threshold: float = 0.0,
) -> pl.DataFrame:
    """Compare each assignment with a pathway-matched baseline at demand-cell level."""
    cohort_key = "decision_cohort" if "decision_cohort" in results.columns else "pathway_id"
    keys = [cohort_key, "demand_cell_id"]
    baseline = results.filter(pl.col("scenario_id") == baseline_scenario_id).select(
        *keys,
        pl.col(outcome).alias("baseline_value"),
    )
    if baseline.is_empty():
        raise ValueError(f"Baseline scenario not present: {baseline_scenario_id}")
    compared = (
        results.join(baseline, on=keys, how="inner", validate="m:1")
        .with_columns((pl.col(outcome) - pl.col("baseline_value")).alias("difference"))
        .with_columns(
            pl.when(pl.col("difference") < -threshold)
            .then(pl.lit("better"))
            .when(pl.col("difference") > threshold)
            .then(pl.lit("worse"))
            .otherwise(pl.lit("similar"))
            .alias("direction")
        )
    )
    return compared


def better_worse_summary(compared: pl.DataFrame) -> pl.DataFrame:
    """Calculate weighted better, similar, and worse shares and mean changes."""
    group_columns = ["scenario_id", "pathway_id", "direction"]
    grouped = compared.group_by(group_columns).agg(
        pl.col("expected_courses").sum().alias("expected_courses"),
        weighted_mean("difference"),
    )
    totals = compared.group_by("scenario_id", "pathway_id").agg(
        pl.col("expected_courses").sum().alias("total_expected_courses")
    )
    return (
        grouped.join(totals, on=["scenario_id", "pathway_id"], how="left")
        .with_columns(
            (pl.col("expected_courses") / pl.col("total_expected_courses")).alias("share")
        )
        .sort(group_columns)
    )
