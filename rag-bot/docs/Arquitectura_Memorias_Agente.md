# Arquitectura de Memorias del Agente — Hombre Vigente

**Actualizado:** 8-ago-2026 · **Estado:** las 6 memorias operativas; ciclo de consolidación completo en producción.
**Principio:** *un agente no aprende cuando algo pasa — aprende cuando lo que pasó se consolida.*
**Espejo:** el mismo blueprint instanciado para Central Gas vive en `centralgas:docs/Arquitectura_Memorias_Agente.md`.

La distinción que sostiene todo: **saber ≠ hacer ≠ configurar ≠ recordar.** Cuando todo se
mete en un solo lugar (un prompt gigante, un doc suelto), el sistema se pudre. Cada tipo de
memoria tiene su lugar, su pipeline y su candado.

## Las 6 memorias

| # | Memoria | Qué es | Dónde vive en HV |
|---|---|---|---|
| 1 | **Trabajo** | Contexto del turno en curso | `frozen_context.py` (contexto congelado por turno) + estado del beta en `hv_beta_states` |
| 2 | **Episódica** | Lo que pasó, con fecha y porqué | `decision_log.py` → **`hv_decision_log` en Postgres** (migración 004, dual-write con JSONL fallback) + `hv_agent_traces` (costo/latencia por turno) |
| 3 | **Semántica** | Lo que sabe y puede citar | Monografías (`kb/`) → `kb_pipeline.py` → embeddings → pgvector. Se edita SOLO vía repo |
| 4 | **Procedimental** | Reglas que ejecuta, no que recuerda | Gates en código (Av.2 péptidos, onco, psiquiatría), claim-guard del newsletter, idempotencia C1, onboarding determinístico, Índice Vigente framing-as-code — cada una con test |
| 5 | **Parámetros** | Números que cambian sin deploy | ~25 env vars `HV_*` (umbrales cosine, feature flags, modelos LLM) en Fly |
| 6 | **Estado del mundo** | El ground truth operativo | Neon Postgres SSOT: `hv_beta_states`, `hv_pending_actions`, `hv_kb_embeddings`. `HV_STATE_PERSISTENCE=postgres` |

## El ciclo de consolidación (en producción)

```
EXPERIENCIA   turno real del concierge / acción proactiva
    → EPISÓDICA    hv_decision_log + hv_agent_traces (crudo, barato, redactado de PII)
    → DESTILACIÓN  knowledge_gap_detector → reporte semanal (workflow rag-bot-knowledge-gaps, --from-prod)
    → ROUTER       knowledge_promote.py: staging a pending JSON; un humano aprueba (patrón CMU)
    → CANDADOS     process-promotions corre golden gates ANTES de abrir el PR
    → DESPLIEGUE   PR → merge → nightly re-embed → prod
```

## El router (dónde va cada aprendizaje nuevo)

- ¿Se necesita para **responder**? → semántica (monografía/FAQ, vía promoción)
- ¿Debe **impedir o forzar** algo? → procedimental (código + test; nunca solo prompt)
- ¿Es un **número** que cambia? → env var `HV_*`
- ¿Es **contexto** de quien opera/desarrolla? → episódica (decision log, docs/decisions)
- ¿Es **confidencial o estratégico**? → ninguna memoria compartida

## Los dos guardianes

1. **Memoria con CI/CD** — el corpus se shippea por pipeline (fuente → embed → deploy);
   nunca se edita "en vivo". El entrypoint de Fly aplica migraciones y re-sincroniza embeddings.
2. **Memoria con regresión** — golden set en 3 niveles: gates-only en cada PR (CI),
   retrieval completo nightly, y regresión proactiva. Nadie cambia lo que el agente sabe
   por accidente.

## Test de madurez (respuestas al 8-ago-2026)

1. *¿Dónde quedó escrito el último error pagado?* — En el candado mismo: los 7 bugs del
   pipeline del newsletter viven como comentarios en los workflows + `approvals/*.json`;
   los tests bomba-de-tiempo, en `test_observability.py` con timestamps dinámicos.
2. *¿Qué impide que se repita?* — Componentes, no personas: idempotencia (`_already_sent`,
   UNIQUE `idemp_key`), gates, golden set.
3. *¿Si borro el chat de ayer, el agente amanece más tonto?* — No: lo aprendido está en
   Postgres, en el corpus versionado o en un test.

## Pendientes

- **Manifiesto de parámetros** (`PARAMETERS.md` o `/admin/config`): la memoria #5 existe
  pero no es auditable sin grepear. Único hueco abierto del blueprint.
- Regla de higiene permanente: si un aprendizaje nuevo no pasa por el router, no existe —
  vive en la cabeza de alguien y se va a perder.
