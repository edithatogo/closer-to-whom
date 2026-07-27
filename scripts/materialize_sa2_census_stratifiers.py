"""Materialise public 2023 Census SA2 ethnicity and vehicle-access stratifiers."""

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
DEFAULT_ETHNICITY_OUTPUT = ROOT / "data/derived/sa2-ethnicity.parquet"
DEFAULT_VEHICLE_OUTPUT = ROOT / "data/derived/sa2-vehicle-access.parquet"
DEFAULT_DEMOGRAPHIC_OUTPUT = ROOT / "data/derived/sa2-demographic-allocation.parquet"
DEFAULT_REPORT = ROOT / "reports/sa2-census-stratifiers.json"
INDIVIDUALS_LAYER = (
    "https://services2.arcgis.com/vKb0s8tBIA3bdocZ/arcgis/rest/services/"
    "2023_Census_totals_by_topic_for_individuals_by_SA2/FeatureServer/1"
)
HOUSEHOLDS_LAYER = (
    "https://services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/"
    "2023_Census_totals_by_topic_for_households_by_SA2/FeatureServer/1"
)
ETHNICITY_FIELDS = {
    "european": "VAR_1_158",
    "maori": "VAR_1_159",
    "pacific_peoples": "VAR_1_160",
    "asian": "VAR_1_161",
    "melaa": "VAR_1_162",
    "other_ethnicity": "VAR_1_163",
}
ETHNICITY_TOTAL_STATED = "VAR_1_168"
FEMALE_POPULATION_FIELD = "VAR_1_286"
VEHICLE_FIELDS = {
    "no_motor_vehicle": "VAR_4_136",
    "not_elsewhere_included": "VAR_4_142",
    "total": "VAR_4_143",
    "total_stated": "VAR_4_144",
}
JsonGetter = Callable[[str], dict[str, Any]]


def _get_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "closer-to-home/1.0 evidence-materializer"})
    with urlopen(request, timeout=60) as response:
        payload = json.loads(response.read())
    if not isinstance(payload, dict):
        raise TypeError("ArcGIS response must be an object")
    return payload


def fetch_attributes(
    layer_url: str,
    fields: list[str],
    *,
    getter: JsonGetter = _get_json,
    page_size: int = 2000,
    snapshot_dir: Path | None = None,
    snapshot_prefix: str = "arcgis",
) -> list[dict[str, Any]]:
    """Fetch all attributes in stable SA2-code order with bounded requests."""
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        query = urlencode(
            {
                "where": "1=1",
                "outFields": ",".join(fields),
                "returnGeometry": "false",
                "orderByFields": "SA22023_V1_00",
                "resultOffset": offset,
                "resultRecordCount": page_size,
                "f": "json",
            }
        )
        snapshot = (
            snapshot_dir / f"{snapshot_prefix}-page{offset // page_size}.json"
            if snapshot_dir is not None
            else None
        )
        if snapshot is not None and snapshot.is_file():
            payload = json.loads(snapshot.read_text(encoding="utf-8"))
        else:
            payload = getter(f"{layer_url}/query?{query}")
        if payload.get("error"):
            raise ValueError(f"ArcGIS query failed: {payload['error']}")
        features = payload.get("features")
        if not isinstance(features, list):
            raise TypeError("ArcGIS query features must be a list")
        page = [feature["attributes"] for feature in features]
        rows.extend(page)
        if len(page) < page_size and not payload.get("exceededTransferLimit"):
            break
        if not page:
            raise ValueError("ArcGIS pagination did not advance")
        offset += len(page)
    codes = [str(row["SA22023_V1_00"]) for row in rows]
    if len(codes) != len(set(codes)):
        raise ValueError("ArcGIS response contains duplicate SA2 codes")
    return rows


def _population_codes(path: Path) -> pl.DataFrame:
    return (
        pl.read_parquet(path)
        .select(
            pl.col("AREA_POPES_SUB_004").cast(pl.String).alias("geography_code"),
            pl.col("OBS_VALUE").cast(pl.Int64).alias("population_2025"),
        )
        .unique(subset="geography_code")
        .sort("geography_code")
    )


