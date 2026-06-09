# ADR: SSOT en Postgres, política dual-write, SSOT de turn_number y los 4 puntos clave (slots, reentry temporal)

**Fecha**: 2026-06-10  
**Contexto**: Implementación del agente proactivo para Hombre Vigente siguiendo la Guía Agéntica Estándar (v1 2026-06-08). El usuario especificó explícitamente 4 puntos de aclaración al inicio del trabajo. Se construyeron las Capas 1-3 + loop proactivo + Capa 7 (ops, health, gates) en orden estricto de la Guía para minimizar rework.

## Contexto

Durante el análisis inicial de la Guía y arranque de Fase 1, el usuario proveyó 4 puntos verbatim que debían ser respetados en diseño y código:

1. Modelo de slots (derivados vs. persistidos)
2. SSOT de turn_number
3. Política de lectura en dual-write (postgres-first)
4. Aclarar que TRAJ-HV-005 no cubre ReentryHandler temporal (se resolvió con TRAJ-HV-010)

Además, la Guía enfatiza:
- Postgres como única fuente de verdad (SSOT) con JSONB + state_version + optimistic locking.
- Fire-and-forget para traces (Capa 2).
- last_active_at dentro del state (no external updated_at).
- ReentryHandler con bandas humanas exactas (24h-72h, 3d-7d, 7d+).
- "Se corrige": feature flags + branches deterministas + gates de salud antes de acciones reales.
- ADRs para decisiones arquitecturales.

Se implementó dual-write (files/postgres) con política clara durante transición, pero priorizando postgres.

## Decisión

Adoptamos la siguiente arquitectura y políticas:

- **SSOT Postgres (Capa 1)**: hv_beta_states con state_data JSONB + state_version. Migrations con .down.sql. Índices parciales en phase y last_active_at. `last_active_at` vive dentro del JSONB.
- **Política de dual-write y lecturas (punto 3)**: 
  - Modo "postgres" (default inteligente cuando hay DATABASE_URL postgres).
  - Lecturas: SIEMPRE de Postgres cuando está configurado y disponible. Fallback a files SOLO en error de lectura (degradación explícita + warning).
  - Escrituras: persistencia principal en postgres (con optimistic lock + 1-retry en StateVersionConflictError). Files como mirror legacy durante transición.
  - Scripts y health exponen warnings claros: "Para producción usa HV_STATE_PERSISTENCE=postgres".
- **SSOT de turn_number (punto 2)**: 
  - next_turn_number() consulta atómicamente hv_agent_traces: `COALESCE(MAX(turn_number), 0) + 1` con `IS NOT DISTINCT FROM` por beta_id.
  - StateManager.record_turn() y transiciones usan el valor autoritativo de traces para el payload del trace.
  - state["turn_count"] se mantiene como copia denormalizada para lecturas rápidas (sin query extra).
- **Modelo de slots (punto 1)**: Derivados en derive_state_from_intake / sync_from_intake (desde intake Tally), pero se persisten explícitamente en state_data JSONB. fill_slot es idempotente.
- **Reentry temporal (punto 4)**: TRAJ-HV-010 añade soporte explícito "set_last_active" + "force-old-last-active" en trajectory_runner. Reentry.compute_resume_message implementa las bandas exactas de la Guía. TRAJ-HV-005 se clarificó como no cubriendo el caso temporal (solo preservación de datos en re-sync).
- **"Se corrige" (Capa 7 + flags)**: 
  - compute_proactive_health_score() + is_healthy (score >=70 AND ssot=postgres).
  - Gate real en execute_pending_action / nightly / API: bloquea si !is_healthy (deja acción en pending con status=blocked_by_health).
  - Feature flags (HV_FEATURE_*) default ON para rollback <5s de branches (PROACTIVE_EXECUTION, HEALTH_GATE, RAG_LLM, etc.).
  - --force / force=true como override explícito solo para ops.
- Traces (Capa 2): fire-and-forget, normalize_model_id, cost estimation, turn_number en cada payload, persist en RAG paths + proactive + state mutations.

## Alternativas consideradas (y por qué se descartaron)

- Usar solo files para todo: descartado (drift, no ACID, viola Capa 1 de la Guía y el requisito explícito de Postgres como SSOT).
- Dual-write simétrico sin política de lectura postgres-first: descartado (el usuario especificó "postgres-first reads, fallback solo en error").
- Mantener turn_count 100% local sin query a traces: descartado (viola punto 2 y el "Turn counter atómico" del checklist; race conditions en concurrencia).
- TRAJ-HV-005 extendido para cubrir temporal: descartado (el usuario dijo explícitamente que no lo cubre; se creó TRAJ-HV-010 separado).
- Health score sin requerir ssot=postgres: descartado (debilitaría la recomendación fuerte de la Guía y el gate de seguridad).
- Feature flags complejos (JSON, DB, etc.): descartado (Guía pide simple env-based, default ON, toggle sin redeploy).

## Re-activación / próximos pasos

- Cuando se migre 100% a postgres en prod: remover lógica de fallback files (o dejar solo para dev).
- Enriquecer next_turn_number para soportar conversation_id cuando se introduzca (Guía usa IS NOT DISTINCT FROM para ambos).
- Agregar más ADRs para decisiones futuras (ej. thresholds de cosine, modelo de calibration, sender real de WhatsApp).
- Correr calibrate_proactive.py semanalmente + revisar drift + health trend.
- Actualizar este ADR si cambia la política de dual-write o se introduce conversation_id.

## Trailer

Ratified-by: Autonomous implementation following Guía Agéntica Estándar + explicit 4 points from user  
Ratified-at: 2026-06-10  
Related: state_persistence.py, state_manager.py (record_turn), beta_state.py (sync), traces.py (next_turn_number fallback), action_handler.py (health gate + flags), runbook.md, trajectories-hv.json (TRAJ-HV-010)

---

Este ADR documenta las decisiones clave tomadas para respetar la Guía y los 4 puntos del usuario. Se creó como parte del paso autónomo para avanzar el checklist de production-ready ("ADR para cada decisión arquitectural").