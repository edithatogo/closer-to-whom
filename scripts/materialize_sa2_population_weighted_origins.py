"""Materialise population-weighted SA1 centroid origins within each denominator SA2."""

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
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

from closer_to_whom.io import write_parquet_deterministic

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POPULATION = ROOT / "data/derived/stats-nz-population.parquet"
DEFAULT_BASELINE = ROOT / "data/derived/sa2-routing-points.parquet"
DEFAULT_OUTPUT = ROOT / "data/derived/sa2-population-weighted-origins.parquet"
DEFAULT_REPORT = ROOT / "reports/sa2-population-weighted-origins.json"
SA1_LAYER = (
    "https://services2.arcgis.com/vKb0s8tBIA3bdocZ/arcgis/rest/services/"
    "2023_Census_totals_by_topic_for_individuals_by_SA1/FeatureServer/1"
)
SA2_LAYER = (
    "https://services2.arcgis.com/vKb0s8tBIA3bdocZ/arcgis/rest/services/"
    "Statistical_Area_2_2023/FeatureServer/0"
)
JsonGetter = Callable[[str], dict[str, Any]]


def _get_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "closer-to-home/1.0 evidence-materializer"})
    with urlopen(request, timeout=180) as response:
        payload = json.loads(response.read())
    if not isinstance(payload, dict):
        raise TypeError("ArcGIS response must be an object")
    return payload


