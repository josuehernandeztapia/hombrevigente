-- Rollback de 003_hv_pending_actions.sql
-- Siguiendo el patrón del documento: .down.sql explícito

BEGIN;

DROP INDEX IF EXISTS idx_hv_pending_actions_beta_status;
DROP INDEX IF EXISTS idx_hv_pending_actions_idemp_status;

DROP TABLE IF EXISTS hv_pending_actions;

COMMIT;
