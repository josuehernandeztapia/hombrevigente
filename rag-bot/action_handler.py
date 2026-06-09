"""
Action Handler for Proactive Signals — following the Guía Agéntica Estándar exactly.

The guide separates:
- Detector (ver / scan) -> emits Signals
- Specialized Agent (decidir / handleSignal) -> produces Actions

This module closes that loop using the existing primitives we built:
- StateManager (get_state, resume_conversation, get_suggested_next_action)
- Reentry logic (already produces good resume texts)
- BetaState (phase, slots, next_action)

For the Hombre Vigente beta program, actions are typically "outreach" suggestions:
- Re-engagement messages
- Specific reminders based on missing slots
- Escalation notes

We persist "pending actions" lightly so a future execution layer (WhatsApp sender, etc.) can consume them.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from state_manager import state_manager as sm
from signal_detector import BetaSignal, handle_signal as base_handle_signal  # reuse logging+trace if wanted
from feature_flags import is_enabled  # Guía Capa 5: default ON, disable via HV_FEATURE_XXX=false for <5s rollback


def _pending_actions_path() -> Path:
    base = Path(os.getenv("HV_PENDING_ACTIONS_DIR", "data/pending_actions"))
    base.mkdir(parents=True, exist_ok=True)
    return base / "pending_actions.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state_for_action(beta_id: str) -> Optional[Dict[str, Any]]:
    state, _ = sm.get_state(beta_id)
    return state if state else None


def generate_action_for_signal(signal: BetaSignal) -> Dict[str, Any]:
    """
    Core: turn a signal into a concrete, human-usable action.
    Uses StateManager + Reentry to make suggestions high-quality and contextual.
    For certain signals (low_progress), enriches with RAG retrieval for evidence-based
    suggestions (tying Capa 4 RAG into proactive agente per Guía layers).
    """
    beta_id = signal.beta_id
    state = _load_state_for_action(beta_id) or {}

    phase = state.get("phase", "unknown")
    next_action = sm.get_suggested_next_action(beta_id) or "Revisar manualmente"

    resume = sm.resume_conversation(beta_id)
    resume_text = resume.get("text") if resume else None

    suggested_message = None
    action_type = "review"

    if signal.signal_type in ("no_activity_7d", "no_activity_72h"):
        action_type = "reengage"
        if resume_text:
            suggested_message = resume_text
        else:
            suggested_message = f"Hola, notamos que tu protocolo en {phase} lleva un tiempo sin movimiento. {next_action}. ¿Te gustaría retomar?"
    elif signal.signal_type == "stalled_onboarding":
        action_type = "tally_reminder"
        suggested_message = f"Para avanzar en tu onboarding necesitamos que completes el Tally. {next_action}. ¿Necesitas el link de nuevo?"
    elif signal.signal_type == "low_progress":
        action_type = "checkin"
        base = f"Vemos que llevas {phase} con progreso parcial. {next_action}. ¿Cómo te sientes con el protocolo hasta ahora?"
        # Capa 4 RAG enrichment for evidence-based suggestion (best-effort, no breakage if no index)
        rag_snippet = ""
        try:
            from rag_retrieval_local import rag_query_local
            from pathlib import Path
            import os
            idx = Path(os.getenv("HV_EMBEDDINGS_INDEX", "knowledge_base/embeddings_local.json"))
            if idx.exists():
                q = f"protocolo en {phase} bajo progreso o estancado consejos"
                res = rag_query_local(q, index_path=idx, kb_route="longevity", top_k=1, use_llm=False, log=False)
                if res and res.get("answer"):
                    rag_snippet = " " + res["answer"][:200].strip()
        except Exception:
            pass  # silent fallback, preserves existing behavior
        suggested_message = base + rag_snippet
    elif signal.signal_type == "missing_labs":
        action_type = "labs_reminder"
        suggested_message = "Para personalizar mejor tu protocolo necesitamos tus labs recientes. ¿Puedes subirlos? Te puedo dar las instrucciones exactas."
    else:
        suggested_message = f"Signal {signal.signal_type} detectado en {phase}. Acción recomendada: {next_action}"

    action = {
        "action_id": f"act-{beta_id}-{signal.signal_type}-{int(datetime.now().timestamp())}",
        "beta_id": beta_id,
        "signal": signal.to_dict(),
        "action_type": action_type,
        "phase": phase,
        "suggested_message": suggested_message,
        "next_action_from_state": next_action,
        "resume_context": resume_text,
        "severity": signal.severity,
        "created_at": _now(),
        "status": "pending",  # pending | sent | done | ignored
    }
    return action


def persist_pending_action(action: Dict[str, Any]) -> None:
    """Append to a simple JSONL for consumption by future execution layer."""
    path = _pending_actions_path()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(action, ensure_ascii=False) + "\n")


def handle_signal_to_action(signal: BetaSignal) -> Dict[str, Any]:
    """
    Main entry point for the "decidir" side.
    Combines base logging/trace with real action generation + persistence.
    """
    # Optional: still do the basic log+trace from the detector
    base_handle_signal(signal)

    action = generate_action_for_signal(signal)
    persist_pending_action(action)

    print(f"[action] {action['action_id']} | {action['action_type']} for {action['beta_id']} | {action['suggested_message'][:80]}...")

    return action


def load_pending_actions(status: Optional[str] = "pending", limit: int = 50) -> List[Dict[str, Any]]:
    """Simple reader for ops / future sender."""
    path = _pending_actions_path()
    if not path.exists():
        return []
    actions = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
                if status is None or a.get("status") == status:
                    actions.append(a)
            except Exception:
                continue
    return actions[-limit:][::-1]  # most recent first


# Convenience: run the full detect + act pipeline
def run_detect_and_act() -> List[Dict[str, Any]]:
    from signal_detector import BetaSignalDetector
    detector = BetaSignalDetector()
    signals = detector.scan()
    results = []
    for s in signals:
        action = handle_signal_to_action(s)
        results.append(action)
    return results


def simulate_proactive_for_beta(beta_id: str) -> Dict[str, Any]:
    """
    Pure simulation: what signals + suggested actions would the proactive system
    produce for this beta *right now*, without any side effects or persistence.
    Useful for ops debugging and "what would happen if...".
    Also previews the state changes that execution would cause (last_active_at bump, history entry).
    """
    from state_persistence import list_all_betas
    from signal_detector import BetaSignalDetector

    all_betas = list_all_betas()
    state = next((b for b in all_betas if b.get("beta_id") == beta_id), None)
    if not state:
        return {"beta_id": beta_id, "error": "beta not found"}

    detector = BetaSignalDetector()
    signals = detector.scan(states=[state])

    simulated = []
    would_update_state = False
    for sig in signals:
        action = generate_action_for_signal(sig)  # pure, no persist
        simulated.append({
            "signal": sig.to_dict(),
            "would_generate_action": {
                "action_type": action.get("action_type"),
                "suggested_message": action.get("suggested_message"),
            },
        })
        would_update_state = True

    # Preview of state mutation that execute_pending_action would do
    simulated_state_after = dict(state)
    if would_update_state:
        simulated_state_after["last_active_at"] = _now()
        history = simulated_state_after.get("history", [])
        history.append({
            "at": _now(),
            "from_phase": state.get("phase"),
            "to_phase": state.get("phase"),
            "note": "proactive_action_simulated_execution",
        })
        simulated_state_after["history"] = history
        simulated_state_after["last_proactive_at"] = _now()

    return {
        "beta_id": beta_id,
        "phase": state.get("phase"),
        "last_active_at": state.get("last_active_at"),
        "simulated_signals_and_actions": simulated,
        "count": len(simulated),
        "would_update_state": would_update_state,
        "simulated_state_after": simulated_state_after if would_update_state else None,
    }


def compute_proactive_health_score() -> Dict[str, Any]:
    """
    Produces a simple 0-100 "Proactive Health Score" for the agent.
    Aggregates:
    - Pending proactive debt (higher pending = lower score)
    - Last calibration drift (any drift penalizes)
    - SSOT compliance (non-postgres penalizes)
    - Trace metrics (error rate and cost from last 24h)
    This is a pragmatic ops signal, not a perfect metric. Goal: >80 is healthy.
    """
    from state_persistence import list_all_betas
    from traces import get_trace_stats

    score = 100.0
    details = {}

    # 1. Pending actions debt
    pending = load_pending_actions(limit=1000)
    pending_count = len([p for p in pending if p.get("status") == "pending"])
    debt_penalty = min(pending_count * 3, 30)  # 3 points per pending, max 30
    score -= debt_penalty
    details["pending_actions"] = pending_count
    details["pending_debt_penalty"] = debt_penalty

    # 2. Last calibration drift
    calibration = {}
    try:
        cal_path = Path("data/proactive_calibration.json")
        if cal_path.exists():
            calibration = json.loads(cal_path.read_text(encoding="utf-8"))
    except Exception:
        pass

    drift = calibration.get("drift", {})
    if drift and "note" not in drift:
        drift_penalty = min((drift.get("added", 0) + drift.get("removed", 0)) * 5, 20)
        # Additional penalty for richer message/output drift (Guía Aprende: re-run & compare outputs)
        msg_changes = drift.get("message_changes", 0)
        sig_msg_drift = drift.get("significant_message_drift", 0)
        avg_sim = drift.get("avg_message_similarity", 1.0)
        if msg_changes > 0:
            drift_penalty += min(msg_changes * 3, 10)
        if sig_msg_drift > 0:
            drift_penalty += min(sig_msg_drift * 4, 12)
        if avg_sim < 0.9:
            drift_penalty += min(int((0.9 - avg_sim) * 20), 8)
        score -= drift_penalty
        details["calibration_drift"] = drift
        details["calibration_drift_penalty"] = drift_penalty
    else:
        details["calibration_drift"] = "no previous baseline or no drift"

    # 3. SSOT
    mode = os.getenv("HV_STATE_PERSISTENCE", "files")
    if mode != "postgres":
        score -= 15
        details["ssot_penalty"] = 15
        details["ssot_mode"] = mode
    else:
        details["ssot_mode"] = "postgres (good)"

    # 4. Trace health (last 24h)
    try:
        trace_stats = get_trace_stats(window_hours=24)
        error_rate = trace_stats.get("error_rate", 0.0)
        total_cost = trace_stats.get("total_cost_usd", 0.0)
        error_penalty = min(error_rate * 100, 15)  # up to 15 for high error rate
        cost_penalty = min(total_cost * 2, 10)     # rough: high cost in 24h hurts a bit
        score -= (error_penalty + cost_penalty)
        details["traces_24h"] = {
            "error_rate": error_rate,
            "total_cost_usd": total_cost,
            "error_penalty": error_penalty,
            "cost_penalty": cost_penalty,
        }
    except Exception:
        details["traces_24h"] = "unavailable"

    final_score = max(0, min(100, int(round(score))))
    ssot_ok = str(details.get("ssot_mode", "")).startswith("postgres")
    is_healthy = (final_score >= 70) and ssot_ok
    return {
        "score": final_score,
        "is_healthy": is_healthy,
        "details": details,
        "computed_at": _now(),
        "thresholds": {
            "healthy_min": 70,
            "ssot_required_for_healthy": True,
            "interpretation": "is_healthy = (score >= 70 AND ssot=postgres). Use for gating and daily ops review.",
        },
        "interpretation": "100 = perfect proactive health. <70 = needs attention (review pending, drift, SSOT, costs). is_healthy gates safe execution.",
    }


def log_proactive_health_score() -> Dict[str, Any]:
    """Appends current health score to a small history file for trend analysis."""
    hs = compute_proactive_health_score()
    history_path = Path("data/proactive_health_history.jsonl")
    history_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": _now(),
        "score": hs["score"],
        "pending_actions": hs["details"].get("pending_actions", 0),
        "ssot_mode": hs["details"].get("ssot_mode"),
        "calibration_drift": hs["details"].get("calibration_drift"),
    }

    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return hs


def get_proactive_health_trend(limit: int = 7) -> List[Dict[str, Any]]:
    """Returns the last N health score entries for trend visualization."""
    history_path = Path("data/proactive_health_history.jsonl")
    if not history_path.exists():
        return []

    entries = []
    with history_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue

    return entries[-limit:]


def compute_agent_metrics() -> Dict[str, Any]:
    """
    Computes the key success metrics from the Guía Agéntica (Métricas de éxito table)
    using available traces, state, and proactive data.

    Covers (pragmatically):
    - p50 / p95 latency (enhanced via traces + PERCENTILE_CONT)
    - error_rate, cost/turn
    - % branches deterministas vs LLM (branch_taken classification)
    - resume rate proxy (recent activity + stale-but-recently-touched betas)
    - MTTD proxy (mean seconds from error trace to next observed trace for same beta)
    - signals/acciones counts
    - trace coverage note
    Aligned to Guía thresholds.
    """
    from traces import get_trace_stats, read_traces  # module scope for all sub-tries
    metrics = {
        "computed_at": _now(),
        "source": "traces + state + proactive artifacts (Guía Métricas de éxito)",
        "guia_thresholds": {
            "p50_latency_ms_healthy": "< 1500",
            "p95_latency_ms_healthy": "< 5000",
            "error_rate_healthy": "< 0.01",
            "cost_per_turn_usd_healthy": "< 0.005",
            "deterministic_branch_pct_healthy": "> 60",
            "resume_rate_healthy": "> 0.30",
            "mttd_seconds_healthy": "< 120",
        },
    }

    # From traces (last 24h) — now with real p50/p95 when available
    try:
        from traces import get_trace_stats, read_traces
        t = get_trace_stats(window_hours=24)
        avg_cost = t.get("total_cost_usd", 0.0)
        count = max(1, t.get("count", 1))
        avg_cost_per_turn = round(avg_cost / count, 6) if count else 0.0
        metrics["traces_24h"] = {
            "count": t.get("count", 0),
            "errors": t.get("errors", 0),
            "error_rate": t.get("error_rate", 0.0),
            "avg_latency_ms": t.get("avg_latency_ms", 0),
            "p50_latency_ms": t.get("p50_latency_ms"),
            "p95_latency_ms": t.get("p95_latency_ms"),
            "total_cost_usd": t.get("total_cost_usd", 0.0),
            "avg_cost_per_turn_usd": avg_cost_per_turn,
        }
        metrics["latency"] = {
            "p50_ms": t.get("p50_latency_ms"),
            "p95_ms": t.get("p95_latency_ms"),
            "note": t.get("note", "p50/p95 from DB or approx"),
        }
    except Exception as e:
        metrics["traces_24h"] = {"error": str(e)}

    # Deterministic vs LLM branches (Capa 5 Guía)
    try:
        recent_traces = read_traces(limit=200, since_hours=24)
        det = 0
        llmish = 0
        for tr in recent_traces:
            b = (tr.get("branch_taken") or "").lower()
            if not b:
                continue
            # Classify: LLM-ish if branch indicates model call or RAG+LLM path
            if any(k in b for k in ["llm", "gpt", "openai", "anthropic", "generate", "rag_llm", "completion"]):
                llmish += 1
            else:
                # proactive, execute_, reentry, greeting, slot, transition, intake, deterministic knowns count as det
                det += 1
        total_br = det + llmish
        det_pct = round(det / total_br, 4) if total_br > 0 else None
        metrics["branches"] = {
            "total_classified_24h": total_br,
            "deterministic": det,
            "llm_or_rag_llm": llmish,
            "deterministic_pct": det_pct,
            "healthy_if": "> 0.60 per Guía",
        }
    except Exception as e:
        metrics["branches"] = {"error": str(e)}

    # Proactive + engagement / resume proxies
    try:
        pending = load_pending_actions(limit=1000)
        pending_count = len([p for p in pending if p.get("status") == "pending"])
        executed_count = 0
        try:
            exec_path = _executed_actions_path()
            if exec_path.exists():
                with exec_path.open(encoding="utf-8") as f:
                    executed_count = sum(1 for line in f if line.strip())
        except Exception:
            pass

        hs = compute_proactive_health_score()
        metrics["proactive"] = {
            "pending_actions": pending_count,
            "executed_actions_sample": executed_count,
            "health_score": hs.get("score"),
            "is_healthy": hs.get("is_healthy"),
        }

        # Resume rate + engagement per Guía (conversaciones que retoman tras 24h+)
        betas = list_all_betas()
        now = datetime.now(timezone.utc)
        recent_activity = 0
        stale_but_recent = 0  # proxy: had gap >24h and then touched in last 7d
        for b in betas:
            last = b.get("last_active_at") or b.get("last_proactive_at")
            if not last:
                continue
            try:
                ts = datetime.fromisoformat(str(last).replace("Z", "+00:00"))
                age_h = (now - ts).total_seconds() / 3600.0
                if age_h < 24 * 7:
                    recent_activity += 1
                if age_h < 24 * 7 and age_h > 24:
                    # touched recently after a potential gap (best-effort without full per-beta history)
                    stale_but_recent += 1
            except Exception:
                pass
        total_betas = len(betas) or 1
        resume_proxy = round(stale_but_recent / total_betas, 4)
        metrics["engagement"] = {
            "recently_active_betas": recent_activity,
            "total_betas": len(betas),
            "recent_activity_rate": round(recent_activity / total_betas, 4),
            "resume_rate_proxy": resume_proxy,
            "note": "resume_rate_proxy approximates 'conversaciones que retoman tras 24h+' via stale-but-recently-active. >0.30 healthy per Guía.",
        }
    except Exception as e:
        metrics["proactive"] = {"error": str(e)}

    # MTTD proxy (mean time to detect incidente) — time from error trace to next trace (any) for same beta
    try:
        err_traces = read_traces(limit=100, errors_only=True, since_hours=24*7)
        all_recent = read_traces(limit=300, since_hours=24*7)
        # group by beta
        from collections import defaultdict
        by_beta: Dict[str, list] = defaultdict(list)
        for tr in (err_traces + all_recent):
            bid = tr.get("beta_id") or "system"
            try:
                ts = datetime.fromisoformat(str(tr.get("created_at", "")).replace("Z", "+00:00"))
                by_beta[bid].append((ts, tr.get("success", True)))
            except Exception:
                continue
        deltas = []
        for bid, events in by_beta.items():
            events.sort(key=lambda x: x[0])
            for i, (ts, ok) in enumerate(events):
                if ok:  # success
                    continue
                # find next event after this error
                for j in range(i+1, len(events)):
                    nts = events[j][0]
                    delta_s = (nts - ts).total_seconds()
                    if delta_s > 0:
                        deltas.append(min(delta_s, 3600))  # cap at 1h per incident for sanity
                        break
        mttd = round(sum(deltas) / len(deltas)) if deltas else None
        metrics["mttd_proxy"] = {
            "seconds": mttd,
            "incidents_observed": len(deltas),
            "healthy_if": "< 120s per Guía (proxy from error-to-next-trace)",
            "note": "Best-effort; real MTTD would tie to explicit incident tickets.",
        }
    except Exception as e:
        metrics["mttd_proxy"] = {"error": str(e)}

    # Signals / acciones (from Capa 6/7)
    try:
        metrics["signals_acciones"] = {
            "pending_actions_now": metrics.get("proactive", {}).get("pending_actions", 0),
            "note": "Full signals-emitidos/acciones-tomadas available via /admin/signals + last_proactive_run.json + calibration",
        }
    except Exception:
        pass

    # SSOT + trace coverage + turn stats (Guía Métricas de éxito)
    mode = os.getenv("HV_STATE_PERSISTENCE", "files")
    metrics["ssot"] = {
        "mode": mode,
        "postgres_recommended": mode == "postgres",
    }
    try:
        betas = list_all_betas()
        total_turns = sum(int(b.get("turn_count", 0) or 0) for b in betas)
        tr = metrics.get("traces_24h", {})
        tr_count = tr.get("count", 0) if isinstance(tr, dict) else 0
        coverage = round(tr_count / max(1, total_turns), 4) if total_turns else None
        metrics["trace_coverage"] = {
            "traces_in_window": tr_count,
            "beta_turn_count_total": total_turns,
            "approx_coverage": coverage,
            "healthy_if": "> 0.95 per Guía (note: windowed vs lifetime)",
        }
        # Add average turns per beta for "turn count promedio"
        avg_turns = round(total_turns / max(1, len(betas)), 2) if betas else 0
        metrics["turns"] = {
            "total_betas": len(betas),
            "total_turns": total_turns,
            "avg_turns_per_beta": avg_turns,
            "note": "Guía: depende del dominio; si cae a 1 el agente no engancha.",
        }
    except Exception:
        metrics["trace_coverage"] = {"note": "unavailable"}

    # Overall health summary (Guía aligned)
    hs = (metrics.get("proactive") or {}).get("health_score") or 0
    err = (metrics.get("traces_24h") or {}).get("error_rate", 1.0)
    overall = max(0, min(100, int(0.6 * hs + 0.4 * (100 - err * 100))))
    metrics["overall_health_approx"] = {
        "score": overall,
        "note": "Composite per prior logic; prefer proactive.health_score + is_healthy + branches.deterministic_pct for Go/NoGo.",
    }

    return metrics


def _executed_actions_path() -> Path:
    base = Path(os.getenv("HV_PENDING_ACTIONS_DIR", "data/pending_actions"))
    base.mkdir(parents=True, exist_ok=True)
    return base / "executed_actions.jsonl"


def _get_proactive_health() -> Dict[str, Any]:
    """Best-effort fetch of current health (used for execution gates)."""
    try:
        return compute_proactive_health_score()
    except Exception:
        return {"score": 0, "is_healthy": False, "computed_at": _now()}


def execute_pending_action(action: Dict[str, Any], *, dry_run: bool = False, force: bool = False) -> Dict[str, Any]:
    """
    Executes a pending action: "sends" the suggested outreach (simulated for now),
    marks it executed, persists the record, and emits a trace.

    In real life this would call the WhatsApp / messaging layer with the message.

    Safety gate (Guía "se corrige"):
    - Real execution (not dry_run) is blocked unless is_healthy (score >=70 AND postgres SSOT)
      or force=True (explicit override for ops).
    - When blocked, the action stays in pending and is marked with status "blocked_by_health".
    """
    if action.get("status") != "pending":
        return action

    beta_id = action["beta_id"]
    message = action.get("suggested_message", "")

    # === Execution gate (Guía "se corrige" + feature flags Capa 5) ===
    # Flags default ON. Disable with HV_FEATURE_HEALTH_GATE=false or HV_FEATURE_PROACTIVE_EXECUTION=false
    health_gate_on = is_enabled("HEALTH_GATE", default=True)
    execution_on = is_enabled("PROACTIVE_EXECUTION", default=True)

    if not dry_run and not force:
        if not execution_on:
            print(f"[execute][BLOCKED] beta={beta_id} HV_FEATURE_PROACTIVE_EXECUTION=false. "
                  "Action left pending. Set flag=true or use --force.")
            action = dict(action)
            action["status"] = "blocked_by_feature_flag"
            action["blocked_at"] = _now()
            action["block_reason"] = {"flag": "PROACTIVE_EXECUTION", "value": False}
            try:
                payload = build_turn_payload(
                    beta_id=beta_id,
                    branch_taken="execute_blocked_by_feature_flag",
                    input_body=f"proactive action blocked for {action.get('signal', {}).get('signal_type')}",
                    output_body="",
                    state_after={"block": action["block_reason"]},
                    success=False,
                    error_message="blocked_by_feature_flag",
                )
                persist_turn_trace(payload)
            except Exception:
                pass
            return action

        if health_gate_on:
            hs = _get_proactive_health()
            if not hs.get("is_healthy", False):
                print(f"[execute][BLOCKED] beta={beta_id} health={hs.get('score')} is_healthy=False. "
                      f"Action left pending. Use --force or fix SSOT/health to proceed.")
                action = dict(action)
                action["status"] = "blocked_by_health"
                action["blocked_at"] = _now()
                action["block_reason"] = {
                    "health_score": hs.get("score"),
                    "is_healthy": False,
                    "ssot_mode": hs.get("details", {}).get("ssot_mode"),
                }
                try:
                    payload = build_turn_payload(
                        beta_id=beta_id,
                        branch_taken="execute_blocked_by_health",
                        input_body=f"proactive action blocked for {action.get('signal', {}).get('signal_type')}",
                        output_body="",
                        state_after={"block": action["block_reason"]},
                        success=False,
                        error_message="blocked_by_is_healthy_gate",
                    )
                    persist_turn_trace(payload)
                except Exception:
                    pass
                return action

    if dry_run:
        print(f"[execute][dry-run] Would send to {beta_id}: {message[:80]}...")
    else:
        # Real execution path (only reached if dry_run or force or is_healthy)
        print(f"[execute] SENT to {beta_id}: {message[:80]}...")

        # Record in BetaState that a proactive outreach happened.
        # This is important so future signal detection can take it into account
        # (e.g. don't re-trigger the same "no_activity_7d" immediately).
        try:
            state, _ = sm.get_state(beta_id)
            if state:
                history = state.get("history", [])
                history.append({
                    "at": _now(),
                    "from_phase": state.get("phase"),
                    "to_phase": state.get("phase"),
                    "note": f"proactive_action_executed: {action.get('action_type')}",
                })
                state["history"] = history
                state["last_proactive_at"] = _now()
                # Also bump a virtual "reminder_sent" concept via last_active to suppress
                # immediate re-detection of the same signal.
                state["last_active_at"] = _now()

                # Best effort — use record_turn which handles last_active and turn bump
                try:
                    sm.record_turn(beta_id, channel="proactive")
                except Exception:
                    pass
        except Exception:
            pass

    # Mark executed (only for actual execution paths)
    action = dict(action)
    action["status"] = "executed" if not dry_run else "dry_run_executed"
    action["executed_at"] = _now()
    action["dry_run"] = dry_run

    # Persist: append to executed log
    exec_path = _executed_actions_path()
    with exec_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(action, ensure_ascii=False) + "\n")

    # Remove from pending (rewrite pending file without this one)
    # Only remove on successful real or dry execution. Blocked actions stay in pending.
    pending_path = _pending_actions_path()
    if pending_path.exists():
        remaining = []
        with pending_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                    if a.get("action_id") != action.get("action_id"):
                        remaining.append(a)
                except Exception:
                    remaining.append(line)  # keep bad lines
        with pending_path.open("w", encoding="utf-8") as f:
            for a in remaining:
                if isinstance(a, dict):
                    f.write(json.dumps(a, ensure_ascii=False) + "\n")
                else:
                    f.write(str(a) + "\n")

    # Trace the execution
    try:
        payload = build_turn_payload(
            beta_id=beta_id,
            branch_taken=f"execute_{action.get('action_type', 'action')}",
            input_body=f"executing proactive action for {action.get('signal', {}).get('signal_type')}",
            output_body=message,
            state_after={"action": action},
            success=True,
        )
        persist_turn_trace(payload)
    except Exception:
        pass

    return action


def execute_all_pending(*, dry_run: bool = False, beta_id: Optional[str] = None, force: bool = False) -> List[Dict[str, Any]]:
    """Executes (or dry-runs) all current pending actions, optionally filtered by beta.
    Logs proactive health after execution so that every exec (script or API) updates the Aprende history.

    force=True bypasses the is_healthy gate (use with care, only for ops).
    """
    pending = load_pending_actions()
    executed = []
    for a in pending:
        if beta_id and a.get("beta_id") != beta_id:
            continue
        if a.get("status") != "pending":
            continue
        res = execute_pending_action(a, dry_run=dry_run, force=force)
        executed.append(res)
    # Log health on every exec path (covers /admin/pending_actions/execute and the script)
    try:
        log_proactive_health_score()
    except Exception:
        pass
    return executed
