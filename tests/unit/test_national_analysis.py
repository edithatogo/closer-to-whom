import importlib.util
from pathlib import Path

import polars as pl

_SPEC = importlib.util.spec_from_file_location(
    "materialize_national_analysis",
    Path(__file__).parents[2] / "scripts" / "materialize_national_analysis.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build_outputs = _MODULE.build_outputs


def test_national_analysis_keeps_claims_bounded(tmp_path: Path) -> None:
    demand = pl.DataFrame(
        {
            "demand_cell_id": ["a", "b"],
            "geography_code": ["1", "2"],
            "expected_courses": [2.0, 1.0],
        }
    )
    facilities = pl.DataFrame({"facility_id": [f"f{i}" for i in range(19)]})
    minutes = [[10.0 + i for i in range(19)], [20.0 + i for i in range(19)]]
    kilometres = [[5.0 + i for i in range(19)], [8.0 + i for i in range(19)]]
    spatial = pl.DataFrame(
        {
            "geography_code": [code for code in ("1", "2") for _ in range(19)],
            "routing_point_id": [f"{code}-p" for code in ("1", "2") for _ in range(19)],
            "routing_weight": [1.0] * 38,
            "facility_id": [f"f{i}" for _ in range(2) for i in range(19)],
            "one_way_minutes": [10.0 + i for i in range(19)] + [20.0 + i for i in range(19)],
            "route_is_approximation": [False] * 38,
        }
    )
    spatial_path = tmp_path / "spatial.parquet"
    spatial.write_parquet(spatial_path)

    outputs = build_outputs(
        demand,
        facilities,
        __import__("numpy").asarray(minutes),
        __import__("numpy").asarray(kilometres),
        spatial_path=spatial_path,
        vehicle_rate=0.37,
        vehicle_rate_lower=0.23,
        vehicle_rate_upper=1.20,
    )

    assert set(outputs) == {
        "scenario_summary",
        "optimisation_frontier",
        "uncertainty_analysis",
        "mcda_outputs",
        "voi_outputs",
    }
    assert outputs["scenario_summary"]["operational_recommendation"] is False
    assert outputs["optimisation_frontier"]["optimality_claimed"] is False
    assert outputs["mcda_outputs"]["clinical_safety_is_compensatory"] is False
    assert outputs["voi_outputs"]["monetary_evpi_status"] == "not_estimated"
    assert outputs["voi_outputs"]["microdata_enbs_status"] == "not_estimable_from_public_inputs"
