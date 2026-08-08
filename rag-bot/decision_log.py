"""
Audit trail de decisiones RAG — patrón CMU agent-decision-log.ts (fail-open JSONL).

Dual-write (migración 004): además del JSONL local, cada decisión se inserta
best-effort en hv_decision_log (Postgres SSOT). La lectura prefiere Postgres
cuando está configurado — así knowledge gaps ve TODAS las máquinas, no solo
el volumen local. Un `path` explícito fuerza modo archivo (tests, tooling).
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Postgres opcional — mismo patrón guarded-import de traces.py.
try:
    from pgvector_retrieval import _connection, is_pgvector_configured
except Exception:
    _connection = None
    is_pgvector_configured = lambda: False  # noqa: E731

REDACT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"sk-[A-Za-z0-9_\-]{20,}"), "[OPENAI_KEY]"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[EMAIL]"),
    (re.compile(r"\+?\d{10,15}"), "[PHONE]"),
]


def _default_log_path() -> Path:
    return Path(os.getenv("HV_DECISION_LOG_PATH", "data/decision_log.jsonl"))


def redact_for_preview(text: str) -> str:
    out = text
    for pattern, repl in REDACT_PATTERNS:
        out = pattern.sub(repl, out)
    if len(out) > 200:
        out = out[:200] + "…"
    return out


@dataclass
class RagDecisionEntry:
    query: str
    query_normalized: str
    kb_route: str
    gate_path: str
    role: str = "default"
    gate_code: Optional[str] = None
    top_score: Optional[float] = None
    confidence: Optional[str] = None
    chunks_used: int = 0
    top_service: Optional[str] = None
    latency_ms: Optional[int] = None
    source: str = "cli"
    use_llm: bool = True
    beta_id: Optional[str] = None
    turn_number: Optional[int] = None
    channel: Optional[str] = None
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_json(self) -> Dict[str, Any]:
        d = asdict(self)
        d["query"] = redact_for_preview(self.query)
        return d


def _logging_enabled() -> bool:
    return os.getenv("HV_DECISION_LOG_ENABLED", "true").lower() not in (
        "0",
        "false",
        "no",
    )


def _pg_enabled() -> bool:
    """True si el dual-write a hv_decision_log debe intentarse."""
    if os.getenv("HV_DECISION_LOG_PG", "true").lower() in ("0", "false", "no"):
        return False
    try:
        return _connection is not None and is_pgvector_configured()
    except Exception:
        return False


def _parse_ts(raw: str) -> datetime:
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _write_to_postgres(row: Dict[str, Any]) -> bool:
    """INSERT fail-open a hv_decision_log. Nunca lanza al caller."""
    try:
        with _connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO hv_decision_log
                        (entry_id, ts, beta_id, channel, source, kb_route,
                         gate_path, gate_code, top_score, confidence, payload)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (entry_id) DO NOTHING
                    """,
                    (
                        row.get("entry_id"),
                        _parse_ts(row["timestamp"]),
                        row.get("beta_id"),
                        row.get("channel"),
                        row.get("source"),
                        row.get("kb_route"),
                        row.get("gate_path"),
                        row.get("gate_code"),
                        row.get("top_score"),
                        row.get("confidence"),
                        json.dumps(row, ensure_ascii=False),
                    ),
                )
        return True
    except Exception as e:
        print(f"[decision-log] WARN: postgres insert failed (fail-open): {e}")
        return False


def _read_from_postgres(cutoff: datetime) -> Optional[List[Dict[str, Any]]]:
    """SELECT por ventana. None = error (el caller cae a archivo)."""
    try:
        with _connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT payload FROM hv_decision_log WHERE ts >= %s ORDER BY ts ASC",
                    (cutoff,),
                )
                rows: List[Dict[str, Any]] = []
                for (payload,) in cur.fetchall():
                    rows.append(payload if isinstance(payload, dict) else json.loads(payload))
                return rows
    except Exception as e:
        print(f"[decision-log] WARN: postgres read failed, falling back to file: {e}")
        return None


def log_rag_decision(entry: RagDecisionEntry, path: Optional[Path] = None) -> Optional[str]:
    """Append JSONL + INSERT best-effort a Postgres. Fail-open: nunca lanza al caller.

    `path` explícito = modo archivo puro (tests/tooling operan sobre un log concreto).
    """
    if not _logging_enabled():
        return None
    row = entry.to_json()
    log_path = path or _default_log_path()
    file_ok = False
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(row, ensure_ascii=False)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        file_ok = True
    except OSError as e:
        print(f"[decision-log] warn: could not write {log_path}: {e}")

    pg_ok = False
    if path is None and _pg_enabled():
        pg_ok = _write_to_postgres(row)

    return entry.entry_id if (file_ok or pg_ok) else None


def read_decisions(
    *,
    days: int = 7,
    path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Postgres primero (SSOT cross-máquina); archivo como bootstrap/fallback.
    if path is None and _pg_enabled():
        rows = _read_from_postgres(cutoff)
        if rows:
            return rows

    log_path = path or _default_log_path()
    if not log_path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with log_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = row.get("timestamp")
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if dt >= cutoff:
                rows.append(row)
    return rows


def log_from_rag_result(
    result: Dict[str, Any],
    *,
    query_normalized: str,
    role: str = "default",
    source: str = "cli",
    use_llm: bool = True,
    latency_ms: Optional[int] = None,
    beta_id: Optional[str] = None,
    turn_number: Optional[int] = None,
    channel: Optional[str] = None,
) -> Optional[str]:
    sources = result.get("sources") or []
    top_service = sources[0].get("service") if sources else None
    parse_block = result.get("parse") or {}
    top_score = parse_block.get("top_score")
    if top_score is None and sources:
        top_score = sources[0].get("score")

    entry = RagDecisionEntry(
        query=result.get("query", ""),
        query_normalized=query_normalized,
        kb_route=result.get("kb_route", "all"),
        gate_path=result.get("gate_path", "unknown"),
        role=role,
        gate_code=result.get("gate"),
        top_score=float(top_score) if top_score is not None else None,
        confidence=result.get("confidence"),
        chunks_used=int(result.get("chunks_used") or len(sources)),
        top_service=top_service,
        latency_ms=latency_ms,
        source=source,
        use_llm=use_llm,
        beta_id=beta_id,
        turn_number=turn_number,
        channel=channel,
    )
    return log_rag_decision(entry)