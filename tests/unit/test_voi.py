from __future__ import annotations

import numpy as np
import pytest

from closer_to_whom.voi import (
    core_voi,
    evppi_discrete_groups,
    evppi_quantile_bins,
    evsi_from_posterior_net_benefit,
    perspective_net_benefit,
    population_value,
    research_value,
)

NET = np.array([[10.0, 5.0], [0.0, 8.0], [10.0, 4.0], [0.0, 9.0]])


def test_core_voi() -> None:
    result = core_voi(NET)
    assert result.evpi_per_decision >= 0
    assert result.probability_optimal.sum() == pytest.approx(1.0)
    assert result.expected_opportunity_loss.shape == (2,)


def test_evppi_methods() -> None:
    labels = [0, 1, 0, 1]
    discrete = evppi_discrete_groups(NET, labels)
    binned = evppi_quantile_bins(NET, np.array([0.0, 1.0, 0.2, 0.8]), bins=2)
    assert discrete >= 0
    assert binned >= 0
    with pytest.raises(ValueError):
        evppi_discrete_groups(NET, [0])


def test_evsi_population_and_research() -> None:
    posterior = np.array([[9.0, 6.0], [3.0, 8.0]])
    assert evsi_from_posterior_net_benefit(NET, posterior) >= 0
    assert population_value(10, annual_affected_decisions=100, years=2) > 1000
    value = research_value(
        research_id="study",
        evsi_per_decision=10,
        annual_affected_decisions=100,
        years=5,
        research_cost=1000,
    )
    assert value.break_even_research_cost == value.discounted_population_evsi
    assert value.expected_net_benefit_of_sampling == pytest.approx(
        value.discounted_population_evsi - 1000
    )


def test_perspective_net_benefit() -> None:
    components = {"time": np.ones((4, 2)), "cost": np.full((4, 2), 2.0)}
    net = perspective_net_benefit(components, {"time": 1.0, "cost": 3.0})
    assert np.all(net == -7)
    with pytest.raises(ValueError):
        perspective_net_benefit(components, {"missing": 1.0})
