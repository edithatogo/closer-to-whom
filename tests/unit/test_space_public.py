import importlib.util
from pathlib import Path


def _module():
    path = Path(__file__).parents[2] / "scripts/check_space_public.py"
    spec = importlib.util.spec_from_file_location("check_space_public", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_space_probe_receipt_is_content_addressed(monkeypatch) -> None:
    class Response:
        status = 200

        class Headers:
            @staticmethod
            def get(name: str, default: str = "") -> str:
                return "text/html" if name == "Content-Type" else default

        headers = Headers()

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        @staticmethod
        def read() -> bytes:
            return b"<h1>Closer to whom</h1><p>Research boundary: aggregate</p>"

    module = _module()
    monkeypatch.setattr(module, "urlopen", lambda *_args, **_kwargs: Response())
    receipt = module.probe("https://example.test/index.html")
    assert receipt["status"] == "passed"
    assert len(receipt["body_sha256"]) == 64
