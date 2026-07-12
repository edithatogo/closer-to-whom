"""Materialise an evidence-graded facility census without weakening claim boundaries."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl
import yaml

from closer_to_whom.io import write_parquet_deterministic
from closer_to_whom.models import Facility
from closer_to_whom.registry import facilities_to_frame
from closer_to_whom.types import CapabilityStatus

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/public/service-census-records.yaml"
DEFAULT_OUTPUT = ROOT / "data/derived/facility-registry.parquet"
DEFAULT_FLOW = ROOT / "reports/service-census-flow.json"
DEFAULT_DISAGREEMENTS = ROOT / "reports/service-census-disagreements.csv"

_EMPTY_SCHEMA = {
    "facility_id": pl.String,
    "name": pl.String,
    "region": pl.String,
    "district": pl.String,
    "latitude": pl.Float64,
    "longitude": pl.Float64,
    "facility_type": pl.String,
    "public_or_private": pl.String,
    "capability_status": pl.String,
    "evidence_grade": pl.Int8,
    "source_ids": pl.List(pl.String),
    "formulations": pl.List(pl.String),
    "delivery_modes": pl.List(pl.String),
    "opening_hours_per_week": pl.Float64,
    "redistribution_allowed": pl.Boolean,
}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a mapping in {path}")
    return payload


def _load_source_ids(path: Path) -> tuple[set[str], set[str]]:
    payload = _load_yaml(path)
    records = payload.get("sources", [])
    if not isinstance(records, list):
        raise TypeError("Source registry sources must be a list")
    known: set[str] = set()
    open_redistributable: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or not record.get("source_id"):
            raise ValueError("Every source registry record needs source_id")
        source_id = str(record["source_id"])
        known.add(source_id)
        if record.get("licence_state") == "open" and record.get("redistribution_allowed") is True:
            open_redistributable.add(source_id)
    return known, open_redistributable


def _validated_facilities(records: list[Any], source_registry: Path) -> tuple[Facility, ...]:
    known, open_redistributable = _load_source_ids(source_registry)
    facilities: list[Facility] = []
    seen: set[str] = set()
    for raw in records:
        if not isinstance(raw, dict):
            raise TypeError("Each census record must be a mapping")
        facility = Facility.model_validate(raw)
        if facility.facility_id in seen:
            raise ValueError(f"Duplicate facility_id: {facility.facility_id}")
        seen.add(facility.facility_id)
        missing = set(facility.source_ids) - known
        if missing:
            raise ValueError(f"Unknown source IDs for {facility.facility_id}: {sorted(missing)}")
        if facility.redistribution_allowed and not set(facility.source_ids) <= open_redistributable:
            raise ValueError(
                f"Redistributable facility {facility.facility_id} has non-open source evidence"
            )
        if facility.capability_status is CapabilityStatus.UNKNOWN and facility.formulations:
            raise ValueError(
                f"Unknown capability cannot claim formulations: {facility.facility_id}"
            )
        facilities.append(facility)
    return tuple(sorted(facilities, key=lambda item: item.facility_id))


def _empty_frame() -> pl.DataFrame:
    return pl.DataFrame(schema=_EMPTY_SCHEMA)


def _network_counts(facilities: tuple[Facility, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label, threshold, statuses in (
        ("conservative", 2, {CapabilityStatus.CONFIRMED}),
        ("plausible", 3, {CapabilityStatus.CONFIRMED, CapabilityStatus.PLAUSIBLE}),
        ("broad", 4, {CapabilityStatus.CONFIRMED, CapabilityStatus.PLAUSIBLE}),
    ):
        counts[label] = sum(
            facility.evidence_grade.rank <= threshold and facility.capability_status in statuses
            for facility in facilities
        )
    return counts


def materialize(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    flow_path: Path = DEFAULT_FLOW,
    disagreements_path: Path = DEFAULT_DISAGREEMENTS,
    source_registry: Path = ROOT / "data/public/source-registry.yaml",
) -> dict[str, Any]:
    """Validate census records and write deterministic registry and audit outputs."""
    payload = _load_yaml(input_path)
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise TypeError("Census records must be a list")
    facilities = _validated_facilities(records, source_registry)
    frame = facilities_to_frame(facilities) if facilities else _empty_frame()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(frame, output_path, sort_by=("facility_id",))

    disagreements = payload.get("disagreements", [])
    if not isinstance(disagreements, list):
        raise TypeError("Disagreements must be a list")
    if any(not isinstance(item, dict) for item in disagreements):
        raise TypeError("Each disagreement record must be a mapping")
    disagreements_path.parent.mkdir(parents=True, exist_ok=True)
    with disagreements_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ("facility_id", "issue", "reviewer_a", "reviewer_b", "adjudication")
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(
            {field: item.get(field, "") for field in fieldnames} for item in disagreements
        )

    status_counts = Counter(facility.capability_status.value for facility in facilities)
    grade_counts = Counter(str(facility.evidence_grade.rank) for facility in facilities)
    freeze_date = payload.get("freeze_date") or datetime.now(UTC).date().isoformat()
    flow = {
        "schema_version": "1.0.0",
        "freeze_date": str(freeze_date),
        "input": input_path.relative_to(ROOT).as_posix()
        if input_path.is_relative_to(ROOT)
        else input_path.as_posix(),
        "facility_count": len(facilities),
        "status_counts": dict(sorted(status_counts.items())),
        "evidence_grade_counts": dict(sorted(grade_counts.items())),
        "network_counts": _network_counts(facilities),
        "disagreement_count": len(disagreements),
        "parquet_fingerprint": fingerprint,
        "claim_boundary": (
            "Only explicitly adjudicated public-source records may enter this registry; "
            "synthetic fixtures and undocumented capability remain non-observed or unknown."
        ),
    }
    flow_path.parent.mkdir(parents=True, exist_ok=True)
    flow_path.write_text(
        json.dumps(flow, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return flow


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--flow-output", type=Path, default=DEFAULT_FLOW)
    parser.add_argument("--disagreements-output", type=Path, default=DEFAULT_DISAGREEMENTS)
    parser.add_argument(
        "--source-registry", type=Path, default=ROOT / "data/public/source-registry.yaml"
    )
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(
                input_path=args.input,
                output_path=args.output,
                flow_path=args.flow_output,
                disagreements_path=args.disagreements_output,
                source_registry=args.source_registry,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