def fetch_sa1_centroids(
    *,
    getter: JsonGetter = _get_json,
    page_size: int = 2000,
    snapshot_dir: Path | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    offset = 0
    while True:
        query = urlencode(
            {
                "where": "1=1",
                "outFields": "SA12023_V1_00,VAR_1_3",
                "returnGeometry": "false",
                "returnCentroid": "true",
                "outSR": 4326,
                "orderByFields": "SA12023_V1_00",
                "resultOffset": offset,
                "resultRecordCount": page_size,
                "f": "json",
            }
        )
        snapshot = (
            snapshot_dir / f"sa1-centroids-page{offset // page_size}.json"
            if snapshot_dir is not None
            else None
        )
        if snapshot is not None and snapshot.is_file():
            payload = json.loads(snapshot.read_text(encoding="utf-8"))
        else:
            payload = getter(f"{SA1_LAYER}/query?{query}")
        if payload.get("error"):
            raise ValueError(f"SA1 centroid query failed: {payload['error']}")
        features = payload.get("features")
        if not isinstance(features, list):
            raise TypeError("SA1 features must be a list")
        for feature in features:
            attributes = feature["attributes"]
            centroid = feature.get("centroid")
            if not centroid:
                continue
            rows.append(
                {
                    "sa1_code": str(attributes["SA12023_V1_00"]),
                    "population_2023": int(attributes.get("VAR_1_3") or 0),
                    "longitude": float(centroid["x"]),
                    "latitude": float(centroid["y"]),
                }
            )
        if len(features) < page_size and not payload.get("exceededTransferLimit"):
            break
        if not features:
            raise ValueError("SA1 pagination did not advance")
        offset += len(features)
    codes = [str(row["sa1_code"]) for row in rows]
    if len(codes) != len(set(codes)):
        raise ValueError("SA1 response contains duplicate codes")
    return rows


def fetch_sa2_polygons(
    *,
    getter: JsonGetter = _get_json,
    page_size: int = 2000,
    snapshot_dir: Path | None = None,
) -> list[dict[str, Any]]:
    features: list[dict[str, Any]] = []
    offset = 0
    page = 0
    while True:
        snapshot = (
            snapshot_dir / f"sa2-polygons-page{page}.geojson"
            if snapshot_dir is not None
            else None
        )
        if snapshot is not None and snapshot.is_file():
            payload = json.loads(snapshot.read_text(encoding="utf-8"))
        else:
            query = urlencode(
                {
                    "where": "1=1",
                    "outFields": "SA22023_V1_00",
                    "returnGeometry": "true",
                    "outSR": 4326,
                    "orderByFields": "SA22023_V1_00",
                    "resultOffset": offset,
                    "resultRecordCount": page_size,
                    "f": "geojson",
                }
            )
            payload = getter(f"{SA2_LAYER}/query?{query}")
        page_features = payload.get("features")
        if not isinstance(page_features, list):
            raise TypeError("SA2 GeoJSON features must be a list")
        features.extend(page_features)
        exceeded = bool(payload.get("properties", {}).get("exceededTransferLimit"))
        if len(page_features) < page_size and not exceeded:
            break
        if not page_features:
            raise ValueError("SA2 pagination did not advance")
        offset += len(page_features)
        page += 1
    codes = [str(feature["properties"]["SA22023_V1_00"]) for feature in features]
    if len(codes) != len(set(codes)):
        raise ValueError("SA2 response contains duplicate codes")
    return features


def assign_sa2(
    sa1_rows: list[dict[str, object]],
    sa2_features: list[dict[str, Any]],
) -> list[dict[str, object]]:
    digitised = [feature for feature in sa2_features if feature.get("geometry")]
    polygons = [shape(feature["geometry"]) for feature in digitised]
    codes = [str(feature["properties"]["SA22023_V1_00"]) for feature in digitised]
    tree = STRtree(polygons)
    assigned: list[dict[str, object]] = []
    for row in sa1_rows:
        point = Point(float(row["longitude"]), float(row["latitude"]))
        candidates = tree.query(point, predicate="intersects")
        matches = sorted(codes[int(index)] for index in candidates if polygons[int(index)].covers(point))
        if len(matches) != 1:
            continue
        assigned.append({**row, "geography_code": matches[0]})
    return assigned


def build_origins(
    population: pl.DataFrame,
    baseline: pl.DataFrame,
    assigned: list[dict[str, object]],
) -> pl.DataFrame:
    denominator_codes = set(population["geography_code"].to_list())
    positive = [
        row
        for row in assigned
        if int(row["population_2023"]) > 0 and row["geography_code"] in denominator_codes
    ]
    totals: dict[str, int] = {}
    for row in positive:
        code = str(row["geography_code"])
        totals[code] = totals.get(code, 0) + int(row["population_2023"])
    output = [
        {
            "geography_code": str(row["geography_code"]),
            "routing_point_id": f"SA2-{row['geography_code']}-SA1-{row['sa1_code']}",
            "source_geography_code": str(row["sa1_code"]),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "routing_weight": int(row["population_2023"]) / totals[str(row["geography_code"])],
            "routing_point_method": "stats_nz_sa1_2023_population_weighted_centroid",
            "source_population_2023": int(row["population_2023"]),
        }
        for row in positive
    ]
    covered = set(totals)
    for row in baseline.iter_rows(named=True):
        code = str(row["geography_code"])
        if code in denominator_codes and code not in covered:
            output.append(
                {
                    "geography_code": code,
                    "routing_point_id": str(row["routing_point_id"]),
                    "source_geography_code": None,
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "routing_weight": 1.0,
                    "routing_point_method": "true_centroid_zero_sa1_population_fallback",
                    "source_population_2023": 0,
                }
            )
    result = pl.DataFrame(output).sort(("geography_code", "routing_point_id"))
    weight_errors = (
        result.group_by("geography_code")
        .agg(pl.col("routing_weight").sum().alias("weight_sum"))
        .filter((pl.col("weight_sum") - 1.0).abs() > 1e-10)
    )
    if weight_errors.height:
        raise ValueError("Population-weighted origin weights do not sum to one")
    if result["geography_code"].n_unique() != population.height:
        raise ValueError("Population-weighted origins do not cover every denominator SA2")
    return result


def materialize(
    population_path: Path,
    baseline_path: Path,
    output_path: Path,
    report_path: Path,
    *,
    getter: JsonGetter = _get_json,
    snapshot_dir: Path | None = None,
) -> dict[str, object]:
    population = (
        pl.read_parquet(population_path)
        .select(
            pl.col("AREA_POPES_SUB_004").cast(pl.String).alias("geography_code"),
            pl.col("OBS_VALUE").cast(pl.Int64).alias("population_2025"),
        )
        .unique(subset="geography_code")
        .sort("geography_code")
    )
    baseline = pl.read_parquet(baseline_path)
    sa1_rows = fetch_sa1_centroids(getter=getter, snapshot_dir=snapshot_dir)
    sa2_features = fetch_sa2_polygons(getter=getter, snapshot_dir=snapshot_dir)
    assigned = assign_sa2(sa1_rows, sa2_features)
    origins = build_origins(population, baseline, assigned)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(
        origins, output_path, sort_by=("geography_code", "routing_point_id")
    )
    fallback = origins.filter(
        pl.col("routing_point_method") == "true_centroid_zero_sa1_population_fallback"
    )
    fallback_population = fallback.select("geography_code").join(
        population, on="geography_code", how="left"
    )
    report: dict[str, object] = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "materialized_population_weighted_sensitivity",
        "source_ids": [
            "candidate.statsnz-sa1-census-population-2023",
            "candidate.statsnz-sa2-boundaries-2023",
        ],
        "source_sa1_feature_count": len(sa1_rows),
        "assigned_sa1_feature_count": len(assigned),
        "unassigned_sa1_feature_count": len(sa1_rows) - len(assigned),
        "positive_population_sa1_origin_count": origins.height - fallback.height,
        "denominator_sa2_count": population.height,
        "fallback_sa2_count": fallback.height,
        "fallback_positive_population_sa2_count": fallback_population.filter(
            pl.col("population_2025") > 0
        ).height,
        "fallback_zero_population_sa2_count": fallback_population.filter(
            pl.col("population_2025") == 0
        ).height,
        "fallback_positive_population_2025_total": fallback_population.filter(
            pl.col("population_2025") > 0
        )["population_2025"].sum(),
        "fallback_sa2_codes": fallback["geography_code"].to_list(),
        "origin_count": origins.height,
        "parquet_fingerprint": fingerprint,
        "claim_boundary": (
            "Origins are public aggregate SA1 polygon centroids weighted by 2023 Census usually "
            "resident population. They are sensitivity points, never people, addresses, observed "
            "journeys, or patient locations."
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
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--snapshot-dir", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                args.population,
                args.baseline,
                args.output,
                args.report,
                snapshot_dir=args.snapshot_dir,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
