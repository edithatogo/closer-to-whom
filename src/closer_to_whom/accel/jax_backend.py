"""JAX/XLA kernels with NumPy reference implementations."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np


def course_travel_numpy(
    one_way_km: np.ndarray,
    one_way_minutes: np.ndarray,
    visits: np.ndarray,
    cost_per_km: np.ndarray,
    fixed_cost_per_visit: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Reference vectorised course travel and direct-cost kernel."""
    distance = 2.0 * one_way_km * visits
    minutes = 2.0 * one_way_minutes * visits
    direct_cost = distance * cost_per_km + visits * fixed_cost_per_visit
    return distance, minutes, direct_cost


@lru_cache(maxsize=1)
def _jax_modules() -> tuple[Any, Any]:
    try:
        import jax
        import jax.numpy as jnp
    except ImportError as exc:  # pragma: no cover - optional environment
        raise RuntimeError("JAX backend is unavailable; install closer-to-whom[accel]") from exc
    jax.config.update("jax_enable_x64", True)
    return jax, jnp


def jax_available() -> bool:
    """Return whether JAX can be imported without making it a core dependency."""
    try:
        _jax_modules()
    except RuntimeError:
        return False
    return True


def course_travel_jax(
    one_way_km: np.ndarray,
    one_way_minutes: np.ndarray,
    visits: np.ndarray,
    cost_per_km: np.ndarray,
    fixed_cost_per_visit: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Execute the course kernel through a JIT-compiled JAX function."""
    jax, jnp = _jax_modules()

    @jax.jit
    def kernel(
        distance_input: Any,
        time_input: Any,
        visit_input: Any,
        kilometre_cost: Any,
        fixed_cost: Any,
    ) -> tuple[Any, Any, Any]:
        distance = 2.0 * distance_input * visit_input
        minutes = 2.0 * time_input * visit_input
        direct_cost = distance * kilometre_cost + visit_input * fixed_cost
        return distance, minutes, direct_cost

    outputs = kernel(
        jnp.asarray(one_way_km, dtype=jnp.float64),
        jnp.asarray(one_way_minutes, dtype=jnp.float64),
        jnp.asarray(visits, dtype=jnp.float64),
        jnp.asarray(cost_per_km, dtype=jnp.float64),
        jnp.asarray(fixed_cost_per_visit, dtype=jnp.float64),
    )
    return tuple(np.asarray(value) for value in outputs)  # type: ignore[return-value]


def differential_check(*, seed: int = 0, size: int = 1024, tolerance: float = 1e-10) -> float:
    """Return the maximum absolute JAX-versus-NumPy error."""
    if size <= 0:
        raise ValueError("Differential check size must be positive")
    rng = np.random.default_rng(seed)
    inputs = (
        rng.uniform(0.0, 500.0, size),
        rng.uniform(0.0, 600.0, size),
        rng.uniform(0.0, 30.0, size),
        rng.uniform(0.0, 2.0, size),
        rng.uniform(0.0, 100.0, size),
    )
    reference = course_travel_numpy(*inputs)
    accelerated = course_travel_jax(*inputs)
    maximum = max(float(np.max(np.abs(left - right))) for left, right in zip(reference, accelerated, strict=True))
    if maximum > tolerance:
        raise AssertionError(f"JAX differential error {maximum} exceeds tolerance {tolerance}")
    return maximum
