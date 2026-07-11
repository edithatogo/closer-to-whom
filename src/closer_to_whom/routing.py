"""Routing contracts and deterministic offline route approximations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np
import polars as pl

EARTH_RADIUS_KM = 6371.0088


@dataclass(frozen=True, slots=True)
class RouteEstimate:
    """One-way route estimate between an origin and destination."""

    distance_km: float
    duration_minutes: float
    engine: str
    engine_version: str
    approximation: bool

    def __post_init__(self) -> None:
        if self.distance_km < 0 or self.duration_minutes < 0:
            raise ValueError("Route distance and duration must be non-negative")


@runtime_checkable
class RouteEngine(Protocol):
    """Protocol implemented by offline and externally backed route engines."""

    @property
    def identity(self) -> str:
        """Return an engine and version identity."""

    def route(
        self,
        origin_latitude: float,
        origin_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
    ) -> RouteEstimate:
        """Estimate one-way distance and duration."""


def haversine_km(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
) -> float:
    """Calculate great-circle distance between two WGS84 coordinates."""
    lat1, lon1, lat2, lon2 = map(
        math.radians,
        (origin_latitude, origin_longitude, destination_latitude, destination_longitude),
    )
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def haversine_matrix_km(origins: np.ndarray, destinations: np.ndarray) -> np.ndarray:
    """Vectorised pairwise great-circle distance matrix."""
    if origins.ndim != 2 or destinations.ndim != 2 or origins.shape[1] != 2 or destinations.shape[1] != 2:
        raise ValueError("Origins and destinations must have shape (n, 2)")
    lat1 = np.radians(origins[:, 0])[:, None]
    lon1 = np.radians(origins[:, 1])[:, None]
    lat2 = np.radians(destinations[:, 0])[None, :]
    lon2 = np.radians(destinations[:, 1])[None, :]
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    a = np.sin(d_lat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(d_lon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


@dataclass(frozen=True, slots=True)
class OfflineApproximationEngine:
    """Deterministic fallback for tests and early public-data prototyping.

    It is not a substitute for a road-network engine in publication analyses.
    """

    road_circuity: float = 1.25
    average_speed_kmh: float = 65.0
    fixed_access_minutes: float = 5.0
    version: str = "1"

    def __post_init__(self) -> None:
        if self.road_circuity < 1.0:
            raise ValueError("Road circuity must be at least one")
        if self.average_speed_kmh <= 0:
            raise ValueError("Average speed must be positive")
        if self.fixed_access_minutes < 0:
            raise ValueError("Fixed access minutes cannot be negative")

    @property
    def identity(self) -> str:
        """Return a stable engine identity."""
        return f"offline-approximation:{self.version}"

    def route(
        self,
        origin_latitude: float,
        origin_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
    ) -> RouteEstimate:
        """Approximate a road route from great-circle distance."""
        distance = haversine_km(
            origin_latitude,
            origin_longitude,
            destination_latitude,
            destination_longitude,
        ) * self.road_circuity
        duration = distance / self.average_speed_kmh * 60.0 + self.fixed_access_minutes
        return RouteEstimate(distance, duration, "offline-approximation", self.version, True)


def build_route_matrix(
    demand: pl.DataFrame,
    facilities: pl.DataFrame,
    engine: RouteEngine,
) -> pl.DataFrame:
    """Build a deterministic origin-destination matrix for aggregate demand cells."""
    required_demand = {"demand_cell_id", "latitude", "longitude"}
    required_facilities = {"facility_id", "latitude", "longitude"}
    if missing := required_demand - set(demand.columns):
        raise ValueError(f"Demand missing route columns: {sorted(missing)}")
    if missing := required_facilities - set(facilities.columns):
        raise ValueError(f"Facilities missing route columns: {sorted(missing)}")
    rows: list[dict[str, str | float | bool]] = []
    for origin in demand.select(sorted(required_demand)).unique().sort("demand_cell_id").iter_rows(named=True):
        for destination in facilities.select(sorted(required_facilities)).sort("facility_id").iter_rows(named=True):
            route = engine.route(
                float(origin["latitude"]),
                float(origin["longitude"]),
                float(destination["latitude"]),
                float(destination["longitude"]),
            )
            rows.append(
                {
                    "demand_cell_id": str(origin["demand_cell_id"]),
                    "facility_id": str(destination["facility_id"]),
                    "one_way_km": route.distance_km,
                    "one_way_minutes": route.duration_minutes,
                    "route_engine": route.engine,
                    "route_engine_version": route.engine_version,
                    "route_is_approximation": route.approximation,
                }
            )
    return pl.DataFrame(rows).sort(["demand_cell_id", "facility_id"])
