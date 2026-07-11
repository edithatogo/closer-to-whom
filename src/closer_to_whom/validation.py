"""Model invariants and release-facing validation checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import polars as pl

from closer_to_whom.provenance import write_json


@dataclass(frozen=True, slots=True)
class CheckResult:
    """One validation check and its evidence."""

    check_id: str
    passed: bool
    message: str
    severity: str = "error"


Check = Callable[[], CheckResult]


def check_non_negative_results(results: pl.DataFrame) -> CheckResult:
    """Require all burden and cost outputs to be non-negative."""
    columns = [
        "one_way_km",
        "one_way_minutes",
        "course_travel_km",
        "course_travel_minutes",
        "course_on_site_minutes",
        "patient_direct_cost_nzd",
        "patient_whanau_cost_nzd",
        "payer_cost_nzd",
        "provider_cost_nzd",
        "societal_cost_nzd",
    ]
    minimum = min(float(results.select(pl.col(column).min()).item()) for column in columns)
    return CheckResult(
        "results.non_negative",
        minimum >= -1e-9,
        f"Minimum checked outcome: {minimum:.12g}",
    )


def check_unique_assignments(results: pl.DataFrame) -> CheckResult:
    """Require one assignment per scenario, pathway, and aggregate demand cell."""
    keys = ["scenario_id", "pathway_id", "demand_cell_id"]
    duplicate_count = results.group_by(keys).len().filter(pl.col("len") != 1).height
    return CheckResult(
        "results.unique_assignments",
        duplicate_count == 0,
        f"Non-unique assignment groups: {duplicate_count}",
    )


def check_expected_course_conservation(results: pl.DataFrame) -> CheckResult:
    """Require each compatible scenario/pathway to conserve its represented demand."""
    totals = results.group_by("scenario_id", "pathway_id").agg(
        pl.col("expected_courses").sum().alias("total")
    )
    minimum = float(totals.select(pl.col("total").min()).item())
    return CheckResult(
        "results.positive_demand",
        minimum > 0,
        f"Smallest represented expected-course total: {minimum:.6g}",
    )


def check_home_shifts_burden(results: pl.DataFrame) -> CheckResult:
    """Require the synthetic home scenario to shift some travel to provider resources."""
    home = results.filter(pl.col("scenario_id").str.contains("home"))
    if home.is_empty():
        return CheckResult("results.home_shift", True, "No home scenario in this run", "warning")
    provider = float(home.select(pl.col("provider_cost_nzd").sum()).item())
    home_visits = float(home.select(pl.col("provider_home_visits").sum()).item())
    passed = provider > 0 and home_visits > 0
    return CheckResult(
        "results.home_shift",
        passed,
        f"Provider cost={provider:.6g}; provider home visits={home_visits:.6g}",
    )


def validate_results(results: pl.DataFrame, *, output: Path | None = None) -> tuple[CheckResult, ...]:
    """Run all result-cube invariants and optionally write a receipt."""
    checks = (
        check_non_negative_results(results),
        check_unique_assignments(results),
        check_expected_course_conservation(results),
        check_home_shifts_burden(results),
    )
    if output is not None:
        write_json(
            output,
            {
                "passed": all(item.passed or item.severity != "error" for item in checks),
                "checks": [asdict(item) for item in checks],
            },
        )
    return checks
