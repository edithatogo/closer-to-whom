import json
from pathlib import Path


def test_static_space_is_generated_and_no_javascript_is_required() -> None:
    root = Path(__file__).parents[2]
    page = (root / "spaces/static/index.html").read_text(encoding="utf-8")
    manifest = json.loads((root / "spaces/static/provenance.json").read_text(encoding="utf-8"))
    assert "Skip to main content" in page
    assert '<main id="main">' in page
    assert "<table>" in page
    assert manifest["javascript_required"] is False
    assert manifest["aggregate_only"] is True
