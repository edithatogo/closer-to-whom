"""Materialise deterministic SA2 polygon centroids for aggregate routing."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
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
LAYER_URL = (
    "https://services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/"
    "2023_Census_totals_by_topic_for_households_by_SA2/FeatureServer/1"
)
QUERY_URL = f"{LAYER_URL}/query"
PAGE_SIZE = 1000
FetchPage = Callable[[int, int], dict[str, Any]]


def fetch_page(offset: int, page_size: int) -> dict[str, Any]:
    """Fetch one bounded ArcGIS centroid page in WGS84."""
    query = urlencode(
        {
            "where": "1=1",
            "outFields": "SA22023_V1_00,SA22023_V1_00_NAME",
            "returnGeometry": "false",
            "returnCentroid": "true",
            "outSR": "4326",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "orderByFields": "OBJECTID",
            "f": "json",
        }
    )
    request = Request(
        f"{QUERY_URL}?{query}",
        headers={"User-Agent": "closer-to-home/1.0 evidence-materializer"},
    )
    with urlopen(request, timeout=60) as response:
        payload = json.loads(response.read())
    if not isinstance(payload, dict) or payload.get("error"):
        raise ValueError(f"ArcGIS query failed: {payload.get('error', payload)!r}")
    return payload


def snapshot_fetcher(snapshot_dir: Path) -> FetchPage:
    """Load captured ArcGIS pages without weakening the same validation path."""

    def fetch(offset: int, _page_size: int) -> dict[str, Any]:
        path = snapshot_dir / f"offset-{offset}.json"
        if not path.is_file():
            raise FileNotFoundError(f"Missing captured ArcGIS page: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("error"):
            raise ValueError(f"Invalid captured ArcGIS page: {path}")
        return payload

    return fetch


def _collect(fetcher: FetchPage, page_size: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        payload = fetcher(offset, page_size)
        features = payload.get("features", [])
        if not isinstance(features, list):
            raise TypeError("ArcGIS features must be a list")
        for feature in features:
            attributes = feature.get("attributes", {})
            centroid = feature.get("centroid", {})
            code = str(attributes.get("SA22023_V1_00", "")).strip()
            if not code or "x" not in centroid or "y" not in centroid:
                raise ValueError("ArcGIS feature lacks an SA2 code or centroid")
            rows.append(
                {
                    "geography_code": code,
                    "geography_name": str(attributes.get("SA22023_V1_00_NAME", "")).strip(),
                    "routing_point_id": f"SA2-{code}-centroid",
                    "latitude": float(centroid["y"]),
                    "longitude": float(centroid["x"]),
                    "routing_weight": 1.0,
                    "routing_point_method": "official_polygon_centroid",
                }
            )
        if not payload.get("exceededTransferLimit"):
            break
        if not features:
            raise ValueError("ArcGIS transfer limit continued with an empty page")
        offset += len(features)
    return rows


def materialize(
    population_path: Path = DEFAULT_POPULATION,
    output_path: Path = DEFAULT_OUTPUT,
    report_path: Path = DEFAULT_REPORT,
    *,
    fetcher: FetchPage = fetch_page,
    page_size: int = PAGE_SIZE,
) -> dict[str, Any]:
    """Join official polygon centroids to the captured aggregate population codes."""
    if page_size <= 0 or page_size > 2000:
        raise ValueError("page_size must be between 1 and 2000")
    population = pl.read_parquet(population_path)
    area_column = "AREA_POPES_SUB_004"
    if area_column not in population.columns:
        raise ValueError(f"Population artifact lacks {area_column}")
    population_codes = (
        population.select(pl.col(area_column).cast(pl.String).alias("geography_code"))
        .unique()
        .sort("geography_code")
    )
    points = pl.DataFrame(_collect(fetcher, page_size))
    if points["geography_code"].n_unique() != points.height:
        raise ValueError("ArcGIS response contains duplicate SA2 codes")
    matched = population_codes.join(points, on="geography_code", how="left")
    missing = matched.filter(pl.col("latitude").is_null())["geography_code"].to_list()
    if missing:
        raise ValueError(f"Missing centroids for population SA2 codes: {missing[:10]}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(
        matched, output_path, sort_by=("geography_code", "routing_point_id")
    )
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "materialized_single_centroid_baseline",
        "source_id": "candidate.statsnz-sa2-2023-arcgis",
        "source_url": LAYER_URL,
        "population_code_count": population_codes.height,
        "routing_point_count": matched.height,
        "routing_weight_rule": "one centroid with weight 1.0 per SA2",
        "parquet_fingerprint": fingerprint,
        "uncertainty": (
            "A polygon centroid is a reproducible spatial baseline, not a population-weighted "
            "origin or observed residence; multi-point sensitivity analysis remains required."
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
    parser.add_argument("--page-size", type=int, default=PAGE_SIZE)
    parser.add_argument(
        "--snapshot-dir",
        type=Path,
        help="Read offset-N.json pages captured from the fixed ArcGIS query instead of networking",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                args.population,
                args.output,
                args.report,
                page_size=args.page_size,
                fetcher=snapshot_fetcher(args.snapshot_dir) if args.snapshot_dir else fetch_page,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
