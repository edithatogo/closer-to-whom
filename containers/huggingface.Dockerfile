# syntax=docker/dockerfile:1.7
FROM python:3.15-slim@sha256:2da676046630d7bf14c6764ae1143dc7fa0377a53f94bf5a642f0b214aca5bce AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy
WORKDIR /build
COPY containers/uv-requirements.txt /tmp/uv-requirements.txt
RUN python -m pip install --no-cache-dir --require-hashes -r /tmp/uv-requirements.txt && rm /tmp/uv-requirements.txt
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN uv build && WHEEL=$(ls dist/*.whl) && uv pip install --system --target /install "${WHEEL}" dash plotly gunicorn

FROM python:3.15-slim@sha256:2da676046630d7bf14c6764ae1143dc7fa0377a53f94bf5a642f0b214aca5bce AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    CTW_RESULT_DIR=/app/artifacts/demo
RUN useradd --create-home --uid 1000 appuser
WORKDIR /app
COPY --from=builder /install /usr/local/lib/python3.14/site-packages
COPY app.py ./
COPY artifacts ./artifacts
RUN mkdir -p /app/artifacts/demo && chown -R appuser:appuser /app/artifacts
USER appuser
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860', timeout=3)"
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--threads", "4", "--timeout", "120", "app:server"]
