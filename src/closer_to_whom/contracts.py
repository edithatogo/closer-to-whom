"""Arrow schemas, fingerprints, and table validation."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

import pyarrow as pa

SCHEMA_VERSION: Final[str] = "1.0.0"

FACILITY_SCHEMA = pa.schema(
    [
        pa.field("facility_id", pa.string(), nullable=False),
        pa.field("name", pa.string(), nullable=False),
        pa.field("region", pa.string(), nullable=False),
        pa.field("district", pa.string(), nullable=False),
        pa.field("latitude", pa.float64(), nullable=False),
        pa.field("longitude", pa.float64(), nullable=False),
        pa.field("facility_type", pa.string(), nullable=False),
        pa.field("public_or_private", pa.string(), nullable=False),
        pa.field("capability_status", pa.string(), nullable=False),
        pa.field("evidence_grade", pa.int8(), nullable=False),
        pa.field("source_ids", pa.list_(pa.string()), nullable=False),
        pa.field("formulations", pa.list_(pa.string()), nullable=False),
        pa.field("delivery_modes", pa.list_(pa.string()), nullable=False),
        pa.field("opening_hours_per_week", pa.float64(), nullable=True),
        pa.field("redistribution_allowed", pa.bool_(), nullable=False),
    ],
    metadata={b"ctw:schema": b"facility", b"ctw:version": SCHEMA_VERSION.encode()},
)

DEMAND_SCHEMA = pa.schema(
    [
        pa.field("demand_cell_id", pa.string(), nullable=False),
        pa.field("geography_code", pa.string(), nullable=False),
        pa.field("geography_level", pa.string(), nullable=False),
        pa.field("routing_point_id", pa.string(), nullable=False),
        pa.field("latitude", pa.float64(), nullable=False),
        pa.field("longitude", pa.float64(), nullable=False),
        pa.field("region", pa.string(), nullable=False),
        pa.field("district", pa.string(), nullable=False),
        pa.field("ethnicity", pa.string(), nullable=False),
        pa.field("deprivation_quintile", pa.int8(), nullable=False),
        pa.field("rurality", pa.string(), nullable=False),
        pa.field("expected_courses", pa.float64(), nullable=False),
        pa.field("data_classification", pa.string(), nullable=False),
    ],
    metadata={b"ctw:schema": b"demand", b"ctw:version": SCHEMA_VERSION.encode()},
)

RESULT_SCHEMA = pa.schema(
    [
        pa.field("scenario_id", pa.string(), nullable=False),
        pa.field("pathway_id", pa.string(), nullable=False),
        pa.field("demand_cell_id", pa.string(), nullable=False),
        pa.field("facility_id", pa.string(), nullable=False),
        pa.field("ethnicity", pa.string(), nullable=False),
        pa.field("deprivation_quintile", pa.int8(), nullable=False),
        pa.field("rurality", pa.string(), nullable=False),
        pa.field("expected_courses", pa.float64(), nullable=False),
        pa.field("one_way_km", pa.float64(), nullable=False),
        pa.field("one_way_minutes", pa.float64(), nullable=False),
        pa.field("course_travel_km", pa.float64(), nullable=False),
        pa.field("course_travel_minutes", pa.float64(), nullable=False),
        pa.field("course_on_site_minutes", pa.float64(), nullable=False),
        pa.field("patient_direct_cost_nzd", pa.float64(), nullable=False),
        pa.field("patient_whanau_cost_nzd", pa.float64(), nullable=False),
        pa.field("payer_cost_nzd", pa.float64(), nullable=False),
        pa.field("provider_cost_nzd", pa.float64(), nullable=False),
        pa.field("societal_cost_nzd", pa.float64(), nullable=False),
        pa.field("model_version", pa.string(), nullable=False),
        pa.field("assumptions_fingerprint", pa.string(), nullable=False),
    ],
    metadata={b"ctw:schema": b"result", b"ctw:version": SCHEMA_VERSION.encode()},
)


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One machine-readable schema validation issue."""

    code: str
    message: str
    field: str | None = None


def schema_fingerprint(schema: pa.Schema) -> str:
    """Return a stable SHA-256 fingerprint for an Arrow schema."""
    payload = schema.serialize().to_pybytes()
    return hashlib.sha256(payload).hexdigest()


def table_fingerprint(table: pa.Table, *, sort_by: tuple[str, ...] = ()) -> str:
    """Return a stable content digest after optional deterministic sorting."""
    if sort_by:
        table = table.sort_by([(name, "ascending") for name in sort_by])
    sink = pa.BufferOutputStream()
    options = pa.ipc.IpcWriteOptions(compression=None)
    with pa.ipc.new_stream(sink, table.schema, options=options) as writer:
        writer.write_table(table.combine_chunks())
    return hashlib.sha256(sink.getvalue().to_pybytes()).hexdigest()


def validate_table(table: pa.Table, expected: pa.Schema) -> tuple[ValidationIssue, ...]:
    """Validate required columns, nullability, and castability against a contract."""
    issues: list[ValidationIssue] = []
    expected_names = set(expected.names)
    actual_names = set(table.column_names)
    for missing in sorted(expected_names - actual_names):
        issues.append(
            ValidationIssue("missing_column", f"Missing required column: {missing}", missing)
        )
    for extra in sorted(actual_names - expected_names):
        issues.append(ValidationIssue("extra_column", f"Unexpected column: {extra}", extra))
    if issues:
        return tuple(issues)
    for field in expected:
        column = table[field.name]
        if not field.nullable and column.null_count:
            issues.append(
                ValidationIssue(
                    "null_not_allowed",
                    f"Column {field.name} contains {column.null_count} null values",
                    field.name,
                )
            )
        try:
            column.cast(field.type, safe=True)
        except (pa.ArrowInvalid, pa.ArrowNotImplementedError) as exc:
            issues.append(
                ValidationIssue(
                    "type_mismatch",
                    f"Column {field.name} cannot be safely cast to {field.type}: {exc}",
                    field.name,
                )
            )
    return tuple(issues)


def registry_manifest() -> Mapping[str, Mapping[str, str]]:
    """Return the public schema registry manifest."""
    schemas = {
        "facility": FACILITY_SCHEMA,
        "demand": DEMAND_SCHEMA,
        "result": RESULT_SCHEMA,
    }
    return {
        name: {"version": SCHEMA_VERSION, "sha256": schema_fingerprint(schema)}
        for name, schema in schemas.items()
    }


def registry_manifest_json() -> str:
    """Serialise the schema registry deterministically."""
    return json.dumps(registry_manifest(), indent=2, sort_keys=True) + "\n"
