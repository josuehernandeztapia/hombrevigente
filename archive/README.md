# Archive — material histórico y demos

Contenido **archivado** (junio 2026). No es el runtime activo del producto. Se conserva para pitch histórico, referencia de contratos API y provenance del KB.

## Qué sigue activo (fuera de `archive/`)

| Ruta | Uso |
|------|-----|
| `rag-bot/knowledge_base/` | Corpus RAG (estética + longevidad) |
| `rag-bot/generate_embeddings.py`, `rag_retrieval.py` | Pipeline RAG |
| `rag-bot/servicios_completos.json`, `arquetipos_modelo_financiero.json` | Catálogo y arquetipos canónicos |
| `blueprint/core/financial-engine.js` | Motor financiero (recalibrar con MVP-0) |
| `estrategia_2026/`, `wiki/` | Operación y mapa de negocio |
| `index.html`, `modelofinanciero.html`, `pitchdeck.html`, `encuesta*.html` | Público / pitch honesto |

---

## Subcarpetas

### `legacy-demos/`
Duplicados HTML del modelo financiero y laboratorio.

### `demo-investor-backend/`
FastAPI + 3 agentes **mock** (DiagnósticoVigente, PersonaVigente, OptiVigente). Referencia de endpoints para un backend futuro (Neon + Fly); no ejecutar como producción.

### `demo-termico/`
`geminidiagnostico.html`, `diagnostic-demo.js` — simulación front-end del diagnóstico térmico.

### `pitch-html/`
Vision board, ecosistema, mvtech, war room, ai-ecosystem.js — narrativa inversor / arquitectura aspiracional.

### `lab-llm/`
Prototipos `grok.html`, `modelogemini.html`, `prototipo_vigente.html`.

### `docs-investor-2025/`
Documentación era "demo seed round": README_DEMO, CHANGELOG agentes, análisis RAG, queries inversor, `test_results_rag.json`.

### `ssot-v1-legacy/`
SSOT v1.1/v1.2 y Manual de Vuelo (texto masivo). Sustituido por `rag-bot/knowledge_base/longevity/` + `wiki/`.

### `synthetic-data/`
`generador_sintetico_v2/v3.py`, JSON "validados" (Faker seed=42). Herramienta de simulación — **no** datos de clientes reales.

### `kb-provenance/`
Logs de enriquecimiento del KB estético (ENRICHMENT_*, REPORTE_*, SESSION_STATUS). Provenance del corpus, no contenido clínico.

---

*Backend mínimo productivo: pendiente (Neon + Fly). Ver `estrategia_2026/MVP0_Playbook.md`.*