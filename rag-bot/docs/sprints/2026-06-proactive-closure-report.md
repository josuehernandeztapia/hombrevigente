# Sprint Closure Report — Proactivo Hombre Vigente (2026-06)

**Veredicto**: Núcleo del agente proactivo **cerrado** según la Guía Agéntica Estándar + los 4 puntos específicos del usuario + checklist production-ready. Quedan ítems menores/no-bloqueantes (ver abajo).

## DoD (Definition of Done) y veredicto contra cada criterio (Guía + 4 puntos + checklist)

- [x] **Capa 1 — SSOT en Postgres**: hv_beta_states con state_data JSONB + state_version, optimistic lock, last_active_at dentro del state, migrations + .down.sql. Política de lectura postgres-first (fallback solo en error). **Veredicto**: ✅ (cumple punto 3 del usuario y Guía).
- [x] **Capa 2 — Observability / Traces**: hv_agent_traces con turn_number como SSOT atómico (next_turn_number con IS NOT DISTINCT FROM), normalize_model_id, cost estimation (PRICING), p50/p95 (PERCENTILE_CONT), fire-and-forget, sanitización PII, endpoints admin PIN. **Veredicto**: ✅ (cumple punto 2 del usuario).
- [x] **Capa 3 — State Machine resumible**: StateManager con get/fill/transition/record_turn (idempotente, version, last_active), ReentryHandler con bandas exactas de la Guía (24h-72h, 3d-7d, 7d+), TRAJ-HV-010 para cobertura temporal explícita. **Veredicto**: ✅ (cumple punto 4 del usuario — TRAJ-HV-005 no cubría temporal; ahora cubierto).
- [x] **Capa 4 — RAG**: Integración en proactive (enrichment opcional para low_progress con rag_query_local + snippet de evidencia). Trazas con costos en paths RAG. **Veredicto**: ✅ (tie-in de capas).
- [x] **Capa 5 — Agente y routing**: generate_action_for_signal + detector, feature flags (Capa 5 Guía), branches con golden regression (proactive-golden.json + runner). **Veredicto**: ✅.
- [x] **Capa 6 — Loop de aprendizaje**: Calibration con drift enriquecido (signals + message content via difflib + avg_similarity + significant_drift), proactive golden trajectories (data/proactive-golden.json + scripts/proactive_golden.py), señal detection + actions. Corre en CI, nightly y scheduled. **Veredicto**: ✅.
- [x] **Capa 7 — Admin UI y operaciones**: Múltiples endpoints PIN (/metrics, /calibrate, /agent_status, /signals/run, /pending_actions/execute, etc.), runbook completo, workflows GH (dedicado proactive health-aware + golden logic + calibrate; integración en nightly; CI con smoke + golden + quality gate que falla en health bajo), scripts (beta_ops_review, execute, calibrate, proactive_golden), health gating + is_healthy (score >=70 + ssot=postgres) + feature flags para "se corrige". **Veredicto**: ✅.
- [x] **4 puntos del usuario**:
  1. Slots: derivados (derive/sync) pero persistidos en state_data. ✅
  2. SSOT de turn_number: next_turn_number desde hv_agent_traces (atómico); denormalizado en state para lecturas rápidas. ✅
  3. Política de lectura dual-write: postgres-first (solo fallback en error de lectura). ✅
  4. TRAJ-HV-005 no cubría Reentry temporal → cubierto explícitamente por TRAJ-HV-010 + compute_resume_message. ✅
- [x] **Checklist production-ready de la Guía** (ver sección detallada en runbook.md): traces, PII, admin PIN endpoints (4+), state JSONB+version+lock, last_active inside state, Reentry bands, cost normalize, turn atómico, feature flags, migrations+.down, CI+tests, admin UI mínima (endpoints+scripts+runbook), runbook, ADRs. **Veredicto**: ✅ (casi todo; ver pendings menores abajo).
- [x] **ADRs**: Dos creados (2026-06-10 para 4 puntos + dual-write + turn SSOT + reentry; 2026-06-10 para se corrige/aprende con health+flags+drift+golden+CI). **Veredicto**: ✅.
- [x] **Golden + calibración + CI/scheduled**: RAG golden + proactive golden + calibration con drift de mensajes + CI quality gate + workflows. **Veredicto**: ✅.
- [x] **Runbook actualizado**: Principios, comandos, fallas, gates, métricas Guía, workflows, estado vs checklist. **Veredicto**: ✅.

