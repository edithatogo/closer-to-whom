"""Treatment-pathway construction and resource summaries."""

from __future__ import annotations

from collections.abc import Iterable

import polars as pl

from closer_to_whom.models import Pathway, VisitType
from closer_to_whom.types import Formulation


def default_synthetic_pathways() -> tuple[Pathway, ...]:
    """Return transparent synthetic pathways for software demonstrations only."""
    source_ids = ("synthetic.clinical-fixture",)
    return (
        Pathway(
            pathway_id="early_trastuzumab_iv_demo",
            decision_cohort="early_her2_demo",
            name="Early HER2-positive pathway - IV demonstration",
            indication="early",
            formulation=Formulation.TRASTUZUMAB_IV,
            visits=(
                VisitType(
                    visit_type_id="iv_administration",
                    count=18.0,
                    administration_minutes=60.0,
                    observation_minutes=30.0,
                    other_on_site_minutes=30.0,
                    requires_hospital=True,
                    requires_resuscitation=True,
                ),
            ),
            clinically_reviewed=False,
            source_ids=source_ids,
        ),
        Pathway(
            pathway_id="early_trastuzumab_sc_demo",
            decision_cohort="early_her2_demo",
            name="Early HER2-positive pathway - SC demonstration",
            indication="early",
            formulation=Formulation.TRASTUZUMAB_SC,
            visits=(
                VisitType(
                    visit_type_id="sc_administration",
                    count=18.0,
                    administration_minutes=5.0,
                    observation_minutes=15.0,
                    other_on_site_minutes=15.0,
                    may_be_home=True,
                ),
            ),
            clinically_reviewed=False,
            source_ids=source_ids,
        ),
        Pathway(
            pathway_id="metastatic_phesgo_demo",
            decision_cohort="metastatic_pertuzumab_demo",
            name="Metastatic pertuzumab-trastuzumab SC demonstration",
            indication="metastatic",
            formulation=Formulation.PHESGO_SC,
            visits=(
                VisitType(
                    visit_type_id="initial_phesgo",
                    count=1.0,
                    administration_minutes=8.0,
                    observation_minutes=30.0,
                    other_on_site_minutes=20.0,
                    requires_hospital=True,
                    requires_resuscitation=True,
                ),
                VisitType(
                    visit_type_id="maintenance_phesgo",
                    count=11.0,
                    administration_minutes=5.0,
                    observation_minutes=15.0,
                    other_on_site_minutes=15.0,
                    may_be_home=True,
                ),
            ),
            clinically_reviewed=False,
            source_ids=source_ids,
        ),
    )


def pathway_summary(pathway: Pathway) -> dict[str, str | float | bool]:
    """Flatten a pathway into aggregate course resources."""
    administrations = pathway.expected_administrations
    on_site_minutes = sum(visit.count * visit.on_site_minutes for visit in pathway.visits)
    hospital_visits = sum(visit.count for visit in pathway.visits if visit.requires_hospital)
    home_eligible_visits = sum(visit.count for visit in pathway.visits if visit.may_be_home)
    return {
        "pathway_id": pathway.pathway_id,
        "decision_cohort": pathway.decision_cohort,
        "pathway_name": pathway.name,
        "indication": pathway.indication,
        "formulation": pathway.formulation.value,
        "expected_administrations": administrations,
        "course_on_site_minutes": on_site_minutes,
        "hospital_required_visits": hospital_visits,
        "home_eligible_visits": home_eligible_visits,
        "clinically_reviewed": pathway.clinically_reviewed,
    }


def pathways_to_frame(pathways: Iterable[Pathway]) -> pl.DataFrame:
    """Return one aggregate row per pathway."""
    return pl.DataFrame([pathway_summary(pathway) for pathway in pathways]).sort("pathway_id")
