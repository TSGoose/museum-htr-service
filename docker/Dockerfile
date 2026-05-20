FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
ARG INSTALL_OCR=false
RUN if [ "$INSTALL_OCR" = "true" ]; then \
      uv pip install --system -e ".[ocr]" --group dev; \
    else \
      uv pip install --system -e . --group dev; \
    fi

FROM base AS runtime
COPY . .
