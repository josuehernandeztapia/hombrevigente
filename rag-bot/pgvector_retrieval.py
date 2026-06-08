"""
Retrieval RAG vía Neon/pgvector — patrón CMU partes-mercado-retrieval.ts.

Activo cuando HV_RETRIEVAL_BACKEND=pgvector y DATABASE_URL apunta a Postgres.
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

from confidence_gate import score_to_confidence
from kb_pipeline import (
    SCORE_COSINE_WEIGHT,
    SCORE_META_WEIGHT,
    TIER_WEIGHTS,
    CONFIDENCE_WEIGHTS,
)
from query_preprocess import strip_command_words

EMBEDDING_DIMS = 1536


def _tier_weight(tier: str) -> float:
    return TIER_WEIGHTS.get(tier.upper(), 0.65)


def _confidence_weight(conf: str) -> float:
    return CONFIDENCE_WEIGHTS.get(conf.lower(), 0.70)


def _combined_score(cosine: float, meta: Dict[str, Any]) -> float:
    tier_w = _tier_weight(meta.get("evidencia_tier", "unknown"))
    if meta.get("doc_subtype") == "tarjeta":
        tier_w = max(tier_w, _confidence_weight(meta.get("confianza", "media")))
    return SCORE_COSINE_WEIGHT * cosine + SCORE_META_WEIGHT * tier_w


def database_url() -> Optional[str]:
    url = os.getenv("HV_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    url = url.strip()
    if not url or url.startswith("sqlite"):
        return None
    if "postgres" not in url:
        return None
    return url


def is_pgvector_configured() -> bool:
    return database_url() is not None


def vector_literal(vec: List[float]) -> str:
    return "[" + ",".join(f"{v:.6f}" for v in vec) + "]"


@contextmanager
def _connection():
    import psycopg

    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL/HV_DATABASE_URL postgres no configurada")
    conn = psycopg.connect(url)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _embed_query(query: str, *, preprocess: bool = True) -> List[float]:
    from rag_retrieval_local import embed_query

    return embed_query(query, preprocess=preprocess)


def _row_to_candidate(row: Dict[str, Any]) -> Dict[str, Any]:
    meta = row.get("metadata") or {}
    if isinstance(meta, str):
        meta = json.loads(meta)
    cosine = float(row["cosine"])
    combined = _combined_score(cosine, meta)
    conf = score_to_confidence(combined)
    return {
        "id": row["id"],
        "text": row["text"],
        "cosine": cosine,
        "score": combined,
        "confidence": conf,
        "service_name": row.get("service_name") or meta.get("service_name", ""),
        "section_title": row.get("section_title") or meta.get("section_title", ""),
        "kb_type": row.get("kb_type", meta.get("kb_type", "")),
        "metadata": meta,
    }


def retrieve_pgvector(
    query: str,
    *,
    kb_route: str = "all",
    top_k: int = 5,
    avenida_max: str = "1",
    min_confidence: str = "medium",
) -> List[Dict[str, Any]]:
    query_vec = _embed_query(query)
    q_lit = vector_literal(query_vec)
    fetch_k = max(top_k * 4, 20)

    sql = """
        SELECT id, text, kb_type, service_name, section_title, metadata,
               1 - (embedding <=> %s::vector) AS cosine
        FROM hv_kb_chunks
        WHERE is_active = true
          AND embedding IS NOT NULL
          AND (%s = 'all' OR kb_type = %s)
          AND has_falta_fuente = false
          AND NOT (flag_seguridad = 'alto-riesgo' AND %s = 'longevity')
          AND NOT (%s = '1' AND avenida_hv = '2')
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """
    params = (
        q_lit,
        kb_route,
        kb_route,
        kb_route,
        avenida_max,
        q_lit,
        fetch_k,
    )

    import psycopg
    from psycopg.rows import dict_row

    with _connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

    candidates: List[Dict[str, Any]] = []
    for row in rows:
        cand = _row_to_candidate(row)
        conf = cand["confidence"]
        if kb_route == "longevity" and conf == "low":
            continue
        if min_confidence == "high" and conf != "high":
            continue
        candidates.append(cand)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]


def upsert_chunk(
    chunk: Dict[str, Any],
    *,
    conn: Any,
) -> bool:
    meta = chunk.get("metadata", {})
    emb = chunk.get("embedding")
    if not emb:
        return False

    sql = """
        INSERT INTO hv_kb_chunks (
            id, text, content_hash, kb_type, doc_subtype, avenida_hv,
            evidencia_tier, has_falta_fuente, flag_seguridad,
            service_name, section_title, metadata, embedding, embedded_at, updated_at
        ) VALUES (
            %(id)s, %(text)s, %(content_hash)s, %(kb_type)s, %(doc_subtype)s, %(avenida_hv)s,
            %(evidencia_tier)s, %(has_falta_fuente)s, %(flag_seguridad)s,
            %(service_name)s, %(section_title)s, %(metadata)s::jsonb,
            %(embedding)s::vector, NOW(), NOW()
        )
        ON CONFLICT (id) DO UPDATE SET
            text = EXCLUDED.text,
            content_hash = EXCLUDED.content_hash,
            kb_type = EXCLUDED.kb_type,
            doc_subtype = EXCLUDED.doc_subtype,
            avenida_hv = EXCLUDED.avenida_hv,
            evidencia_tier = EXCLUDED.evidencia_tier,
            has_falta_fuente = EXCLUDED.has_falta_fuente,
            flag_seguridad = EXCLUDED.flag_seguridad,
            service_name = EXCLUDED.service_name,
            section_title = EXCLUDED.section_title,
            metadata = EXCLUDED.metadata,
            embedding = EXCLUDED.embedding,
            embedded_at = NOW(),
            updated_at = NOW(),
            is_active = true
        WHERE hv_kb_chunks.content_hash IS DISTINCT FROM EXCLUDED.content_hash
    """
    params = {
        "id": chunk["id"],
        "text": chunk["text"],
        "content_hash": chunk.get("content_hash", ""),
        "kb_type": meta.get("kb_type", "longevity"),
        "doc_subtype": meta.get("doc_subtype", "monografia"),
        "avenida_hv": meta.get("avenida_hv", "unknown"),
        "evidencia_tier": meta.get("evidencia_tier", "unknown"),
        "has_falta_fuente": bool(meta.get("has_falta_fuente")),
        "flag_seguridad": meta.get("flag_seguridad", "ninguno"),
        "service_name": meta.get("service_name"),
        "section_title": meta.get("section_title"),
        "metadata": json.dumps(meta, ensure_ascii=False),
        "embedding": vector_literal(emb),
    }
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount > 0


def sync_chunks_to_pgvector(
    chunks: List[Dict[str, Any]],
    *,
    trigger: str = "manual",
) -> Dict[str, int]:
    embedded = skipped = 0
    with _connection() as conn:
        for chunk in chunks:
            if upsert_chunk(chunk, conn=conn):
                embedded += 1
            else:
                skipped += 1
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO hv_embedding_runs
                    (finished_at, n_embedded, n_skipped, n_total, trigger)
                VALUES (NOW(), %s, %s, %s, %s)
                """,
                (embedded, skipped, len(chunks), trigger),
            )
    return {"embedded": embedded, "skipped": skipped, "total": len(chunks)}


def run_migration(sql_path: Optional[str] = None) -> None:
    path = sql_path or str(
        __import__("pathlib").Path(__file__).resolve().parent
        / "migrations"
        / "001_hv_kb_embeddings.sql"
    )
    sql = open(path, encoding="utf-8").read()
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)