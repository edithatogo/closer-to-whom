"""Area-level equity metrics with explicit ecological limitations."""

from __future__ import annotations

import polars as pl

from closer_to_whom.metrics import weighted_mean, weighted_quantile


def equity_summary(
    results: pl.DataFrame,
    *,
    group_column: str,
    outcome: str = "course_travel_minutes",
) -> pl.DataFrame:
    """Summarise weighted burden by public aggregate population stratum."""
    if group_column not in results.columns:
        raise ValueError(f"Unknown equity group column: {group_column}")
    group_columns = ["scenario_id", "pathway_id", group_column]
    means = results.group_by(group_columns).agg(
        pl.col("expected_courses").sum().alias("expected_courses"),
        weighted_mean(outcome),
    )
    tails: list[dict[str, str | float | int]] = []
    for key, group in results.group_by(group_columns, maintain_order=True):
        values = key if isinstance(key, tuple) else (key,)
        row = dict(zip(group_columns, values, strict=True))
        row["p90"] = weighted_quantile(group, outcome, 0.90)
        row["p95"] = weighted_quantile(group, outcome, 0.95)
        tails.append(row)
    return means.join(pl.DataFrame(tails), on=group_columns, how="left").sort(group_columns)


def equity_gap(
    summary: pl.DataFrame,
    *,
    group_column: str,
    reference_group: str,
    comparison_group: str,
    mean_column: str,
) -> pl.DataFrame:
    """Calculate absolute and relative gaps between two aggregate groups."""
    keys = ["scenario_id", "pathway_id"]
    reference = summary.filter(pl.col(group_column) == reference_group).select(
        *keys,
        pl.col(mean_column).alias("reference_value"),
    )
    comparison = summary.filter(pl.col(group_column) == comparison_group).select(
        *keys,
        pl.col(mean_column).alias("comparison_value"),
    )
    return (
        comparison.join(reference, on=keys, how="inner", validate="1:1")
        .with_columns(
            (pl.col("comparison_value") - pl.col("reference_value")).alias("absolute_gap"),
            (pl.col("comparison_value") / pl.col("reference_value")).alias("relative_ratio"),
        )
        .sort(keys)
    )


def worst_served_share(
    results: pl.DataFrame,
    *,
    outcome: str = "course_travel_minutes",
    top_fraction: float = 0.10,
) -> pl.DataFrame:
    """Identify aggregate demand contained in the highest-burden tail."""
    if not 0.0 < top_fraction <= 1.0:
        raise ValueError("top_fraction must be in (0, 1]")
    rows: list[dict[str, str | float]] = []
    for key, group in results.group_by(["scenario_id", "pathway_id"], maintain_order=True):
        scenario_id, pathway_id = key
        threshold = weighted_quantile(group, outcome, 1.0 - top_fraction)
        tail = group.filter(pl.col(outcome) >= threshold)
        rows.append(
            {
                "scenario_id": str(scenario_id),
                "pathway_id": str(pathway_id),
                "threshold": threshold,
                "tail_expected_courses": float(tail.select(pl.col("expected_courses").sum()).item()),
            }
        )
    return pl.DataFrame(rows).sort(["scenario_id", "pathway_id"])
