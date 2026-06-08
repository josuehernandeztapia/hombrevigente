#!/usr/bin/env bash
# Bootstrap Fly app hv-rag-api (secrets desde rag-bot/.env, sin imprimir valores).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

APP="${FLY_APP:-hv-rag-api}"
ORG="${FLY_ORG:-personal}"

if ! flyctl apps list --json | python3 -c "import json,sys; apps=[a['Name'] for a in json.load(sys.stdin)]; sys.exit(0 if '${APP}' in apps else 1)"; then
  echo "Creating Fly app ${APP}..."
  flyctl apps create "${APP}" --org "${ORG}"
fi

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

SECRETS=()
[ -n "${OPENAI_API_KEY:-}" ] && SECRETS+=("OPENAI_API_KEY=${OPENAI_API_KEY}")
[ -n "${HV_ADMIN_PIN:-}" ] && SECRETS+=("HV_ADMIN_PIN=${HV_ADMIN_PIN}")

if [ "${#SECRETS[@]}" -gt 0 ]; then
  echo "Setting Fly secrets (${#SECRETS[@]} keys) on ${APP}..."
  flyctl secrets set "${SECRETS[@]}" --app "${APP}"
else
  echo "WARN: no OPENAI_API_KEY/HV_ADMIN_PIN in .env — set secrets manually:"
  echo "  fly secrets set OPENAI_API_KEY=... HV_ADMIN_PIN=... --app ${APP}"
fi

if ! flyctl volumes list --app "${APP}" --json | python3 -c "import json,sys; v=json.load(sys.stdin); sys.exit(0 if any(x.get('Name')=='hv_rag_data' for x in v) else 1)" 2>/dev/null; then
  echo "Creating volume hv_rag_data (1GB) in dfw..."
  flyctl volumes create hv_rag_data --region dfw --size 1 --app "${APP}" --yes
fi

echo "Deploying ${APP}..."
flyctl deploy --app "${APP}" --wait-timeout 600

echo "Health:"
flyctl checks list --app "${APP}" || true
echo "URL: https://${APP}.fly.dev/api/health"