-- Down: HV Beta States
BEGIN;
DROP INDEX IF EXISTS idx_hv_beta_states_last_active;
DROP TABLE IF EXISTS hv_beta_states;
COMMIT;