def _ethnicity_frame(population: pl.DataFrame, attributes: list[dict[str, Any]]) -> pl.DataFrame:
    source_rows: list[dict[str, object]] = []
    for row in attributes:
        raw_denominator = row.get(ETHNICITY_TOTAL_STATED)
        denominator = (
            int(raw_denominator)
            if raw_denominator is not None and int(raw_denominator) >= 0
            else None
        )
        for group, field in ETHNICITY_FIELDS.items():
            raw_count = row.get(field)
            count = int(raw_count) if raw_count is not None and int(raw_count) >= 0 else None
            source_rows.append(
                {
                    "geography_code": str(row["SA22023_V1_00"]),
                    "geography_name_2023": str(row["SA22023_V1_00_NAME"]),
                    "ethnicity_group": group,
                    "ethnicity_count_2023": count,
                    "ethnicity_total_stated_2023": denominator,
                }
            )
    groups = pl.DataFrame({"ethnicity_group": list(ETHNICITY_FIELDS)})
    expected = population.join(groups, how="cross")
    source = pl.DataFrame(source_rows)
    return (
        expected.join(source, on=("geography_code", "ethnicity_group"), how="left")
        .with_columns(
            pl.when(pl.col("ethnicity_total_stated_2023") > 0)
            .then(
                pl.col("ethnicity_count_2023").cast(pl.Float64)
                / pl.col("ethnicity_total_stated_2023")
            )
            .otherwise(None)
            .alias("total_response_share"),
            pl.when(pl.col("geography_name_2023").is_null())
            .then(pl.lit("unknown_sa2_version_mismatch"))
            .when(
                pl.col("ethnicity_count_2023").is_null()
                | pl.col("ethnicity_total_stated_2023").is_null()
            )
            .then(pl.lit("unknown_source_suppressed_or_unavailable"))
            .otherwise(pl.lit("matched_2023_sa2_code"))
            .alias("ethnicity_status"),
        )
        .sort(("geography_code", "ethnicity_group"))
    )


def _vehicle_frame(population: pl.DataFrame, attributes: list[dict[str, Any]]) -> pl.DataFrame:
    rows = []
    for row in attributes:
        values = {
            name: (int(row[field]) if row.get(field) is not None and int(row[field]) >= 0 else None)
            for name, field in VEHICLE_FIELDS.items()
        }
        rows.append(
            {
                "geography_code": str(row["SA22023_V1_00"]),
                "geography_name_2023": str(row["SA22023_V1_00_NAME"]),
                **values,
            }
        )
    source = pl.DataFrame(rows)
    return (
        population.join(source, on="geography_code", how="left")
        .with_columns(
            pl.when(pl.col("total_stated") > 0)
            .then(pl.col("no_motor_vehicle").cast(pl.Float64) / pl.col("total_stated"))
            .otherwise(None)
            .alias("no_motor_vehicle_share"),
            pl.when(pl.col("geography_name_2023").is_null())
            .then(pl.lit("unknown_sa2_version_mismatch"))
            .when(pl.col("no_motor_vehicle").is_null() | pl.col("total_stated").is_null())
            .then(pl.lit("unknown_source_suppressed_or_unavailable"))
            .otherwise(pl.lit("matched_2023_sa2_code"))
            .alias("vehicle_access_status"),
        )
        .sort("geography_code")
    )


def _demographic_frame(population: pl.DataFrame, attributes: list[dict[str, Any]]) -> pl.DataFrame:
    rows = []
    for row in attributes:
        raw_female = row.get(FEMALE_POPULATION_FIELD)
        female = int(raw_female) if raw_female is not None and int(raw_female) >= 0 else None
        rows.append(
            {
                "geography_code": str(row["SA22023_V1_00"]),
                "geography_name_2023": str(row["SA22023_V1_00_NAME"]),
                "female_population_2023": female,
            }
        )
    return (
        population.join(pl.DataFrame(rows), on="geography_code", how="left")
        .with_columns(
            pl.when(pl.col("geography_name_2023").is_null())
            .then(pl.lit("unknown_sa2_version_mismatch"))
            .when(pl.col("female_population_2023").is_null())
            .then(pl.lit("unknown_source_suppressed_or_unavailable"))
            .otherwise(pl.lit("matched_2023_sa2_code"))
            .alias("female_population_status")
        )
        .sort("geography_code")
    )


