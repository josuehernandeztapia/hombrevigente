# ADR: Mecanismos de "se corrige" y "aprende" en el agente proactivo (health gate, feature flags, calibration con drift de mensajes, proactive golden, CI gates)

**Fecha**: 2026-06-10  
**Contexto**: Después de implementar la base (SSOT, traces, state + reentry, signals/actions), se construyó el loop proactivo completo. Se necesitaban mecanismos explícitos para que el sistema "se corrige" (evita acciones dañinas) y "aprende" (mejora con uso vía calibración y golden), siguiendo la Guía Agéntica y los 4 puntos del usuario (especialmente SSOT, dual-write, reentry temporal).

## Decisión

Adoptamos un conjunto integrado de mecanismos:

- **Health score + is_healthy** (0-100, con umbral 70 + ssot=postgres): 
  - Penaliza pending actions, calibration drift (incluyendo ahora message_changes y significant_message_drift via difflib), error rate, cost, y no-postgres.
  - is_healthy = (score >=70 AND ssot=postgres).
  - Usado para gatear ejecución real en execute_pending_action, nightly, y workflows (fuerza dry-run si no healthy).
  - Expuesto en /admin/agent_status, /admin/metrics, /api/health, y scripts.

- **Feature flags** (HV_FEATURE_XXX=false, default ON):
  - Controlan HEALTH_GATE, PROACTIVE_EXECUTION, RAG_LLM (para el enrichment en low_progress), PROACTIVE_NIGHTLY, etc.
  - Permiten rollback en <5s sin redeploy (per Guía Capa 5).
  - Expuestos en /api/health y agent_status.

- **Calibration con drift enriquecido** (Capa 6 Aprende):
  - Corre en scheduled (workflow + nightly) y bajo demanda (/admin/calibrate).
  - Detecta drift en signals/actions + en contenido de suggested_message (usando SequenceMatcher para avg_similarity y significant_message_drift).
  - Penaliza health score.
  - Guarda baseline en data/proactive_calibration.json.
  - Emite trace y loguea health.

- **Proactive golden regression** (protección de "handler"):
  - data/proactive-golden.json con campos estables (action_type, suggested_message_starts_with, has_resume_context) para 4 señales clave.
  - scripts/proactive_golden.py (reusable, con path setup).
  - Corren en CI (proactive-smoke con quality gate que falla en health bajo), rag-bot-nightly.yml (scheduled), y se menciona en el workflow dedicado.
  - Protege contra regresiones en generate_action_for_signal (incluyendo el enrichment RAG opcional).

- **Gates en CI / workflows / nightly**:
  - Quality gate en CI: falla si health <50, warning en drift alto.
  - Workflow dedicado: health-aware (parsea is_healthy del status para decidir dry), siempre llama signals + execute(dry por defecto) + calibrate + metrics/status final.
  - Nightly: incluye proactive-dry + calibrate + golden explícito.
  - Todo respeta los 4 puntos (SSOT en traces para turns, postgres-first, slots derivados+persistidos, reentry temporal cubierto por TRAJ-HV-010).

- **Observabilidad**: traces para todo (incluyendo calibration y blocks), health history, last_proactive_run, agent_status con trend y calibration.

## Alternativas consideradas

- Solo feature flags sin health score: descartado (no da señal agregada de "salud" para gating automático).
- Calibration solo en signals (sin message drift): descartado (pierde la comparación de outputs reales que pide la Guía para "re-corre el handler y compara output").
- Golden solo inline en CI (sin script dedicado ni archivo): descartado (menos reusable y mantenible; la Guía recomienda golden trajectories explícitas).
- Ejecutar golden en el workflow dedicado contra el server: no aplica directamente (el golden es para la lógica del handler, no para datos del server; se cubre vía CI y nightly).
- Health sin requerir ssot=postgres: debilitaría la recomendación fuerte de SSOT de la Guía.

## Re-activación / próximos pasos

- Cuando se agreguen nuevos signal_types o enrichment RAG: actualizar proactive-golden.json y los samples.
- Si drift sistemático: investigar en signal_detector / action_handler o en el KB (RAG).
- Posible extensión: auto-toggle de feature flags en el workflow si drift alto sostenido (con override manual).
- Más ADRs para decisiones futuras (ej. thresholds de similarity, integración más profunda de RAG en proactive).
- Monitoreo en prod: alertar si is_healthy=false o significant_message_drift >0 en corridas scheduled.

## Trailer

Ratified-by: Autonomous implementation following Guía Agéntica + 4 puntos del usuario  
Ratified-at: 2026-06-10  
Related: action_handler.py (generate + health), signal_detector.py, scripts/calibrate_proactive.py + proactive_golden.py, .github/workflows/* (proactive + nightly + ci), api/main.py (/calibrate, /metrics, agent_status), docs/runbook.md, data/proactive-golden.json + proactive_calibration.json, ADR-001 (4 puntos + dual-write + turn SSOT + reentry)

---

Este ADR documenta los mecanismos centrales de "se corrige" (gates + flags + health) y "aprende" (calibration con drift de outputs + golden regression + CI/scheduled validation) que cierran el loop proactivo de la Guía.