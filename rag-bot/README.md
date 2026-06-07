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
├── generate_embeddings.py    # KB → Pinecone
├── rag_retrieval.py          # Query semántica + GPT-4o-mini
├── test_rag.py               # Suite de pruebas
├── verify_setup.py           # Chequeo de .env y deps
├── servicios_completos.json  # Catálogo + adherence + BNPL
├── arquetipos_modelo_financiero.json
├── requirements.txt
├── .env.example
├── DOCUMENTACION_TECNICA_RAG.md
└── CONFIG_SETUP.md
```

---

## Quick start

```bash
cd rag-bot
pip install -r requirements.txt
cp .env.example .env   # OPENAI_API_KEY, PINECONE_API_KEY

# Embeddings (servicios + longevidad)
python generate_embeddings.py --source all

# Probar RAG
python rag_retrieval.py
python test_rag.py
```

---

## Fuentes (`--source`)

| Flag | Carga |
|------|--------|
| `servicios` | `knowledge_base/servicios/[0-9][0-9]_*.md` |
| `longevity` | Monografías `00–29` + `longevity/tarjetas/*.md` |
| `all` | Ambas |

---

## Próximo paso (fuera de este folder)

API mínima en Neon + Fly exponiendo `POST /rag/query` — no revivir `archive/demo-investor-backend/`.