-- HV Pending Actions — Idempotencia C1 (Guía: acciones proactivas exactly-once)
-- Ledger atómico de acciones proactivas para deduplicación fuerte cuando
-- HV_STATE_PERSISTENCE=postgres|dual. El UNIQUE en idemp_key previene doble
-- persist/ejecución incluso si el cron y un run manual corren a la vez.
-- El store operativo sigue siendo el JSONL (load/execute); esta tabla es el
-- ledger de idempotencia (persist = INSERT ON CONFLICT, execute = is_idemp + mark).
--
-- Siguiendo el patrón de 001/002: BEGIN/COMMIT + IF NOT EXISTS (idempotente),
-- prefijo hv_* para aislamiento en el mismo Neon.

BEGIN;

CREATE TABLE IF NOT EXISTS hv_pending_actions (
  id                BIGSERIAL PRIMARY KEY,
  beta_id           TEXT NOT NULL,
  action_id         TEXT,
  idemp_key         TEXT NOT NULL UNIQUE,            -- C1: beta:signal:phase:hour_bucket
  signal_type       TEXT,
  action_type       TEXT,
  suggested_message TEXT,
  status            TEXT NOT NULL DEFAULT 'pending', -- pending | executed | dry_run_executed | blocked_*
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  executed_at       TIMESTAMPTZ,
  metadata          JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Lookup por idempotencia (el UNIQUE ya crea índice, pero lo dejamos explícito por status).
CREATE INDEX IF NOT EXISTS idx_hv_pending_actions_idemp_status
  ON hv_pending_actions (idemp_key, status);
-- Cola por beta + estado.
CREATE INDEX IF NOT EXISTS idx_hv_pending_actions_beta_status
  ON hv_pending_actions (beta_id, status, created_at DESC);

COMMIT;
