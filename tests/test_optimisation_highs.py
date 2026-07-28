from __future__ import annotations

import numpy as np

from closer_to_whom.optimisation_highs import solve_p_median_milp
from closer_to_whom.robust_optimisation import robust_p_median_oracle


def test_p_median_milp_selects_extremes() -> None:
    costs = np.array([[0.0, 5.0, 10.0], [10.0, 5.0, 0.0]])
    demand = np.array([1.0, 1.0])
    result = solve_p_median_milp(costs, demand, 2)
    assert result.optimal
    assert result.selected_indices == (0, 2)
    assert result.objective == 0.0


def test_robust_oracle_orders_by_maximum_regret() -> None:
    costs = np.array(
        [
            [[0.0, 10.0], [10.0, 0.0]],
            [[2.0, 8.0], [8.0, 2.0]],
        ]
    )
    result = robust_p_median_oracle(costs, np.array([1.0, 1.0]), 1)
    assert len(result) == 2
    assert result[0].maximum_regret == result[1].maximum_regret


def test_robust_oracle_accepts_probabilities_and_rejects_bad_shapes() -> None:
    costs = np.ones((2, 2, 2))
    result = robust_p_median_oracle(
        costs, np.array([1.0, 2.0]), 1, scenario_probabilities=np.array([0.25, 0.75])
    )
    assert result[0].expected_objective == 3.0
    with np.testing.assert_raises(ValueError):
        robust_p_median_oracle(np.ones((2, 2)), np.array([1.0, 2.0]), 1)
    with np.testing.assert_raises(ValueError):
        robust_p_median_oracle(costs, np.array([1.0]), 1)
    with np.testing.assert_raises(ValueError):
        robust_p_median_oracle(costs, np.array([1.0, 2.0]), 1, np.array([-1.0, 2.0]))
