-- HV RAG — pgvector scaffold (patrón CMU 0032_partes_mercado_embeddings.sql)
--
-- Tabla de chunks del knowledge base HV con embeddings text-embedding-3-small (1536).
-- Re-embed diferencial vía content_hash (mismo patrón que embed_kb_local.py / JSON).

BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS hv_kb_chunks (
  id TEXT PRIMARY KEY,
  text TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  kb_type TEXT NOT NULL CHECK (kb_type IN ('servicios', 'longevity')),
  doc_subtype TEXT NOT NULL DEFAULT 'monografia',
  avenida_hv TEXT NOT NULL DEFAULT 'unknown',
  evidencia_tier TEXT NOT NULL DEFAULT 'unknown',
  has_falta_fuente BOOLEAN NOT NULL DEFAULT false,
  flag_seguridad TEXT NOT NULL DEFAULT 'ninguno',
  service_name TEXT,
  section_title TEXT,
  metadata JSONB NOT NULL DEFAULT '{}',
  embedding vector(1536),
  embedded_at TIMESTAMPTZ,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hv_kb_chunks_kb_type
  ON hv_kb_chunks (kb_type) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_hv_kb_chunks_hash
  ON hv_kb_chunks (content_hash);

CREATE INDEX IF NOT EXISTS idx_hv_kb_chunks_embedding
  ON hv_kb_chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 50);

-- Hybrid FTS (opcional — combinar con vector en MVP-1)
ALTER TABLE hv_kb_chunks
  ADD COLUMN IF NOT EXISTS search_vector tsvector
  GENERATED ALWAYS AS (to_tsvector('spanish', coalesce(text, ''))) STORED;

CREATE INDEX IF NOT EXISTS idx_hv_kb_chunks_fts
  ON hv_kb_chunks USING gin (search_vector);

CREATE TABLE IF NOT EXISTS hv_embedding_runs (
  id SERIAL PRIMARY KEY,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  n_embedded INTEGER NOT NULL DEFAULT 0,
  n_skipped INTEGER NOT NULL DEFAULT 0,
  n_total INTEGER NOT NULL DEFAULT 0,
  model TEXT NOT NULL DEFAULT 'text-embedding-3-small',
  trigger TEXT NOT NULL,
  error TEXT
);

CREATE INDEX IF NOT EXISTS idx_hv_embedding_runs_started
  ON hv_embedding_runs (started_at DESC);

COMMIT;