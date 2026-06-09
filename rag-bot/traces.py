"""
Full Agent Turn Traces — Fase 3 (Capa 2 de la Guía Agéntica Estándar).

Persiste cada turno del agente con:
- input/output
- branch_taken (determinista, gate, rag, llm, etc.)
- state_before / state_after (snapshots del BetaState)
- llm_calls (array con modelo, tokens si disponible)
- latency_ms, total_cost_usd (stub + normalización)
- turn_number, beta_id (como origination), role, success, error
- Fire-and-forget: el INSERT NUNCA bloquea la respuesta al usuario.

Uso:
    from traces import persist_turn_trace, build_turn_payload
    payload = build_turn_payload(...)
    persist_turn_trace(payload)   # no espera

Admin endpoints (PIN-gated) se agregan en api/main.py.

Reutiliza redacción PII de decision_log.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# Reutilizar redacción de PII (ya probada)
try:
    from decision_log import redact_for_preview, _default_log_path as _decision_log_path
except Exception:
    def redact_for_preview(text: str) -> str:
        return text[:200] + "…" if len(text) > 200 else text
    _decision_log_path = None

# Reutilizar conexión Postgres del layer existente
try:
    from pgvector_retrieval import _connection, is_pgvector_configured
except Exception:
    _connection = None
    is_pgvector_configured = lambda: False


def _traces_enabled() -> bool:
    return os.getenv("HV_TRACES_ENABLED", "true").lower() not in ("0", "false", "no")


def _get_db_connection():
    if not is_pgvector_configured or not is_pgvector_configured():
        return None
    if _connection is None:
        return None
    try:
        return _connection()
    except Exception:
        return None


def normalize_model_id(model: str) -> str:
    """
    Patrón exacto de la Guía Agéntica Estándar para que los costos no den 0 silenciosamente.
    Quita sufijos de release (gpt-4o-mini-2024-07-18 → gpt-4o-mini).
    """
    if not model:
        return model
    import re
    # OpenAI style
    stripped = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", model)
    if stripped != model:
        return stripped
    # Anthropic legacy
    stripped2 = re.sub(r"-\d{8}$", "", model)
    if stripped2 != model:
        return stripped2
    return model


# Pricing table (USD per 1M tokens) — fácil de extender. 
# Fuente aproximada 2025 para los modelos que usa HV.
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 5.0, "output": 15.0},
    "gpt-4o-2024-08-06": {"input": 5.0, "output": 15.0},  # alias
}

def _estimate_cost(model: str, prompt_tokens: int = 0, completion_tokens: int = 0) -> float:
    """Calcula costo usando normalize + tabla de precios. Stub realista."""
    norm = normalize_model_id(model or "")
    price = PRICING.get(norm) or PRICING.get("gpt-4o-mini")
    # fallback muy conservador
    inp = price.get("input", 0.15) / 1_000_000
    out = price.get("output", 0.60) / 1_000_000
    return (prompt_tokens * inp) + (completion_tokens * out)


def build_turn_payload(
    *,
    beta_id: Optional[str] = None,
    turn_number: Optional[int] = None,
    role: str = "concierge",
    phase: Optional[str] = None,
    input_body: str = "",
    input_metadata: Optional[Dict] = None,
    branch_taken: str = "unknown",
    output_body: str = "",
    output_confidence: Optional[str] = None,
    latency_ms: Optional[int] = None,
    llm_calls: Optional[List[Dict]] = None,
    state_before: Optional[Dict] = None,
    state_after: Optional[Dict] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    channel: Optional[str] = None,
) -> Dict[str, Any]:
    """Construye el payload completo para hv_agent_traces."""
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "beta_id": beta_id,
        "turn_number": turn_number,
        "role": role,
        "phase": phase,
        "input_body": redact_for_preview(input_body) if input_body else None,
        "input_metadata": input_metadata or {},
        "branch_taken": branch_taken,
        "output_body": redact_for_preview(output_body) if output_body else None,
        "output_confidence": output_confidence,
        "latency_ms": latency_ms,
        "total_cost_usd": 0.0,
        "llm_calls": llm_calls or [],
        "state_before": state_before,
        "state_after": state_after,
        "success": success,
        "error_message": error_message,
        "channel": channel,
        "created_at": now,
    }

    # Calcular costo si hay llm_calls
    total_cost = 0.0
    for call in (llm_calls or []):
        model = call.get("model", "")
        pt = call.get("prompt_tokens", 0) or 0
        ct = call.get("completion_tokens", 0) or 0
        total_cost += _estimate_cost(model, pt, ct)
    payload["total_cost_usd"] = round(total_cost, 6)

    return payload


def persist_turn_trace(payload: Dict[str, Any]) -> Optional[str]:
    """
    Fire-and-forget insert a hv_agent_traces.
    NUNCA lanza al caller. Patrón recomendado en la Guía.
    """
    if not _traces_enabled():
        return None

    # Si no hay DB, solo logueamos (o podríamos caer a JSONL extendido)
    conn_ctx = _get_db_connection()
    if conn_ctx is None:
        # Fallback silencioso: podríamos loguear a decision_log o stdout
        # Por ahora solo warn en dev
        if os.getenv("ENVIRONMENT", "development") == "development":
            print(f"[traces] (no-db) turn {payload.get('turn_number')} branch={payload.get('branch_taken')}")
        return None

    try:
        with conn_ctx as conn:
            with conn.cursor() as cur:
                sql = """
                    INSERT INTO hv_agent_traces (
                        beta_id, turn_number, role, phase,
                        input_body, input_metadata, branch_taken,
                        output_body, latency_ms, total_cost_usd,
                        llm_calls, state_before, state_after,
                        success, error_message, created_at
                    ) VALUES (
                        %(beta_id)s, %(turn_number)s, %(role)s, %(phase)s,
                        %(input_body)s, %(input_metadata)s::jsonb, %(branch_taken)s,
                        %(output_body)s, %(latency_ms)s, %(total_cost_usd)s,
                        %(llm_calls)s::jsonb, %(state_before)s::jsonb, %(state_after)s::jsonb,
                        %(success)s, %(error_message)s, %(created_at)s
                    )
                    RETURNING id
                """
                cur.execute(sql, {
                    "beta_id": payload.get("beta_id"),
                    "turn_number": payload.get("turn_number"),
                    "role": payload.get("role"),
                    "phase": payload.get("phase"),
                    "input_body": payload.get("input_body"),
                    "input_metadata": json.dumps(payload.get("input_metadata") or {}),
                    "branch_taken": payload.get("branch_taken"),
                    "output_body": payload.get("output_body"),
                    "latency_ms": payload.get("latency_ms"),
                    "total_cost_usd": payload.get("total_cost_usd"),
                    "llm_calls": json.dumps(payload.get("llm_calls") or []),
                    "state_before": json.dumps(payload.get("state_before") or {}),
                    "state_after": json.dumps(payload.get("state_after") or {}),
                    "success": payload.get("success", True),
                    "error_message": payload.get("error_message"),
                    "created_at": payload.get("created_at"),
                })
                row = cur.fetchone()
                return str(row[0]) if row else None
    except Exception as e:
        # Fire-and-forget: nunca romper el flujo
        print(f"[traces] WARN: insert failed (fail-open): {e}")
        return None


# ------------------------------------------------------------------
# Lectura para admin (simple, se puede enriquecer)
# ------------------------------------------------------------------

def read_traces(
    *,
    limit: int = 50,
    beta_id: Optional[str] = None,
    role: Optional[str] = None,
    errors_only: bool = False,
    since_hours: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Lee trazas desde Postgres (mejor esfuerzo)."""
    conn_ctx = _get_db_connection()
    if conn_ctx is None:
        return []

    try:
        with conn_ctx as conn:
            with conn.cursor() as cur:
                where = []
                params: List[Any] = []
                if beta_id:
                    where.append("beta_id = %s")
                    params.append(beta_id)
                if role:
                    where.append("role = %s")
                    params.append(role)
                if errors_only:
                    where.append("success = false")
                if since_hours:
                    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
                    where.append("created_at >= %s")
                    params.append(cutoff)

                sql = "SELECT * FROM hv_agent_traces"
                if where:
                    sql += " WHERE " + " AND ".join(where)
                sql += " ORDER BY created_at DESC LIMIT %s"
                params.append(limit)

                cur.execute(sql, params)
                rows = cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        print(f"[traces] WARN: read failed: {e}")
        return []


