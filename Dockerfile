# syntax=docker/dockerfile:1.7
FROM python:3.12-slim
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
RUN python -m pip install --no-cache-dir uv
COPY . .
RUN uv sync --frozen --all-extras
ENTRYPOINT ["uv", "run", "closer-to-whom"]
CMD ["doctor"]
