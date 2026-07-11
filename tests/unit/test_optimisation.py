from __future__ import annotations

import numpy as np
import pytest

from closer_to_whom.optimisation import (
    ParetoPoint,
    greedy_p_median,
    maximal_coverage,
    pareto_frontier,
    solve_location_allocation,
)

COSTS = np.array([[1.0, 10.0, 5.0], [9.0, 1.0, 5.0], [4.0, 4.0, 1.0]])
WEIGHTS = np.array([1.0, 1.0, 1.0])


def test_exact_p_median_and_p_center() -> None:
    median = solve_location_allocation(COSTS, WEIGHTS, site_count=2, objective="p_median")
    center = solve_location_allocation(COSTS, WEIGHTS, site_count=2, objective="p_center")
    assert median.optimal and center.optimal
    assert len(median.selected_indices) == 2
    assert median.objective_value <= 6
    assert center.objective_value <= 4


def test_maximal_coverage_and_greedy() -> None:
    coverage = maximal_coverage(COSTS, WEIGHTS, site_count=1, threshold=1.0)
    assert coverage.objective_value == 1.0
    greedy = greedy_p_median(COSTS, WEIGHTS, site_count=2)
    assert len(greedy.selected_indices) == 2
    assert not greedy.optimal


def test_problem_validation_and_oracle_limit() -> None:
    with pytest.raises(ValueError):
        solve_location_allocation(COSTS, WEIGHTS, site_count=0)
    with pytest.raises(ValueError, match="HiGHS"):
        solve_location_allocation(np.ones((2, 20)), np.ones(2), site_count=10, max_enumerations=2)
    with pytest.raises(ValueError):
        maximal_coverage(COSTS, WEIGHTS, site_count=1, threshold=-1)


def test_pareto_frontier() -> None:
    points = (
        ParetoPoint("a", (1.0, 3.0)),
        ParetoPoint("b", (2.0, 2.0)),
        ParetoPoint("c", (3.0, 3.0)),
    )
    frontier = pareto_frontier(points, minimise=(True, True))
    assert {point.label for point in frontier} == {"a", "b"}
    assert pareto_frontier((), minimise=()) == ()
    with pytest.raises(ValueError):
        pareto_frontier(points, minimise=(True,))
