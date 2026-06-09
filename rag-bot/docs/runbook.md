# Runbook — Agente Proactivo Hombre Vigente (Guía Agéntica Estándar)

Este runbook cubre las fallas más comunes y los comandos para diagnosticar y resolver, alineado con el checklist de "production-ready" de la Guía.

## Principios
- Postgres es la única fuente de verdad (SSOT). Si ves `ssot_postgres_recommended: true` en health, actúa.
- `is_healthy` (en health_score y agent_status) = (score >= 70 AND ssot=postgres). Es la señal de "se corrige" para gating de ejecución real.
- **Feature flags** (Capa 5 Guía): HV_FEATURE_XXX=false deshabilita branches/gates sin redeploy (default ON). Ver /api/health y feature_flags.py. Ej: HV_FEATURE_HEALTH_GATE=false, HV_FEATURE_PROACTIVE_EXECUTION=false.
- Todo cambio de estado pasa por StateManager (optimistic lock + version).
- Las acciones proactivas se generan y se ejecutan de forma traceable (traces + pending_actions + executed_actions).
- Corre en dry-run por defecto. Nunca ejecutes en prod sin `--dry-run` primero.
- **Gate de ejecución real**: Las acciones proactivas reales (no dry-run) están bloqueadas a menos que `is_healthy=true` (score ≥70 **y** SSOT=postgres). Usa `--force` / `force=true` solo en emergencias de ops. El nightly fuerza dry-run automáticamente cuando no está healthy.

## Comandos de diagnóstico rápido

```bash
# Salud general del agente (incluye costos, deuda proactiva, última corrida, calibración + is_healthy)
curl -H "x-admin-pin: $HV_ADMIN_PIN" \
  "https://hv-rag-api.fly.dev/admin/agent_status"

# Métricas completas Guía (p50/p95, % determinista, resume proxy, MTTD proxy, etc.)
curl -H "x-admin-pin: $HV_ADMIN_PIN" \
  "https://hv-rag-api.fly.dev/admin/metrics"

# Vista operativa de betas + acciones pendientes + health + is_healthy
python scripts/beta_ops_review.py

# Ver acciones pendientes
python scripts/detect_beta_signals.py --pending

# Correr ciclo proactivo completo en dry-run (recomendado antes de cualquier ejecución)
python scripts/run_proactive_nightly.py --dry-run --sample 50

# Ejecutar acciones pendientes (¡cuidado! — gateado por is_healthy)
python scripts/execute_pending_actions.py --dry-run
python scripts/execute_pending_actions.py --force   # solo emergencias (bypassa is_healthy)
python scripts/execute_pending_actions.py          # real solo si is_healthy=true

# Scheduled proactivo vía GitHub Actions (Capa 7 Guía — recomendado para prod)
# Ver .github/workflows/rag-bot-proactive.yml
# - Diario: fetch status (is_healthy), signals/run (detect+act), execute dry (health-aware), /admin/calibrate (drift en signals + contenido de mensajes con similarity + baseline), final /admin/metrics + status
# - Manual dispatch con input execute_real=true (solo si is_healthy o emergencia)
# Siempre loguea health (Aprende loop). Calibration se corre en cada ciclo scheduled. Drift de mensajes ahora penaliza health y es más semántico (difflib).
```

**Gate de seguridad importante**:
- Cualquier ejecución real (no `--dry-run`) se bloquea automáticamente si `is_healthy=false`.
- Cuando se bloquea, la acción **permanece en pending** con `status=blocked_by_health` y se emite un trace.
- El script y el endpoint `/admin/pending_actions/execute?force=true` permiten override explícito (solo ops).
- El nightly ya fuerza dry-run cuando no está healthy.

## Fallas comunes y resolución

### 1. "ssot_postgres_recommended: true" o modo files en producción
**Síntoma**: Health muestra `ssot: files` o `ssot_postgres_recommended: true`. Las señales/calibración usan datos desactualizados.

