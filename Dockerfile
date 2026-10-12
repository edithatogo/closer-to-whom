# syntax=docker/dockerfile:1.7
FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170
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
