# ── Stage 1: build dependencies ────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Stage 2: production runtime ────────────────────────────
FROM python:3.12-slim AS runtime

# System dependencies for reportlab font rendering and pypdf.
# libfreetype6: TrueType/OpenType rasterizer used by reportlab
# libjpeg62-turbo: JPEG codec for embedded images
# fontconfig + fonts-dejavu-core: fallback fonts if PDF references
#   a non-standard face during watermark overlay generation
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libfreetype6 \
        libjpeg62-turbo \
        fontconfig \
        fonts-dejavu-core && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY alembic.ini .
COPY alembic/ alembic/
COPY app/ app/
COPY docker-entrypoint.sh .

RUN sed -i 's/\r$//' docker-entrypoint.sh && chmod +x docker-entrypoint.sh

RUN mkdir -p /app/storage/manuals /app/storage/submissions && \
    chown -R nobody:nogroup /app/storage

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
