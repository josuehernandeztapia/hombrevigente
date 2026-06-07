# Hombre Vigente — Repositorio Central

Repositorio del ecosistema **Hombre Vigente**: club de estética regenerativa masculina + capa de longevidad, operado con IA.

> **Versión:** Junio 2026 · Pre-operativo (MVP-0 en validación)

---

## Estructura real del repo

| Carpeta / archivo | Contenido |
|-------------------|-----------|
| [`estrategia_2026/`](estrategia_2026/) | **Documento maestro** — plan, síntesis unificada, MVP-0 operativo, research, deck |
| [`wiki/`](wiki/) | 8 CORE + 2 GAP (resúmenes navegables por dominio) |
| [`rag-bot/`](rag-bot/) | Backend FastAPI, pipeline RAG, knowledge base clínica, generador sintético |
| [`blueprint/`](blueprint/) | `financial-engine.js` + demos de diagnóstico |
| `*.html` | Demos y prototipos (modelo financiero, pitch, war room, diagnóstico) |
| [`archive/`](archive/) | HTMLs legacy archivados (duplicados y laboratorio) |
| [`rag-bot/Leer/`](rag-bot/Leer/) | SSOT v1.1 + v1.2 + Manual de Vuelo (sin duplicados HTML) |

---

## Por dónde empezar

1. **Estrategia y próximos pasos** → [`estrategia_2026/SINTESIS_Relato_Unificado_HombreVigente.md`](estrategia_2026/SINTESIS_Relato_Unificado_HombreVigente.md)
2. **Lanzar validación** → [`estrategia_2026/MVP0_Playbook.md`](estrategia_2026/MVP0_Playbook.md)
3. **Revisión honesta del repo** → [`estrategia_2026/Revision_Quirurgica_Repo_HombreVigente.md`](estrategia_2026/Revision_Quirurgica_Repo_HombreVigente.md)
4. **Wiki por dominio** → [`wiki/README.md`](wiki/README.md)

---

## Estado actual (honesto)

- **Validado:** insight de dolor + encuesta N=442 (interés declarado, no conversión).
- **Funcional:** pipeline RAG sobre 26 servicios estéticos; motor financiero (`financial-engine.js`).
- **Simulado:** agentes IA backend (mocks demo); diagnóstico térmico (front-end demo).
- **Pendiente:** 5–10 betas reales (MVP-0 concierge por WhatsApp).

---

## Deploy

GitHub Pages publica los HTMLs y assets estáticos. `rag-bot/` y `wiki/` quedan fuera del deploy (ver `.github/workflows/static.yml`).