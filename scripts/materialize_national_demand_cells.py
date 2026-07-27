"""Assemble one source-backed aggregate baseline demand cell per denominator SA2."""

from __future__ import annotations

import argparse
import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl

from closer_to_whom.io import write_parquet_deterministic
from closer_to_whom.models import DemandCell

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEMOGRAPHIC = ROOT / "data/derived/sa2-demographic-allocation.parquet"
DEFAULT_ROUTING_POINTS = ROOT / "data/derived/sa2-routing-points.parquet"
DEFAULT_RURALITY = ROOT / "data/derived/sa2-rurality.parquet"
DEFAULT_DEPRIVATION = ROOT / "data/derived/sa2-deprivation.parquet"
DEFAULT_CALIBRATION = ROOT / "reports/national-demand-calibration.json"
DEFAULT_OUTPUT = ROOT / "data/derived/national-demand-cells.parquet"
DEFAULT_REPORT = ROOT / "reports/national-demand-cells.json"


def build_demand_cells(
    demographic: pl.DataFrame,
    routing_points: pl.DataFrame,
    rurality: pl.DataFrame,
    deprivation: pl.DataFrame,
    *,
    annual_expected_courses: float,
) -> tuple[pl.DataFrame, dict[str, Any]]:
    if annual_expected_courses <= 0:
        raise ValueError("annual_expected_courses must be positive")
    frame = (
        demographic.join(
            routing_points.select(
                "geography_code",
                "routing_point_id",
                "latitude",
                "longitude",
                "routing_point_method",
            ),
            on="geography_code",
            how="left",
        )
        .join(
            rurality.select(
                "geography_code",
                "urban_rural_name",
                "rurality_status",
            ),
            on="geography_code",
            how="left",
        )
        .join(
            deprivation.select(
                "geography_code",
                "deprivation_decile",
                "deprivation_status",
            ),
            on="geography_code",
            how="left",
        )
    )
    required = ("routing_point_id", "latitude", "longitude")
    if any(frame[column].null_count() for column in required):
        raise ValueError("Every demand cell requires an official baseline routing point")
    known = frame.filter(pl.col("female_population_2023").is_not_null())
    known_population = known["population_2025"].sum()
    female_total = known["female_population_2023"].sum()
    if not known_population or not female_total:
        raise ValueError("Known female population is required for allocation")
    national_female_share = float(female_total) / float(known_population)
    frame = frame.with_columns(
        pl.when(pl.col("female_population_2023").is_not_null())
        .then(pl.col("female_population_2023").cast(pl.Float64))
        .otherwise(pl.col("population_2025").cast(pl.Float64) * national_female_share)
        .alias("allocation_weight"),
        pl.when(pl.col("female_population_2023").is_not_null())
        .then(pl.lit("census_female_population_2023"))
        .otherwise(pl.lit("population_2025_scaled_by_national_female_share"))
        .alias("allocation_method"),
        ((pl.col("deprivation_decile") + 1) // 2)
        .cast(pl.Int8)
        .alias("deprivation_quintile"),
        pl.col("urban_rural_name").fill_null("unknown").alias("rurality"),
    )
    weight_total = frame["allocation_weight"].sum()
    if not weight_total or weight_total <= 0:
        raise ValueError("Demand allocation weights must have a positive sum")
    frame = frame.with_columns(
        (pl.col("allocation_weight") / weight_total * annual_expected_courses).alias(
            "expected_courses"
        )
    )
    rows = []
    for row in frame.iter_rows(named=True):
        cell = DemandCell(
            demand_cell_id=f"SA2-{row['geography_code']}-aggregate",
            geography_code=str(row["geography_code"]),
            geography_level="SA2",
            routing_point_id=str(row["routing_point_id"]),
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            region="unknown_not_materialized",
            district="unknown_not_materialized",
            ethnicity="aggregate_all_total_response_profiles_separate",
            deprivation_quintile=row["deprivation_quintile"],
            rurality=str(row["rurality"]),
            expected_courses=float(row["expected_courses"]),
            data_classification="generated_aggregate",
        )
        rows.append(
            {
                **cell.model_dump(mode="json"),
                "population_2025": int(row["population_2025"]),
                "female_population_2023": row["female_population_2023"],
                "allocation_weight": float(row["allocation_weight"]),
                "allocation_method": str(row["allocation_method"]),
                "deprivation_status": str(row["deprivation_status"]),
                "rurality_status": str(row["rurality_status"]),
            }
        )
    result = pl.DataFrame(rows).with_columns(
        pl.col("deprivation_quintile").cast(pl.Int8),
        pl.col("female_population_2023").cast(pl.Int64),
    )
    total = result["expected_courses"].sum()
    if not math.isclose(total, annual_expected_courses, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("Spatial demand allocation does not reconcile to national calibration")
    audit = {
        "national_female_share_fallback": national_female_share,
        "female_population_matched_rows": result.filter(
            pl.col("allocation_method") == "census_female_population_2023"
        ).height,
        "female_population_fallback_rows": result.filter(
            pl.col("allocation_method")
            == "population_2025_scaled_by_national_female_share"
        ).height,
        "deprivation_known_rows": result["deprivation_quintile"].len()
        - result["deprivation_quintile"].null_count(),
        "deprivation_explicit_unknown_rows": result["deprivation_quintile"].null_count(),
        "rurality_explicit_unknown_rows": result.filter(
            pl.col("rurality") == "unknown"
        ).height,
        "zero_expected_course_rows": result.filter(
            pl.col("expected_courses") == 0
        ).height,
    }
    return result.sort("demand_cell_id"), audit


def materialize(
    demographic_path: Path = DEFAULT_DEMOGRAPHIC,
    routing_points_path: Path = DEFAULT_ROUTING_POINTS,
    rurality_path: Path = DEFAULT_RURALITY,
    deprivation_path: Path = DEFAULT_DEPRIVATION,
    calibration_path: Path = DEFAULT_CALIBRATION,
    output_path: Path = DEFAULT_OUTPUT,
    report_path: Path = DEFAULT_REPORT,
) -> dict[str, Any]:
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    annual_expected_courses = float(calibration["annual_expected_courses"])
    frame, audit = build_demand_cells(
        pl.read_parquet(demographic_path),
        pl.read_parquet(routing_points_path),
        pl.read_parquet(rurality_path),
        pl.read_parquet(deprivation_path),
        annual_expected_courses=annual_expected_courses,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(
        frame, output_path, sort_by=("demand_cell_id",)
    )
    report: dict[str, Any] = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "materialized_aggregate_baseline",
        "demand_cell_count": frame.height,
        "annual_expected_courses": annual_expected_courses,
        "materialized_expected_courses": frame["expected_courses"].sum(),
        "parquet_fingerprint": fingerprint,
        "allocation_basis": (
            "2023 Census female population by SA2; source-unavailable cells use 2025 population "
            "scaled by the national observed female share and remain explicitly identified"
        ),
        "source_ids": [
            "candidate.statsnz-population-estimates-2023-base",
            "candidate.statsnz-sa1-census-population-2023",
            "candidate.statsnz-sa2-2023-centroid-true",
            "candidate.statsnz-urban-rural-2023-generalised",
            "candidate.nzdep2023",
            "candidate.teaho-breast-qpi-2025",
            "candidate.teaho-cancer-medicines-gap-2022",
            "candidate.healthnz-health-independence-2024",
        ],
        "audit": audit,
        "claim_boundary": (
            "Rows are modelled public aggregate SA2 expectations, not patients, observed demand, "
            "small-area incidence, eligibility decisions, or actual treatment use. Ethnicity and "
            "vehicle-access profiles remain separate ecological stratifier artifacts."
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
    parser.add_argument("--demographic", type=Path, default=DEFAULT_DEMOGRAPHIC)
    parser.add_argument("--routing-points", type=Path, default=DEFAULT_ROUTING_POINTS)
    parser.add_argument("--rurality", type=Path, default=DEFAULT_RURALITY)
    parser.add_argument("--deprivation", type=Path, default=DEFAULT_DEPRIVATION)
    parser.add_argument("--calibration", type=Path, default=DEFAULT_CALIBRATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                args.demographic,
                args.routing_points,
                args.rurality,
                args.deprivation,
                args.calibration,
                args.output,
                args.report,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
