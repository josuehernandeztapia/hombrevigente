#!/bin/sh
set -eu

cd /app

INDEX_PATH="${HV_EMBEDDINGS_INDEX:-/data/embeddings_local.json}"
mkdir -p "$(dirname "$INDEX_PATH")"

if [ -n "${OPENAI_API_KEY:-}" ]; then
  echo "[entrypoint] sync embeddings → ${INDEX_PATH}"
  python embed_kb_local.py --source all --output "${INDEX_PATH}"
else
  echo "[entrypoint] WARN: OPENAI_API_KEY unset"
fi

if [ ! -f "${INDEX_PATH}" ]; then
  echo "[entrypoint] WARN: index missing — /api/health will be degraded"
fi

exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8080}"