**Acción**:
- Verifica que `HV_DATABASE_URL` y `HV_STATE_PERSISTENCE=postgres` estén seteados en Fly secrets.
- Corre el backfill si hay datos en files:
  ```bash
  python scripts/backfill_beta_states.py --dry-run
  python scripts/backfill_beta_states.py
  ```
- Redeploy.

**Prevención**: En prod siempre `HV_STATE_PERSISTENCE=postgres`. El código ahora defaulta a postgres cuando hay DATABASE_URL postgres.

### 2. Muchas acciones pendientes / deuda proactiva alta
**Síntoma**: `/admin/agent_status` muestra `pending_actions > 5` o el ops review muestra muchos "PENDING".

**Acción**:
1. Revisa qué está pasando:
   ```bash
   python scripts/beta_ops_review.py
   ```
2. Corre en dry-run para ver los mensajes que se enviarían:
   ```bash
   python scripts/run_proactive_nightly.py --dry-run
   ```
3. Ejecuta (solo si los mensajes tienen sentido):
   ```bash
   python scripts/execute_pending_actions.py --dry-run
   python scripts/execute_pending_actions.py
   ```
4. Si hay muchos de un mismo tipo, revisa si hay un bug en el generador de acciones (ver `action_handler.py`).

### 3. Calibración muestra drift
**Síntoma**: En `/admin/agent_status` o al correr `calibrate_proactive.py` ves `drift.added` o `drift.removed` > 0.

**Acción**:
- Corre manualmente con sample completo:
  ```bash
  python scripts/calibrate_proactive.py --sample 0
  ```
- Compara el `data/proactive_calibration.json` actual vs el anterior.
- Si el drift es esperado (cambios intencionales en lógica de señales/acciones), está bien.
- Si es inesperado, revisa cambios recientes en `signal_detector.py` o `action_handler.py` y agrega tests en `test_beta_state.py` o un nuevo test de calibración.
- La calibración se guarda como baseline automáticamente.

### 4. No se están generando señales/acciones (0 triggered)
**Síntoma**: `actions_generated: 0` en la corrida nightly o en `detect_beta_signals.py`.

**Posibles causas**:
- Todas las betas están "saludables" (buen last_active_at, slots completos, etc.).
- El detector no está viendo los estados correctos (ver SSOT arriba).
- Filtro demasiado estricto en `signal_detector.py`.

**Acción**:
- Fuerza un estado "malo" temporalmente en un beta de prueba (solo en dev):
  ```bash
  python scripts/beta_state_cli.py advance <beta-id> onboarding --note "test stalled"
  # Luego fuerza last_active_at viejo editando el JSON o vía DB
  ```
- Corre el detector y verifica que aparezca la señal.
- Revisa los thresholds implícitos en `signal_detector.py` (horas, progreso, etc.).

### 5. Ejecución falla o no actualiza el estado
**Síntoma**: Las acciones se marcan executed pero el BetaState no se actualiza (no aparece "proactive_action_executed" en history, o last_active_at no se mueve).

**Acción**:
- Revisa logs de la ejecución (debe imprimir "[execute] SENT...").
- Verifica que `sm.record_turn(...)` no esté fallando por version conflict (el código hace best-effort).
- En caso de error, el pending se mueve a executed_actions.jsonl de todas formas (para no perder trazabilidad).
- Revisa trazas con `/admin/traces?beta_id=<id>`.

### 6. Costos aparecen en 0 o muy altos en agent_status
**Síntoma**: `traces_24h.total_cost_usd == 0` o valores extraños.

**Acción**:
- Asegúrate de que los `llm_calls` en las trazas tengan `prompt_tokens` y `completion_tokens` (el RAG path ya lo hace en algunos casos; el path proactivo es mayormente determinista por ahora).
- La normalización de modelo (`normalize_model_id`) está en `traces.py`.
- Si usas modelos nuevos, agrégalos a `PRICING` en `traces.py`.
- Corre una query RAG con `parse=1` y revisa el campo de costo en la traza.

