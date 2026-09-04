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
  echo "[entrypoint] apply migration 003 (hv_pending_actions — idempotencia C1)"
  python -c "from pgvector_retrieval import run_migration; run_migration('migrations/003_hv_pending_actions.sql')" || \
    echo "[entrypoint] WARN: migration 003 failed — proactive idempotency ledger unavailable"
  echo "[entrypoint] apply migration 004 (hv_decision_log — memoria episódica SSOT)"
  python -c "from pgvector_retrieval import run_migration; run_migration('migrations/004_hv_decision_log.sql')" || \
    echo "[entrypoint] WARN: migration 004 failed — decision log queda solo en JSONL local"
fi

EMBEDDED_NEW=0
EMBED_OK=0
if [ -n "${OPENAI_API_KEY:-}" ]; then
  echo "[entrypoint] sync embeddings → ${INDEX_PATH}"
  # NO fatal. Con `set -e`, un fallo aquí mataba el contenedor antes de uvicorn:
  # el 03-sep-2026 OpenAI devolvió 429 insufficient_quota (sin créditos) y la
  # máquina entró en crash-loop hasta el máximo de reinicios — prod caída por
  # un problema de facturación, con el índice anterior intacto en /data
  # (embed_kb_local escribe el archivo solo al final, así que un crash no lo
  # corrompe). Un sync fallido debe degradar (índice viejo, health lo reporta),
  # nunca tumbar el API: onboarding, handoff, admin y /api/v1 no necesitan OpenAI.
  if python embed_kb_local.py --source all --output "${INDEX_PATH}"; then
    EMBED_OK=1
  else
    echo "[entrypoint] WARN: embeddings sync FAILED (¿OpenAI sin créditos/red?) — sirviendo el índice existente si lo hay"
  fi
  if [ -f "${INDEX_PATH}" ] && [ "${EMBED_OK}" = "1" ]; then
    EMBEDDED_NEW=$(python -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('stats',{}).get('embedded_new',0))" "${INDEX_PATH}" 2>/dev/null || echo 0)
  fi
  if [ "${EMBED_OK}" = "1" ] && [ "${HV_RETRIEVAL_BACKEND:-json}" = "pgvector" ] && [ -n "${HV_DATABASE_URL:-}" ]; then
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