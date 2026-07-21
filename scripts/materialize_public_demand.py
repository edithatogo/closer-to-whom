"""Materialise public aggregate demand cells with reproducible routing weights."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl
import yaml

from closer_to_whom.io import write_parquet_deterministic
from closer_to_whom.models import DemandCell

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/public/demand-geography-records.yaml"
DEFAULT_OUTPUT = ROOT / "data/derived/demand-cells.parquet"
DEFAULT_REPORT = ROOT / "reports/demand-geography-flow.json"


def _load(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def materialize(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    report_path: Path = DEFAULT_REPORT,
) -> dict[str, Any]:
    """Validate aggregate demand records and write a deterministic Parquet dataset."""
    payload = _load(input_path)
    raw_records = payload.get("records", [])
    if not isinstance(raw_records, list):
        raise TypeError("Demand records must be a list")
    if raw_records and str(payload.get("status", "")).lower() not in {"frozen", "active"}:
        raise ValueError(
            "non-empty demand records require an explicitly frozen or active public-input manifest"
        )
    if raw_records and not payload.get("freeze_date"):
        raise ValueError("non-empty demand records require freeze_date")
    cells: list[DemandCell] = []
    weights: dict[str, float] = defaultdict(float)
    seen_points: set[str] = set()
    for raw in raw_records:
        if not isinstance(raw, dict):
            raise TypeError("Each demand record must be a mapping")
        weight = float(raw.pop("routing_weight", 1.0))
        if not 0.0 <= weight <= 1.0:
            raise ValueError("routing_weight must be between zero and one")
        cell = DemandCell.model_validate(raw)
        if cell.routing_point_id in seen_points:
            raise ValueError(f"Duplicate routing_point_id: {cell.routing_point_id}")
        seen_points.add(cell.routing_point_id)
        weights[cell.demand_cell_id] += weight
        cells.append(cell)
    errors = {key: round(value, 12) for key, value in weights.items() if abs(value - 1.0) > 1e-9}
    if errors:
        raise ValueError(f"Routing weights must sum to one per demand cell: {errors}")
    if cells:
        frame = pl.DataFrame([cell.model_dump(mode="json") for cell in cells])
    else:
        frame = pl.DataFrame(
            schema={
                "demand_cell_id": pl.String,
                "geography_code": pl.String,
                "geography_level": pl.String,
                "routing_point_id": pl.String,
                "latitude": pl.Float64,
                "longitude": pl.Float64,
                "region": pl.String,
                "district": pl.String,
                "ethnicity": pl.String,
                "deprivation_quintile": pl.Int64,
                "rurality": pl.String,
                "expected_courses": pl.Float64,
                "data_classification": pl.String,
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(
        frame, output_path, sort_by=("demand_cell_id", "routing_point_id")
    )
    report = {
        "schema_version": "1.0.0",
        "freeze_date": payload.get("freeze_date") or datetime.now(UTC).date().isoformat(),
        "record_count": len(cells),
        "demand_cell_count": len(weights),
        "expected_courses_total": sum(cell.expected_courses for cell in cells),
        "routing_weight_sums": dict(
            sorted((key, round(value, 12)) for key, value in weights.items())
        ),
        "parquet_fingerprint": fingerprint,
        "claim_boundary": "Records are public aggregate or synthetic demand cells, never patients or patient-like rows.",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(json.dumps(materialize(args.input, args.output, args.report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
