from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from closer_to_whom.assignment import assign_services
from closer_to_whom.demand import demand_cells_to_frame
from closer_to_whom.registry import eligible_facilities, facilities_to_frame, load_facilities
from closer_to_whom.routing import OfflineApproximationEngine, build_route_matrix
from closer_to_whom.synthetic import synthetic_scenarios
from closer_to_whom.types import DeliveryMode, Formulation


def test_eligible_facilities(bundle: dict[str, object]) -> None:
    facilities = bundle["facilities"]
    selected = eligible_facilities(  # type: ignore[arg-type]
        facilities,
        formulation=Formulation.TRASTUZUMAB_IV,
        delivery_modes=frozenset({DeliveryMode.IV_HOSPITAL}),
        evidence_grade_threshold=1,
    )
    assert len(selected) == 12
    community = eligible_facilities(  # type: ignore[arg-type]
        facilities,
        formulation=Formulation.TRASTUZUMAB_SC,
        delivery_modes=frozenset({DeliveryMode.SC_COMMUNITY}),
        evidence_grade_threshold=3,
        include_plausible=True,
    )
    assert [item.facility_id for item in community] == ["SYN_COMMUNITY"]


def test_load_facilities_round_trip(bundle: dict[str, object], tmp_path: Path) -> None:
    frame = facilities_to_frame(bundle["facilities"])  # type: ignore[arg-type]
    csv_frame = frame.with_columns(
        pl.col("source_ids").list.join("|"),
        pl.col("formulations").list.join("|"),
        pl.col("delivery_modes").list.join("|"),
    ).with_columns(
        pl.col("evidence_grade").replace_strict(
            {
                1: "1_explicit_named_treatment",
                2: "2_explicit_solid_tumour_sact",
                3: "3_ambiguous_oncology_or_outreach",
                4: "4_historical_or_indirect",
            }
        )
    )
    path = tmp_path / "facilities.csv"
    csv_frame.write_csv(path)
    loaded = load_facilities(path)
    assert len(loaded) == len(bundle["facilities"])  # type: ignore[arg-type]


def test_assign_central_and_domicile(bundle: dict[str, object]) -> None:
    demand = demand_cells_to_frame(bundle["demand"])  # type: ignore[arg-type]
    facilities = facilities_to_frame(bundle["facilities"]).filter(  # type: ignore[arg-type]
        pl.col("facility_type") == "synthetic_hospital"
    )
    routes = build_route_matrix(demand, facilities, OfflineApproximationEngine())
    scenarios = {item.scenario_id: item for item in synthetic_scenarios()}
    central = assign_services(demand, facilities, routes, scenarios["s0_auckland_only_iv"])
    assert central.get_column("facility_id").unique().to_list() == ["SYN_AKL"]
    domicile = assign_services(demand, facilities, routes, scenarios["s1_domicile_district_iv"])
    assert domicile.height == demand.height


def test_assign_no_candidates_raises(bundle: dict[str, object]) -> None:
    demand = demand_cells_to_frame(bundle["demand"])  # type: ignore[arg-type]
    scenario = synthetic_scenarios()[2]
    with pytest.raises(ValueError, match="no eligible"):
        assign_services(
            demand, pl.DataFrame({"facility_id": [], "district": []}), pl.DataFrame(), scenario
        )
