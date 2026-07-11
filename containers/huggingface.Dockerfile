# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy
WORKDIR /build
RUN python -m pip install --no-cache-dir uv
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN uv build && WHEEL=$(ls dist/*.whl) && uv pip install --system --target /install "${WHEEL}" dash plotly gunicorn

FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    CTW_RESULT_DIR=/app/artifacts/demo
RUN useradd --create-home --uid 1000 appuser
WORKDIR /app
COPY --from=builder /install /usr/local/lib/python3.12/site-packages
COPY app.py ./
COPY artifacts/demo ./artifacts/demo
USER appuser
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860', timeout=3)"
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--threads", "4", "--timeout", "120", "app:server"]
