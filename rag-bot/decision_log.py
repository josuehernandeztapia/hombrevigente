"""
Audit trail de decisiones RAG — patrón CMU agent-decision-log.ts (fail-open JSONL).
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


def log_rag_decision(entry: RagDecisionEntry, path: Optional[Path] = None) -> Optional[str]:
    """Append una fila JSONL. Fail-open: nunca lanza al caller."""
    if not _logging_enabled():
        return None
    log_path = path or _default_log_path()
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry.to_json(), ensure_ascii=False)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        return entry.entry_id
    except OSError as e:
        print(f"[decision-log] warn: could not write {log_path}: {e}")
        return None


def read_decisions(
    *,
    days: int = 7,
    path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    log_path = path or _default_log_path()
    if not log_path.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
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