FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 TL_WEB_ROOT=/app/web
WORKDIR /app
RUN useradd --create-home --uid 10001 tenderlens
COPY pyproject.toml README.md ./
COPY tenderlens ./tenderlens
COPY web ./web
RUN pip install ".[testnet]"
USER 10001:10001
EXPOSE 8787 8091
