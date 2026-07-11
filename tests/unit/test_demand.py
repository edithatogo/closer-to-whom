from __future__ import annotations

import polars as pl
import pytest

from closer_to_whom.demand import (
    DemandFactors,
    allocate_to_routing_points,
    calibrate_to_total,
    demand_cells_to_frame,
    expected_courses,
)


def test_expected_courses_and_factor_validation() -> None:
    factors = DemandFactors(0.01, 0.2, 0.5, 0.8)
    assert factors.combined_rate == pytest.approx(0.0008)
    assert expected_courses(1000, factors) == pytest.approx(0.8)
    with pytest.raises(ValueError, match="Population"):
        expected_courses(-1, factors)
    with pytest.raises(ValueError, match="between zero and one"):
        DemandFactors(1.1, 0.2, 0.5, 0.8)


def test_demand_cells_to_frame(bundle: dict[str, object]) -> None:
    frame = demand_cells_to_frame(bundle["demand"])  # type: ignore[arg-type]
    assert frame.height == 10
    assert frame.schema["deprivation_quintile"] == pl.Int8


def test_calibrate_to_total(bundle: dict[str, object]) -> None:
    frame = demand_cells_to_frame(bundle["demand"])  # type: ignore[arg-type]
    calibrated = calibrate_to_total(frame, target_expected_courses=100.0)
    assert calibrated.select(pl.col("expected_courses").sum()).item() == pytest.approx(100.0)
    with pytest.raises(NotImplementedError):
        calibrate_to_total(frame, target_expected_courses=100, group_columns=("region",))
    with pytest.raises(ValueError):
        calibrate_to_total(frame, target_expected_courses=-1)
    with pytest.raises(ValueError):
        calibrate_to_total(pl.DataFrame(), target_expected_courses=1)


def test_allocate_to_routing_points() -> None:
    areas = pl.DataFrame({"geography_code": ["A"], "expected_courses": [10.0]})
    weights = pl.DataFrame(
        {
            "geography_code": ["A", "A"],
            "routing_point_id": ["R1", "R2"],
            "weight": [0.25, 0.75],
            "latitude": [-41.0, -41.1],
            "longitude": [174.0, 174.1],
        }
    )
    allocated = allocate_to_routing_points(areas, weights)
    assert allocated.get_column("expected_courses").to_list() == [2.5, 7.5]
    with pytest.raises(ValueError, match="sum to one"):
        allocate_to_routing_points(areas, weights.with_columns(pl.lit(0.2).alias("weight")))
