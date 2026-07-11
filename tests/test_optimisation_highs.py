from __future__ import annotations

import numpy as np

from closer_to_whom.optimisation_highs import solve_p_median_milp
from closer_to_whom.robust_optimisation import robust_p_median_oracle


def test_p_median_milp_selects_extremes() -> None:
    costs=np.array([[0.0,5.0,10.0],[10.0,5.0,0.0]])
    demand=np.array([1.0,1.0])
    result=solve_p_median_milp(costs,demand,2)
    assert result.optimal
    assert result.selected_indices == (0,2)
    assert result.objective == 0.0


def test_robust_oracle_orders_by_maximum_regret() -> None:
    costs=np.array([
        [[0.0,10.0],[10.0,0.0]],
        [[2.0,8.0],[8.0,2.0]],
    ])
    result=robust_p_median_oracle(costs,np.array([1.0,1.0]),1)
    assert len(result) == 2
    assert result[0].maximum_regret == result[1].maximum_regret
