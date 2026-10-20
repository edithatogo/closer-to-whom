# syntax=docker/dockerfile:1.7
FROM python:3.15-slim@sha256:2da676046630d7bf14c6764ae1143dc7fa0377a53f94bf5a642f0b214aca5bce
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
ENV UV_CACHE_DIR=/tmp/uv-cache
RUN addgroup --system appuser && ++    adduser --system --uid 1000 --ingroup appuser appuser && ++    mkdir -p /tmp/uv-cache && ++    chown -R appuser:appuser /tmp/uv-cache
COPY containers/uv-requirements.txt /tmp/uv-requirements.txt
RUN python -m pip install --no-cache-dir --require-hashes -r /tmp/uv-requirements.txt && rm /tmp/uv-requirements.txt
COPY --chown=appuser:appuser pyproject.toml README.md LICENSE uv.lock ./
COPY --chown=appuser:appuser src ./src
RUN uv sync --frozen --all-extras
USER appuser
ENTRYPOINT ["uv", "run", "closer-to-whom"]
CMD ["doctor"]