def materialize(
    population_path: Path,
    ethnicity_output: Path,
    vehicle_output: Path,
    demographic_output: Path,
    report_path: Path,
    *,
    getter: JsonGetter = _get_json,
    snapshot_dir: Path | None = None,
) -> dict[str, object]:
    population = _population_codes(population_path)
    common = ["SA22023_V1_00", "SA22023_V1_00_NAME"]
    ethnicity_attributes = fetch_attributes(
        INDIVIDUALS_LAYER,
        [
            *common,
            *ETHNICITY_FIELDS.values(),
            ETHNICITY_TOTAL_STATED,
            FEMALE_POPULATION_FIELD,
        ],
        getter=getter,
        snapshot_dir=snapshot_dir,
        snapshot_prefix="census-individuals",
    )
    vehicle_attributes = fetch_attributes(
        HOUSEHOLDS_LAYER,
        [*common, *VEHICLE_FIELDS.values()],
        getter=getter,
        snapshot_dir=snapshot_dir,
        snapshot_prefix="census-households",
    )
    ethnicity = _ethnicity_frame(population, ethnicity_attributes)
    vehicle = _vehicle_frame(population, vehicle_attributes)
    demographic = _demographic_frame(population, ethnicity_attributes)
    ethnicity_output.parent.mkdir(parents=True, exist_ok=True)
    ethnicity_fingerprint = write_parquet_deterministic(
        ethnicity, ethnicity_output, sort_by=("geography_code", "ethnicity_group")
    )
    vehicle_fingerprint = write_parquet_deterministic(
        vehicle, vehicle_output, sort_by=("geography_code",)
    )
    demographic_fingerprint = write_parquet_deterministic(
        demographic, demographic_output, sort_by=("geography_code",)
    )
    ethnicity_unknown = ethnicity.filter(
        pl.col("ethnicity_status") != "matched_2023_sa2_code"
    ).height
    vehicle_unknown = vehicle.filter(
        pl.col("vehicle_access_status") != "matched_2023_sa2_code"
    ).height
    demographic_unknown = demographic.filter(
        pl.col("female_population_status") != "matched_2023_sa2_code"
    ).height
    report: dict[str, object] = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": (
            "materialized_complete"
            if ethnicity_unknown == 0 and vehicle_unknown == 0
            else "materialized_with_explicit_unknowns"
        ),
        "population_reference_year": 2025,
        "source_geography_version": "SA2 2023",
        "source_ids": [
            "candidate.statsnz-ethnicity-2023-sa2",
            "candidate.statsnz-motor-vehicles-2023-sa2",
        ],
        "source_feature_counts": {
            "ethnicity": len(ethnicity_attributes),
            "vehicle_access": len(vehicle_attributes),
        },
        "ethnicity_rows": ethnicity.height,
        "ethnicity_matched_rows": ethnicity.height - ethnicity_unknown,
        "ethnicity_explicit_unknown_rows": ethnicity_unknown,
        "ethnicity_fingerprint": ethnicity_fingerprint,
        "vehicle_access_rows": vehicle.height,
        "vehicle_access_matched_rows": vehicle.height - vehicle_unknown,
        "vehicle_access_explicit_unknown_rows": vehicle_unknown,
        "vehicle_access_fingerprint": vehicle_fingerprint,
        "demographic_allocation_rows": demographic.height,
        "demographic_allocation_matched_rows": demographic.height - demographic_unknown,
        "demographic_allocation_explicit_unknown_rows": demographic_unknown,
        "demographic_allocation_fingerprint": demographic_fingerprint,
        "claim_boundary": (
            "All values are public aggregate Census area statistics. Ethnicity uses overlapping "
            "total-response groups and is never an individual attribute. Vehicle access is a "
            "household-area proxy, not observed transport availability for any person."
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
    parser.add_argument("--ethnicity-output", type=Path, default=DEFAULT_ETHNICITY_OUTPUT)
    parser.add_argument("--vehicle-output", type=Path, default=DEFAULT_VEHICLE_OUTPUT)
    parser.add_argument("--demographic-output", type=Path, default=DEFAULT_DEMOGRAPHIC_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--snapshot-dir", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                args.population,
                args.ethnicity_output,
                args.vehicle_output,
                args.demographic_output,
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
