"""Materialise official Stats NZ Urban Rural 2023 classes for aggregate SA2 origins."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import time
from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import polars as pl
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

from closer_to_whom.io import write_parquet_deterministic

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POINTS = ROOT / "data/derived/sa2-routing-points.parquet"
DEFAULT_OUTPUT = ROOT / "data/derived/sa2-rurality.parquet"
DEFAULT_REPORT = ROOT / "reports/sa2-rurality.json"
DEFAULT_CACHE = ROOT / ".tmp/sa2-rurality-layer-cache"
LAYER_ID = 111198
EXPECTED_TOTAL_FEATURE_COUNT = 745
EXPECTED_EMPTY_GEOMETRY_COUNT = 4
EXPECTED_DIGITISED_FEATURE_COUNT = EXPECTED_TOTAL_FEATURE_COUNT - EXPECTED_EMPTY_GEOMETRY_COUNT
LAYER_URL = "https://datafinder.stats.govt.nz/layer/111198-urban-rural-2023-generalised/"
ARCGIS_LAYER_URL = (
    "https://services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/UR2023/FeatureServer/0"
)
ARCGIS_EXPECTED_FEATURE_COUNT = 689
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

    @property
    def cache_name(self) -> str:
        parts = (self.depth, self.west, self.south, self.east, self.north)
        return "_".join(str(part).replace("-", "m").replace(".", "p") for part in parts) + ".json"


def _get_json(url: str) -> dict[str, Any]:
    if os.name == "nt":
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                payload = json.loads(_powershell_text(url))
                if not isinstance(payload, dict):
                    raise TypeError("Stats NZ query response must be an object")
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
            else:
                return payload
        raise RuntimeError("Windows native query failed after three attempts") from last_error
    request = Request(url, headers={"User-Agent": "closer-to-home/1.0 evidence-materializer"})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=60) as response:
                payload = json.loads(response.read())
            if not isinstance(payload, dict):
                raise TypeError("Stats NZ query response must be an object")
        except (OSError, TimeoutError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
        else:
            return payload
    raise RuntimeError("Stats NZ query failed after three attempts") from last_error


def _powershell_text(url: str) -> str:
    environment = dict(os.environ)
    environment["CTW_QUERY_URL"] = url
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            (
                "$ProgressPreference='SilentlyContinue'; "
                "$c=(Invoke-WebRequest -UseBasicParsing -Uri $env:CTW_QUERY_URL "
                "-TimeoutSec 60).Content; "
                "if($c -is [byte[]]){"
                "[Console]::Out.Write([Text.Encoding]::UTF8.GetString($c))"
                "}else{[Console]::Out.Write([string]$c)}"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        env=environment,
    )
    if result.returncode or not result.stdout.strip():
        raise RuntimeError("Windows native HTTP retrieval failed")
    return result.stdout


def _powershell_download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    environment["CTW_QUERY_URL"] = url
    environment["CTW_QUERY_OUTPUT"] = str(destination)
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            (
                "$ProgressPreference='SilentlyContinue'; "
                "Invoke-WebRequest -UseBasicParsing -Uri $env:CTW_QUERY_URL "
                "-OutFile $env:CTW_QUERY_OUTPUT -TimeoutSec 120"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=150,
        env=environment,
    )
    if result.returncode or not destination.is_file():
        raise RuntimeError("Windows native HTTP download failed")


def fetch_arcgis_polygons(cache_dir: Path = DEFAULT_CACHE) -> list[dict[str, Any]]:
    cache_path = cache_dir / "stats-nz-ur2023-clipped.geojson"
    if not cache_path.is_file():
        query = urlencode(
            {
                "where": "1=1",
                "outFields": ("UR2023_V1_00,UR2023_V1_00_NAME,IUR2023_V1_00,IUR2023_V1_00_NAME"),
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "geojson",
            }
        )
        if os.name != "nt":
            raise RuntimeError("ArcGIS bulk retrieval currently requires the Windows transport")
        _powershell_download(f"{ARCGIS_LAYER_URL}/query?{query}", cache_path)
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    features = payload.get("features", [])
    if not isinstance(features, list) or len(features) != ARCGIS_EXPECTED_FEATURE_COUNT:
        raise ValueError(
            f"Expected {ARCGIS_EXPECTED_FEATURE_COUNT} clipped rurality features, "
            f"got {len(features) if isinstance(features, list) else 'invalid'}"
        )
    return features


def anonymous_query_token() -> str:
    if os.name == "nt":
        page = _powershell_text(LAYER_URL)
    else:
        request = Request(
            LAYER_URL,
            headers={"User-Agent": "closer-to-home/1.0 evidence-materializer"},
        )
        with urlopen(request, timeout=60) as response:
            page = response.read().decode("utf-8")
    match = TOKEN_PATTERN.search(page)
    if not match:
        raise ValueError("Stats NZ public layer did not provide an anonymous query token")
    token = str(json.loads(match.group(1)).get("key", "")).strip()
    if not token:
        raise ValueError("Stats NZ anonymous query token is empty")
    return token


def initial_cells() -> list[Cell]:
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


def _query_cell(
    cell: Cell,
    token: str,
    getter: JsonGetter,
    cache_dir: Path,
) -> tuple[Cell, list[dict[str, Any]]]:
    cache_path = cache_dir / cell.cache_name
    if cache_path.is_file():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if not isinstance(cached, list):
            raise TypeError(f"Invalid cached rurality page: {cache_path}")
        return cell, cached
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
        raise ValueError("Stats NZ rurality query returned an invalid response") from exc
    if not isinstance(features, list):
        raise TypeError("Stats NZ rurality features must be a list")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(features, separators=(",", ":"), sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return cell, features


def fetch_all_polygons(
    token: str,
    *,
    getter: JsonGetter = _get_json,
    workers: int = 12,
    cache_dir: Path = DEFAULT_CACHE,
) -> list[dict[str, Any]]:
    pending = initial_cells()
    unique: dict[str, dict[str, Any]] = {}
    while pending:
        next_pending: list[Cell] = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = executor.map(
                lambda cell: _query_cell(cell, token, getter, cache_dir),
                pending,
            )
            for cell, features in results:
                if len(features) == 100:
                    if cell.depth >= 7:
                        raise ValueError("Stats NZ rurality query remained capped")
                    next_pending.extend(cell.subdivide())
                    continue
                for feature in features:
                    feature_id = str(feature.get("id", "")).strip()
                    if feature_id:
                        unique[feature_id] = feature
        pending = next_pending
    if len(unique) != EXPECTED_DIGITISED_FEATURE_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_DIGITISED_FEATURE_COUNT} digitised rurality polygons, "
            f"got {len(unique)}"
        )
    return [unique[key] for key in sorted(unique, key=int)]


def classify_point(
    point: dict[str, Any],
    features: list[dict[str, Any]],
) -> dict[str, Any]:
    geometries = [shape(feature["geometry"]) for feature in features]
    return _classify_with_index(point, features, geometries, STRtree(geometries))


def _classify_with_index(
    point: dict[str, Any],
    features: list[dict[str, Any]],
    geometries: list[Any],
    tree: STRtree,
) -> dict[str, Any]:
    base = {
        "geography_code": str(point["geography_code"]),
        "routing_point_id": str(point["routing_point_id"]),
    }
    query_point = Point(float(point["longitude"]), float(point["latitude"]))
    matches = [
        int(index)
        for index in tree.query(query_point)
        if geometries[int(index)].covers(query_point)
    ]
    if len(matches) != 1:
        return {
            **base,
            "rurality_status": "unknown_no_polygon" if not matches else "unknown_ambiguous",
            "urban_rural_code": None,
            "urban_rural_name": None,
            "indicator_code": None,
            "indicator_name": None,
        }
    properties = features[matches[0]].get("properties", {})
    return {
        **base,
        "rurality_status": "matched_official_urban_rural_2023",
        "urban_rural_code": str(properties["UR2023_V1_00"]),
        "urban_rural_name": str(properties["UR2023_V1_00_NAME"]),
        "indicator_code": str(properties["IUR2023_V1_00"]),
        "indicator_name": str(properties["IUR2023_V1_00_NAME"]),
    }


def _query_datafinder_point(
    point: dict[str, Any],
    token: str,
    getter: JsonGetter,
    cache_dir: Path,
) -> dict[str, Any]:
    cache_path = cache_dir / "point-refinement" / f"{point['geography_code']}.json"
    if cache_path.is_file():
        features = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        query = urlencode(
            {
                "key": token,
                "layer": LAYER_ID,
                "x": float(point["longitude"]),
                "y": float(point["latitude"]),
                "max_results": 3,
                "radius": 0,
                "geometry": "false",
                "with_field_names": "true",
            }
        )
        payload = getter(f"{QUERY_URL}?{query}")
        try:
            features = payload["vectorQuery"]["layers"][str(LAYER_ID)]["features"]
        except (KeyError, TypeError) as exc:
            raise ValueError("Stats NZ point refinement returned an invalid response") from exc
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(features, separators=(",", ":"), sort_keys=True),
            encoding="utf-8",
            newline="\n",
        )
    base = {
        "geography_code": str(point["geography_code"]),
        "routing_point_id": str(point["routing_point_id"]),
    }
    if not isinstance(features, list) or len(features) != 1:
        return {
            **base,
            "rurality_status": (
                "unknown_no_polygon"
                if isinstance(features, list) and not features
                else "unknown_ambiguous"
            ),
            "urban_rural_code": None,
            "urban_rural_name": None,
            "indicator_code": None,
            "indicator_name": None,
        }
    properties = features[0]["properties"]
    return {
        **base,
        "rurality_status": "matched_official_urban_rural_2023_refined",
        "urban_rural_code": str(properties["UR2023_V1_00"]),
        "urban_rural_name": str(properties["UR2023_V1_00_NAME"]),
        "indicator_code": str(properties["IUR2023_V1_00"]),
        "indicator_name": str(properties["IUR2023_V1_00_NAME"]),
    }


def refine_unknowns(
    rows: list[dict[str, Any]],
    point_rows: list[dict[str, Any]],
    token: str,
    getter: JsonGetter,
    cache_dir: Path,
    workers: int,
) -> list[dict[str, Any]]:
    points_by_code = {str(point["geography_code"]): point for point in point_rows}
    unresolved = [
        points_by_code[str(row["geography_code"])]
        for row in rows
        if str(row["rurality_status"]).startswith("unknown_")
    ]
    with ThreadPoolExecutor(max_workers=min(workers, 8)) as executor:
        refined = list(
            executor.map(
                lambda point: _query_datafinder_point(point, token, getter, cache_dir),
                unresolved,
            )
        )
    refined_by_code = {str(row["geography_code"]): row for row in refined}
    return [refined_by_code.get(str(row["geography_code"]), row) for row in rows]


def materialize(
    points_path: Path = DEFAULT_POINTS,
    output_path: Path = DEFAULT_OUTPUT,
    report_path: Path = DEFAULT_REPORT,
    *,
    token: str | None = None,
    getter: JsonGetter = _get_json,
    workers: int = 12,
    cache_dir: Path = DEFAULT_CACHE,
    source: str = "arcgis",
) -> dict[str, Any]:
    if not 1 <= workers <= 16:
        raise ValueError("workers must be between 1 and 16")
    points = (
        pl.read_parquet(points_path)
        .select(["geography_code", "routing_point_id", "latitude", "longitude"])
        .sort("geography_code")
    )
    if source == "arcgis":
        features = fetch_arcgis_polygons(cache_dir)
    elif source == "datafinder":
        query_token = token or anonymous_query_token()
        features = fetch_all_polygons(
            query_token,
            getter=getter,
            workers=workers,
            cache_dir=cache_dir,
        )
    else:
        raise ValueError("source must be arcgis or datafinder")
    geometries = [shape(feature["geometry"]) for feature in features]
    tree = STRtree(geometries)
    point_rows = points.to_dicts()
    rows = [_classify_with_index(point, features, geometries, tree) for point in point_rows]
    refinement_count = 0
    if source == "arcgis":
        refinement_count = sum(str(row["rurality_status"]).startswith("unknown_") for row in rows)
        if refinement_count:
            rows = refine_unknowns(
                rows,
                point_rows,
                token or anonymous_query_token(),
                getter,
                cache_dir,
                workers,
            )
    frame = pl.DataFrame(rows).sort("geography_code")
    if frame["geography_code"].n_unique() != points.height:
        raise ValueError("Rurality output must contain exactly one row per SA2 routing point")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(frame, output_path, sort_by=("geography_code",))
    status_counts = dict(sorted(Counter(frame["rurality_status"].to_list()).items()))
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": (
            "materialized_complete"
            if status_counts == {"matched_official_urban_rural_2023": points.height}
            else "materialized_with_explicit_unknowns"
        ),
        "source_id": "candidate.statsnz-urban-rural-2023-generalised",
        "source_url": LAYER_URL,
        "source_layer_id": LAYER_ID,
        "retrieval_url": ARCGIS_LAYER_URL if source == "arcgis" else LAYER_URL,
        "retrieval_variant": (
            "official_coastline_clipped_cartographic_layer"
            if source == "arcgis"
            else "official_full_extent_generalised_layer"
        ),
        "canonical_point_refinement_count": refinement_count,
        "source_feature_count": len(features),
        "source_total_feature_count": EXPECTED_TOTAL_FEATURE_COUNT,
        "source_empty_geometry_count": EXPECTED_EMPTY_GEOMETRY_COUNT,
        "routing_point_count": points.height,
        "rurality_row_count": frame.height,
        "status_counts": status_counts,
        "parquet_fingerprint": fingerprint,
        "uncertainty": (
            "The class is assigned at the official SA2 true centroid. Boundary-spanning SA2s and "
            "within-area population distributions require separate spatial sensitivity analysis."
        ),
        "claim_boundary": (
            "This is an aggregate geographic stratifier, not an individual residence, patient "
            "classification, observed travel mode, or treatment-access outcome."
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
    parser.add_argument("--points", type=Path, default=DEFAULT_POINTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--source", choices=("arcgis", "datafinder"), default="arcgis")
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                args.points,
                args.output,
                args.report,
                workers=args.workers,
                cache_dir=args.cache_dir,
                source=args.source,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
