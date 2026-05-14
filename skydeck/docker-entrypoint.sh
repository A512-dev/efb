#!/bin/bash
set -e

# ── wait for database ─────────────────────────────────────
MAX_RETRIES="${DB_WAIT_RETRIES:-30}"
RETRY_INTERVAL="${DB_WAIT_INTERVAL:-2}"

echo "[entrypoint] Verifying database readiness …"
for i in $(seq 1 "$MAX_RETRIES"); do
    if python -c "
from sqlalchemy import create_engine, text
from app.core.config import settings
e = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
with e.connect() as c:
    c.execute(text('SELECT 1'))
" 2>/dev/null; then
        echo "[entrypoint] Database is ready."
        break
    fi

    if [ "$i" = "$MAX_RETRIES" ]; then
        echo "[entrypoint] Database unreachable after $((MAX_RETRIES * RETRY_INTERVAL))s — aborting."
        exit 1
    fi

    echo "[entrypoint]   attempt $i/$MAX_RETRIES …"
    sleep "$RETRY_INTERVAL"
done

# ── run migrations ─────────────────────────────────────────
echo "[entrypoint] Running Alembic migrations …"
alembic upgrade head

# ── optional seed ──────────────────────────────────────────
if [ "${RUN_SEED}" = "true" ]; then
    echo "[entrypoint] Seeding database …"
    python -m app.seed
fi

# ── start server ───────────────────────────────────────────
echo "[entrypoint] Starting uvicorn on port ${BACKEND_PORT:-8000} …"
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${BACKEND_PORT:-8000}" \
    --workers "${UVICORN_WORKERS:-1}" \
    --log-level "${LOG_LEVEL:-info}"
