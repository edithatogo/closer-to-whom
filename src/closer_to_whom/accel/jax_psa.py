"""JAX/XLA kernels with NumPy oracles for repeated aggregate PSA calculations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt

type FloatArray = npt.NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class DifferentialResult:
    """Numerical equivalence receipt for an accelerated kernel."""

    available: bool
    passed: bool
    maximum_absolute_error: float
    maximum_relative_error: float
    draws: int
    cells: int


def course_cost_numpy(
    distances_km: FloatArray,
    travel_minutes: FloatArray,
    administrations: FloatArray,
    cost_per_km: FloatArray,
    value_per_minute: FloatArray,
) -> FloatArray:
    """Reference calculation for draw × cell aggregate course burden."""

    return administrations * (
        distances_km * cost_per_km[:, None] + travel_minutes * value_per_minute[:, None]
    )


def course_cost_jax(
    distances_km: FloatArray,
    travel_minutes: FloatArray,
    administrations: FloatArray,
    cost_per_km: FloatArray,
    value_per_minute: FloatArray,
) -> FloatArray:
    """JIT-compiled equivalent; import JAX only at the optional boundary."""

    try:
        import jax
        import jax.numpy as jnp
    except ImportError as exc:  # pragma: no cover - optional environment
        raise RuntimeError("JAX acceleration extra is not installed") from exc

    @jax.jit
    def kernel(
        distance: Any,
        travel: Any,
        administrations_: Any,
        kilometre_cost: Any,
        minute_value: Any,
    ) -> Any:
        return administrations_ * (
            distance * kilometre_cost[:, None] + travel * minute_value[:, None]
        )

    result = kernel(
        jnp.asarray(distances_km),
        jnp.asarray(travel_minutes),
        jnp.asarray(administrations),
        jnp.asarray(cost_per_km),
        jnp.asarray(value_per_minute),
    )
    return np.asarray(result, dtype=np.float64)


def differential_check(
    *,
    draws: int = 256,
    cells: int = 128,
    seed: int = 20260711,
    absolute_tolerance: float = 1e-5,
    relative_tolerance: float = 1e-5,
) -> DifferentialResult:
    """Compare JAX/XLA against the deterministic NumPy oracle."""

    rng = np.random.default_rng(seed)
    distance = rng.uniform(0.0, 600.0, size=(draws, cells)).astype(np.float64)
    travel = rng.uniform(0.0, 900.0, size=(draws, cells)).astype(np.float64)
    administrations = rng.integers(1, 30, size=(draws, cells)).astype(np.float64)
    kilometre_cost = rng.uniform(0.2, 1.5, size=draws).astype(np.float64)
    minute_value = rng.uniform(0.1, 2.0, size=draws).astype(np.float64)
    expected = course_cost_numpy(distance, travel, administrations, kilometre_cost, minute_value)
    try:
        observed = course_cost_jax(distance, travel, administrations, kilometre_cost, minute_value)
    except RuntimeError:
        return DifferentialResult(
            available=False,
            passed=False,
            maximum_absolute_error=float("nan"),
            maximum_relative_error=float("nan"),
            draws=draws,
            cells=cells,
        )
    absolute = np.abs(observed - expected)
    denominator = np.maximum(np.abs(expected), np.finfo(np.float64).eps)
    relative = absolute / denominator
    passed = bool(
        np.allclose(
            observed,
            expected,
            atol=absolute_tolerance,
            rtol=relative_tolerance,
        )
    )
    return DifferentialResult(
        available=True,
        passed=passed,
        maximum_absolute_error=float(absolute.max(initial=0.0)),
        maximum_relative_error=float(relative.max(initial=0.0)),
        draws=draws,
        cells=cells,
    )
