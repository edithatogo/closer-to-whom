# syntax=docker/dockerfile:1.7
FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928
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
