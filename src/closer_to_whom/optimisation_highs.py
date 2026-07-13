"""MILP location-allocation using SciPy's HiGHS interface."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

type FloatArray = npt.NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class PMedianMilpResult:
    """Auditable p-median solution."""

    selected_indices: tuple[int, ...]
    assignments: tuple[int, ...]
    objective: float
    optimal: bool
    solver_message: str


def solve_p_median_milp(
    costs: FloatArray,
    demand: FloatArray,
    facilities_to_select: int,
    *,
    time_limit_seconds: float = 60.0,
) -> PMedianMilpResult:
    """Solve binary p-median with origin assignment and facility-open variables."""

    matrix = np.asarray(costs, dtype=np.float64)
    weights = np.asarray(demand, dtype=np.float64)
    if matrix.ndim != 2:
        raise ValueError("costs must be a two-dimensional origin x facility matrix")
    origins, facilities = matrix.shape
    if weights.shape != (origins,):
        raise ValueError("demand must contain one non-negative value per origin")
    if not np.isfinite(matrix).all() or (matrix < 0).any():
        raise ValueError("costs must be finite and non-negative")
    if not np.isfinite(weights).all() or (weights < 0).any():
        raise ValueError("demand must be finite and non-negative")
    if not 1 <= facilities_to_select <= facilities:
        raise ValueError("facilities_to_select must be between 1 and candidate count")

    assignment_variables = origins * facilities
    total_variables = assignment_variables + facilities
    objective = np.zeros(total_variables, dtype=np.float64)
    objective[:assignment_variables] = (matrix * weights[:, None]).ravel()

    rows = origins + assignment_variables + 1
    constraints = lil_matrix((rows, total_variables), dtype=np.float64)
    lower = np.full(rows, -np.inf, dtype=np.float64)
    upper = np.full(rows, np.inf, dtype=np.float64)

    row = 0
    # Every origin is assigned exactly once.
    for origin in range(origins):
        start = origin * facilities
        constraints[row, start : start + facilities] = 1.0
        lower[row] = 1.0
        upper[row] = 1.0
        row += 1

    # x_ij <= y_j.
    for origin in range(origins):
        for facility in range(facilities):
            x_index = origin * facilities + facility
            y_index = assignment_variables + facility
            constraints[row, x_index] = 1.0
            constraints[row, y_index] = -1.0
            upper[row] = 0.0
            row += 1

    # Select exactly p facilities.
    constraints[row, assignment_variables:] = 1.0
    lower[row] = float(facilities_to_select)
    upper[row] = float(facilities_to_select)

    result = milp(
        c=objective,
        integrality=np.ones(total_variables, dtype=np.int8),
        bounds=Bounds(np.zeros(total_variables), np.ones(total_variables)),  # pyright: ignore[reportArgumentType]
        constraints=LinearConstraint(constraints.tocsr(), lower, upper),  # pyright: ignore[reportArgumentType]
        options={"time_limit": time_limit_seconds, "presolve": True},
    )
    if result.x is None:
        raise RuntimeError(f"p-median solver returned no solution: {result.message}")
    selected = tuple(
        int(index) for index, value in enumerate(result.x[assignment_variables:]) if value > 0.5
    )
    assignment_matrix = result.x[:assignment_variables].reshape(origins, facilities)
    assignments = tuple(int(index) for index in assignment_matrix.argmax(axis=1))
    return PMedianMilpResult(
        selected_indices=selected,
        assignments=assignments,
        objective=float(result.fun),
        optimal=bool(result.success),
        solver_message=str(result.message),
    )
