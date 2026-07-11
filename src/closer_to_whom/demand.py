"""Aggregate expected-demand modelling without simulated individuals."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import polars as pl

from closer_to_whom.models import DemandCell


@dataclass(frozen=True, slots=True)
class DemandFactors:
    """Multiplicative factors converting population to expected courses."""

    incidence_per_person: float
    her2_positive_probability: float
    clinical_eligibility_probability: float
    treatment_uptake_probability: float

    def __post_init__(self) -> None:
        for name, value in (
            ("incidence_per_person", self.incidence_per_person),
            ("her2_positive_probability", self.her2_positive_probability),
            ("clinical_eligibility_probability", self.clinical_eligibility_probability),
            ("treatment_uptake_probability", self.treatment_uptake_probability),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between zero and one")

    @property
    def combined_rate(self) -> float:
        """Return the aggregate treated-course rate per person."""
        return (
            self.incidence_per_person
            * self.her2_positive_probability
            * self.clinical_eligibility_probability
            * self.treatment_uptake_probability
        )


def expected_courses(population: float, factors: DemandFactors) -> float:
    """Estimate fractional aggregate treatment courses."""
    if population < 0:
        raise ValueError("Population cannot be negative")
    return population * factors.combined_rate


def demand_cells_to_frame(cells: Iterable[DemandCell]) -> pl.DataFrame:
    """Convert validated aggregate cells to a canonical frame."""
    rows = [cell.model_dump(mode="json") for cell in cells]
    frame = pl.DataFrame(rows)
    if frame.is_empty():
        return frame
    return frame.with_columns(
        pl.col("deprivation_quintile").cast(pl.Int8),
        pl.col("expected_courses").cast(pl.Float64),
    ).sort("demand_cell_id")


def calibrate_to_total(
    frame: pl.DataFrame,
    *,
    target_expected_courses: float,
    group_columns: tuple[str, ...] = (),
) -> pl.DataFrame:
    """Scale aggregate expected demand to a public calibration total."""
    if target_expected_courses < 0:
        raise ValueError("Target expected courses cannot be negative")
    if frame.is_empty():
        if target_expected_courses == 0:
            return frame
        raise ValueError("Cannot calibrate an empty frame to a positive total")
    if group_columns:
        raise NotImplementedError("Group-specific targets require an explicit target table")
    current = float(frame.select(pl.col("expected_courses").sum()).item())
    if current <= 0:
        raise ValueError("Current aggregate expected courses must be positive")
    factor = target_expected_courses / current
    return frame.with_columns((pl.col("expected_courses") * factor).alias("expected_courses"))


def allocate_to_routing_points(
    area_frame: pl.DataFrame,
    routing_weights: pl.DataFrame,
) -> pl.DataFrame:
    """Fractionally allocate area demand to public population-weighted routing points."""
    required_area = {"geography_code", "expected_courses"}
    required_weights = {"geography_code", "routing_point_id", "weight", "latitude", "longitude"}
    if missing := required_area - set(area_frame.columns):
        raise ValueError(f"Area demand missing columns: {sorted(missing)}")
    if missing := required_weights - set(routing_weights.columns):
        raise ValueError(f"Routing weights missing columns: {sorted(missing)}")
    sums = routing_weights.group_by("geography_code").agg(pl.col("weight").sum().alias("sum_weight"))
    bad = sums.filter((pl.col("sum_weight") - 1.0).abs() > 1e-9)
    if bad.height:
        raise ValueError("Routing-point weights must sum to one within each geography")
    return (
        area_frame.join(routing_weights, on="geography_code", how="inner", validate="1:m")
        .with_columns((pl.col("expected_courses") * pl.col("weight")).alias("expected_courses"))
        .drop("weight")
    )
