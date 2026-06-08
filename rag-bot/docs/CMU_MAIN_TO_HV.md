# CMU `origin/main` → HV `rag-bot` — Checklist de portabilidad

**Fuente CMU:** `origin/main` @ `682a8fd` (2026-06-07) — leído con `git show`, **sin checkout** en `cmu-decision`.  
**Rama local CMU intacta:** `feat/uh-promotora-fc-shadow-harness` (no se modificó ni se hizo commit).

### Máxima: no afectar CMU

| Recurso | CMU (intocable) | HV (separado) |
|---------|-----------------|---------------|
| Repo | `cmu-decision` | `hombrevigente/rag-bot` |
| Fly app | `cmu-originacion` | `hv-rag-api` |
| Neon DB | schema/tablas CMU | schema HV propio (`hv_kb_chunks`, etc.) |
| Secrets Fly | solo `cmu-originacion` | solo `hv-rag-api` |
| Patrón | leer con `git show origin/main:...` | portar/adaptar, nunca commit en CMU |

Misma org Fly (`personal`) y misma cuenta Neon **sí** — proyectos/apps/schemas **no** se mezclan.

---

## Leyenda

| Estado | Significado |
|--------|-------------|
| ✅ | Ya portado a HV |
| 🔶 | Parcial / patrón adaptado |
| ⏳ | Pendiente — copiar patrón |
| ⛔ | No portar (dominio CMU/taxis) |

---

## 1. Retrieval & confianza (core RAG)

