from __future__ import annotations

import pyarrow as pa

from closer_to_whom.contracts import (
    DEMAND_SCHEMA,
    FACILITY_SCHEMA,
    registry_manifest,
    schema_fingerprint,
    table_fingerprint,
    validate_table,
)


def test_schema_fingerprint_is_stable_and_distinct() -> None:
    assert schema_fingerprint(FACILITY_SCHEMA) == schema_fingerprint(FACILITY_SCHEMA)
    assert schema_fingerprint(FACILITY_SCHEMA) != schema_fingerprint(DEMAND_SCHEMA)


def test_table_fingerprint_is_sort_stable() -> None:
    left = pa.table({"id": [2, 1], "value": ["b", "a"]})
    right = pa.table({"id": [1, 2], "value": ["a", "b"]})
    assert table_fingerprint(left, sort_by=("id",)) == table_fingerprint(right, sort_by=("id",))


def test_validate_table_reports_missing_and_extra_columns() -> None:
    table = pa.table({"unexpected": [1]})
    issues = validate_table(table, DEMAND_SCHEMA)
    codes = {issue.code for issue in issues}
    assert {"missing_column", "extra_column"}.issubset(codes)


def test_validate_table_reports_null_and_type() -> None:
    schema = pa.schema([pa.field("id", pa.int8(), nullable=False)])
    null_table = pa.table({"id": pa.array([None], type=pa.int8())})
    assert {issue.code for issue in validate_table(null_table, schema)} == {"null_not_allowed"}
    string_table = pa.table({"id": ["not-an-int"]})
    assert {issue.code for issue in validate_table(string_table, schema)} == {"type_mismatch"}


def test_registry_manifest_contains_all_contracts() -> None:
    manifest = registry_manifest()
    assert set(manifest) == {"facility", "demand", "result"}
    assert all(len(value["sha256"]) == 64 for value in manifest.values())
