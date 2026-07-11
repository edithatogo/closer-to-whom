"""Transparent service-assignment rules."""

from __future__ import annotations

import polars as pl

from closer_to_whom.models import Scenario
from closer_to_whom.types import AssignmentRule


def assign_services(
    demand: pl.DataFrame,
    facilities: pl.DataFrame,
    routes: pl.DataFrame,
    scenario: Scenario,
) -> pl.DataFrame:
    """Assign each aggregate demand cell to one eligible facility."""
    if routes.is_empty() or facilities.is_empty():
        raise ValueError(f"Scenario {scenario.scenario_id} has no eligible assignments")
    candidates = routes.join(
        facilities.select("facility_id", "district"),
        on="facility_id",
        how="inner",
        validate="m:1",
    ).join(
        demand.select("demand_cell_id", pl.col("district").alias("demand_district")),
        on="demand_cell_id",
        how="inner",
        validate="m:1",
    )
    if candidates.is_empty():
        raise ValueError(f"Scenario {scenario.scenario_id} has no eligible assignments")

    if scenario.assignment_rule is AssignmentRule.CENTRAL_ONLY:
        selected = candidates.filter(pl.col("facility_id") == scenario.central_facility_id)
        if selected.select(pl.col("demand_cell_id").n_unique()).item() != demand.height:
            raise ValueError("Central facility is unavailable for one or more demand cells")
        return selected.sort("demand_cell_id")

    if scenario.assignment_rule is AssignmentRule.DOMICILE_DISTRICT:
        candidates = candidates.with_columns(
            (pl.col("district") != pl.col("demand_district")).cast(pl.Int8).alias("outside_district")
        )
        return (
            candidates.sort(["demand_cell_id", "outside_district", "one_way_minutes", "facility_id"])
            .group_by("demand_cell_id", maintain_order=True)
            .first()
            .drop("outside_district")
        )

    # The uncapacitated potential-access implementation is the declared fallback for both nearest
    # and optimisation scenarios. The optimisation module separately proposes candidate networks.
    return (
        candidates.sort(["demand_cell_id", "one_way_minutes", "facility_id"])
        .group_by("demand_cell_id", maintain_order=True)
        .first()
    )
