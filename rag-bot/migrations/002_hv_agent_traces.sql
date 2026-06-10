-- HV Agent Traces — SSOT atómico de turn_number + costo por evento del agente.
-- Resuelve el race del turn_number denormalizado en state_data (ver state_persistence.py L15).
-- next_turn_number(beta_id) hace allocation atómico via UNIQUE(beta_id, turn_number) + advisory lock.
-- También registra costo/tokens de cada acción (proactiva o reactiva) para el factor "cost" del health score
-- y para receipts del sender real (send_proactive_action.py / sender.py).
BEGIN;

CREATE TABLE IF NOT EXISTS hv_agent_traces (
  id            BIGSERIAL PRIMARY KEY,
  beta_id       TEXT        NOT NULL,
  turn_number   INTEGER     NOT NULL,
  role          TEXT        NOT NULL DEFAULT 'proactive',   -- proactive | reactive | system
  event_type    TEXT,                                       -- send | block | generate | receipt | ...
  action_id     TEXT,
  idemp_key     TEXT,
  model         TEXT,
  tokens_in     INTEGER     NOT NULL DEFAULT 0,
  tokens_out    INTEGER     NOT NULL DEFAULT 0,
  cost_usd      NUMERIC(12,6) NOT NULL DEFAULT 0,
  status        TEXT,                                       -- sent | failed | executed | dry_run_executed | blocked
  metadata      JSONB       NOT NULL DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  -- Allocation atómico de turn_number por beta: dos inserts concurrentes con el mismo
  -- (beta_id, turn_number) chocan contra este UNIQUE en vez de duplicar el turno.
  CONSTRAINT uq_hv_agent_traces_beta_turn UNIQUE (beta_id, turn_number)
);

-- Timeline por beta + costo agregado por ventana.
CREATE INDEX IF NOT EXISTS idx_hv_agent_traces_beta_created
  ON hv_agent_traces (beta_id, created_at DESC);
-- Lookup de receipts/idempotencia por acción.
CREATE INDEX IF NOT EXISTS idx_hv_agent_traces_idemp
  ON hv_agent_traces (idemp_key);

COMMIT;
