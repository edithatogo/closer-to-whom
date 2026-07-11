from __future__ import annotations

import numpy as np
import pytest

from closer_to_whom.accel.jax_psa import course_cost_numpy, differential_check


def test_numpy_course_cost_shape_and_value() -> None:
    result=course_cost_numpy(
        np.array([[10.0,20.0]]),
        np.array([[30.0,40.0]]),
        np.array([[2.0,3.0]]),
        np.array([0.5]),
        np.array([1.0]),
    )
    np.testing.assert_allclose(result,np.array([[70.0,150.0]]))


def test_jax_differential_when_available() -> None:
    result=differential_check(draws=8,cells=4)
    if not result.available:
        pytest.skip("JAX optional extra not installed")
    assert result.passed
