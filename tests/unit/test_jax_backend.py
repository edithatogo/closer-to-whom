from __future__ import annotations

import numpy as np
import pytest

from closer_to_whom.accel.jax_backend import (
    course_travel_jax,
    course_travel_numpy,
    differential_check,
    jax_available,
)


def test_numpy_kernel() -> None:
    inputs = tuple(np.array([value], dtype=float) for value in (10, 20, 3, 0.5, 2))
    distance, minutes, cost = course_travel_numpy(*inputs)
    assert distance[0] == 60
    assert minutes[0] == 120
    assert cost[0] == 36


@pytest.mark.jax
def test_jax_differential_if_available() -> None:
    if not jax_available():
        pytest.skip("JAX optional dependency is not installed")
    assert differential_check(size=128) <= 1e-10
    inputs = tuple(np.array([value], dtype=float) for value in (10, 20, 3, 0.5, 2))
    assert np.allclose(course_travel_jax(*inputs)[0], np.array([60.0]))
