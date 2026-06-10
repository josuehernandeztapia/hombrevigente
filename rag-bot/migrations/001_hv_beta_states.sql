-- HV Beta States — SSOT de estado por beta (modo HV_STATE_PERSISTENCE=postgres)
-- Columnas derivadas de state_persistence.py (_load_from_postgres / _save_to_postgres / scan_all_states):
--   beta_id (PK, requerido por ON CONFLICT (beta_id)), state_data JSONB, state_version (optimistic lock),
--   updated_at (SET NOW() en cada save). created_at/last_active_at para auditoría + ReentryHandler (Fase 4).
-- Nota: turn_number y last_active_at viven hoy denormalizados dentro de state_data; la columna
--   last_active_at queda disponible (nullable) para escaneos de reentry sin parsear el JSONB.
BEGIN;

CREATE TABLE IF NOT EXISTS hv_beta_states (
  beta_id        TEXT PRIMARY KEY,
  state_data     JSONB       NOT NULL DEFAULT '{}'::jsonb,
  state_version  INTEGER     NOT NULL DEFAULT 0,
  last_active_at TIMESTAMPTZ,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Escaneo de reentry / proactivo por inactividad (state_persistence.scan_all_states + ReentryHandler).
CREATE INDEX IF NOT EXISTS idx_hv_beta_states_last_active
  ON hv_beta_states (last_active_at DESC NULLS LAST);

COMMIT;
