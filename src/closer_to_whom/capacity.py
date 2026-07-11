"""Implied infrastructure and workforce requirements."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl


@dataclass(frozen=True, slots=True)
class CapacityAssumptions:
    """Transparent conversion assumptions for implied capacity."""

    working_days_per_year: float = 240.0
    productive_hours_per_fte_year: float = 1500.0
    active_nursing_fraction_of_on_site_time: float = 0.45
    chair_utilisation_target: float = 0.80
    peak_to_mean_factor: float = 1.25

    def __post_init__(self) -> None:
        values = (
            self.working_days_per_year,
            self.productive_hours_per_fte_year,
            self.active_nursing_fraction_of_on_site_time,
            self.chair_utilisation_target,
            self.peak_to_mean_factor,
        )
        if any(value <= 0 for value in values):
            raise ValueError("Capacity assumptions must be positive")
        if self.active_nursing_fraction_of_on_site_time > 1:
            raise ValueError("Active nursing fraction cannot exceed one")
        if self.chair_utilisation_target > 1:
            raise ValueError("Chair utilisation target cannot exceed one")


def implied_capacity(
    results: pl.DataFrame,
    *,
    assumptions: CapacityAssumptions | None = None,
) -> pl.DataFrame:
    """Convert expected assignments to implied workload, not observed capacity."""
    cfg = assumptions or CapacityAssumptions()
    required = {
        "scenario_id",
        "pathway_id",
        "facility_id",
        "expected_courses",
        "patient_visits",
        "provider_home_visits",
        "course_on_site_minutes",
    }
    if missing := required - set(results.columns):
        raise ValueError(f"Results missing capacity columns: {sorted(missing)}")
    workload = results.with_columns(
        (pl.col("expected_courses") * pl.col("patient_visits")).alias("annual_patient_visits"),
        (pl.col("expected_courses") * pl.col("provider_home_visits")).alias(
            "annual_home_visits"
        ),
        (pl.col("expected_courses") * pl.col("course_on_site_minutes")).alias(
            "annual_on_site_minutes"
        ),
    )
    return (
        workload.group_by("scenario_id", "pathway_id", "facility_id")
        .agg(
            pl.col("expected_courses").sum().alias("annual_expected_courses"),
            pl.col("annual_patient_visits").sum(),
            pl.col("annual_home_visits").sum(),
            pl.col("annual_on_site_minutes").sum(),
        )
        .with_columns(
            (pl.col("annual_on_site_minutes") / 60.0).alias("annual_chair_hours"),
            (
                pl.col("annual_on_site_minutes")
                * cfg.active_nursing_fraction_of_on_site_time
                / 60.0
            ).alias("annual_active_nursing_hours"),
            (pl.col("annual_patient_visits") / cfg.working_days_per_year).alias(
                "mean_patient_visits_per_day"
            ),
        )
        .with_columns(
            (
                pl.col("annual_chair_hours")
                / (cfg.productive_hours_per_fte_year * cfg.chair_utilisation_target)
            ).alias("implied_chair_fte_equivalent"),
            (
                pl.col("annual_active_nursing_hours") / cfg.productive_hours_per_fte_year
            ).alias("implied_nursing_fte"),
            (pl.col("mean_patient_visits_per_day") * cfg.peak_to_mean_factor).alias(
                "peak_equivalent_visits_per_day"
            ),
        )
        .sort(["scenario_id", "pathway_id", "facility_id"])
    )
