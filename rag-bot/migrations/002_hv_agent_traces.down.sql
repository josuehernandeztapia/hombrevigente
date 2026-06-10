-- Down: HV Agent Traces
BEGIN;
DROP INDEX IF EXISTS idx_hv_agent_traces_idemp;
DROP INDEX IF EXISTS idx_hv_agent_traces_beta_created;
DROP TABLE IF EXISTS hv_agent_traces;
COMMIT;
