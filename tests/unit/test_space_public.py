from scripts.check_space_public import probe


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

    monkeypatch.setattr("scripts.check_space_public.urlopen", lambda *_args, **_kwargs: Response())
    receipt = probe("https://example.test/index.html")
    assert receipt["status"] == "passed"
    assert len(receipt["body_sha256"]) == 64
