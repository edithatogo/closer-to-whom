from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_primary_docker_context_excludes_local_secrets_and_state() -> None:
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
    required_patterns = {
        ".env",
        ".env.*",
        "*.pem",
        "*.key",
        "credentials*",
        ".secrets",
        ".ssh",
        "*.sqlite*",
    }
    assert required_patterns <= set(dockerignore.splitlines())


def test_primary_dockerfile_uses_non_root_runtime_and_bounded_uv_cache() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "adduser --system" in dockerfile
    assert "USER appuser" in dockerfile
    assert "UV_CACHE_DIR=/tmp/uv-cache" in dockerfile
    assert "COPY . ." not in dockerfile
    assert "COPY --chown=appuser:appuser pyproject.toml README.md LICENSE uv.lock ./" in dockerfile
    assert "COPY --chown=appuser:appuser src ./src" in dockerfile
