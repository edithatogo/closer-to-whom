from __future__ import annotations

import numpy as np
import pytest

from closer_to_whom.mcda import normalise_matrix, stochastic_acceptability, weighted_sum


def test_normalisation_and_weighted_sum() -> None:
    matrix = np.array([[1.0, 10.0], [2.0, 5.0], [3.0, 1.0]])
    minimise = np.array([True, True])
    normalised = normalise_matrix(matrix, minimise=minimise)
    assert np.all((normalised >= 0) & (normalised <= 1))
    result = weighted_sum(matrix, np.array([0.8, 0.2]), minimise=minimise)
    assert result.ranking.shape == (3,)
    with pytest.raises(ValueError):
        weighted_sum(matrix, np.array([-1.0, 2.0]), minimise=minimise)


def test_stochastic_acceptability() -> None:
    matrix = np.array([[1.0, 10.0], [2.0, 5.0], [3.0, 1.0]])
    result = stochastic_acceptability(
        matrix,
        minimise=np.array([True, True]),
        draws=2000,
        seed=42,
    )
    assert np.allclose(result.rank_acceptability.sum(axis=1), 1.0)
    assert np.allclose(result.first_rank_probability.sum(), 1.0)
    with pytest.raises(ValueError):
        stochastic_acceptability(matrix, minimise=np.array([True, True]), draws=0)
