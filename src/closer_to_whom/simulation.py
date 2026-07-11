"""End-to-end aggregate policy-simulation engine."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict

import polars as pl

from closer_to_whom import __version__
from closer_to_whom.assignment import assign_services
from closer_to_whom.costs import calculate_course_burden
from closer_to_whom.demand import demand_cells_to_frame
from closer_to_whom.models import CostRates, DemandCell, Facility, Pathway, Scenario
from closer_to_whom.pathways import pathway_summary
from closer_to_whom.registry import eligible_facilities, facilities_to_frame
from closer_to_whom.routing import OfflineApproximationEngine, RouteEngine, build_route_matrix
from closer_to_whom.types import DeliveryMode


def _home_mode(scenario: Scenario) -> bool:
    return DeliveryMode.SC_HOME in scenario.allowed_delivery_modes


def _community_mode(scenario: Scenario) -> bool:
    return DeliveryMode.SC_COMMUNITY in scenario.allowed_delivery_modes


def _eligible_for_scenario(
    facilities: tuple[Facility, ...],
    pathway: Pathway,
    scenario: Scenario,
) -> tuple[Facility, ...]:
    modes = scenario.allowed_delivery_modes
    # Home models use the nearest hospital as provider base and for any hospital-required doses.
    if _home_mode(scenario):
        modes = frozenset({DeliveryMode.SC_HOSPITAL})
    return eligible_facilities(
        facilities,
        formulation=pathway.formulation,
        delivery_modes=modes,
        evidence_grade_threshold=scenario.evidence_grade_threshold,
        include_plausible=scenario.evidence_grade_threshold >= 3,
    )


def simulate_scenario_pathway(
    *,
    demand_cells: Iterable[DemandCell],
    facilities: Iterable[Facility],
    pathway: Pathway,
    scenario: Scenario,
    cost_rates: CostRates,
    assumptions_fingerprint: str,
    route_engine: RouteEngine | None = None,
) -> pl.DataFrame:
    """Simulate one pathway and service configuration using aggregate demand cells."""
    if pathway.formulation not in scenario.allowed_formulations:
        return pl.DataFrame()
    demand_tuple = tuple(demand_cells)
    facility_tuple = tuple(facilities)
    eligible = _eligible_for_scenario(facility_tuple, pathway, scenario)
    if not eligible:
        return pl.DataFrame()

    demand = demand_cells_to_frame(demand_tuple)
    facility_frame = facilities_to_frame(eligible)
    engine = route_engine or OfflineApproximationEngine()
    routes = build_route_matrix(demand, facility_frame, engine)
    assignment = assign_services(demand, facility_frame, routes, scenario)

    if scenario.patient_one_way_cap_km is not None:
        assignment = assignment.with_columns(
            pl.col("one_way_km").clip(upper_bound=scenario.patient_one_way_cap_km)
        )
    if scenario.patient_one_way_cap_minutes is not None:
        assignment = assignment.with_columns(
            pl.col("one_way_minutes").clip(upper_bound=scenario.patient_one_way_cap_minutes)
        )

    pathway_data = pathway_summary(pathway)
    total_visits = float(pathway_data["expected_administrations"])
    hospital_visits = float(pathway_data["hospital_required_visits"])
    home_visits = float(pathway_data["home_eligible_visits"]) if _home_mode(scenario) else 0.0
    patient_visits = hospital_visits if _home_mode(scenario) else total_visits
    course_on_site_minutes = float(pathway_data["course_on_site_minutes"])

    demand_lookup = {row["demand_cell_id"]: row for row in demand.iter_rows(named=True)}
    rows: list[dict[str, str | int | float | bool]] = []
    for assigned in assignment.sort("demand_cell_id").iter_rows(named=True):
        demand_row = demand_lookup[str(assigned["demand_cell_id"])]
        one_way_km = float(assigned["one_way_km"])
        one_way_minutes = float(assigned["one_way_minutes"])
        provider_round_trip_km = one_way_km * 2.0 * home_visits
        provider_minutes = (
            one_way_minutes * 2.0 + course_on_site_minutes / max(total_visits, 1.0)
        ) * home_visits
        burden = calculate_course_burden(
            one_way_km=one_way_km,
            one_way_minutes=one_way_minutes,
            visits=patient_visits,
            course_on_site_minutes=course_on_site_minutes,
            rates=cost_rates,
            public_transport_share=0.0,
            nta_eligible_share=0.0,
            home_provider_round_trip_km=provider_round_trip_km,
            home_provider_minutes=provider_minutes,
        )
        row: dict[str, str | int | float | bool] = {
            "scenario_id": scenario.scenario_id,
            "scenario_name": scenario.name,
            "scenario_kind": scenario.kind.value,
            "pathway_id": pathway.pathway_id,
            "decision_cohort": pathway.decision_cohort,
            "formulation": pathway.formulation.value,
            "demand_cell_id": str(assigned["demand_cell_id"]),
            "facility_id": str(assigned["facility_id"]),
            "region": str(demand_row["region"]),
            "district": str(demand_row["district"]),
            "ethnicity": str(demand_row["ethnicity"]),
            "deprivation_quintile": int(demand_row["deprivation_quintile"]),
            "rurality": str(demand_row["rurality"]),
            "expected_courses": float(demand_row["expected_courses"]),
            "one_way_km": one_way_km,
            "one_way_minutes": one_way_minutes,
            "patient_visits": patient_visits,
            "provider_home_visits": home_visits,
            "route_is_approximation": bool(assigned["route_is_approximation"]),
            "model_version": __version__,
            "assumptions_fingerprint": assumptions_fingerprint,
        }
        row.update(asdict(burden))
        rows.append(row)
    return pl.DataFrame(rows).sort(["scenario_id", "pathway_id", "demand_cell_id"])


def simulate_all(
    *,
    demand_cells: Iterable[DemandCell],
    facilities: Iterable[Facility],
    pathways: Iterable[Pathway],
    scenarios: Iterable[Scenario],
    cost_rates: CostRates,
    assumptions_fingerprint: str,
    route_engine: RouteEngine | None = None,
) -> pl.DataFrame:
    """Run every compatible active pathway and scenario."""
    demand_tuple = tuple(demand_cells)
    facility_tuple = tuple(facilities)
    frames: list[pl.DataFrame] = []
    for scenario in sorted(
        (item for item in scenarios if item.active), key=lambda item: item.scenario_id
    ):
        for pathway in sorted(pathways, key=lambda item: item.pathway_id):
            frame = simulate_scenario_pathway(
                demand_cells=demand_tuple,
                facilities=facility_tuple,
                pathway=pathway,
                scenario=scenario,
                cost_rates=cost_rates,
                assumptions_fingerprint=assumptions_fingerprint,
                route_engine=route_engine,
            )
            if not frame.is_empty():
                frames.append(frame)
    if not frames:
        raise ValueError("No compatible scenario-pathway combinations were simulated")
    return pl.concat(frames, how="diagonal_relaxed").sort(
        ["scenario_id", "pathway_id", "demand_cell_id"]
    )
