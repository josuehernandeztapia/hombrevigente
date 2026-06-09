#!/bin/sh
set -eu

cd /app

INDEX_PATH="${HV_EMBEDDINGS_INDEX:-/data/embeddings_local.json}"
STATES_DIR="${HV_BETA_STATES_DIR:-/data/beta_states}"
LOG_PATH="${HV_DECISION_LOG_PATH:-/data/decision_log.jsonl}"
mkdir -p "$(dirname "$INDEX_PATH")" "$STATES_DIR" "$(dirname "$LOG_PATH")"

# Estado operativo: hv_beta_states en Postgres es SSOT (Guía).
# Directorio útil para fallback files + índice + logs.
echo "[entrypoint] HV_STATE_PERSISTENCE=${HV_STATE_PERSISTENCE:-files} (postgres recomendado en prod)"

# Migración antes de embed/pgvector: tablas SSOT listas pronto; health puede pasar tras uvicorn.
if [ -n "${HV_DATABASE_URL:-}" ]; then
  echo "[entrypoint] apply migration 002 (hv_beta_states + hv_agent_traces)"
  python -c "from pgvector_retrieval import run_migration; run_migration('migrations/002_hv_beta_states.sql')" || \
    echo "[entrypoint] WARN: migration 002 failed — state/traces may be unavailable"
fi

EMBEDDED_NEW=0
if [ -n "${OPENAI_API_KEY:-}" ]; then
  echo "[entrypoint] sync embeddings → ${INDEX_PATH}"
  python embed_kb_local.py --source all --output "${INDEX_PATH}"
  if [ -f "${INDEX_PATH}" ]; then
    EMBEDDED_NEW=$(python -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('stats',{}).get('embedded_new',0))" "${INDEX_PATH}")
  fi
  if [ "${HV_RETRIEVAL_BACKEND:-json}" = "pgvector" ] && [ -n "${HV_DATABASE_URL:-}" ]; then
    if [ "${HV_FORCE_PGVECTOR_SYNC:-0}" = "1" ] || [ "${EMBEDDED_NEW}" != "0" ]; then
      echo "[entrypoint] sync pgvector (embedded_new=${EMBEDDED_NEW})"
      python embed_kb_pgvector.py --from-json "${INDEX_PATH}" --trigger fly-entrypoint || \
        echo "[entrypoint] WARN: pgvector sync failed — json fallback active"
    else
      echo "[entrypoint] skip pgvector sync (embedded_new=0; HV_FORCE_PGVECTOR_SYNC=1 to force)"
    fi
  fi
else
  echo "[entrypoint] WARN: OPENAI_API_KEY unset"
fi

if [ ! -f "${INDEX_PATH}" ]; then
  echo "[entrypoint] WARN: index missing — /api/health will be degraded"
fi

exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8080}"