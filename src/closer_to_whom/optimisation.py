"""Transparent location-allocation and multiobjective optimisation."""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass(frozen=True, slots=True)
class LocationSolution:
    """One location-allocation solution."""

    selected_indices: tuple[int, ...]
    assignment_indices: tuple[int, ...]
    objective_value: float
    objective: str
    optimal: bool
    solver: str


@dataclass(frozen=True, slots=True)
class ParetoPoint:
    """One non-dominated configuration and its objectives."""

    label: str
    objectives: tuple[float, ...]
    payload: object | None = None


def _validate_problem(costs: np.ndarray, demand_weights: np.ndarray, site_count: int) -> None:
    if costs.ndim != 2:
        raise ValueError("Costs must be a two-dimensional demand-by-site matrix")
    if demand_weights.ndim != 1 or demand_weights.shape[0] != costs.shape[0]:
        raise ValueError("Demand weights must match the number of demand rows")
    if np.any(costs < 0) or np.any(demand_weights < 0):
        raise ValueError("Costs and weights must be non-negative")
    if not 1 <= site_count <= costs.shape[1]:
        raise ValueError("Site count must be between one and the number of candidate sites")
    if float(demand_weights.sum()) <= 0:
        raise ValueError("Total demand weight must be positive")


def _evaluate_subset(
    costs: np.ndarray,
    demand_weights: np.ndarray,
    subset: tuple[int, ...],
    objective: Literal["p_median", "p_center"],
) -> tuple[float, tuple[int, ...]]:
    sub_costs = costs[:, subset]
    local_assignments = np.argmin(sub_costs, axis=1)
    assignment = tuple(subset[index] for index in local_assignments.tolist())
    minimum = np.min(sub_costs, axis=1)
    if objective == "p_median":
        value = float(np.dot(minimum, demand_weights))
    else:
        positive = demand_weights > 0
        value = float(np.max(minimum[positive]))
    return value, assignment


def solve_location_allocation(
    costs: np.ndarray,
    demand_weights: np.ndarray,
    *,
    site_count: int,
    objective: Literal["p_median", "p_center"] = "p_median",
    max_enumerations: int = 500_000,
) -> LocationSolution:
    """Solve small and medium location problems exactly by deterministic enumeration.

    Larger production problems should use the Arrow-compatible HiGHS/JuMP adapter. Exact
    enumeration is retained as a solver-independent oracle for differential testing.
    """
    _validate_problem(costs, demand_weights, site_count)
    combinations = math.comb(costs.shape[1], site_count)
    if combinations > max_enumerations:
        raise ValueError(
            f"Problem requires {combinations:,} subsets; use the HiGHS or JuMP backend"
        )
    best_subset: tuple[int, ...] | None = None
    best_assignment: tuple[int, ...] | None = None
    best_value = math.inf
    for subset in itertools.combinations(range(costs.shape[1]), site_count):
        value, assignment = _evaluate_subset(costs, demand_weights, subset, objective)
        if value < best_value - 1e-12:
            best_value = value
            best_subset = subset
            best_assignment = assignment
    if best_subset is None or best_assignment is None:  # pragma: no cover - validated non-empty
        raise RuntimeError("No feasible location solution")
    return LocationSolution(
        selected_indices=best_subset,
        assignment_indices=best_assignment,
        objective_value=best_value,
        objective=objective,
        optimal=True,
        solver="enumeration-oracle",
    )


def maximal_coverage(
    costs: np.ndarray,
    demand_weights: np.ndarray,
    *,
    site_count: int,
    threshold: float,
    max_enumerations: int = 500_000,
) -> LocationSolution:
    """Maximise weighted demand within an explicit travel-cost threshold."""
    _validate_problem(costs, demand_weights, site_count)
    if threshold < 0:
        raise ValueError("Coverage threshold must be non-negative")
    combinations = math.comb(costs.shape[1], site_count)
    if combinations > max_enumerations:
        raise ValueError("Coverage problem exceeds enumeration oracle limit")
    best_coverage = -1.0
    best_subset: tuple[int, ...] | None = None
    best_assignment: tuple[int, ...] | None = None
    for subset in itertools.combinations(range(costs.shape[1]), site_count):
        selected = costs[:, subset]
        minimum = np.min(selected, axis=1)
        coverage = float(demand_weights[minimum <= threshold].sum())
        if coverage > best_coverage + 1e-12:
            best_coverage = coverage
            local = np.argmin(selected, axis=1)
            best_assignment = tuple(subset[index] for index in local.tolist())
            best_subset = subset
    if best_subset is None or best_assignment is None:  # pragma: no cover
        raise RuntimeError("No feasible coverage solution")
    return LocationSolution(
        selected_indices=best_subset,
        assignment_indices=best_assignment,
        objective_value=best_coverage,
        objective="maximal_coverage",
        optimal=True,
        solver="enumeration-oracle",
    )


def greedy_p_median(
    costs: np.ndarray,
    demand_weights: np.ndarray,
    *,
    site_count: int,
) -> LocationSolution:
    """Deterministic scalable heuristic used only when explicitly requested."""
    _validate_problem(costs, demand_weights, site_count)
    selected: list[int] = []
    remaining = set(range(costs.shape[1]))
    current = np.full(costs.shape[0], np.inf)
    for _ in range(site_count):
        candidate_values = []
        for candidate in sorted(remaining):
            proposed = np.minimum(current, costs[:, candidate])
            candidate_values.append((float(np.dot(proposed, demand_weights)), candidate, proposed))
        value, chosen, proposed = min(candidate_values, key=lambda item: (item[0], item[1]))
        del value
        selected.append(chosen)
        remaining.remove(chosen)
        current = proposed
    assignments_local = np.argmin(costs[:, selected], axis=1)
    assignments = tuple(selected[index] for index in assignments_local.tolist())
    return LocationSolution(
        selected_indices=tuple(selected),
        assignment_indices=assignments,
        objective_value=float(np.dot(current, demand_weights)),
        objective="p_median",
        optimal=False,
        solver="deterministic-greedy",
    )


def pareto_frontier(
    points: tuple[ParetoPoint, ...], *, minimise: tuple[bool, ...]
) -> tuple[ParetoPoint, ...]:
    """Return non-dominated points for mixed minimise/maximise objectives."""
    if not points:
        return ()
    dimension = len(points[0].objectives)
    if len(minimise) != dimension:
        raise ValueError("Objective direction count does not match point dimension")
    if any(len(point.objectives) != dimension for point in points):
        raise ValueError("All Pareto points must have the same dimension")

    transformed = [
        tuple(value if minimise[index] else -value for index, value in enumerate(point.objectives))
        for point in points
    ]
    keep: list[ParetoPoint] = []
    for index, point in enumerate(points):
        target = transformed[index]
        dominated = False
        for other_index, other in enumerate(transformed):
            if other_index == index:
                continue
            weakly_better = all(
                left <= right + 1e-12 for left, right in zip(other, target, strict=True)
            )
            strictly_better = any(
                left < right - 1e-12 for left, right in zip(other, target, strict=True)
            )
            if weakly_better and strictly_better:
                dominated = True
                break
        if not dominated:
            keep.append(point)
    return tuple(sorted(keep, key=lambda item: item.label))
