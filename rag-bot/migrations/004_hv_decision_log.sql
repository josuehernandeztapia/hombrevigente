-- HV Decision Log — memoria episódica en SSOT (Guía: el registro de decisiones
-- RAG vivía solo como JSONL en el volumen de UNA máquina Fly; no era consultable
-- ni sobrevivía a un escalado multi-máquina). Esta tabla es el destino Postgres
-- del dual-write de decision_log.py: el JSONL sigue como fallback local barato.
--
-- Siguiendo el patrón de 001/002/003: BEGIN/COMMIT + IF NOT EXISTS (idempotente),
-- prefijo hv_* para aislamiento en el mismo Neon.

BEGIN;

CREATE TABLE IF NOT EXISTS hv_decision_log (
  id         BIGSERIAL PRIMARY KEY,
  entry_id   TEXT NOT NULL UNIQUE,        -- uuid corto generado por RagDecisionEntry
  ts         TIMESTAMPTZ NOT NULL,
  beta_id    TEXT,
  channel    TEXT,
  source     TEXT,
  kb_route   TEXT,
  gate_path  TEXT,
  gate_code  TEXT,
  top_score  REAL,
  confidence TEXT,
  payload    JSONB NOT NULL DEFAULT '{}'::jsonb  -- fila completa (query ya redactada)
);

-- Lectura por ventana temporal (read_decisions / knowledge gaps semanal).
CREATE INDEX IF NOT EXISTS idx_hv_decision_log_ts
  ON hv_decision_log (ts DESC);
-- Historial por beta.
CREATE INDEX IF NOT EXISTS idx_hv_decision_log_beta
  ON hv_decision_log (beta_id, ts DESC);

COMMIT;
