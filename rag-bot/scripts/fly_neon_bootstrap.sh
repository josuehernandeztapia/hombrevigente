#!/usr/bin/env bash
# Neon pgvector para HV — usa credenciales CMU local (.env) SOLO lectura.
# Aplica tablas hv_* en la misma Neon; secrets solo en hv-rag-api (nunca cmu-originacion).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CMU_ENV="${CMU_ENV_FILE:-/Users/juanjosuehernandeztapia/cmu-decision/.env}"
APP="${FLY_APP:-hv-rag-api}"

if [ ! -f "$CMU_ENV" ]; then
  echo "ERROR: CMU .env no encontrado en $CMU_ENV" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$CMU_ENV"
set +a

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL vacío en CMU .env" >&2
  exit 1
fi

export HV_DATABASE_URL="${HV_DATABASE_URL:-$DATABASE_URL}"
cd "$ROOT"

pip install -q -r requirements-rag-pgvector.txt

echo "[1/4] Migración hv_kb_chunks (schema aislado, prefijo hv_*)..."
python embed_kb_pgvector.py --migrate-only

echo "[2/4] Sync embeddings JSON → pgvector..."
python embed_kb_pgvector.py --from-json knowledge_base/embeddings_local.json --trigger fly-bootstrap

echo "[3/4] Fly secrets en ${APP} (no toca cmu-originacion)..."
flyctl secrets set \
  "HV_DATABASE_URL=${HV_DATABASE_URL}" \
  HV_RETRIEVAL_BACKEND=pgvector \
  --app "${APP}"

if [ -n "${ADMIN_OBS_PIN:-}" ] && [ -z "${HV_ADMIN_PIN:-}" ]; then
  flyctl secrets set "HV_ADMIN_PIN=${ADMIN_OBS_PIN}" --app "${APP}"
fi

echo "[4/4] Redeploy ${APP}..."
flyctl deploy --app "${APP}" --wait-timeout 600

echo "Smoke (pgvector):"
curl -sS "https://${APP}.fly.dev/api/health"
echo ""
curl -sS "https://${APP}.fly.dev/rag/query?q=homocisteina%20TMG&use_llm=false" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('backend ok:', d.get('chunks_used',0)>0, 'path:', d.get('gate_path'))"