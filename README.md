# Hombre Vigente — Repositorio Central

Repositorio del ecosistema **Hombre Vigente**: club de estética regenerativa masculina + capa de longevidad.

> **Versión:** Junio 2026 · Pre-operativo (MVP-0 en validación) · Rama de trabajo: **`main`**

---

## Mapa activo (lo que usamos hoy)

| Ruta | Contenido |
|------|-----------|
| [`estrategia_2026/`](estrategia_2026/) | Plan maestro, MVP-0, playbook WhatsApp, research, deck |
| [`wiki/`](wiki/) | 8 CORE + 2 GAP (navegación por dominio) |
| [`rag-bot/knowledge_base/`](rag-bot/knowledge_base/) | **Core producto** — 26 servicios estéticos + SSOT longevidad (29 monografías + 15 tarjetas) |
| [`rag-bot/generate_embeddings.py`](rag-bot/generate_embeddings.py) | Ingesta KB → Pinecone |
| [`rag-bot/rag_retrieval.py`](rag-bot/rag_retrieval.py) | Query RAG + GPT |
| [`rag-bot/servicios_completos.json`](rag-bot/servicios_completos.json) | Catálogo, adherence, membresías, BNPL |
| [`blueprint/core/financial-engine.js`](blueprint/core/financial-engine.js) | Motor financiero (metodología; recalibrar con betas reales) |
| `index.html`, `modelofinanciero.html`, `pitchdeck.html`, `encuesta*.html` | Público / pitch / encuesta N=442 |
| [`archive/`](archive/) | Demos, mocks, SSOT viejo, datos sintéticos — **no runtime** |

---

## Por dónde empezar

1. **Estrategia** → [`estrategia_2026/SINTESIS_Relato_Unificado_HombreVigente.md`](estrategia_2026/SINTESIS_Relato_Unificado_HombreVigente.md)
2. **Lanzar MVP-0** → [`estrategia_2026/MVP0_Playbook.md`](estrategia_2026/MVP0_Playbook.md) · **Sprint actual** → [`estrategia_2026/SPRINT_01_MVP0_Concierge.md`](estrategia_2026/SPRINT_01_MVP0_Concierge.md)
3. **Auditoría honesta** → [`estrategia_2026/Revision_Quirurgica_Repo_HombreVigente.md`](estrategia_2026/Revision_Quirurgica_Repo_HombreVigente.md)
4. **RAG** → [`rag-bot/README.md`](rag-bot/README.md)
5. **Qué hay archivado** → [`archive/README.md`](archive/README.md)

---

## Estado actual (honesto)

| Real | Simulado / archivado |
|------|----------------------|
| KB estética + longevidad | 3 agentes FastAPI mock → `archive/demo-investor-backend/` |
| Pipeline RAG (con `.env`) | Diagnóstico térmico HTML → `archive/demo-termico/` |
| `financial-engine.js` (método) | 5K clientes Faker → `archive/synthetic-data/` |
| Encuesta N=442 (interés, no conversión) | Claims "9 agentes production-ready" en HTML viejos |

**Pendiente:** 5–10 betas MVP-0 (WhatsApp + tracker). Backend API (Neon + Fly) — después.

---

## Espejo local (fuera de git)

`~/Downloads/longevity/` — turnaround, índice SSOT, copia de tarjetas. Sincronizar manualmente con `rag-bot/knowledge_base/longevity/` cuando cambie el corpus.

---

## Deploy

GitHub Pages publica HTML/assets de la raíz y `blueprint/`. `rag-bot/` y `wiki/` no se despliegan (`.github/workflows/static.yml`).