import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "inspect_stats_nz_structure",
    Path(__file__).parents[2] / "scripts" / "inspect_stats_nz_structure.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
inspect_structure = _MODULE.inspect_structure


def test_inspect_structure_preserves_code_lists_and_labels(tmp_path: Path) -> None:
    source = tmp_path / "structure.xml"
    source.write_text(
        '<Structure xmlns="urn:test"><Codelist id="AREA"><Name>Area</Name><Code id="A1"><Name>Example</Name></Code></Codelist></Structure>',
        encoding="utf-8",
    )
    result = inspect_structure(source)
    assert result["codelist_count"] == 1
    assert result["codelists"][0]["codes"] == [{"id": "A1", "names": ["Example"]}]
