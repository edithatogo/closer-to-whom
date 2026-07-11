"""Shared enums and strongly typed identifiers."""

from __future__ import annotations

from enum import StrEnum
from typing import NewType

FacilityId = NewType("FacilityId", str)
DemandCellId = NewType("DemandCellId", str)
ScenarioId = NewType("ScenarioId", str)
PathwayId = NewType("PathwayId", str)
SourceId = NewType("SourceId", str)
AssumptionId = NewType("AssumptionId", str)


class EvidenceGrade(StrEnum):
    """Strength of public evidence for a service capability."""

    GRADE_1 = "1_explicit_named_treatment"
    GRADE_2 = "2_explicit_solid_tumour_sact"
    GRADE_3 = "3_ambiguous_oncology_or_outreach"
    GRADE_4 = "4_historical_or_indirect"

    @property
    def rank(self) -> int:
        """Return a numeric rank where one is the strongest evidence."""
        return int(self.value.split("_", maxsplit=1)[0])


class CapabilityStatus(StrEnum):
    """Publicly supportable capability state."""

    CONFIRMED = "confirmed"
    PLAUSIBLE = "plausible"
    UNKNOWN = "unknown"
    EXCLUDED = "excluded"


class DeliveryMode(StrEnum):
    """Treatment delivery configuration."""

    IV_HOSPITAL = "iv_hospital"
    IV_SATELLITE = "iv_satellite"
    SC_HOSPITAL = "sc_hospital"
    SC_COMMUNITY = "sc_community"
    SC_HOME = "sc_home"
    HYBRID = "hybrid"


class Formulation(StrEnum):
    """Anti-HER2 medicine formulation or combination."""

    TRASTUZUMAB_IV = "trastuzumab_iv"
    TRASTUZUMAB_SC = "trastuzumab_sc"
    PHESGO_SC = "phesgo_sc"


class Perspective(StrEnum):
    """Economic perspective."""

    PATIENT = "patient"
    PATIENT_WHANAU = "patient_whanau"
    PAYER = "payer"
    PROVIDER = "provider"
    SOCIETAL = "societal"


class ScenarioKind(StrEnum):
    """Policy status attached to a scenario."""

    CURRENT_DOCUMENTED = "current_documented"
    LICENSED_FUNDING_UNCERTAIN = "licensed_funding_uncertain"
    COMMISSIONING_COUNTERFACTUAL = "commissioning_counterfactual"
    INFRASTRUCTURE_EXPLORATORY = "infrastructure_exploratory"


class AssignmentRule(StrEnum):
    """Service-assignment rule used by a scenario."""

    CENTRAL_ONLY = "central_only"
    DOMICILE_DISTRICT = "domicile_district"
    NEAREST_ELIGIBLE = "nearest_eligible"
    OPTIMISED = "optimised"
    FIXED = "fixed"


class LicenceState(StrEnum):
    """Redistribution status for a source."""

    OPEN = "open"
    PUBLIC_NOT_REDISTRIBUTABLE = "public_not_redistributable"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


class DataClassification(StrEnum):
    """Repository data classification."""

    PUBLIC_AGGREGATE = "public_aggregate"
    SYNTHETIC = "synthetic"
    GENERATED_AGGREGATE = "generated_aggregate"
    LICENSED = "licensed"
    CONFIDENTIAL = "confidential"
