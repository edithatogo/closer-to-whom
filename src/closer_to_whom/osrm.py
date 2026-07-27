"""Fail-closed client for a locally hosted OSRM table service."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, cast
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

import polars as pl

JsonFetcher = Callable[[str], dict[str, Any]]


def _validate_loopback_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
        "127.0.0.1",
        "localhost",
        "::1",
    }:
        raise ValueError("OSRM base URL must use HTTP(S) on a loopback host")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("OSRM base URL cannot contain credentials, query, or fragment")
    return base_url.rstrip("/")


def _fetch_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "closer-to-home/1.0 local-osrm"})
    with urlopen(request, timeout=120) as response:
        payload = json.loads(response.read())
    if not isinstance(payload, dict):
        raise TypeError("OSRM response must be a JSON object")
    return payload


@dataclass(frozen=True, slots=True)
class LocalOsrmTableClient:
    """Query bounded origin batches against a self-hosted OSRM instance."""

    base_url: str
    version: str
    fetcher: JsonFetcher = _fetch_json
    origin_batch_size: int = 50

    def __post_init__(self) -> None:
        object.__setattr__(self, "base_url", _validate_loopback_url(self.base_url))
        if not self.version.strip():
            raise ValueError("OSRM version must be recorded")
        if not 1 <= self.origin_batch_size <= 100:
            raise ValueError("origin_batch_size must be between 1 and 100")

    @property
    def identity(self) -> str:
        return f"osrm:{self.version}"

    def matrix(self, origins: pl.DataFrame, destinations: pl.DataFrame) -> pl.DataFrame:
        """Return a deterministic aggregate origin-destination matrix."""
        required_origins = {"demand_cell_id", "latitude", "longitude"}
        required_destinations = {"facility_id", "latitude", "longitude"}
        if missing := required_origins - set(origins.columns):
            raise ValueError(f"Origins missing route columns: {sorted(missing)}")
        if missing := required_destinations - set(destinations.columns):
            raise ValueError(f"Destinations missing route columns: {sorted(missing)}")
        origin_rows = origins.select(sorted(required_origins)).sort("demand_cell_id").to_dicts()
        destination_rows = (
            destinations.select(sorted(required_destinations)).sort("facility_id").to_dicts()
        )
        rows: list[dict[str, str | float | bool]] = []
        for start in range(0, len(origin_rows), self.origin_batch_size):
            batch = origin_rows[start : start + self.origin_batch_size]
            payload = self._table(batch, destination_rows)
            distances = payload.get("distances")
            durations = payload.get("durations")
            if payload.get("code") != "Ok" or not _valid_matrix(
                distances, len(batch), len(destination_rows)
            ):
                raise ValueError("OSRM returned an invalid distance matrix")
            if not _valid_matrix(durations, len(batch), len(destination_rows)):
                raise ValueError("OSRM returned an invalid duration matrix")
            distance_matrix = cast(list[list[float | None]], distances)
            duration_matrix = cast(list[list[float | None]], durations)
            for origin_index, origin in enumerate(batch):
                for destination_index, destination in enumerate(destination_rows):
                    distance = distance_matrix[origin_index][destination_index]
                    duration = duration_matrix[origin_index][destination_index]
                    if distance is None or duration is None:
                        raise ValueError("OSRM returned an unroutable origin-destination pair")
                    rows.append(
                        {
                            "demand_cell_id": str(origin["demand_cell_id"]),
                            "facility_id": str(destination["facility_id"]),
                            "one_way_km": float(distance) / 1000.0,
                            "one_way_minutes": float(duration) / 60.0,
                            "route_engine": "osrm",
                            "route_engine_version": self.version,
                            "route_is_approximation": False,
                        }
                    )
        return pl.DataFrame(rows).sort(["demand_cell_id", "facility_id"])

    def _table(
        self,
        origins: Sequence[dict[str, Any]],
        destinations: Sequence[dict[str, Any]],
    ) -> dict[str, Any]:
        points = [*origins, *destinations]
        coordinates = ";".join(
            f"{float(point['longitude']):.8f},{float(point['latitude']):.8f}" for point in points
        )
        source_indexes = ";".join(str(index) for index in range(len(origins)))
        destination_indexes = ";".join(str(index) for index in range(len(origins), len(points)))
        query = urlencode(
            {
                "sources": source_indexes,
                "destinations": destination_indexes,
                "annotations": "distance,duration",
            }
        )
        return self.fetcher(f"{self.base_url}/table/v1/driving/{coordinates}?{query}")


def _valid_matrix(value: Any, rows: int, columns: int) -> bool:
    return (
        isinstance(value, list)
        and len(value) == rows
        and all(isinstance(row, list) and len(row) == columns for row in value)
    )
