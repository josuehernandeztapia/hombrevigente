-- HV Pending Actions — C1 de la Guía + auditoría
BEGIN;
CREATE TABLE IF NOT EXISTS hv_pending_actions (
  id BIGSERIAL PRIMARY KEY,
  beta_id TEXT NOT NULL,
  action_id TEXT NOT NULL,
  idemp_key TEXT NOT NULL UNIQUE,
  signal_type TEXT,
  action_type TEXT,
  suggested_message TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  executed_at TIMESTAMPTZ,
  dry_run BOOLEAN DEFAULT FALSE,
  block_reason JSONB,
  metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_hv_pending_actions_beta_status ON hv_pending_actions (beta_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_hv_pending_actions_idemp ON hv_pending_actions (idemp_key);
COMMIT;
