import hashlib
import importlib.util
from pathlib import Path


def _module():
    path = Path(__file__).parents[2] / "scripts/generate_sbom.py"
    spec = importlib.util.spec_from_file_location("generate_sbom", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sbom_binds_exact_artifact_digest(tmp_path: Path) -> None:
    artifact = tmp_path / "example.whl"
    artifact.write_bytes(b"wheel-content")
    payload = _module().build_sbom(artifact)
    properties = {item["name"]: item["value"] for item in payload["properties"]}
    assert (
        properties["closer-to-whom:artifact:sha256"] == hashlib.sha256(b"wheel-content").hexdigest()
    )
    assert properties["closer-to-whom:artifact:type"] == "python-wheel"
    assert "artifact" not in payload["metadata"]
