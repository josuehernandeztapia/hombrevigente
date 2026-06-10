"""
rag_retrieval_local.py (G5) — Local retrieval over knowledge_base/embeddings_local.json.

Recovers the source for the module action_handler imports best-effort
(`from rag_retrieval_local import rag_query_local`). Previously only a .pyc existed,
so RAG enrichment silently no-op'd. Contract kept identical:

    rag_query_local(query: str, *, use_llm: bool = False, top_k: int = 3) -> dict
        -> {"answer": str, "context": str, "chunks": [...], "scores": [...]}

Retrieval strategy (degrades gracefully, never raises):
  1. If OPENAI_API_KEY is set -> embed the query (text-embedding-3-small) and rank
     chunks by cosine similarity against the stored 1536-d embeddings.
  2. Otherwise -> lexical token-overlap (Jaccard) over chunk text, so enrichment
     still works offline / without API credentials.

use_llm=True is accepted for API parity but synthesis is optional: without an LLM
client available it returns the stitched top-k context as the answer.
"""
from __future__ import annotations

import json
import math
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_EMB_MODEL = "text-embedding-3-small"


def _kb_path() -> Path:
    candidates = [
        os.getenv("HV_KB_EMB_PATH", ""),
        "rag-bot/knowledge_base/embeddings_local.json",
        "knowledge_base/embeddings_local.json",
        "data/knowledge_base/embeddings_local.json",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return Path(c)
    # Default (may not exist -> callers treat empty index as no enrichment)
    return Path("knowledge_base/embeddings_local.json")


@lru_cache(maxsize=1)
def _load_index() -> Tuple[Tuple[str, ...], Tuple[Tuple[float, ...], ...]]:
    """Returns (texts, embeddings) as immutable tuples (cache-friendly). Empty if absent."""
    p = _kb_path()
    if not p.exists():
        return tuple(), tuple()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return tuple(), tuple()
    texts: List[str] = []
    embs: List[Tuple[float, ...]] = []
    for ch in data.get("chunks", []):
        t = ch.get("text")
        e = ch.get("embedding")
        if not t:
            continue
        texts.append(t)
        embs.append(tuple(e) if e else tuple())
    return tuple(texts), tuple(embs)


def _cosine(a: List[float], b: Tuple[float, ...]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


_TOKEN_RE = re.compile(r"[a-záéíóúñ0-9]+", re.IGNORECASE)


def _tokens(s: str) -> set:
    return set(_TOKEN_RE.findall((s or "").lower()))


def _lexical_score(query: str, text: str) -> float:
    q, t = _tokens(query), _tokens(text)
    if not q or not t:
        return 0.0
    inter = len(q & t)
    if inter == 0:
        return 0.0
    return inter / len(q | t)  # Jaccard


def _embed_query(query: str) -> Optional[List[float]]:
    """Embed via OpenAI if key present; None otherwise (caller falls back to lexical)."""
    if not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI  # lazy, optional dependency
        client = OpenAI()
        resp = client.embeddings.create(model=_EMB_MODEL, input=query)
        return list(resp.data[0].embedding)
    except Exception:
        return None


def rag_query_local(
    query: str,
    *,
    use_llm: bool = False,
    top_k: int = 3,
) -> Dict[str, Any]:
    """Retrieve top-k chunks for `query`. Never raises; returns empty answer if no index."""
    texts, embs = _load_index()
    if not texts:
        return {"answer": "", "context": "", "chunks": [], "scores": []}

    qvec = _embed_query(query)
    scored: List[Tuple[float, int]] = []
    have_vectors = qvec is not None and any(len(e) for e in embs)
    if have_vectors:
        for i, e in enumerate(embs):
            scored.append((_cosine(qvec, e), i))  # type: ignore[arg-type]
    else:
        for i, t in enumerate(texts):
            scored.append((_lexical_score(query, t), i))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [(s, i) for s, i in scored[:top_k] if s > 0]

    chunks = [texts[i] for _, i in top]
    scores = [round(s, 4) for s, _ in top]
    context = "\n\n".join(chunks)
    # use_llm synthesis is optional; without an LLM client we return the context as answer.
    answer = context if not use_llm else _maybe_synthesize(query, context)
    return {"answer": answer, "context": context, "chunks": chunks, "scores": scores,
            "retrieval": "cosine" if have_vectors else "lexical"}


def _maybe_synthesize(query: str, context: str) -> str:
    """Optional LLM synthesis (Anthropic). Falls back to raw context if unavailable."""
    if not context or not os.getenv("ANTHROPIC_API_KEY"):
        return context
    try:
        from anthropic import Anthropic  # lazy, optional
        client = Anthropic()
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            messages=[{"role": "user",
                       "content": f"Contexto:\n{context}\n\nPregunta: {query}\n"
                                  f"Responde breve y solo con base en el contexto."}],
        )
        parts = [b.text for b in msg.content if getattr(b, "type", None) == "text"]
        return ("".join(parts)).strip() or context
    except Exception:
        return context
