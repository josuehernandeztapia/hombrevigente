"""
action_handler.py — Proactive action generation + execution with health gating (Guía 7-layer "se corrige").

Includes:
- BetaSignal + generate_action_for_signal (reentry bands per TRAJ-HV-010, RAG best-effort enrichment for low_progress)
- compute_proactive_health_score + is_healthy (ssot=postgres + score>=70) + logging
- execute_pending_action with C1 idempotency (via persistence layer), health gate (block if !healthy unless dry_run/force), trace/cost
- execute_all_pending
- load/persist/mark/is_idemp delegation to state_persistence (postgres-first, ON CONFLICT for C1) with file fallback + [warn] hygiene for audit #3
- Note on C1: current JSONL rewrite (in state_persistence file path) is racy under concurrency; PG + UNIQUE is the robust path.

Ref: AUDITORIA_CODIGO_HV_2026-06-09.md (C1, #3), 4 points (esp. postgres-first reads, TRAJ-HV-010), Guía agentic.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional local RAG (best-effort, never breaks generation)
try:
    from rag_retrieval_local import rag_query_local as _rag_query_local  # type: ignore
except Exception:
    _rag_query_local = None


# ------------------------------------------------------------------
# Types
# ------------------------------------------------------------------

@dataclass
class BetaSignal:
    beta_id: str
    signal_type: str  # no_activity_72h | stalled_onboarding | low_progress | missing_labs | ...
    phase: Optional[str] = None
    last_active_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pending_actions_path() -> Path:
    raw = os.getenv("HV_PENDING_ACTIONS_DIR", "data/pending_actions")
    p = Path(raw)
    p.mkdir(parents=True, exist_ok=True)
    return p / "pending_actions.jsonl"


# ------------------------------------------------------------------
# Health (compute + log) — "se corrige" + is_healthy gate
# ------------------------------------------------------------------

def compute_proactive_health_score(
    *,
    pending_count: int = 0,
    drift: float = 0.0,
    ssot: str = "files",
    recent_error: bool = False,
    recent_cost_usd: float = 0.0,
    last_run_age_minutes: Optional[float] = None,
) -> Dict[str, Any]:
    """
    health_score = 100 - penalties.
    Penalties (aligned to Guía + audit): pending*3 + drift*5 + ssot_not_postgres*15 + error*10 + cost factor.
    is_healthy = (score >= 70) AND (ssot == "postgres")
    """
    score = 100
    penalties: List[Dict[str, Any]] = []

    if pending_count > 0:
        p = int(pending_count) * 3
        score -= p
        penalties.append({"type": "pending", "count": pending_count, "penalty": p})

    if drift and drift > 0:
        p = min(25, int(round(drift * 5)))
        score -= p
        penalties.append({"type": "drift", "value": drift, "penalty": p})

    if ssot != "postgres":
        p = 15
        score -= p
        penalties.append({"type": "ssot", "current": ssot, "penalty": p})

    if recent_error:
        p = 10
        score -= p
        penalties.append({"type": "error", "penalty": p})

    if recent_cost_usd and recent_cost_usd > 0.5:
        p = min(10, int(recent_cost_usd * 4))
        score -= p
        penalties.append({"type": "cost", "cost_usd": recent_cost_usd, "penalty": p})

    score = max(0, min(100, score))
    is_healthy = bool(score >= 70 and ssot == "postgres")

    return {
        "score": score,
        "is_healthy": is_healthy,
        "details": {
            "penalties": penalties,
            "pending_count": pending_count,
            "drift": drift,
            "ssot": ssot,
            "last_run_age_minutes": last_run_age_minutes,
        },
        "thresholds": {"healthy_min": 70, "ssot_required": "postgres"},
        "interpretation": "healthy" if is_healthy else "degraded_or_blocked",
        "computed_at": _utc_now(),
    }


def log_proactive_health_score(health: Dict[str, Any], *, beta_id: Optional[str] = None) -> None:
    """Append to jsonl + echo key fact (is_healthy)."""
    try:
        root = Path(os.getenv("HV_DATA_DIR", "data"))
        root.mkdir(parents=True, exist_ok=True)
        hist = root / "proactive_health_history.jsonl"
        rec = dict(health)
        if beta_id:
            rec["beta_id"] = beta_id
        with hist.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass  # never break on logging
    # Echo for ops / CI
    try:
        print(f"[health] is_healthy={health.get('is_healthy')} score={health.get('score')} ssot={health.get('details',{}).get('ssot')}")
    except Exception:
        pass


# ------------------------------------------------------------------
# Reentry / resume (TRAJ-HV-010 bands, simplified but faithful)
# ------------------------------------------------------------------

def _compute_resume_message(last_active_at: Optional[str], phase: Optional[str] = None) -> Tuple[Optional[str], bool]:
    """
    Returns (resume_message or None, has_resume_context).
    Bands (approx from Guía): <48h light/none; 48h-7d follow-up; >7d reentry with prior context.
    """
    if not last_active_at:
        return None, False
    try:
        last = datetime.fromisoformat(last_active_at.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - last).total_seconds() / 3600.0
    except Exception:
        return None, False

    if age_h < 48:
        return None, False
    if age_h < 168:  # 7d
        msg = "Sigues con el protocolo? Avísame cómo vas con los labs o el tally."
        return msg, True
    # reentry >7d / 72h+
    msg = "Hola de nuevo. ¿Cómo has estado? Cuando quieras retomamos donde quedamos (puedo recordarte el último paso)."
    return msg, True


# ------------------------------------------------------------------
# Generation (with optional RAG enrichment best-effort for low_progress)
# ------------------------------------------------------------------

_SIGNAL_TO_ACTION: Dict[str, str] = {
    "no_activity_72h": "reengage",
    "stalled_onboarding": "tally_reminder",
    "low_progress": "checkin",
    "missing_labs": "labs_reminder",
}

def _maybe_enrich_with_rag(suggested: str, signal: BetaSignal) -> str:
    """RAG enrichment only for low_progress/checkin — best effort, never fails generation."""
    if signal.signal_type != "low_progress":
        return suggested
    try:
        if _rag_query_local is None:
            return suggested
        # cheap local index check (optional)
        kb = Path(os.getenv("HV_KB_EMB_PATH", "rag-bot/knowledge_base/embeddings_local.json"))
        if not kb.exists():
            kb = Path("data/knowledge_base/embeddings_local.json")
        if not kb.exists():
            return suggested
        q = f"progreso del beta {signal.beta_id} en onboarding o labs recientes"
        res = _rag_query_local(q, use_llm=False)  # type: ignore
        ans = (res or {}).get("answer") or (res or {}).get("context") or ""
        if ans:
            snippet = " " + str(ans).strip()[:200]
            return (suggested or "").rstrip() + snippet
    except Exception:
        # best-effort: silent
        pass
    return suggested


def generate_action_for_signal(
    signal: BetaSignal,
    *,
    now: Optional[str] = None,
    rag_snippet: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Deterministic action suggestion. Idempotency key includes beta+signal+phase (hour bucket for safety).
    Resume context computed from last_active bands (TRAJ-HV-010).
    """
    action_type = _SIGNAL_TO_ACTION.get(signal.signal_type, "checkin")
    base = {
        "no_activity_72h": "Hola, hace tiempo que no tenemos actividad. ¿Quieres retomar?",
        "stalled_onboarding": "Recuerda completar el Tally de síntomas cuando puedas.",
        "low_progress": "Check-in rápido: ¿cómo vas con el protocolo esta semana?",
        "missing_labs": "Te faltan labs recientes. ¿Ya los subiste o necesitas ayuda agendando?",
    }.get(signal.signal_type, "Hola, aquí para ayudarte con tu protocolo.")

    suggested = base
    if rag_snippet:
        suggested = (suggested or "").rstrip() + " " + rag_snippet[:180]
    else:
        suggested = _maybe_enrich_with_rag(suggested, signal)

    resume_msg, has_resume = _compute_resume_message(signal.last_active_at, signal.phase)
    if resume_msg:
        suggested = f"{suggested} {resume_msg}".strip()

    hour_bucket = int(time.time() // 3600)
    idemp_key = f"{signal.beta_id}:{signal.signal_type}:{signal.phase or ''}:{hour_bucket}"

    action: Dict[str, Any] = {
        "action_id": f"act-{int(time.time()*1000)}",
        "beta_id": signal.beta_id,
        "idemp_key": idemp_key,
        "signal_type": signal.signal_type,
        "action_type": action_type,
        "suggested_message": suggested,
        "status": "pending",
        "created_at": now or _utc_now(),
        "dry_run": False,
        "resume_context": resume_msg,
        "has_resume": has_resume,
        "metadata": dict(signal.metadata or {}),
    }
    return action


# ------------------------------------------------------------------
# C1 wiring (postgres pending) + #3 reinforce — delegation to state_persistence
# (the functions below are what get called by scripts/tests; they prefer PG layer)
# ------------------------------------------------------------------

# Import the smart (postgres-first) implementations for delegation.
# These already implement ON CONFLICT / UNIQUE for C1 and postgres-first reads.
try:
    from state_persistence import (
        load_pending_actions as _load_pending_persistence,
        persist_pending_action as _persist_pending_persistence,
        mark_pending_executed as _mark_pending_executed_persistence,
        is_idemp_already_executed as _is_idemp_executed_persistence,
        log_trace as _log_trace_persistence,
    )
except Exception as e:
    print(f"[action_handler][warn] could not import persistence delegation (will use legacy): {e}")
    _load_pending_persistence = None
    _persist_pending_persistence = None
    _mark_pending_executed_persistence = None
    _is_idemp_executed_persistence = None
    _log_trace_persistence = None


def log_trace(beta_id: str, **kw) -> Optional[int]:
    """Best-effort trace into hv_agent_traces (G3). No-op if persistence unavailable."""
    if _log_trace_persistence is None:
        return None
    try:
        return _log_trace_persistence(beta_id, **kw)
    except Exception as e:
        print(f"[action_handler][warn] log_trace failed: {e}")
        return None


def load_pending_actions(status: Optional[str] = "pending", limit: int = 50, beta_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if _load_pending_persistence is not None:
        try:
            return _load_pending_persistence(status=status, limit=limit, beta_id=beta_id)
        except Exception as e:
            print(f"[action_handler][warn] postgres load_pending failed (fallback to files): {e}")
    # legacy files path (kept for compatibility when no persistence)
    path = _pending_actions_path()
    if not path.exists():
        return []
    actions: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
                if status is None or a.get("status") == status:
                    if beta_id is None or a.get("beta_id") == beta_id:
                        actions.append(a)
            except Exception:
                continue  # #3 hygiene: narrow except + continue (no bare pass)
    return actions[-limit:][::-1] if limit else actions


def persist_pending_action(action: Dict[str, Any]) -> None:
    if _persist_pending_persistence is not None:
        try:
            _persist_pending_persistence(action)
            return
        except Exception as e:
            print(f"[action_handler][warn] postgres persist_pending failed (fallback to files): {e}")
    path = _pending_actions_path()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(action, ensure_ascii=False) + "\n")


def _legacy_mark_executed_files(action: Dict[str, Any], *, dry_run: bool = False, final_status: Optional[str] = None) -> None:
    """Minimal legacy marker for when persistence mark not wired."""
    exec_path = _pending_actions_path().with_name("executed_actions.jsonl")
    rec = dict(action)
    rec["status"] = final_status or ("dry_run_executed" if dry_run else "executed")
    rec["executed_at"] = _utc_now()
    with exec_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def mark_pending_executed(
    action: Dict[str, Any],
    *,
    dry_run: bool = False,
    block_reason: Optional[Dict[str, Any]] = None,
    final_status: Optional[str] = None,
) -> None:
    if _mark_pending_executed_persistence is not None:
        try:
            _mark_pending_executed_persistence(
                action,
                dry_run=dry_run,
                block_reason=block_reason,
                final_status=final_status,
            )
            return
        except Exception as e:
            print(f"[action_handler][warn] postgres mark_executed failed (fallback): {e}")
    _legacy_mark_executed_files(action, dry_run=dry_run, final_status=final_status)


def is_idemp_already_executed(idemp_key: str) -> bool:
    if _is_idemp_executed_persistence is not None:
        try:
            return _is_idemp_executed_persistence(idemp_key)
        except Exception as e:
            print(f"[action_handler][warn] postgres idemp check failed (fallback): {e}")
    # Fallback: look in executed jsonl (best effort)
    exec_path = _pending_actions_path().with_name("executed_actions.jsonl")
    if not exec_path.exists():
        return False
    try:
        with exec_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    if e.get("idemp_key") == idemp_key:
                        return True
                except Exception:
                    continue
    except Exception:
        pass
    return False


# ------------------------------------------------------------------
# Execute with gate + idemp (C1) + health block
# ------------------------------------------------------------------

def execute_pending_action(
    action: Dict[str, Any],
    *,
    dry_run: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Executes (or dry-runs) a pending action.
    - Idempotency first (C1): if already executed by idemp_key → short-circuit.
    - Health gate: if not (dry_run or force) and not is_healthy → persist block_reason and return blocked.
    - On proceed: mark executed (PG or files), return trace with cost (fire-and-forget style).
    """
    action = dict(action)
    idemp_key = action.get("idemp_key") or f"{action.get('beta_id')}:{action.get('signal_type')}:{action.get('action_id','')}"
    action["idemp_key"] = idemp_key

    # C1 idemp check (delegates to PG UNIQUE check when available)
    if is_idemp_already_executed(idemp_key):
        return {
            "status": "already_executed",
            "action_id": action.get("action_id"),
            "idemp_key": idemp_key,
            "trace": {"skipped": True, "reason": "idempotent"},
        }

    # Health gate (only for real execution)
    health = compute_proactive_health_score(
        pending_count=len(load_pending_actions(status="pending", limit=100)),
        ssot=os.getenv("HV_STATE_PERSISTENCE", "files"),
    )
    is_healthy = bool(health.get("is_healthy"))

    if not dry_run and not force and not is_healthy:
        block = {
            "reason": "blocked_by_health",
            "health": health,
            "action_id": action.get("action_id"),
            "idemp_key": idemp_key,
            "at": _utc_now(),
        }
        # Record the block so it is auditable (mark as blocked)
        try:
            mark_pending_executed(action, dry_run=False, block_reason=block, final_status="blocked_by_health")
        except Exception:
            pass
        log_trace(
            action.get("beta_id", ""), role="proactive", event_type="block",
            action_id=action.get("action_id"), idemp_key=idemp_key,
            status="blocked_by_health", cost_usd=0.0,
            metadata={"reason": "blocked_by_health", "score": health.get("score")},
        )
        return {
            "status": "blocked_by_health",
            "block_reason": block,
            "action_id": action.get("action_id"),
            "idemp_key": idemp_key,
            "health": health,
        }

    # Proceed. Dry-run never delivers; real execution calls the sender (G2) and only
    # marks the action 'executed' (idempotency-consuming) when actually delivered.
    beta_id = action.get("beta_id", "")
    try:
        if dry_run:
            mark_pending_executed(action, dry_run=True, final_status="dry_run_executed")
            tn = log_trace(beta_id, role="proactive", event_type="send",
                           action_id=action.get("action_id"), idemp_key=idemp_key,
                           status="dry_run", cost_usd=0.0, metadata={"dry_run": True})
            return {
                "status": "dry_run_executed", "action_id": action.get("action_id"),
                "idemp_key": idemp_key, "beta_id": beta_id, "dry_run": True,
                "cost_usd": 0.0, "turn_number": tn, "health_at_exec": health,
            }

        # Real delivery via provider abstraction (LogSender if flag/creds absent → status 'skipped').
        from sender import send_action  # lazy import to avoid any cycle
        result = send_action(action)
        tn = log_trace(
            beta_id, role="proactive", event_type="send",
            action_id=action.get("action_id"), idemp_key=idemp_key,
            status=result.status, cost_usd=result.cost_usd, model=result.model,
            metadata={"provider": result.provider, "receipt_id": result.receipt_id,
                      "error": result.error, **(result.meta or {})},
        )

        # Only a confirmed send consumes the action; skipped/failed stay 'pending' for retry.
        if result.status == "sent":
            mark_pending_executed(action, dry_run=False, final_status="executed")
        return {
            "status": result.status, "action_id": action.get("action_id"),
            "idemp_key": idemp_key, "beta_id": beta_id, "dry_run": False,
            "provider": result.provider, "receipt_id": result.receipt_id,
            "cost_usd": result.cost_usd, "error": result.error,
            "turn_number": tn, "health_at_exec": health,
        }
    except Exception as e:
        print(f"[action_handler][warn] execute failed for {action.get('action_id')}: {e}")
        return {"status": "error", "error": str(e), "action_id": action.get("action_id")}


def execute_all_pending(*, limit: int = 50, dry_run: bool = True, force: bool = False) -> List[Dict[str, Any]]:
    """Batch executor used by cron / GH Action."""
    pending = load_pending_actions(status="pending", limit=limit)
    results: List[Dict[str, Any]] = []
    for a in pending:
        try:
            r = execute_pending_action(a, dry_run=dry_run, force=force)
            results.append(r)
        except Exception as e:
            print(f"[action_handler][warn] execute_all item failed: {e}")
            results.append({"status": "error", "error": str(e)})
    # log health after batch
    try:
        h = compute_proactive_health_score(pending_count=len(load_pending_actions(status="pending", limit=100)))
        log_proactive_health_score(h)
    except Exception:
        pass
    return results


# ------------------------------------------------------------------
# (Optional) one-shot signal → action convenience used by proactive runner
# ------------------------------------------------------------------

def generate_and_persist_for_signal(signal: BetaSignal, *, dry_run: bool = True) -> Dict[str, Any]:
    action = generate_action_for_signal(signal)
    # persist first (C1 protected at PG layer)
    try:
        persist_pending_action(action)
    except Exception as e:
        print(f"[action_handler][warn] persist before exec: {e}")
    # execute (may block or run)
    result = execute_pending_action(action, dry_run=dry_run)
    return {"action": action, "result": result}


# End of module — wiring + core ready for Guía proactive loop + audit items #3/C1.
