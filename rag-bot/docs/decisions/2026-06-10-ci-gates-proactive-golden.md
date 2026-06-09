# ADR: Quality gates en CI + Proactive Golden Regression para "se corrige" en pipeline

**Fecha**: 2026-06-10  
**Contexto**: Al madurar el loop proactivo, se necesitó protección de regresión temprana en PRs y scheduled runs para la lógica de detección + generación de acciones (incluyendo health, drift y el nuevo enrichment RAG). Siguiendo la Guía ("CI con tests pasando", golden trajectories para Aprende, y "se corrige" vía gates).

## Decisión

- En `rag-bot-ci.yml`: job `proactive-smoke` con:
  - Dry cycle + calibration.
  - Quality gate explícito (falla si health <50; warning en significant_message_drift alto).
  - Golden regression contra `data/proactive-golden.json` (action_type, message prefix, resume_context).
- En `rag-bot-nightly.yml`: job `proactive-dry` que también ejecuta el golden (validación scheduled del "handler").
- Script dedicado `scripts/proactive_golden.py` (reusable, con path setup, exit code para CI).
- El workflow dedicado (`rag-bot-proactive.yml`) también ejecuta el golden script como "logic validation" (independiente de los datos del server).
- El golden es estable incluso con RAG enrichment opcional (se aserta el prefix base).

Esto da regresión automática en PRs y scheduled, sin depender 100% del server state.

## Alternativas consideradas

- Solo tests unitarios inline: descartado (menos visible en CI, menos reusable que un script dedicado).
- Hacer fallar el workflow scheduled en drift alto: descartado (scheduled debe ser informativo; los gates duros van en CI).
- Usar solo el inline python -c sin archivo golden: descartado (el archivo permite versionar expectativas y usarlo en múltiples lugares).

## Re-activación / próximos pasos

- Cuando se agreguen nuevos signal_types: actualizar golden.json + samples en el script/CI.
- Posible: gate más estricto en CI (ej. health >=70 y drift=0) una vez que haya más datos reales.
- Integrar el golden también en el workflow de deploy si se quiere.

## Trailer

Ratified-by: Autonomous implementation for CI + golden protection of proactive layer  
Ratified-at: 2026-06-10  
Related: .github/workflows/rag-bot-ci.yml, rag-bot-nightly.yml, rag-bot-proactive.yml, scripts/proactive_golden.py, data/proactive-golden.json, action_handler.py (generate), runbook.md, ADR-002

---

Este mecanismo lleva la "regresión + se corrige" al pipeline de CI/CD, protegiendo la lógica del agente proactivo de forma continua.