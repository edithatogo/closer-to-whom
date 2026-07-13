# syntax=docker/dockerfile:1.7
FROM python:3.14-slim@sha256:b877e50bd90de10af8d82c57a022fc2e0dc731c5320d762a27986facfc3355c1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
RUN python -m pip install --no-cache-dir uv
COPY . .
RUN uv sync --frozen --all-extras
ENTRYPOINT ["uv", "run", "closer-to-whom"]
CMD ["doctor"]