### 7. Estado inconsistente (version conflicts frecuentes)
**Síntoma**: Muchos `StateVersionConflictError` en logs o el StateManager está fallando seguido.

**Acción**:
- El código ya hace un reintento único en la mayoría de paths.
- Si persiste: alguien está escribiendo el estado por fuera del StateManager (evitar).
- En Postgres: revisa que no haya escrituras directas a `hv_beta_states`.
- Para debug: usa `/admin/traces?beta_id=<id>&errors_only=true`.

## Monitoreo recomendado
- Revisa `/admin/agent_status` diariamente o ponlo en un dashboard.
  - Presta especial atención al `proactive.health_score` (0-100) y `proactive.health_score.is_healthy`.
    - is_healthy=true (score >=70 **y** ssot=postgres): listo para ejecución real y gating.
    - >80: saludable.
    - 70-80: vigila (revisa pending y calibración).
    - <70 or !is_healthy: actúa (revisa deuda proactiva, drift, SSOT, costos en traces). El nightly fuerza dry-run cuando <70.
- Corre el nightly (o `run_proactive_nightly.py`) al menos una vez al día. El CI (rag-bot-ci.yml) ahora incluye "proactive-smoke" en PRs para regresión temprana de signals/actions/health/calibration + quality gate (falla si health <50, warning en high message drift) + golden regression (via `python scripts/proactive_golden.py`, usando data/proactive-golden.json como el golden de RAG). low_progress suggestions ahora se enriquecen opcionalmente con RAG (Capa 4) para mensajes basados en evidencia. El rag-bot-nightly.yml también corre "proactive-dry" + calibration + golden para Aprende en el scheduled golden context.
- Para las Métricas de éxito completas de la Guía (p50/p95 latency, % determinista branches, resume_rate_proxy, MTTD proxy, error/cost, cobertura traces): usa `/admin/metrics` (PIN).
- Alerta si:
  - `pending_actions > 10`
  - Drift en calibración > 0 en más de 2 corridas seguidas
  - `ssot_postgres_recommended == true` en prod
  - Costo promedio por turno sube > 2x el baseline
  - health_score < 70 or is_healthy=false
  - deterministic_pct < 0.5 sostenido (demasiado LLM)

## Cuándo escalar a humano
- Si una beta lleva > 14 días sin actividad y las acciones proactivas no están funcionando (o is_healthy=false repetidamente).
- Si hay drift sistemático en las acciones sugeridas (posible bug en la lógica de reenganche).
- Problemas de Postgres (conexión, migraciones pendientes).
- Métricas Guía rojas sostenidas (p95>8s, deterministic_pct<40%, resume_rate<10%, MTTD proxy alto) vía /admin/metrics.

## Referencias
- Guía Agéntica Estándar (las 7 capas y el checklist production-ready)
- `docs/decisions/` — ADRs de decisiones arquitecturales clave (ver 2026-06-10-ssot-dual-write-4-puntos-turn-reentry.md para los 4 puntos + dual-write + turn SSOT + reentry; 2026-06-10-proactive-se-corrige-aprende.md para health gate + is_healthy, feature flags, calibration con message drift, proactive golden y CI gates; 2026-06-10-rag-enrichment-proactive.md para la integración RAG en acciones; 2026-06-10-ci-gates-proactive-golden.md para los quality gates y golden regression en CI).
- `scripts/beta_ops_review.py` — vista humana rápida
- `/admin/betas`, `/admin/agent_status`, `/admin/traces`, `/admin/metrics`
- `action_handler.py` + `signal_detector.py` — el corazón del proactivo
- `state_manager.py` — toda mutación debe pasar por acá
- `feature_flags.py` — toggles para rollback rápido (HV_FEATURE_*=false)
- `scripts/proactive_golden.py` — runner para golden regression proactiva (data/proactive-golden.json)

## Estado actual vs checklist production-ready de la Guía (2026-06)

