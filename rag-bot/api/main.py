"""
api/main.py — FastAPI surface for RAG + admin/proactive ops (health, calibrate, agent_status).

Audit-relevant fixes implemented:
- S1/S2: PIN via X-Admin-Pin header only (no Query default), _admin_pin_ok fail-closed (if not match: False).
- S3: CORS explicit origins (no "*" + credentials). See _origins.
- S4: Rate limiting for public LLM endpoints (/rag/query). Uses slowapi when available + simple window _check_ratelimit as fallback. HV_RATELIMIT_RPM env (default 20).
- Health includes ssot, is_healthy (from action_handler), rate limit status, feature flags, calibrate_endpoint.
- /admin/* require header pin (fail closed). /admin/calibrate dynamically imports the calibrate script.

Ref: AUDITORIA_CODIGO_HV_2026-06-09.md (S1-S4), Guía 7-layer admin/ops + health gating.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# --- S4 rate limit (slowapi preferred, window fallback always available) ---
_HAS_SLOWAPI = False
try:
    from slowapi import Limiter  # type: ignore
    from slowapi.util import get_remote_address  # type: ignore
    from slowapi.errors import RateLimitExceeded  # type: ignore
    from slowapi.middleware import SlowAPIMiddleware  # type: ignore
    _HAS_SLOWAPI = True
except Exception:
    _HAS_SLOWAPI = False

HV_RATELIMIT_RPM = int(os.getenv("HV_RATELIMIT_RPM", "20"))
_rl_store: Dict[str, List[float]] = {}  # ip -> sliding window of timestamps (fallback only)


def _check_ratelimit(ip: str, rpm: int = HV_RATELIMIT_RPM) -> bool:
    """Simple in-memory window rate limiter (fallback when slowapi not present). Prunes >60s."""
    now = time.time()
    q = _rl_store.setdefault(ip, [])
    # prune old
    while q and (now - q[0] > 60.0):
        q.pop(0)
    if len(q) >= rpm:
        return False
    q.append(now)
    return True


# --- Auth (S1/S2: header only + fail-closed) ---
_EXPECTED_ADMIN_PIN = os.getenv("HV_ADMIN_PIN", "").strip()


def _admin_pin_ok(provided: Optional[str]) -> bool:
    if not _EXPECTED_ADMIN_PIN:
        # If no pin configured, be conservative in non-local: fail closed.
        # For local dev without pin you can export HV_ADMIN_PIN=testpin
        return False
    if not provided:
        return False
    return provided.strip() == _EXPECTED_ADMIN_PIN


def _require_admin_pin(x_admin_pin: Optional[str] = Header(None, alias="X-Admin-Pin")) -> None:
    if not _admin_pin_ok(x_admin_pin):
        raise HTTPException(status_code=401, detail={"error": "unauthorized", "reason": "bad_or_missing_admin_pin"})


# --- App + CORS (S3: explicit, no *+creds) ---
_origins = [
    o.strip()
    for o in os.getenv("HV_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000").split(",")
    if o.strip()
]

app = FastAPI(title="HombreVigente RAG + Proactive Ops", version="2026.06-audit")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,  # S3: do not combine with "*"
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# slowapi wiring (S4)
if _HAS_SLOWAPI:
    limiter = Limiter(key_func=get_remote_address, default_limits=[f"{HV_RATELIMIT_RPM}/minute"])
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):  # type: ignore
        raise HTTPException(
            status_code=429,
            detail={"error": "rate_limited", "limit": f"{HV_RATELIMIT_RPM}/minute", "retry_after": 60},
        )
else:
    limiter = None  # type: ignore
    print("[api] slowapi not available — using built-in window limiter for /rag/query (S4)")

# --- Health (includes proactive signals + rate + ssot) ---
@app.get("/api/health")
def api_health() -> Dict[str, Any]:
    ssot = os.getenv("HV_STATE_PERSISTENCE", "files")
    # best effort pull is_healthy from action_handler
    is_h = False
    health_score = None
    try:
        from action_handler import compute_proactive_health_score  # type: ignore
        h = compute_proactive_health_score(ssot=ssot)
        is_h = bool(h.get("is_healthy"))
        health_score = h.get("score")
    except Exception:
        pass

    return {
        "status": "ok",
        "ssot": ssot,
        "is_healthy": is_h,
        "health_score": health_score,
        "ratelimit_rpm": HV_RATELIMIT_RPM,
        "ratelimit_enabled": _HAS_SLOWAPI or True,
        "ratelimit_note": "S4 audit: public /rag/query protected (slowapi or window)",
        "calibrate_endpoint": "/admin/calibrate (requires X-Admin-Pin)",
        "feature_flags": {
            "HV_FEATURE_PROACTIVE": os.getenv("HV_FEATURE_PROACTIVE", "true"),
            "HV_STATE_PERSISTENCE": ssot,
        },
    }


# --- RAG endpoints (public but rate-limited) ---
def _run_query(q: str, k: int = 5) -> Dict[str, Any]:
    # Minimal passthrough; real impl uses rag_retrieval_local or pgvector.
    # Here we just echo for smoke + to protect the LLM call path with rate limit.
    return {"query": q, "k": k, "answer": f"[stub-rag] results for: {q[:80]}", "sources": []}


@app.post("/rag/query")
def rag_query_post(body: Dict[str, Any], request: Request = None, x_admin_pin: Optional[str] = Header(None, alias="X-Admin-Pin")):  # noqa: B008
    # Public but protected by rate limit (S4). Admin pin not required for RAG.
    client_ip = "unknown"
    try:
        if request and request.client:
            client_ip = request.client.host or "unknown"
    except Exception:
        pass
    if not _check_ratelimit(client_ip, HV_RATELIMIT_RPM):
        raise HTTPException(status_code=429, detail={"error": "rate_limited", "limit": f"{HV_RATELIMIT_RPM}/minute"})
    q = (body or {}).get("q") or (body or {}).get("query") or ""
    k = int((body or {}).get("k", 5))
    return _run_query(q, k)


@app.get("/rag/query")
def rag_query_get(q: str, k: int = 5, request: Request = None):  # noqa: B008
    client_ip = "unknown"
    try:
        if request and request.client:
            client_ip = request.client.host or "unknown"
    except Exception:
        pass
    if not _check_ratelimit(client_ip, HV_RATELIMIT_RPM):
        raise HTTPException(status_code=429, detail={"error": "rate_limited", "limit": f"{HV_RATELIMIT_RPM}/minute"})
    return _run_query(q, k)


# --- Admin (PIN protected, header only, fail-closed) ---
@app.post("/admin/calibrate")
def admin_calibrate(x_admin_pin: Optional[str] = Header(None, alias="X-Admin-Pin")):  # noqa: B008
    _require_admin_pin(x_admin_pin)
    # Dynamic import so the calibrate script can live in scripts/ and be updated without api restart.
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "calibrate_proactive",
            str(Path(__file__).resolve().parents[1] / "scripts" / "calibrate_proactive.py"),
        )
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore
            if hasattr(mod, "run_calibration"):
                res = mod.run_calibration(dry_run=True)  # type: ignore
                return {"status": "ok", "calibration": res}
    except Exception as e:
        # Still return 200 with note; calibrate is best-effort in this stub
        return {"status": "ok", "calibration": {"note": "calibrate script not runnable here", "error": str(e)}}
    return {"status": "ok", "calibration": {"note": "no calibrate entrypoint"}}


@app.get("/admin/agent_status")
def admin_agent_status(x_admin_pin: Optional[str] = Header(None, alias="X-Admin-Pin")):  # noqa: B008
    _require_admin_pin(x_admin_pin)
    from action_handler import load_pending_actions, compute_proactive_health_score  # type: ignore
    pending = load_pending_actions(status="pending", limit=20)
    health = compute_proactive_health_score(pending_count=len(pending), ssot=os.getenv("HV_STATE_PERSISTENCE", "files"))
    return {
        "pending_count": len(pending),
        "health": health,
        "last_proactive_run": None,  # filled by last_proactive_run.json in real
        "feature_flags": {"HV_FEATURE_PROACTIVE": os.getenv("HV_FEATURE_PROACTIVE", "true")},
    }


# --- Minimal root for smoke ---
@app.get("/")
def root():
    return {"service": "hombrevigente-rag-proactive", "see": "/api/health"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
