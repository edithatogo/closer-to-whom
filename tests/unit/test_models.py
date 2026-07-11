from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from closer_to_whom.models import (
    DemandCell,
    Facility,
    Scenario,
    SourceRecord,
    UncertaintyParameter,
    VisitType,
)
from closer_to_whom.types import (
    AssignmentRule,
    CapabilityStatus,
    DataClassification,
    DeliveryMode,
    EvidenceGrade,
    Formulation,
    LicenceState,
    ScenarioKind,
)


def test_source_record_fails_closed() -> None:
    with pytest.raises(ValidationError, match="Only an explicitly open"):
        SourceRecord(
            source_id="candidate.test",
            title="Test",
            publisher="Publisher",
            url="https://example.com",
            retrieved_on=date(2026, 1, 1),
            licence_state=LicenceState.UNKNOWN,
            redistribution_allowed=True,
        )


def test_confirmed_facility_requires_capability() -> None:
    with pytest.raises(ValidationError, match="Confirmed facilities"):
        Facility(
            facility_id="FAC_1",
            name="Facility",
            region="Region",
            district="District",
            latitude=-41.0,
            longitude=174.0,
            facility_type="hospital",
            public_or_private="public",
            capability_status=CapabilityStatus.CONFIRMED,
            evidence_grade=EvidenceGrade.GRADE_1,
            source_ids=("source",),
        )


def test_demand_cell_rejects_confidential_classification() -> None:
    with pytest.raises(ValidationError, match="aggregate data"):
        DemandCell(
            demand_cell_id="D1",
            geography_code="G1",
            geography_level="SA2",
            routing_point_id="R1",
            latitude=-41.0,
            longitude=174.0,
            region="Region",
            district="District",
            ethnicity="Māori",
            deprivation_quintile=5,
            rurality="Rural",
            expected_courses=1.2,
            data_classification=DataClassification.CONFIDENTIAL,
        )


def test_central_scenario_requires_site() -> None:
    with pytest.raises(ValidationError, match="central_facility_id"):
        Scenario(
            scenario_id="central",
            name="Central",
            kind=ScenarioKind.INFRASTRUCTURE_EXPLORATORY,
            assignment_rule=AssignmentRule.CENTRAL_ONLY,
            allowed_delivery_modes=frozenset({DeliveryMode.IV_HOSPITAL}),
            allowed_formulations=frozenset({Formulation.TRASTUZUMAB_IV}),
        )


def test_visit_total_minutes() -> None:
    visit = VisitType(
        visit_type_id="visit",
        count=2,
        administration_minutes=5,
        observation_minutes=15,
        other_on_site_minutes=10,
    )
    assert visit.on_site_minutes == 30


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"distribution": "uniform", "base": 1.0}, "Uniform"),
        ({"distribution": "beta", "base": 0.5}, "Beta"),
        ({"distribution": "gamma", "base": 1.0}, "Gamma"),
        (
            {
                "distribution": "discrete",
                "base": 1.0,
                "values": (1.0, 2.0),
                "probabilities": (0.2, 0.2),
            },
            "sum to one",
        ),
    ],
)
def test_uncertainty_parameter_validation(payload: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        UncertaintyParameter(parameter_id="p", **payload)
