-- HV Operational State — Capa 1+3 de la Guía Agéntica Estándar
-- Tabla hv_beta_states: SSOT para estado resumible de betas (phase, slots, turn_count, history, etc.)
-- state_data JSONB + state_version para optimistic locking (patrón exacto de la guía)
-- Incluye skeleton de hv_agent_traces para preparación de Fase 3 (traces completos)
--
-- Siguiendo:
-- - BEGIN/COMMIT + IF NOT EXISTS (idempotente)
-- - Índices parciales sobre paths JSONB
-- - last_active_at dentro de state_data (SSOT para ReentryHandler)
-- - Prefijo hv_* para aislamiento en el mismo Neon (igual que hv_kb_chunks)

BEGIN;

CREATE TABLE IF NOT EXISTS hv_beta_states (
  beta_id TEXT PRIMARY KEY,
  state_data JSONB NOT NULL DEFAULT '{}'::jsonb,
  state_version INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices parciales (rápidos y baratos) — patrón guía
CREATE INDEX IF NOT EXISTS idx_hv_beta_state_phase
  ON hv_beta_states ((state_data->>'phase'))
  WHERE (state_data->>'phase') IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_hv_beta_state_last_active
  ON hv_beta_states ((state_data->>'last_active_at') DESC NULLS LAST);

-- Skeleton para traces (se enriquecerá en Fase 3)
-- turn_number se calculará de forma atómica desde aquí (ver persistencia)
CREATE TABLE IF NOT EXISTS hv_agent_traces (
  id BIGSERIAL PRIMARY KEY,
  beta_id TEXT,
  turn_number INTEGER,
  role TEXT DEFAULT 'concierge',
  phase TEXT,
  input_body TEXT,
  input_metadata JSONB DEFAULT '{}'::jsonb,
  branch_taken TEXT,
  output_body TEXT,
  latency_ms INTEGER,
  total_cost_usd NUMERIC(10,6),
  llm_calls JSONB DEFAULT '[]'::jsonb,
  state_before JSONB,
  state_after JSONB,
  success BOOLEAN,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hv_agent_traces_beta_turn
  ON hv_agent_traces (beta_id, turn_number DESC);

CREATE INDEX IF NOT EXISTS idx_hv_agent_traces_created
  ON hv_agent_traces (created_at DESC);

-- Nota: el counter atómico de turn_number se implementa en Python (Fase 1/3)
-- usando MAX sobre esta tabla + IS NOT DISTINCT FROM (patrón guía)

COMMIT;
