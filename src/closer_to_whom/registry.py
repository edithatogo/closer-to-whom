"""Evidence-graded facility registry loading and filtering."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Literal, cast

import polars as pl

from closer_to_whom.models import Facility
from closer_to_whom.types import CapabilityStatus, DeliveryMode, EvidenceGrade, Formulation

_REQUIRED_COLUMNS = {
    "facility_id",
    "name",
    "region",
    "district",
    "latitude",
    "longitude",
    "facility_type",
    "public_or_private",
    "capability_status",
    "evidence_grade",
    "source_ids",
    "formulations",
    "delivery_modes",
    "redistribution_allowed",
}


def _split_list(value: str | list[str] | None) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return tuple(item.strip() for item in str(value).split("|") if item.strip())


def load_facilities(path: Path) -> tuple[Facility, ...]:
    """Load and validate a CSV or Parquet facility registry."""
    frame = pl.read_parquet(path) if path.suffix == ".parquet" else pl.read_csv(path)
    missing = _REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Facility registry is missing columns: {sorted(missing)}")
    facilities: list[Facility] = []
    for row in frame.iter_rows(named=True):
        facilities.append(
            Facility(
                facility_id=str(row["facility_id"]),
                name=str(row["name"]),
                region=str(row["region"]),
                district=str(row["district"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                facility_type=str(row["facility_type"]),
                public_or_private=cast(
                    Literal["public", "private", "candidate"], str(row["public_or_private"])
                ),
                capability_status=CapabilityStatus(str(row["capability_status"])),
                evidence_grade=EvidenceGrade(str(row["evidence_grade"])),
                source_ids=_split_list(row["source_ids"]),
                formulations=frozenset(
                    Formulation(item) for item in _split_list(row["formulations"])
                ),
                delivery_modes=frozenset(
                    DeliveryMode(item) for item in _split_list(row["delivery_modes"])
                ),
                opening_hours_per_week=(
                    None
                    if row.get("opening_hours_per_week") is None
                    else float(row["opening_hours_per_week"])
                ),
                redistribution_allowed=bool(row["redistribution_allowed"]),
            )
        )
    ids = [facility.facility_id for facility in facilities]
    if len(ids) != len(set(ids)):
        raise ValueError("Facility IDs must be unique")
    return tuple(facilities)


def eligible_facilities(
    facilities: Iterable[Facility],
    *,
    formulation: Formulation,
    delivery_modes: frozenset[DeliveryMode],
    evidence_grade_threshold: int,
    include_plausible: bool = False,
) -> tuple[Facility, ...]:
    """Filter facilities conservatively using public evidence and clinical mode."""
    allowed_status = {CapabilityStatus.CONFIRMED}
    if include_plausible:
        allowed_status.add(CapabilityStatus.PLAUSIBLE)
    selected = [
        facility
        for facility in facilities
        if facility.redistribution_allowed
        and facility.capability_status in allowed_status
        and facility.evidence_grade.rank <= evidence_grade_threshold
        and formulation in facility.formulations
        and bool(delivery_modes.intersection(facility.delivery_modes))
    ]
    return tuple(sorted(selected, key=lambda facility: facility.facility_id))


def facilities_to_frame(facilities: Iterable[Facility]) -> pl.DataFrame:
    """Convert validated facilities to a canonical Polars frame."""
    rows = [
        {
            "facility_id": facility.facility_id,
            "name": facility.name,
            "region": facility.region,
            "district": facility.district,
            "latitude": facility.latitude,
            "longitude": facility.longitude,
            "facility_type": facility.facility_type,
            "public_or_private": facility.public_or_private,
            "capability_status": facility.capability_status.value,
            "evidence_grade": facility.evidence_grade.rank,
            "source_ids": list(facility.source_ids),
            "formulations": sorted(item.value for item in facility.formulations),
            "delivery_modes": sorted(item.value for item in facility.delivery_modes),
            "opening_hours_per_week": facility.opening_hours_per_week,
            "redistribution_allowed": facility.redistribution_allowed,
        }
        for facility in facilities
    ]
    return pl.DataFrame(rows)
