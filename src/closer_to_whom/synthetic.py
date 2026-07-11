"""Deterministic aggregate-only fixtures for testing and demonstrations."""

from __future__ import annotations

from closer_to_whom.models import CostRates, DemandCell, Facility, Scenario
from closer_to_whom.pathways import default_synthetic_pathways
from closer_to_whom.types import (
    AssignmentRule,
    CapabilityStatus,
    DataClassification,
    DeliveryMode,
    EvidenceGrade,
    Formulation,
    ScenarioKind,
)


def synthetic_facilities() -> tuple[Facility, ...]:
    """Return fictional capability records at approximate NZ city coordinates.

    Names and capabilities are deliberately synthetic and must never be presented as an observed
    service census.
    """
    all_formulations = frozenset(Formulation)
    hospital_modes = frozenset(
        {DeliveryMode.IV_HOSPITAL, DeliveryMode.IV_SATELLITE, DeliveryMode.SC_HOSPITAL}
    )
    rows = (
        ("SYN_AKL", "Synthetic Auckland hub", "Northern", "Auckland", -36.8485, 174.7633),
        ("SYN_WRE", "Synthetic Whangārei site", "Northern", "Northland", -35.7251, 174.3237),
        ("SYN_HAM", "Synthetic Hamilton site", "Te Manawa Taki", "Waikato", -37.7870, 175.2793),
        ("SYN_TGA", "Synthetic Tauranga site", "Te Manawa Taki", "Bay of Plenty", -37.6878, 176.1651),
        ("SYN_GIS", "Synthetic Gisborne site", "Te Manawa Taki", "Tairāwhiti", -38.6623, 178.0176),
        ("SYN_NPL", "Synthetic New Plymouth site", "Central", "Taranaki", -39.0556, 174.0752),
        ("SYN_PMR", "Synthetic Palmerston North site", "Central", "MidCentral", -40.3523, 175.6082),
        ("SYN_WLG", "Synthetic Wellington site", "Central", "Capital and Coast", -41.2866, 174.7756),
        ("SYN_NSN", "Synthetic Nelson site", "South Island", "Nelson Marlborough", -41.2706, 173.2840),
        ("SYN_CHC", "Synthetic Christchurch site", "South Island", "Canterbury", -43.5321, 172.6362),
        ("SYN_DUD", "Synthetic Dunedin site", "South Island", "Southern", -45.8788, 170.5028),
        ("SYN_IVC", "Synthetic Invercargill site", "South Island", "Southern", -46.4132, 168.3538),
    )
    return tuple(
        Facility(
            facility_id=facility_id,
            name=name,
            region=region,
            district=district,
            latitude=latitude,
            longitude=longitude,
            facility_type="synthetic_hospital",
            public_or_private="public",
            capability_status=CapabilityStatus.CONFIRMED,
            evidence_grade=EvidenceGrade.GRADE_1,
            source_ids=("synthetic.service-fixture",),
            formulations=all_formulations,
            delivery_modes=hospital_modes,
            opening_hours_per_week=40.0,
        )
        for facility_id, name, region, district, latitude, longitude in rows
    ) + (
        Facility(
            facility_id="SYN_COMMUNITY",
            name="Synthetic distributed community network",
            region="National",
            district="National",
            latitude=-40.9006,
            longitude=174.8860,
            facility_type="synthetic_virtual_candidate",
            public_or_private="candidate",
            capability_status=CapabilityStatus.PLAUSIBLE,
            evidence_grade=EvidenceGrade.GRADE_3,
            source_ids=("synthetic.service-fixture",),
            formulations=frozenset({Formulation.TRASTUZUMAB_SC, Formulation.PHESGO_SC}),
            delivery_modes=frozenset({DeliveryMode.SC_COMMUNITY, DeliveryMode.SC_HOME}),
            opening_hours_per_week=None,
        ),
    )


def synthetic_demand_cells() -> tuple[DemandCell, ...]:
    """Return fictional aggregate expected courses spanning all four regions."""
    rows = (
        ("D_AKL", "SYN001", -36.89, 174.72, "Northern", "Auckland", "Māori", 4, "Urban", 9.5),
        ("D_NTH", "SYN002", -35.23, 173.95, "Northern", "Northland", "Māori", 5, "Rural", 3.1),
        ("D_WKO", "SYN003", -38.10, 175.40, "Te Manawa Taki", "Waikato", "Pacific", 4, "Rural", 4.2),
        ("D_BOP", "SYN004", -38.05, 176.30, "Te Manawa Taki", "Bay of Plenty", "Māori", 5, "Remote", 2.8),
        ("D_HB", "SYN005", -39.49, 176.92, "Central", "Hawke's Bay", "European/Other", 3, "Urban", 4.7),
        ("D_WLG", "SYN006", -41.12, 175.08, "Central", "Hutt Valley", "Pacific", 5, "Urban", 5.0),
        ("D_WC", "SYN007", -42.45, 171.21, "South Island", "West Coast", "European/Other", 4, "Remote", 1.7),
        ("D_CAN", "SYN008", -43.78, 171.75, "South Island", "Canterbury", "Māori", 3, "Rural", 4.0),
        ("D_OTG", "SYN009", -45.18, 169.32, "South Island", "Southern", "European/Other", 2, "Remote", 2.6),
        ("D_STL", "SYN010", -46.15, 168.90, "South Island", "Southern", "Māori", 4, "Rural", 1.9),
    )
    return tuple(
        DemandCell(
            demand_cell_id=demand_id,
            geography_code=geography_code,
            geography_level="SYNTHETIC",
            routing_point_id=f"RP_{geography_code}",
            latitude=latitude,
            longitude=longitude,
            region=region,
            district=district,
            ethnicity=ethnicity,
            deprivation_quintile=deprivation,
            rurality=rurality,
            expected_courses=courses,
            data_classification=DataClassification.SYNTHETIC,
        )
        for (
            demand_id,
            geography_code,
            latitude,
            longitude,
            region,
            district,
            ethnicity,
            deprivation,
            rurality,
            courses,
        ) in rows
    )


