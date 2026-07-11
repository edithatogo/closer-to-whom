from __future__ import annotations

import numpy as np
import pytest

from closer_to_whom.models import UncertaintyParameter
from closer_to_whom.uncertainty import (
    one_way_dsa,
    percentile_interval,
    run_psa,
    sample_parameters,
)


def parameters() -> tuple[UncertaintyParameter, ...]:
    return (
        UncertaintyParameter(
            parameter_id="u",
            distribution="uniform",
            base=0.5,
            lower=0.0,
            upper=1.0,
        ),
        UncertaintyParameter(
            parameter_id="b",
            distribution="beta",
            base=0.5,
            alpha=2.0,
            beta=2.0,
        ),
        UncertaintyParameter(
            parameter_id="g",
            distribution="gamma",
            base=2.0,
            shape=2.0,
            scale=1.0,
        ),
        UncertaintyParameter(
            parameter_id="d",
            distribution="discrete",
            base=1.0,
            values=(1.0, 2.0),
            probabilities=(0.4, 0.6),
        ),
    )


@pytest.mark.parametrize("method", ["pseudo", "latin_hypercube", "sobol"])
def test_sample_parameters(method: str) -> None:
    ids, draws = sample_parameters(parameters(), draws=32, seed=1, method=method)
    assert ids == ("u", "b", "g", "d")
    assert draws.shape == (32, 4)
    assert np.all((draws[:, 0] >= 0) & (draws[:, 0] <= 1))


def test_one_way_dsa() -> None:
    base = {"x": 2.0, "y": 3.0}
    result = one_way_dsa(base, {"x": (1.0, 4.0)}, lambda values: values["x"] * values["y"])
    assert result[0].base_output == 6
    assert result[0].absolute_swing == 9
    with pytest.raises(ValueError):
        one_way_dsa(base, {"z": (1, 2)}, lambda values: 1.0)


def test_run_psa_and_interval() -> None:
    result = run_psa(
        parameters()[:2],
        lambda values: np.array([values["u"], values["b"]]),
        draws=64,
        seed=2,
    )
    assert result.outcomes.shape == (64, 2)
    low, high = percentile_interval(result.outcomes[:, 0])
    assert low < high
    with pytest.raises(ValueError):
        percentile_interval(result.outcomes[:, 0], level=1.0)
