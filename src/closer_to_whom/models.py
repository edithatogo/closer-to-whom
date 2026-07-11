"""Validated domain models for the policy simulation."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

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

Latitude = Annotated[float, Field(ge=-90.0, le=90.0)]
Longitude = Annotated[float, Field(ge=-180.0, le=180.0)]
NonNegativeFloat = Annotated[float, Field(ge=0.0)]
Probability = Annotated[float, Field(ge=0.0, le=1.0)]


class StrictModel(BaseModel):
    """Base model with immutable, strict, forward-compatible validation."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)


class SourceRecord(StrictModel):
    """Provenance and licence record for an external source."""

    source_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9._-]+$")
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    url: HttpUrl
    retrieved_on: date
    publication_date: date | None = None
    licence_state: LicenceState
    redistribution_allowed: bool
    evidence_grade: EvidenceGrade | None = None
    sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    notes: str = ""

    @model_validator(mode="after")
    def fail_closed_redistribution(self) -> SourceRecord:
        """Prevent accidental redistribution of uncertain or restricted material."""
        if self.licence_state is not LicenceState.OPEN and self.redistribution_allowed:
            msg = "Only an explicitly open source may be marked redistributable"
            raise ValueError(msg)
        return self


class Facility(StrictModel):
    """Publicly documented or candidate service location."""

    facility_id: str = Field(min_length=1, pattern=r"^[A-Z0-9][A-Z0-9_-]+$")
    name: str = Field(min_length=1)
    region: str = Field(min_length=1)
    district: str = Field(min_length=1)
    latitude: Latitude
    longitude: Longitude
    facility_type: str
    public_or_private: Literal["public", "private", "candidate"]
    capability_status: CapabilityStatus
    evidence_grade: EvidenceGrade
    source_ids: tuple[str, ...] = Field(min_length=1)
    formulations: frozenset[Formulation] = frozenset()
    delivery_modes: frozenset[DeliveryMode] = frozenset()
    opening_hours_per_week: NonNegativeFloat | None = None
    observed_capacity: None = None
    redistribution_allowed: bool = True

    @model_validator(mode="after")
    def confirmed_needs_capability(self) -> Facility:
        """Require explicit capability for confirmed facilities."""
        if self.capability_status is CapabilityStatus.CONFIRMED and (
            not self.formulations or not self.delivery_modes
        ):
            msg = "Confirmed facilities require at least one formulation and delivery mode"
            raise ValueError(msg)
        return self


class DemandCell(StrictModel):
    """Aggregate expected treatment demand for a public geography and stratum."""

    demand_cell_id: str = Field(min_length=1)
    geography_code: str = Field(min_length=1)
    geography_level: Literal["SA2", "SA3", "TA", "REGION", "SYNTHETIC"]
    routing_point_id: str = Field(min_length=1)
    latitude: Latitude
    longitude: Longitude
    region: str = Field(min_length=1)
    district: str = Field(min_length=1)
    ethnicity: str = Field(min_length=1)
    deprivation_quintile: Annotated[int, Field(ge=1, le=5)]
    rurality: str = Field(min_length=1)
    expected_courses: NonNegativeFloat
    data_classification: DataClassification

    @model_validator(mode="after")
    def aggregate_only(self) -> DemandCell:
        """Reject confidential or individual-like demand rows."""
        allowed = {
            DataClassification.PUBLIC_AGGREGATE,
            DataClassification.SYNTHETIC,
            DataClassification.GENERATED_AGGREGATE,
        }
        if self.data_classification not in allowed:
            msg = "Demand cells must be public, synthetic, or generated aggregate data"
            raise ValueError(msg)
        return self


class VisitType(StrictModel):
    """A visit component in a treatment pathway."""

    visit_type_id: str = Field(min_length=1)
    count: NonNegativeFloat
    administration_minutes: NonNegativeFloat
    observation_minutes: NonNegativeFloat
    other_on_site_minutes: NonNegativeFloat = 0.0
    requires_hospital: bool = False
    requires_resuscitation: bool = False
    may_be_home: bool = False

    @property
    def on_site_minutes(self) -> float:
        """Total service time for one visit."""
        return self.administration_minutes + self.observation_minutes + self.other_on_site_minutes