✅ Tabla `agent_traces` (con costs, p50/p95 via PERCENTILE, turn_number como SSOT atómico, fire-and-forget, normalize_model_id)
✅ PII sanitizada (reutiliza decision_log + redact en traces)
✅ 4+ admin PIN-gated endpoints funcionales (/traces*, /metrics, /agent_status, /calibrate, /signals, /pending_actions/execute, /betas, etc.)
✅ `state_data` JSONB + `state_version` (optimistic lock + 1-retry en StateVersionConflictError)
✅ `last_active_at` dentro del state (no external updated_at)
✅ ReentryHandler con bandas humanas exactas (24h-72h, 3d-7d, 7d+) + TRAJ-HV-010 para cobertura temporal
✅ Cost calc con normalización de modelo (PRICING + normalize en traces + RAG paths)
✅ Turn counter atómico (next_turn_number consulta hv_agent_traces con IS NOT DISTINCT FROM; denormalizado en state para lecturas rápidas)
✅ Feature flags (HV_FEATURE_*=false, default ON; controlan HEALTH_GATE, PROACTIVE_EXECUTION, RAG_LLM enrichment, etc.)
✅ Migrations versionadas con .down.sql (002_hv_beta_states)
✅ CI con tests (rag-bot-ci.yml: unit, RAG golden gates-only, pgvector, + proactive-smoke con dry/calibrate/quality gate/golden regression)
✅ Admin UI mínima (endpoints PIN + scripts + runbook + workflows + beta_ops_review)
✅ Doc de runbook actualizado (principios, comandos, fallas comunes, gates, métricas Guía, scheduled workflows)
✅ ADRs para decisiones clave (2026-06-10 para los 4 puntos + dual-write + turn SSOT + reentry; 2026-06-10 para se corrige/aprende con health+flags+drift+golden+CI; 2026-06-10 para RAG enrichment en proactive; 2026-06-10 para CI gates + proactive golden)
✅ Golden trajectories + calibración para Aprende (RAG golden + proactive-golden.json + runner + calibration con drift de signals + mensajes via difflib + baselines)
✅ GitHub Actions para scheduled (rag-bot-proactive.yml health-aware + calibrate + golden logic check; integración en rag-bot-nightly.yml con proactive-dry + golden)
✅ Health gating + self-correction (is_healthy en execute/nightly/workflows/CI; feature flags; drift penaliza health; blocks dejan acciones pending con trace)

Pendientes menores / nice-to-have (no bloquean cierre del núcleo; aclarados por el usuario):
- Admin UI visual completa: Per aclaración del usuario, la mención a NocoDB **no tiene relación** con esta implementación del núcleo agentic. La migración Airtable → NocoDB (sobre Neon Postgres) es un esfuerzo separado de datos/UI. Para este sprint agentic, los endpoints + scripts + runbook + workflows ya cubren la "admin UI mínima" que pide la Guía.
- Más ADRs: Se agregaron 2 adicionales en este cierre (RAG enrichment en proactive; CI gates + proactive golden). Quedan para decisiones futuras.
- Sprint closure reports formales: Se creó el primero (docs/sprints/2026-06-proactive-closure-report.md) con formato de la Guía (DoD, componentes, verificación, issues, próximos pasos).
- Ejecución real de acciones: El loop completo de decisión + "se corrige" (health gate + is_healthy + flags + dry por defecto + blocks con trace + logging) ya está listo y probado en todos los paths (CI, nightly, workflow, execute). El sender real (WhatsApp/Twilio/etc.) es out-of-scope del núcleo agentic de esta Guía. Se agregó un stub claro en `scripts/send_proactive_action.py` con TODOs para la integración futura.

Con los mecanismos de SSOT, traces, state+reentry, proactive con health/flags/calibration/golden, ops (endpoints+runbook+workflows+CI) y documentación (ADRs+runbook + sprint closure), el núcleo del agente proactivo según la Guía + tus 4 puntos está cerrado.

Mantén este runbook actualizado cuando agregues nuevas señales, acciones o cambios en el StateManager. Los ADRs deben crearse para decisiones importantes (template de la Guía).
