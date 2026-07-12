from pathlib import Path
from runpy import run_path

import pytest

materialize = run_path(
    Path(__file__).parents[2] / "scripts" / "materialize_public_demand.py",
    run_name="public_demand_test",
)["materialize"]


def test_empty_public_demand_template_is_safe(tmp_path: Path) -> None:
    input_path = tmp_path / "demand.yaml"
    input_path.write_text("schema_version: '1.0.0'\nrecords: []\n", encoding="utf-8")
    report = materialize(input_path, tmp_path / "demand.parquet", tmp_path / "flow.json")
    assert report["record_count"] == 0
    assert report["demand_cell_count"] == 0


def test_routing_weights_must_close_to_one(tmp_path: Path) -> None:
    input_path = tmp_path / "demand.yaml"
    input_path.write_text(
        """
schema_version: '1.0.0'
records:
  - demand_cell_id: CELL-1
    geography_code: SA2-1
    geography_level: SYNTHETIC
    routing_point_id: POINT-1
    latitude: -36.85
    longitude: 174.76
    region: Test
    district: Test
    ethnicity: aggregate_unknown
    deprivation_quintile: 3
    rurality: urban
    expected_courses: 1.0
    data_classification: synthetic
    routing_weight: 0.5
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="sum to one"):
        materialize(input_path, tmp_path / "demand.parquet", tmp_path / "flow.json")
