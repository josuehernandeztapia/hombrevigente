-- Rollback de 002_hv_beta_states.sql
-- Siguiendo el patrón del documento: .down.sql explícito

BEGIN;

DROP INDEX IF EXISTS idx_hv_agent_traces_created;
DROP INDEX IF EXISTS idx_hv_agent_traces_beta_turn;
DROP INDEX IF EXISTS idx_hv_beta_state_last_active;
DROP INDEX IF EXISTS idx_hv_beta_state_phase;

DROP TABLE IF EXISTS hv_agent_traces;
DROP TABLE IF EXISTS hv_beta_states;

COMMIT;
