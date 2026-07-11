from __future__ import annotations

import pytest

from closer_to_whom.costs import calculate_course_burden
from closer_to_whom.pathways import default_synthetic_pathways, pathway_summary, pathways_to_frame
from closer_to_whom.synthetic import synthetic_cost_rates


def test_pathway_summaries() -> None:
    pathways = default_synthetic_pathways()
    assert pathways[0].expected_administrations == 18
    summary = pathway_summary(pathways[2])
    assert summary["hospital_required_visits"] == 1
    assert summary["home_eligible_visits"] == 11
    assert pathways_to_frame(pathways).height == 3


def test_course_burden_components() -> None:
    rates = synthetic_cost_rates()
    burden = calculate_course_burden(
        one_way_km=30,
        one_way_minutes=40,
        visits=18,
        course_on_site_minutes=1800,
        rates=rates,
        public_transport_share=0.2,
        nta_eligible_share=0.5,
        home_provider_round_trip_km=100,
        home_provider_minutes=120,
    )
    assert burden.course_travel_km == 1080
    assert burden.patient_direct_cost_nzd > 0
    assert burden.payer_cost_nzd == pytest.approx(1080 * rates.nta_reimbursement_per_km * 0.5)
    assert burden.societal_cost_nzd > burden.patient_direct_cost_nzd
    assert burden.provider_cost_nzd > 0


def test_course_burden_rejects_invalid_inputs() -> None:
    rates = synthetic_cost_rates()
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_course_burden(
            one_way_km=-1,
            one_way_minutes=1,
            visits=1,
            course_on_site_minutes=1,
            rates=rates,
        )
    with pytest.raises(ValueError, match="Shares"):
        calculate_course_burden(
            one_way_km=1,
            one_way_minutes=1,
            visits=1,
            course_on_site_minutes=1,
            rates=rates,
            public_transport_share=1.2,
        )
