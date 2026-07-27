import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

_SPEC = spec_from_file_location(
    "materialize_sa2_true_centroids",
    Path(__file__).parents[2] / "scripts" / "materialize_sa2_true_centroids.py",
)
assert _SPEC and _SPEC.loader
_MODULE = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
Cell = _MODULE.Cell
fetch_all = _MODULE.fetch_all


def test_cell_subdivision_preserves_bounds_and_reduces_radius() -> None:
    cell = Cell(174.0, -37.0, 175.0, -36.0)
    children = cell.subdivide()
    assert len(children) == 4
    assert all(child.depth == 1 for child in children)
    assert all(child.radius_metres < cell.radius_metres for child in children)
    assert min(child.west for child in children) == cell.west
    assert max(child.east for child in children) == cell.east
    assert min(child.south for child in children) == cell.south
    assert max(child.north for child in children) == cell.north


def test_fetch_all_rejects_unsafe_worker_count() -> None:
    with pytest.raises(ValueError, match="workers"):
        fetch_all("token", getter=lambda _url: {}, workers=0)