def synthetic_scenarios() -> tuple[Scenario, ...]:
    """Return a comprehensive but fictional scenario catalogue."""
    return (
        Scenario(
            scenario_id="s0_auckland_only_iv",
            name="Auckland-only IV counterfactual",
            kind=ScenarioKind.INFRASTRUCTURE_EXPLORATORY,
            assignment_rule=AssignmentRule.CENTRAL_ONLY,
            allowed_delivery_modes=frozenset({DeliveryMode.IV_HOSPITAL}),
            allowed_formulations=frozenset({Formulation.TRASTUZUMAB_IV}),
            evidence_grade_threshold=1,
            central_facility_id="SYN_AKL",
        ),
        Scenario(
            scenario_id="s1_domicile_district_iv",
            name="Domicile-district IV assignment",
            kind=ScenarioKind.COMMISSIONING_COUNTERFACTUAL,
            assignment_rule=AssignmentRule.DOMICILE_DISTRICT,
            allowed_delivery_modes=frozenset(
                {DeliveryMode.IV_HOSPITAL, DeliveryMode.IV_SATELLITE}
            ),
            allowed_formulations=frozenset({Formulation.TRASTUZUMAB_IV}),
            evidence_grade_threshold=2,
        ),
        Scenario(
            scenario_id="s2_nearest_iv",
            name="Nearest eligible IV service",
            kind=ScenarioKind.CURRENT_DOCUMENTED,
            assignment_rule=AssignmentRule.NEAREST_ELIGIBLE,
            allowed_delivery_modes=frozenset(
                {DeliveryMode.IV_HOSPITAL, DeliveryMode.IV_SATELLITE}
            ),
            allowed_formulations=frozenset({Formulation.TRASTUZUMAB_IV}),
            evidence_grade_threshold=2,
        ),
        Scenario(
            scenario_id="s3_hospital_sc",
            name="Nearest hospital-based subcutaneous service",
            kind=ScenarioKind.LICENSED_FUNDING_UNCERTAIN,
            assignment_rule=AssignmentRule.NEAREST_ELIGIBLE,
            allowed_delivery_modes=frozenset({DeliveryMode.SC_HOSPITAL}),
            allowed_formulations=frozenset(
                {Formulation.TRASTUZUMAB_SC, Formulation.PHESGO_SC}
            ),
            evidence_grade_threshold=2,
        ),
        Scenario(
            scenario_id="s4_community_sc",
            name="Distributed community subcutaneous service",
            kind=ScenarioKind.COMMISSIONING_COUNTERFACTUAL,
            assignment_rule=AssignmentRule.NEAREST_ELIGIBLE,
            allowed_delivery_modes=frozenset({DeliveryMode.SC_COMMUNITY}),
            allowed_formulations=frozenset(
                {Formulation.TRASTUZUMAB_SC, Formulation.PHESGO_SC}
            ),
            evidence_grade_threshold=3,
            patient_one_way_cap_km=15.0,
            patient_one_way_cap_minutes=25.0,
        ),
        Scenario(
            scenario_id="s5_home_sc",
            name="Healthcare-professional home subcutaneous service",
            kind=ScenarioKind.COMMISSIONING_COUNTERFACTUAL,
            assignment_rule=AssignmentRule.NEAREST_ELIGIBLE,
            allowed_delivery_modes=frozenset({DeliveryMode.SC_HOME}),
            allowed_formulations=frozenset(
                {Formulation.TRASTUZUMAB_SC, Formulation.PHESGO_SC}
            ),
            evidence_grade_threshold=3,
        ),
        Scenario(
            scenario_id="s6_optimised_satellites",
            name="Optimised additional satellite network",
            kind=ScenarioKind.INFRASTRUCTURE_EXPLORATORY,
            assignment_rule=AssignmentRule.OPTIMISED,
            allowed_delivery_modes=frozenset(
                {DeliveryMode.IV_HOSPITAL, DeliveryMode.IV_SATELLITE}
            ),
            allowed_formulations=frozenset({Formulation.TRASTUZUMAB_IV}),
            evidence_grade_threshold=3,
            candidate_site_count=2,
        ),
    )


def synthetic_cost_rates() -> CostRates:
    """Return intentionally illustrative cost assumptions."""
    return CostRates(
        vehicle_running_cost_per_km=0.37,
        vehicle_broad_cost_per_km=1.20,
        nta_reimbursement_per_km=0.44,
        public_transport_fare_per_round_trip=8.0,
        parking_cost_per_visit=12.0,
        patient_time_value_per_hour=25.0,
        companion_time_value_per_hour=25.0,
        companion_probability=0.45,
        provider_time_value_per_hour=65.0,
        provider_vehicle_cost_per_km=0.83,
    )


def synthetic_bundle() -> dict[str, object]:
    """Return all deterministic synthetic components."""
    return {
        "facilities": synthetic_facilities(),
        "demand": synthetic_demand_cells(),
        "pathways": default_synthetic_pathways(),
        "scenarios": synthetic_scenarios(),
        "cost_rates": synthetic_cost_rates(),
    }
