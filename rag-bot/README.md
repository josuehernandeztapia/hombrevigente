# rag-bot — Knowledge Base + RAG

Pipeline de conocimiento para **ChatVigente** (estética) y **Motor de Recomendación** (longevidad MVP-0).

> Mocks de inversor, generador sintético y backend FastAPI demo → [`../archive/`](../archive/README.md)

---

## Estructura activa

```
rag-bot/
├── knowledge_base/
│   ├── servicios/          # 26 monografías estéticas
│   └── longevity/          # SSOT longevidad (00–29) + tarjetas/
├── kb_pipeline.py            # Carga + chunking (compartido)
├── embed_kb_local.py         # KB → JSON local (sin Pinecone) ★
├── rag_retrieval_local.py    # Cosine + gates HV + GPT ★
├── prompts.py / confidence_gate.py / query_preprocess.py
├── golden_runner.py          # Regresión golden-set
├── api/main.py               # POST/GET /rag/query (Fly-ready)
├── docs/qa/golden-set-hv-rag.md
├── data/golden-set-hv-rag.json
├── scripts/sync_golden_set.py
├── scripts/process_knowledge_promotions.py
├── generate_embeddings.py      # KB → Pinecone (legacy)
├── rag_retrieval.py            # Pinecone (legacy)
├── test_rag_local.py         # Gates + routing + golden gates
├── test_rag.py               # Suite Pinecone
├── verify_setup.py           # Chequeo de .env y deps
├── servicios_completos.json  # Catálogo + adherence + BNPL
├── arquetipos_modelo_financiero.json
├── requirements.txt
├── .env.example
├── DOCUMENTACION_TECNICA_RAG.md
└── CONFIG_SETUP.md
```

---

## Quick start (RAG local — recomendado)

```bash
cd rag-bot
pip install -r requirements.txt
cp .env.example .env   # solo OPENAI_API_KEY

# 1. Embeddings → JSON (diferencial por content_hash)
python embed_kb_local.py --source all

# 2. Query con gates HV (Avenida 1 default, sin chunks [FALTA FUENTE])
python rag_retrieval_local.py "homocisteína alta y suplementos"
python rag_retrieval_local.py "cuánto cuesta HIFU" --route servicios
python rag_retrieval_local.py "BPC-157 inyectable" --no-llm   # gate Av.2

# 3. Tests gates/routing + golden-set gates (sin API)
python test_rag_local.py

# 3b. Golden trajectories (intake → triage → RAG frozen, sin LLM)
python trajectory_runner.py
python trajectory_runner.py --id TRAJ-HV-006

# 4. Golden-set completo (requiere OPENAI_API_KEY + embeddings)
python scripts/sync_golden_set.py
python golden_runner.py --gates-only    # CI rápido
python golden_runner.py --full          # retrieval 20 escenarios

# 5. API local
uvicorn api.main:app --reload --port 8080
curl "http://localhost:8080/rag/query?q=homocisteina&parse=1&use_llm=false"
curl -X POST http://localhost:8080/rag/query?parse=1 \
  -H "Content-Type: application/json" \
  -d '{"query":"cuánto cuesta HIFU","role":"concierge"}'

# Perfil congelado (S5) — gates con litio/onco del intake
curl -X POST "http://localhost:8080/rag/query?parse=1&use_llm=false" \
  -H "Content-Type: application/json" \
  -d '{"query":"¿puedo hacer ayuno 16:8?","beta_id":"row-0","channel":"api"}'

# 6. Fly deploy
fly deploy   # desde rag-bot/ (secrets: OPENAI_API_KEY, HV_ADMIN_PIN)
# Prod: POST https://hv-rag-api.fly.dev/rag/query con beta_id row-0 | caso0 | tally-{id}
```

**Legacy Pinecone:** `generate_embeddings.py` + `rag_retrieval.py` (opcional).

**Knowledge Loop:** agregar entradas a `data/knowledge-promotions-pending.json` →
`python scripts/process_knowledge_promotions.py` → `embed_kb_local.py --source all`.

---

## Fuentes (`--source`)

| Flag | Carga |
|------|--------|
| `servicios` | `knowledge_base/servicios/[0-9][0-9]_*.md` |
| `longevity` | Monografías `00–29` + `longevity/tarjetas/*.md` |
| `all` | Ambas |

---

## Beta state (MVP-0 S2)

```bash
python scripts/beta_state_cli.py show --intake fixtures/caso0_intake_p1_entrega.json
python scripts/beta_state_cli.py sync fixtures/caso0_intake_p1_entrega.json --clearance --foto --baseline
```

Persiste en `data/beta_states/{beta_id}.json`. `decision_log` acepta `beta_id`, `turn_number`, `channel`.

## RAG + contexto intake (S5)

```bash
python rag_retrieval_local.py "¿puedo hacer ayuno 16:8?" --beta-id row-0 --no-llm
python scripts/concierge_mvp.py --local --beta-id row-0 "¿puedo tomar NMN?"
```

El perfil congelado alimenta **gates** (litio en intake aunque no esté en la pregunta) y el **prompt** LLM.

---

## Próximo paso (fuera de este folder)

API mínima en Neon + Fly exponiendo `POST /rag/query` — no revivir `archive/demo-investor-backend/`.