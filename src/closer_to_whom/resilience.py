"""Aggregate facility-outage sensitivity analysis.

This module measures the assignments touched by declared facility outages. It
does not reroute demand, infer spare capacity, or make an operational claim.
Those boundaries are deliberate while the public service census is pending.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import polars as pl

_REQUIRED_COLUMNS = {"scenario_id", "pathway_id", "facility_id", "expected_courses"}


def evaluate_facility_outages(
    results: pl.DataFrame,
    outage_scenarios: Mapping[str, Iterable[str]],
) -> pl.DataFrame:
    """Return deterministic aggregate assignment impacts for facility outages.

    ``results`` contains aggregate expected-course assignments, not patients.
    For each scenario/pathway and declared outage set, the result reports the
    expected courses assigned to an affected facility and the remainder that
    is not directly affected in this assignment cube. The remainder must not
    be interpreted as successfully rerouted or as available observed capacity.
    """
    if missing := _REQUIRED_COLUMNS - set(results.columns):
        raise ValueError(f"Results missing resilience columns: {sorted(missing)}")
    if results.is_empty():
        raise ValueError("Resilience analysis requires non-empty aggregate results")
    if results.select(pl.col("expected_courses").is_null().any()).item():
        raise ValueError("Expected courses cannot be null")
    if results.select((pl.col("expected_courses") < 0).any()).item():
        raise ValueError("Expected courses cannot be negative")

    declared: dict[str, frozenset[str]] = {}
    for outage_id, facilities in outage_scenarios.items():
        if not outage_id or outage_id in declared:
            raise ValueError("Outage scenario identifiers must be unique and non-empty")
        facility_ids = frozenset(str(facility_id) for facility_id in facilities)
        if not facility_ids:
            raise ValueError(f"Outage scenario has no facilities: {outage_id}")
        declared[str(outage_id)] = facility_ids
    if not declared:
        raise ValueError("At least one outage scenario is required")

    rows: list[dict[str, str | float | int | bool]] = []
    group_columns = ["scenario_id", "pathway_id"]
    for scenario_id, pathway_id in (
        results.select(group_columns).unique(maintain_order=True).iter_rows()
    ):
        group = results.filter(
            (pl.col("scenario_id") == scenario_id) & (pl.col("pathway_id") == pathway_id)
        )
        total = float(group.select(pl.col("expected_courses").sum()).item())
        for outage_id, facility_ids in sorted(declared.items()):
            affected = float(
                group.filter(pl.col("facility_id").cast(pl.String).is_in(facility_ids))
                .select(pl.col("expected_courses").sum())
                .item()
                or 0.0
            )
            rows.append(
                {
                    "outage_scenario_id": outage_id,
                    "scenario_id": str(scenario_id),
                    "pathway_id": str(pathway_id),
                    "facilities_out": len(facility_ids),
                    "affected_expected_courses": affected,
                    "retained_assignment_expected_courses": total - affected,
                    "affected_share": affected / total if total else 0.0,
                    "rerouting_modelled": False,
                    "observed_capacity_claim": False,
                }
            )
    return pl.DataFrame(rows).sort(["outage_scenario_id", "scenario_id", "pathway_id"])
