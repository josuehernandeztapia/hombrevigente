BEGIN;

DROP INDEX IF EXISTS idx_hv_decision_log_beta;
DROP INDEX IF EXISTS idx_hv_decision_log_ts;
DROP TABLE IF EXISTS hv_decision_log;

COMMIT;
