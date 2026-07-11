from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from closer_to_whom.demand import demand_cells_to_frame
from closer_to_whom.registry import facilities_to_frame
from closer_to_whom.routing import (
    OfflineApproximationEngine,
    build_route_matrix,
    haversine_km,
    haversine_matrix_km,
)


def test_haversine_identity_and_known_scale() -> None:
    assert haversine_km(-41.0, 174.0, -41.0, 174.0) == pytest.approx(0.0)
    assert haversine_km(-41.0, 174.0, -42.0, 174.0) == pytest.approx(111.2, rel=0.01)


def test_haversine_matrix_shape_and_validation() -> None:
    matrix = haversine_matrix_km(
        np.array([[-41.0, 174.0]]), np.array([[-42.0, 174.0], [-43.0, 172.0]])
    )
    assert matrix.shape == (1, 2)
    with pytest.raises(ValueError, match="shape"):
        haversine_matrix_km(np.array([-41.0, 174.0]), np.array([[-42.0, 174.0]]))


def test_offline_engine_validation_and_route() -> None:
    with pytest.raises(ValueError):
        OfflineApproximationEngine(road_circuity=0.9)
    with pytest.raises(ValueError):
        OfflineApproximationEngine(average_speed_kmh=0)
    engine = OfflineApproximationEngine()
    route = engine.route(-41.0, 174.0, -42.0, 174.0)
    assert route.distance_km > 111
    assert route.duration_minutes > 0
    assert route.approximation


def test_route_matrix(bundle: dict[str, object]) -> None:
    demand = demand_cells_to_frame(bundle["demand"])  # type: ignore[arg-type]
    facilities = facilities_to_frame(bundle["facilities"])  # type: ignore[arg-type]
    matrix = build_route_matrix(demand.head(2), facilities.head(3), OfflineApproximationEngine())
    assert matrix.height == 6
    assert matrix.select(pl.col("one_way_km").min()).item() >= 0
