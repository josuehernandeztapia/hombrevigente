BEGIN;

DROP INDEX IF EXISTS idx_hv_kb_chunks_fts;
DROP INDEX IF EXISTS idx_hv_kb_chunks_embedding;
DROP INDEX IF EXISTS idx_hv_kb_chunks_hash;
DROP INDEX IF EXISTS idx_hv_kb_chunks_kb_type;
DROP INDEX IF EXISTS idx_hv_embedding_runs_started;

DROP TABLE IF EXISTS hv_embedding_runs;
DROP TABLE IF EXISTS hv_kb_chunks;

COMMIT;