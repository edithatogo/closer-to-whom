from __future__ import annotations

import numpy as np
from hypothesis import given
from hypothesis import strategies as st

from closer_to_whom.costs import calculate_course_burden
from closer_to_whom.optimisation import solve_location_allocation
from closer_to_whom.routing import haversine_km
from closer_to_whom.synthetic import synthetic_cost_rates


@given(
    st.floats(min_value=-89, max_value=89, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-179, max_value=179, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-89, max_value=89, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-179, max_value=179, allow_nan=False, allow_infinity=False),
)
def test_haversine_symmetry(lat1: float, lon1: float, lat2: float, lon2: float) -> None:
    assert haversine_km(lat1, lon1, lat2, lon2) >= 0
    assert abs(haversine_km(lat1, lon1, lat2, lon2) - haversine_km(lat2, lon2, lat1, lon1)) < 1e-8


@given(
    st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0, max_value=600, allow_nan=False, allow_infinity=False),
    st.integers(min_value=0, max_value=30),
)
def test_course_burden_nonnegative_and_monotone(
    distance: float, minutes: float, visits: int
) -> None:
    rates = synthetic_cost_rates()
    low = calculate_course_burden(
        one_way_km=distance,
        one_way_minutes=minutes,
        visits=visits,
        course_on_site_minutes=0,
        rates=rates,
    )
    high = calculate_course_burden(
        one_way_km=distance + 1,
        one_way_minutes=minutes + 1,
        visits=visits,
        course_on_site_minutes=0,
        rates=rates,
    )
    assert low.course_travel_km >= 0
    assert high.course_travel_km >= low.course_travel_km
    assert high.patient_direct_cost_nzd >= low.patient_direct_cost_nzd


@given(st.integers(min_value=2, max_value=7), st.integers(min_value=1, max_value=4))
def test_more_sites_do_not_worsen_p_median(site_total: int, seed: int) -> None:
    rng = np.random.default_rng(seed)
    costs = rng.uniform(0, 100, size=(5, site_total))
    weights = rng.uniform(0.1, 2.0, size=5)
    one = solve_location_allocation(costs, weights, site_count=1)
    two = solve_location_allocation(costs, weights, site_count=min(2, site_total))
    assert two.objective_value <= one.objective_value + 1e-10
