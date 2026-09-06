#!/bin/sh
# Container entrypoint for the Swaddle API.
#
# Set RUN_MIGRATIONS=1 on platforms without a separate pre-deploy hook so the
# container upgrades the schema before serving. Railway runs the migration as a
# preDeployCommand instead (see railway.json), so it leaves this at 0.
set -eu

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  echo "Running database migrations..."
  alembic -c alembic.ini upgrade head
fi

exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --log-level "${LOG_LEVEL:-info}" \
  --proxy-headers \
  --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-*}"