class Pathway(StrictModel):
    """Clinical pathway represented at an aggregate course level."""

    pathway_id: str = Field(min_length=1)
    decision_cohort: str = Field(min_length=1)
    name: str = Field(min_length=1)
    indication: Literal["early", "metastatic"]
    formulation: Formulation
    visits: tuple[VisitType, ...] = Field(min_length=1)
    clinically_reviewed: bool = False
    source_ids: tuple[str, ...] = Field(min_length=1)

    @property
    def expected_administrations(self) -> float:
        """Expected number of administrations in the pathway."""
        return sum(visit.count for visit in self.visits)


class Scenario(StrictModel):
    """Policy counterfactual with explicit status and assignment rule."""

    scenario_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]+$")
    name: str = Field(min_length=1)
    kind: ScenarioKind
    assignment_rule: AssignmentRule
    allowed_delivery_modes: frozenset[DeliveryMode] = Field(min_length=1)
    allowed_formulations: frozenset[Formulation] = Field(min_length=1)
    evidence_grade_threshold: Annotated[int, Field(ge=1, le=4)] = 2
    central_facility_id: str | None = None
    candidate_site_count: Annotated[int, Field(ge=0)] = 0
    capacity_envelope: Literal["none", "low", "medium", "high"] = "none"
    patient_one_way_cap_km: NonNegativeFloat | None = None
    patient_one_way_cap_minutes: NonNegativeFloat | None = None
    active: bool = True

    @model_validator(mode="after")
    def central_rule_has_site(self) -> Scenario:
        """Require a site for a central-only scenario."""
        if self.assignment_rule is AssignmentRule.CENTRAL_ONLY and not self.central_facility_id:
            msg = "central_facility_id is required for central-only scenarios"
            raise ValueError(msg)
        return self


class CostRates(StrictModel):
    """Economic assumptions used to value a journey."""

    currency: Literal["NZD"] = "NZD"
    vehicle_running_cost_per_km: NonNegativeFloat
    vehicle_broad_cost_per_km: NonNegativeFloat
    nta_reimbursement_per_km: NonNegativeFloat
    public_transport_fare_per_round_trip: NonNegativeFloat
    parking_cost_per_visit: NonNegativeFloat
    patient_time_value_per_hour: NonNegativeFloat
    companion_time_value_per_hour: NonNegativeFloat
    companion_probability: Probability
    provider_time_value_per_hour: NonNegativeFloat
    provider_vehicle_cost_per_km: NonNegativeFloat


class UncertaintyParameter(StrictModel):
    """A scalar uncertain parameter and its sampling rule."""

    parameter_id: str = Field(min_length=1)
    distribution: Literal["fixed", "beta", "gamma", "lognormal", "normal", "uniform", "discrete"]
    base: float
    lower: float | None = None
    upper: float | None = None
    alpha: NonNegativeFloat | None = None
    beta: NonNegativeFloat | None = None
    shape: NonNegativeFloat | None = None
    scale: NonNegativeFloat | None = None
    values: tuple[float, ...] = ()
    probabilities: tuple[float, ...] = ()
    source_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_distribution(self) -> UncertaintyParameter:
        """Validate distribution-specific fields."""
        if self.distribution == "uniform" and (self.lower is None or self.upper is None):
            raise ValueError("Uniform parameters require lower and upper")
        if self.distribution == "beta" and (self.alpha is None or self.beta is None):
            raise ValueError("Beta parameters require alpha and beta")
        if self.distribution == "gamma" and (self.shape is None or self.scale is None):
            raise ValueError("Gamma parameters require shape and scale")
        if self.distribution == "discrete":
            if not self.values or len(self.values) != len(self.probabilities):
                raise ValueError("Discrete parameters require matched values and probabilities")
            if abs(sum(self.probabilities) - 1.0) > 1e-9:
                raise ValueError("Discrete probabilities must sum to one")
        return self


class ResearchDesign(StrictModel):
    """Candidate future research design for EVSI and ENBS."""

    research_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    resolves_parameter_groups: tuple[str, ...] = Field(min_length=1)
    estimated_cost_nzd: NonNegativeFloat
    implementation_years: NonNegativeFloat
    notes: str = ""
