"""Transparent multicriteria decision analysis and stochastic acceptability."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class McdaResult:
    """Deterministic weighted-sum MCDA result."""

    scores: np.ndarray
    ranking: np.ndarray
    normalised_matrix: np.ndarray


@dataclass(frozen=True, slots=True)
class SmaaResult:
    """Stochastic multicriteria acceptability outputs."""

    rank_acceptability: np.ndarray
    first_rank_probability: np.ndarray
    expected_rank: np.ndarray
    weight_samples: np.ndarray


def normalise_matrix(matrix: np.ndarray, *, minimise: np.ndarray) -> np.ndarray:
    """Min-max normalise criteria to [0, 1], where higher is preferred."""
    if matrix.ndim != 2:
        raise ValueError("Criteria matrix must be two-dimensional")
    if minimise.shape != (matrix.shape[1],):
        raise ValueError("Direction vector must match the number of criteria")
    lower = np.min(matrix, axis=0)
    upper = np.max(matrix, axis=0)
    span = upper - lower
    safe_span = np.where(span == 0, 1.0, span)
    benefit = (matrix - lower) / safe_span
    benefit[:, minimise] = 1.0 - benefit[:, minimise]
    benefit[:, span == 0] = 1.0
    return benefit


def weighted_sum(
    matrix: np.ndarray,
    weights: np.ndarray,
    *,
    minimise: np.ndarray,
) -> McdaResult:
    """Score alternatives with explicit, normalised weights."""
    if weights.shape != (matrix.shape[1],):
        raise ValueError("Weights must match the number of criteria")
    if np.any(weights < 0) or float(weights.sum()) <= 0:
        raise ValueError("Weights must be non-negative with a positive sum")
    normalised_weights = weights / weights.sum()
    normalised = normalise_matrix(matrix, minimise=minimise)
    scores = normalised @ normalised_weights
    ranking = np.argsort(-scores, kind="stable")
    return McdaResult(scores=scores, ranking=ranking, normalised_matrix=normalised)


def stochastic_acceptability(
    matrix: np.ndarray,
    *,
    minimise: np.ndarray,
    draws: int = 10_000,
    concentration: np.ndarray | None = None,
    seed: int = 0,
) -> SmaaResult:
    """Estimate rank acceptability over broad Dirichlet weight uncertainty."""
    if draws <= 0:
        raise ValueError("Draws must be positive")
    criteria = matrix.shape[1]
    alpha = np.ones(criteria) if concentration is None else concentration.astype(float)
    if alpha.shape != (criteria,) or np.any(alpha <= 0):
        raise ValueError("Dirichlet concentration must be positive and match criteria")
    rng = np.random.default_rng(seed)
    weights = rng.dirichlet(alpha, size=draws)
    normalised = normalise_matrix(matrix, minimise=minimise)
    scores = weights @ normalised.T
    orders = np.argsort(-scores, axis=1, kind="stable")
    alternatives = matrix.shape[0]
    ranks = np.empty_like(orders)
    row_index = np.arange(draws)[:, None]
    ranks[row_index, orders] = np.arange(alternatives)[None, :]
    acceptability = np.zeros((alternatives, alternatives), dtype=float)
    for alternative in range(alternatives):
        acceptability[alternative] = (
            np.bincount(ranks[:, alternative], minlength=alternatives) / draws
        )
    return SmaaResult(
        rank_acceptability=acceptability,
        first_rank_probability=acceptability[:, 0],
        expected_rank=(acceptability * (np.arange(alternatives) + 1)).sum(axis=1),
        weight_samples=weights,
    )