## Componentes vivos (entregados en este "sprint" proactivo)
- rag-bot/state_persistence.py (next_turn_number, postgres-first)
- rag-bot/state_manager.py (record_turn con turn SSOT, transitions)
- rag-bot/traces.py (p50/p95, costs, turn_number, normalize)
- rag-bot/action_handler.py (generate con RAG enrichment, health_score con is_healthy + message drift penalty, execute con gate)
- rag-bot/signal_detector.py + calibrate_proactive.py (drift enriquecido)
- rag-bot/feature_flags.py
- rag-bot/api/main.py (/calibrate, /metrics, agent_status con health/trend/calibration, health menciona calibrate)
- rag-bot/scripts/ (proactive_golden.py, run_proactive_nightly.py actualizado, execute_pending_actions.py con health log, beta_ops_review.py)
- data/ (proactive-golden.json, proactive_calibration.json)
- .github/workflows/ (rag-bot-proactive.yml con health decision + calibrate + golden logic check; rag-bot-nightly.yml con proactive-dry + golden; rag-bot-ci.yml con smoke + gate + golden)
- docs/decisions/ (2 ADRs)
- docs/sprints/ (este closure report)
- rag-bot/docs/runbook.md (actualizado con checklist status, comandos, gates)

## Verificación en "producción" (simulada / CI / local)
- pytest test_beta_state.py + golden checks: passing.
- python scripts/proactive_golden.py: PASSED.
- python scripts/run_proactive_nightly.py --dry-run --sample 5 + calibrate: OK (health logs, drift).
- Workflows YAML: válidos (proactive golden en los 3).
- Simulación de gates: health <50 falla CI; !is_healthy fuerza dry; flags controlan ejecución/enrichment.
- Traces emitidos para calibration, blocks, RAG enrichment, record_turn, etc.
- 4 puntos verificados en código/comentarios/ADRs (slots derivados+persistidos, turn SSOT en traces, postgres-first, TRAJ-HV-010).
- Ningún breakage a RAG golden, trajectories, state, dual-write, reentry temporal.

## Issues abiertos (no bloquean cierre del núcleo; aclarados por el usuario)
- Admin UI visual completa: Per aclaración del usuario, la mención a NocoDB **no tiene relación** con esta implementación del núcleo agentic. La migración Airtable → NocoDB (sobre Neon Postgres) es un esfuerzo separado de datos/UI. Los endpoints + scripts + runbook + workflows cubren la "admin UI mínima" de la Guía.
- Más ADRs: Se agregaron 2 adicionales durante este cierre (RAG enrichment en proactive; CI gates + proactive golden). Quedan para decisiones futuras.
- Sprint closure reports formales adicionales: Este es el primero (formato Guía aplicado). Se puede agregar más en sprints siguientes.
- Ejecución real de acciones: El loop completo de decisión + "se corrige" (health gate + is_healthy + flags + dry por defecto + blocks con trace + logging + golden regression) ya está listo y probado. El sender real (WhatsApp/Twilio/etc.) es out-of-scope del núcleo agentic. Se agregó un stub claro en `scripts/send_proactive_action.py` con TODOs explícitos para la integración futura.
- En CI los jobs proactive usan la API del server (asumido postgres en prod); para fully offline simulation se usa files fallback con warnings (comportamiento esperado).

## Próximos pasos
- Monitoreo diario: /admin/agent_status + /admin/metrics + beta_ops_review.py + runbook.
- Si drift alto sostenido: investigar signal_detector/action_handler o KB.
- Cuando se agreguen nuevos signals o más RAG en proactive: actualizar proactive-golden.json y samples.
- Posible: auto-toggle de flags en workflow si drift alto (con override).
- Deploy a Fly con HV_STATE_PERSISTENCE=postgres + HV_ADMIN_PIN + DATABASE_URL.
- Futuro: integrar el sender real usando el stub en `scripts/send_proactive_action.py` (el núcleo de decisión + gates ya está completo).

---

**Cierre del sprint**: El núcleo del agente proactivo (SSOT + traces + state/reentry + proactive con se corrige/aprende + ops) está implementado, probado, documentado y alineado con la Guía + tus 4 puntos. Listo para iterar en "ejecución real" o más capas.

Ratified-by: Autonomous steps following Guía + feedback del usuario  
Ratified-at: 2026-06 (cierre)