| CMU (`origin/main`) | HV (`rag-bot`) | Estado | Notas |
|---------------------|----------------|--------|-------|
| `server/agent/retrieval/partes-mercado-retrieval.ts` | `rag_retrieval_local.py` + `pgvector_retrieval.py` | 🔶 | JSON default; `HV_RETRIEVAL_BACKEND=pgvector` |
| `COSINE_HIGH=0.70` / `COSINE_MIN=0.55` (env) | `kb_pipeline.py` | ✅ | Mismos defaults |
| Re-rank `0.7*sim + 0.3*yearMatch` (PR #438) | `_combined_score` 0.7/0.3 tier | 🔶 | HV usa tier E1–E5, no año vehículo |
| `yearMatchScore()` | — | ⏳ | Solo si HV indexa por cohorte/edad en metadata |
| `stripCommandWords` (PR #444) | `query_preprocess.py` | ✅ | `STRIP_PATTERNS` alineado a CMU main |
| `embedQuery` + timeout | `embed_query` | ⏳ | CMU: `withTimeout` 12s — añadir en API |
| Hybrid FTS + ivfflat | `migrations/001_hv_kb_embeddings.sql` | ✅ | Scaffold + `embed_kb_pgvector.py` |
| `formatPartesReply` retrieval-only | `gate_path=escalate` sin LLM | ✅ | Anti-alucinación precios |

---

## 2. NLU & intents (determinista, sin tokens)

| CMU | HV | Estado | Notas |
|-----|-----|--------|-------|
| `precio-refaccion-intent.ts` + `TIPO_PATTERNS` | — | ⛔ | Dominio refacciones taxi |
| Patrón: regex slots → filtros retrieval | `detect_kb_route` + `check_gates` | ✅ | Equivalente HV |
| `server/parsers/nlu-regex.ts` | — | ⏳ | Port selectivo: greeting, continue, docs |
| `intent-confidence.ts` (stakes low/med/high) | `confidence_gate.py` | 🔶 | HV solo RAG path; falta stakes por acción |

---

## 3. Prompts & roles

| CMU | HV | Estado | Notas |
|-----|-----|--------|-------|
| `prompts.ts` + `buildSystemPrompt()` | `prompts.py` | ✅ | |
| `DISCLOSURE_CIFRAS` (cliente) | `DISCLOSURE_LONGEVITY` / `SERVICIOS` | ✅ | |
| Rol `promotora` / `cliente` | Rol `concierge` | ✅ | MVP-0 WhatsApp |
| `VISION_PROMPTS` | — | ⏳ | Cuando HV capture labs/INE en MVP-1 |

---

## 4. Gates & side-effects

| CMU | HV | Estado | Notas |
|-----|-----|--------|-------|
| `confidence-gate.ts` (auto/confirm/escalate) | `confidence_gate.py` | 🔶 | HV: auto/caveat/escalate para RAG |
| `confirmation-flow.ts` (HITL WhatsApp) | — | ⏳ | Agendar cita / enviar protocolo |
| `server/sanity.ts` | gates clínicos Av.2 | ✅ | `check_gates()` |

---

## 5. Eval & regresión

| CMU | HV | Estado | Notas |
|-----|-----|--------|-------|
| `docs/qa/golden-set-llm-eval.md` (120) | `docs/qa/golden-set-hv-rag.md` (20) | ✅ | Expandir a 50+ con tráfico real |
| `scripts/sync-golden-set.py` | `scripts/sync_golden_set.py` | ✅ | |
| `golden-runner.ts` (agente completo) | `golden_runner.py` | 🔶 | HV: gates+retrieval; no runner WhatsApp |
| `golden-set-service.ts` | — | ⏳ | Cargar JSON al boot API |
| `llm-grader-service.ts` | — | ⏳ | Drift semanal post-MVP-0 |

---

## 6. Knowledge Loop

| CMU | HV | Estado | Notas |
|-----|-----|--------|-------|
| `knowledge-gap-detector.ts` | `knowledge_gap_detector.py` | ✅ | CLI + `GET /admin/knowledge/gaps` |
| `admin-knowledge-promote.ts` | `knowledge_promote.py` + API | ✅ | `POST /admin/knowledge/promote` + GET/DELETE pending |
| `knowledge-promotions-pending.json` | `data/knowledge-promotions-pending.json` | ✅ | |
| `process-knowledge-promotions.py` | `scripts/process_knowledge_promotions.py` | ✅ | HV escribe `FAQ_PROMOTED.md` |
| `cron-knowledge-gaps.ts` | `rag-bot-knowledge-gaps.yml` | ✅ | Lunes 16:00 UTC + reporte MD |
| `.github/workflows/auto-embed-knowledge.yml` | `.github/workflows/rag-bot-nightly.yml` | ✅ | Nightly + post-merge KB → embed + `--full` |
| `.github/workflows/process-knowledge-promotions.yml` | `rag-bot-process-promotions.yml` | ✅ | Diario 15:00 UTC → PR |
| — | `.github/workflows/rag-bot-ci.yml` | ✅ | PR: tests + `--gates-only` |

---

## 7. Observabilidad

| CMU | HV | Estado | Notas |
|-----|-----|--------|-------|
| `agent-decision-log.ts` | `decision_log.py` | ✅ | JSONL fail-open |
| `decisionsTaken[]` | `decision_id` + `data/decision_log.jsonl` | ✅ | Por query RAG |
| `?parse=1` debug | `GET/POST /rag/query?parse=1` | ✅ | `api/main.py` |
| `redactForPreview` PII | — | ⏳ | Antes de loguear queries WhatsApp |

---

## 8. Infra & datos

| CMU | HV | Estado | Notas |
|-----|-----|--------|-------|
| `migrations/0030_partes_mercado.sql` | — | ⛔ | Catálogo Aldo |
| `scripts/embed-partes-mercado.py` | `embed_kb_local.py` | 🔶 | Mismo patrón CDC `content_hash` |
| `scripts/ingest-aldo-catalog.py` | — | ⛔ | |
| `fly.toml` + health `/api/health` | `fly.toml` + `rag-bot-fly-deploy.yml` | ✅ | `hv-rag-api`, vol `/data` |
| Feature flags env | thresholds en env | ✅ | `HV_COSINE_HIGH`, `HV_COSINE_MIN` |

---

## 9. Orden de implementación HV (recomendado)

1. ~~Env thresholds~~ ✅
2. ~~STRIP_PATTERNS PR #444~~ ✅
3. ~~`decision_log.py`~~ ✅
4. ~~`knowledge_gap_detector.py`~~ ✅
5. ~~`POST /admin/knowledge/promote`~~ ✅ — PIN + append a pending JSON.
6. ~~GitHub Action~~ ✅ — `rag-bot-ci.yml` (PR) + `rag-bot-nightly.yml` (`--full`).
6b. ~~Knowledge loop crons~~ ✅ — `rag-bot-process-promotions.yml` + `rag-bot-knowledge-gaps.yml`.
7. ~~Neon pgvector~~ ✅ — tablas `hv_*` en Neon CMU; prod `hv-rag-api` con `HV_RETRIEVAL_BACKEND=pgvector`.

---

## 10. Commits CMU relevantes (para `git show` sin checkout)

```bash
cd /Users/juanjosuehernandeztapia/cmu-decision   # solo lectura
git fetch origin
git show origin/main:server/agent/retrieval/partes-mercado-retrieval.ts
git show origin/main:server/agent/intent/precio-refaccion-intent.ts   # stripCommandWords
git show origin/main:server/confidence-gate.ts
git show origin/main:server/agent/services/knowledge-gap-detector.ts
```

| Commit | PR | Qué aporta |
|--------|-----|------------|
| `682a8fd` | #444 | `stripCommandWords` en intent |
| `0c29b92` | #438 | Re-rank año + wire director |
| `e6e5c05` | #437 | Retrieval pgvector fundación |
| `525666e` | #430 | Tabla `partes_mercado` |

---

*Generado sin modificar `cmu-decision`. Para actualizar CMU local: `git checkout main && git pull` (opcional, en branch aparte).*