"""Materialise official Stats NZ SA2 true centroids through anonymous public query access."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import polars as pl

from closer_to_whom.io import write_parquet_deterministic

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POPULATION = ROOT / "data/derived/stats-nz-population.parquet"
DEFAULT_OUTPUT = ROOT / "data/derived/sa2-routing-points.parquet"
DEFAULT_REPORT = ROOT / "reports/sa2-routing-points.json"
LAYER_ID = 111211
LAYER_URL = (
    "https://datafinder.stats.govt.nz/layer/"
    "111211-statistical-area-2-2023-centroid-true/"
)
QUERY_URL = "https://datafinder.stats.govt.nz/services/query/v1/vector.json"
TOKEN_PATTERN = re.compile(
    r'<script id="pre-cached-token" type="application/json">(.*?)</script>',
    re.DOTALL,
)
JsonGetter = Callable[[str], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class Cell:
    west: float
    south: float
    east: float
    north: float
    depth: int = 0

    @property
    def centre(self) -> tuple[float, float]:
        return ((self.west + self.east) / 2.0, (self.south + self.north) / 2.0)

    @property
    def radius_metres(self) -> int:
        _, latitude = self.centre
        lat_km = (self.north - self.south) * 111.2 / 2.0
        lon_km = (self.east - self.west) * 111.2 * math.cos(math.radians(latitude)) / 2.0
        return math.ceil(math.hypot(lat_km, lon_km) * 1000.0 + 1500.0)

    def subdivide(self) -> tuple[Cell, Cell, Cell, Cell]:
        longitude, latitude = self.centre
        depth = self.depth + 1
        return (
            Cell(self.west, self.south, longitude, latitude, depth),
            Cell(longitude, self.south, self.east, latitude, depth),
            Cell(self.west, latitude, longitude, self.north, depth),
            Cell(longitude, latitude, self.east, self.north, depth),
        )


def _get_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "closer-to-home/1.0 evidence-materializer"})
    with urlopen(request, timeout=60) as response:
        payload = json.loads(response.read())
    if not isinstance(payload, dict):
        raise TypeError("Stats NZ query response must be an object")
    return payload


def anonymous_query_token() -> str:
    request = Request(
        LAYER_URL,
        headers={"User-Agent": "closer-to-home/1.0 evidence-materializer"},
    )
    with urlopen(request, timeout=60) as response:
        page = response.read().decode("utf-8")
    match = TOKEN_PATTERN.search(page)
    if not match:
        raise ValueError("Stats NZ public layer did not provide an anonymous query token")
    payload = json.loads(match.group(1))
    token = str(payload.get("key", "")).strip()
    if not token:
        raise ValueError("Stats NZ anonymous query token is empty")
    return token


def _query_cell(cell: Cell, token: str, getter: JsonGetter) -> tuple[Cell, list[dict[str, Any]]]:
    longitude, latitude = cell.centre
    query = urlencode(
        {
            "key": token,
            "layer": LAYER_ID,
            "x": longitude,
            "y": latitude,
            "max_results": 100,
            "radius": min(cell.radius_metres, 100_000),
            "geometry": "true",
            "with_field_names": "true",
        }
    )
    try:
        payload = getter(f"{QUERY_URL}?{query}")
        features = payload["vectorQuery"]["layers"][str(LAYER_ID)]["features"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Stats NZ vector query returned an invalid response") from exc
    if not isinstance(features, list):
        raise TypeError("Stats NZ vector query features must be a list")
    return cell, features


def initial_cells() -> list[Cell]:
    """Cover mainland New Zealand and the Chatham Islands with one-degree cells."""
    cells: list[Cell] = []
    for west, east, south, north in ((166, 179, -48, -34), (-177.5, -175.5, -45, -43)):
        longitude = west
        while longitude < east:
            latitude = south
            while latitude < north:
                cells.append(Cell(longitude, latitude, longitude + 1.0, latitude + 1.0))
                latitude += 1.0
            longitude += 1.0
    return cells


def fetch_all(token: str, *, getter: JsonGetter = _get_json, workers: int = 8) -> list[dict[str, Any]]:
    """Query an adaptive complete-cover grid, subdividing any capped cell."""
    if not 1 <= workers <= 16:
        raise ValueError("workers must be between 1 and 16")
    pending = initial_cells()
    unique: dict[str, dict[str, Any]] = {}
    while pending:
        next_pending: list[Cell] = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = executor.map(lambda cell: _query_cell(cell, token, getter), pending)
            for cell, features in results:
                if len(features) == 100:
                    if cell.depth >= 7:
                        raise ValueError("Stats NZ query remained capped after seven subdivisions")
                    next_pending.extend(cell.subdivide())
                    continue
                for feature in features:
                    properties = feature.get("properties", {})
                    code = str(properties.get("SA22023_V1_00", "")).strip()
                    if code:
                        unique[code] = feature
        pending = next_pending
    return [unique[code] for code in sorted(unique)]


def materialize(
    population_path: Path = DEFAULT_POPULATION,
    output_path: Path = DEFAULT_OUTPUT,
    report_path: Path = DEFAULT_REPORT,
    *,
    token: str | None = None,
    getter: JsonGetter = _get_json,
    workers: int = 8,
) -> dict[str, Any]:
    population = pl.read_parquet(population_path)
    area_column = "AREA_POPES_SUB_004"
    population_codes = (
        population.select(pl.col(area_column).cast(pl.String).alias("geography_code"))
        .unique()
        .sort("geography_code")
    )
    features = fetch_all(token or anonymous_query_token(), getter=getter, workers=workers)
    rows = []
    for feature in features:
        properties = feature["properties"]
        code = str(properties["SA22023_V1_00"])
        rows.append(
            {
                "geography_code": code,
                "geography_name": str(properties["SA22023_V1_00_NAME"]),
                "routing_point_id": f"SA2-{code}-true-centroid",
                "latitude": float(properties["LATITUDE"]),
                "longitude": float(properties["LONGITUDE"]),
                "routing_weight": 1.0,
                "routing_point_method": "stats_nz_true_centroid",
            }
        )
    points = pl.DataFrame(rows)
    matched = population_codes.join(points, on="geography_code", how="left")
    missing = matched.filter(pl.col("latitude").is_null())["geography_code"].to_list()
    if missing:
        raise ValueError(f"Missing true centroids for population SA2 codes: {missing[:10]}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(
        matched, output_path, sort_by=("geography_code", "routing_point_id")
    )
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "materialized_official_true_centroid_baseline",
        "source_id": "candidate.statsnz-sa2-2023-centroid-true",
        "source_url": LAYER_URL,
        "source_layer_id": LAYER_ID,
        "source_feature_count": len(features),
        "population_code_count": population_codes.height,
        "routing_point_count": matched.height,
        "routing_weight_rule": "one official true centroid with weight 1.0 per SA2",
        "parquet_fingerprint": fingerprint,
        "uncertainty": (
            "A true polygon centroid is a reproducible spatial baseline, not a "
            "population-weighted origin or observed residence."
        ),
        "claim_boundary": (
            "Routing points represent aggregate SA2 polygons and never people, patients, "
            "addresses, observed journeys, or treatment demand."
        ),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", type=Path, default=DEFAULT_POPULATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                args.population,
                args.output,
                args.report,
                workers=args.workers,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
