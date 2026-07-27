from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import polars as pl

_SPEC = spec_from_file_location(
    "materialize_sa2_census_stratifiers",
    Path(__file__).parents[2] / "scripts" / "materialize_sa2_census_stratifiers.py",
)
assert _SPEC and _SPEC.loader
_MODULE = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
fetch_attributes = _MODULE.fetch_attributes
materialize = _MODULE.materialize
ethnicity_frame = _MODULE._ethnicity_frame
vehicle_frame = _MODULE._vehicle_frame
demographic_frame = _MODULE._demographic_frame


def test_fetch_attributes_paginates_and_orders() -> None:
    rows = [
        {"SA22023_V1_00": "100100"},
        {"SA22023_V1_00": "100200"},
        {"SA22023_V1_00": "100300"},
    ]

    def getter(url: str) -> dict[str, object]:
        query = parse_qs(urlparse(url).query)
        offset = int(query["resultOffset"][0])
        page_size = int(query["resultRecordCount"][0])
        page = rows[offset : offset + page_size]
        return {
            "features": [{"attributes": row} for row in page],
            "exceededTransferLimit": offset + page_size < len(rows),
        }

    assert (
        fetch_attributes(
            "https://example.test/layer", ["SA22023_V1_00"], getter=getter, page_size=2
        )
        == rows
    )


def test_materialize_keeps_unmatched_codes_unknown(tmp_path: Path) -> None:
    population_path = tmp_path / "population.parquet"
    pl.DataFrame({"AREA_POPES_SUB_004": [100100, 999999], "OBS_VALUE": [100, 10]}).write_parquet(
        population_path
    )

    def getter(url: str) -> dict[str, object]:
        is_ethnicity = "individuals" in url
        attributes: dict[str, object] = {
            "SA22023_V1_00": "100100",
            "SA22023_V1_00_NAME": "Example",
        }
        if is_ethnicity:
            attributes.update(dict.fromkeys(_MODULE.ETHNICITY_FIELDS.values(), 10))
            attributes[_MODULE.ETHNICITY_TOTAL_STATED] = 20
            attributes[_MODULE.FEMALE_POPULATION_FIELD] = 9
        else:
            attributes.update(
                {
                    _MODULE.VEHICLE_FIELDS["no_motor_vehicle"]: 2,
                    _MODULE.VEHICLE_FIELDS["not_elsewhere_included"]: 1,
                    _MODULE.VEHICLE_FIELDS["total"]: 10,
                    _MODULE.VEHICLE_FIELDS["total_stated"]: 9,
                }
            )
        return {"features": [{"attributes": attributes}], "exceededTransferLimit": False}

    report = materialize(
        population_path,
        tmp_path / "ethnicity.parquet",
        tmp_path / "vehicle.parquet",
        tmp_path / "demographic.parquet",
        tmp_path / "report.json",
        getter=getter,
    )
    assert report["ethnicity_rows"] == 12
    assert report["ethnicity_explicit_unknown_rows"] == 6
    assert report["vehicle_access_rows"] == 2
    assert report["vehicle_access_explicit_unknown_rows"] == 1
    assert report["demographic_allocation_rows"] == 2
    assert report["demographic_allocation_explicit_unknown_rows"] == 1
    vehicle = pl.read_parquet(tmp_path / "vehicle.parquet")
    assert (
        vehicle.filter(pl.col("geography_code") == "100100")["no_motor_vehicle_share"].item()
        == 2 / 9
    )


def test_suppression_sentinel_becomes_unknown_not_negative() -> None:
    population = pl.DataFrame({"geography_code": ["100100"], "population_2025": [10]})
    common: dict[str, object] = {
        "SA22023_V1_00": "100100",
        "SA22023_V1_00_NAME": "Example",
    }
    ethnicity_attributes = {
        **common,
        **dict.fromkeys(_MODULE.ETHNICITY_FIELDS.values(), -999),
        _MODULE.ETHNICITY_TOTAL_STATED: 9,
    }
    ethnicity = ethnicity_frame(population, [ethnicity_attributes])
    assert ethnicity["ethnicity_count_2023"].null_count() == 6
    assert ethnicity["total_response_share"].null_count() == 6
    assert (
        ethnicity["ethnicity_status"].unique().item() == "unknown_source_suppressed_or_unavailable"
    )
    vehicle_attributes = {
        **common,
        **dict.fromkeys(_MODULE.VEHICLE_FIELDS.values(), -999),
    }
    vehicle = vehicle_frame(population, [vehicle_attributes])
    assert vehicle["no_motor_vehicle"].item() is None
    assert vehicle["no_motor_vehicle_share"].item() is None
    assert vehicle["vehicle_access_status"].item() == "unknown_source_suppressed_or_unavailable"
    demographic = demographic_frame(
        population,
        [{**common, _MODULE.FEMALE_POPULATION_FIELD: -999}],
    )
    assert demographic["female_population_2023"].item() is None
    assert (
        demographic["female_population_status"].item() == "unknown_source_suppressed_or_unavailable"
    )
