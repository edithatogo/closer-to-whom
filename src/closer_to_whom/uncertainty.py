"""Deterministic, probabilistic, and structural uncertainty tooling."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from scipy import stats
from scipy.stats import qmc

from closer_to_whom.models import UncertaintyParameter

ScalarEvaluator = Callable[[Mapping[str, float]], float]
VectorEvaluator = Callable[[Mapping[str, float]], np.ndarray]


@dataclass(frozen=True, slots=True)
class DsaResult:
    """One-way deterministic sensitivity result."""

    parameter_id: str
    lower_input: float
    upper_input: float
    lower_output: float
    base_output: float
    upper_output: float
    absolute_swing: float


@dataclass(frozen=True, slots=True)
class PsaResult:
    """PSA input draws and corresponding alternative outcomes."""

    parameter_ids: tuple[str, ...]
    draws: np.ndarray
    outcomes: np.ndarray
    method: str
    seed: int


def _uniform_design(draws: int, dimensions: int, *, seed: int, method: str) -> np.ndarray:
    if draws <= 0 or dimensions <= 0:
        raise ValueError("Draw and dimension counts must be positive")
    if method == "pseudo":
        return np.random.default_rng(seed).random((draws, dimensions))
    if method == "latin_hypercube":
        return qmc.LatinHypercube(d=dimensions, seed=seed).random(draws)
    if method == "sobol":
        power = math.ceil(math.log2(draws))
        return qmc.Sobol(d=dimensions, scramble=True, seed=seed).random_base2(power)[:draws]
    raise ValueError(f"Unknown sampling method: {method}")


def _inverse_sample(parameter: UncertaintyParameter, uniforms: np.ndarray) -> np.ndarray:
    epsilon = np.finfo(float).eps
    u = np.clip(uniforms, epsilon, 1.0 - epsilon)
    if parameter.distribution == "fixed":
        return np.full_like(u, parameter.base, dtype=float)
    if parameter.distribution == "uniform":
        assert parameter.lower is not None and parameter.upper is not None
        return parameter.lower + u * (parameter.upper - parameter.lower)
    if parameter.distribution == "beta":
        assert parameter.alpha is not None and parameter.beta is not None
        return stats.beta.ppf(u, parameter.alpha, parameter.beta)
    if parameter.distribution == "gamma":
        assert parameter.shape is not None and parameter.scale is not None
        return stats.gamma.ppf(u, parameter.shape, scale=parameter.scale)
    if parameter.distribution == "lognormal":
        if parameter.lower is None or parameter.upper is None:
            raise ValueError("Lognormal parameters use lower=sigma and upper=scale")
        return stats.lognorm.ppf(u, s=parameter.lower, scale=parameter.upper)
    if parameter.distribution == "normal":
        if parameter.lower is None or parameter.upper is None:
            raise ValueError("Normal parameters use lower=mean and upper=standard deviation")
        return stats.norm.ppf(u, loc=parameter.lower, scale=parameter.upper)
    if parameter.distribution == "discrete":
        cumulative = np.cumsum(np.asarray(parameter.probabilities, dtype=float))
        indices = np.searchsorted(cumulative, u, side="right")
        values = np.asarray(parameter.values, dtype=float)
        return values[np.minimum(indices, len(values) - 1)]
    raise AssertionError("Validated parameter has an unsupported distribution")


def sample_parameters(
    parameters: Sequence[UncertaintyParameter],
    *,
    draws: int,
    seed: int,
    method: str = "sobol",
) -> tuple[tuple[str, ...], np.ndarray]:
    """Sample uncertain parameters using pseudo-random, LHS, or scrambled Sobol designs."""
    if not parameters:
        raise ValueError("At least one uncertainty parameter is required")
    ids = tuple(parameter.parameter_id for parameter in parameters)
    if len(ids) != len(set(ids)):
        raise ValueError("Uncertainty parameter IDs must be unique")
    uniform = _uniform_design(draws, len(parameters), seed=seed, method=method)
    sampled = np.column_stack(
        [_inverse_sample(parameter, uniform[:, index]) for index, parameter in enumerate(parameters)]
    )
    return ids, sampled


def one_way_dsa(
    base_parameters: Mapping[str, float],
    ranges: Mapping[str, tuple[float, float]],
    evaluator: ScalarEvaluator,
) -> tuple[DsaResult, ...]:
    """Run one-way deterministic sensitivity analysis around a base parameter set."""
    base_output = float(evaluator(base_parameters))
    results: list[DsaResult] = []
    for parameter_id in sorted(ranges):
        if parameter_id not in base_parameters:
            raise ValueError(f"DSA range has no base value: {parameter_id}")
        lower, upper = ranges[parameter_id]
        if lower > upper:
            raise ValueError(f"DSA lower bound exceeds upper bound: {parameter_id}")
        lower_values = dict(base_parameters)
        upper_values = dict(base_parameters)
        lower_values[parameter_id] = lower
        upper_values[parameter_id] = upper
        lower_output = float(evaluator(lower_values))
        upper_output = float(evaluator(upper_values))
        results.append(
            DsaResult(
                parameter_id=parameter_id,
                lower_input=lower,
                upper_input=upper,
                lower_output=lower_output,
                base_output=base_output,
                upper_output=upper_output,
                absolute_swing=abs(upper_output - lower_output),
            )
        )
    return tuple(sorted(results, key=lambda item: (-item.absolute_swing, item.parameter_id)))


def run_psa(
    parameters: Sequence[UncertaintyParameter],
    evaluator: VectorEvaluator,
    *,
    draws: int = 4096,
    seed: int = 0,
    method: str = "sobol",
) -> PsaResult:
    """Sample parameters and evaluate all alternatives for each draw."""
    parameter_ids, sampled = sample_parameters(parameters, draws=draws, seed=seed, method=method)
    outputs: list[np.ndarray] = []
    for row in sampled:
        values = dict(zip(parameter_ids, row.tolist(), strict=True))
        outcome = np.asarray(evaluator(values), dtype=float)
        if outcome.ndim != 1:
            raise ValueError("PSA evaluator must return one value per alternative")
        outputs.append(outcome)
    outcomes = np.vstack(outputs)
    if not np.all(np.isfinite(outcomes)):
        raise ValueError("PSA outcomes contain non-finite values")
    return PsaResult(parameter_ids, sampled, outcomes, method, seed)


def percentile_interval(values: np.ndarray, *, level: float = 0.95) -> tuple[float, float]:
    """Return a central percentile interval."""
    if not 0.0 < level < 1.0:
        raise ValueError("Interval level must lie between zero and one")
    alpha = (1.0 - level) / 2.0
    low, high = np.quantile(values, [alpha, 1.0 - alpha])
    return float(low), float(high)