def get_trace_stats(window_hours: int = 24) -> Dict[str, Any]:
    conn_ctx = _get_db_connection()
    if conn_ctx is None:
        return {"window_hours": window_hours, "count": 0, "error_rate": 0.0}

    try:
        with conn_ctx as conn:
            with conn.cursor() as cur:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
                cur.execute(
                    """
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN success = false THEN 1 ELSE 0 END) as errors,
                        AVG(latency_ms) as avg_latency,
                        SUM(total_cost_usd) as total_cost,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) FILTER (WHERE latency_ms IS NOT NULL) as p50_latency,
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) FILTER (WHERE latency_ms IS NOT NULL) as p95_latency
                    FROM hv_agent_traces
                    WHERE created_at >= %s
                    """,
                    (cutoff,),
                )
                row = cur.fetchone()
                total = row[0] or 0
                errors = row[1] or 0
                p50 = row[4]
                p95 = row[5]
                return {
                    "window_hours": window_hours,
                    "count": total,
                    "errors": errors,
                    "error_rate": round(errors / total, 4) if total > 0 else 0.0,
                    "avg_latency_ms": round(row[2] or 0),
                    "p50_latency_ms": round(p50) if p50 is not None else None,
                    "p95_latency_ms": round(p95) if p95 is not None else None,
                    "total_cost_usd": round(row[3] or 0, 6),
                    "note": "p50/p95 computed over traces with latency_ms (Postgres PERCENTILE_CONT)",
                }
    except Exception:
        # Fallback (e.g. older PG without FILTER or no rows): return previous shape + approx
        try:
            # best effort recompute without percentiles
            with conn_ctx as conn:
                with conn.cursor() as cur:
                    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
                    cur.execute(
                        """
                        SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN success = false THEN 1 ELSE 0 END) as errors,
                            AVG(latency_ms) as avg_latency,
                            SUM(total_cost_usd) as total_cost
                        FROM hv_agent_traces
                        WHERE created_at >= %s
                        """,
                        (cutoff,),
                    )
                    row = cur.fetchone()
                    total = row[0] or 0
                    errors = row[1] or 0
                    avg = row[2] or 0
                    return {
                        "window_hours": window_hours,
                        "count": total,
                        "errors": errors,
                        "error_rate": round(errors / total, 4) if total > 0 else 0.0,
                        "avg_latency_ms": round(avg),
                        "p50_latency_ms": round(avg),
                        "p95_latency_ms": round(avg * 1.8),
                        "total_cost_usd": round(row[3] or 0, 6),
                        "note": "percentiles approximated from avg (no DB percentile support or no latency data)",
                    }
        except Exception:
            return {"window_hours": window_hours, "count": 0, "error_rate": 0.0}
