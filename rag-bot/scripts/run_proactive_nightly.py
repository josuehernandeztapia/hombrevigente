#!/usr/bin/env python3
"""
Orchestrator for the full proactive cycle (Fase "proactivo scheduled" per Guía Agéntica).

Runs:
1. Signal detection + action generation
2. (Optional) execution of pending actions (default dry-run for safety)
3. Calibration + drift report

Designed to be called from GitHub Actions (see .github/workflows/rag-bot-proactive.yml)
or cron / server-side.

The recommended prod scheduled path is the GH workflow using the PIN-gated /admin endpoints
(signals/run + pending_actions/execute). The script is excellent for local dev, manual runs,
and full simulation with --sample / calibration.

Usage (recommended for prod):
  python scripts/run_proactive_nightly.py --execute --sample 100

Usage (safe / dev):
  python scripts/run_proactive_nightly.py --dry-run

It always emits a summary trace for observability.
The GH workflow (rag-bot-proactive.yml) drives the scheduled version using admin endpoints
and includes calibration as part of the Aprende loop.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from action_handler import run_detect_and_act, execute_all_pending, load_pending_actions
from signal_detector import BetaSignalDetector
from traces import build_turn_payload, persist_turn_trace
from feature_flags import is_enabled  # Guía Capa 5 feature flags (default ON)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _summary_path() -> Path:
    base = Path(os.getenv("HV_PENDING_ACTIONS_DIR", "data/pending_actions"))
    base.mkdir(parents=True, exist_ok=True)
    return base / "last_proactive_run.json"


def run_proactive_cycle(
    *,
    execute: bool = False,
    dry_run: bool = True,
    sample_size: int = 0,
    run_calibration: bool = True,
) -> Dict[str, Any]:
    """
    Main entrypoint for scheduled proactive work.
    """
    started_at = _now()
    results: Dict[str, Any] = {
        "started_at": started_at,
        "mode": "execute" if execute else "dry_run",
        "sample_size": sample_size,
    }

    # 0. Check health score + is_healthy + feature flags — force dry-run for safety (Guía "se corrige")
    try:
        from action_handler import compute_proactive_health_score
        hs = compute_proactive_health_score()
        health_score = hs.get("score", 100)
        is_healthy = hs.get("is_healthy", False)
        results["health_score_at_start"] = health_score
        results["is_healthy_at_start"] = is_healthy

        health_gate_on = is_enabled("HEALTH_GATE", default=True)
        execution_on = is_enabled("PROACTIVE_EXECUTION", default=True)
        nightly_on = is_enabled("PROACTIVE_NIGHTLY", default=True)

        if not nightly_on:
            print("[proactive_nightly] HV_FEATURE_PROACTIVE_NIGHTLY=false — skipping entire cycle.")
            results["forced_dry_run_reason"] = "feature_flag_PROACTIVE_NIGHTLY"
            return results

        if execute and not dry_run:
            if not execution_on:
                print("[proactive_nightly] HV_FEATURE_PROACTIVE_EXECUTION=false — forcing dry_run.")
                dry_run = True
                results["forced_dry_run_reason"] = "feature_flag_PROACTIVE_EXECUTION"
            elif health_gate_on and (not is_healthy or health_score < 70):
                reason = "is_healthy=False" if not is_healthy else "score<70"
                print(f"[proactive_nightly] {reason} (score={health_score}) — forcing dry_run for safety.")
                dry_run = True
                results["forced_dry_run_reason"] = reason
    except Exception:
        results["health_score_at_start"] = None
        results["is_healthy_at_start"] = None

    # 1. Detect + generate actions (always)
    print("[proactive_nightly] Running detect + act...")
    actions = run_detect_and_act()
    results["actions_generated"] = len(actions)

    # 2. Execute (or dry)
    if execute:
        print(f"[proactive_nightly] Executing pending actions (dry_run={dry_run})...")
        executed = execute_all_pending(dry_run=dry_run)
        results["actions_executed"] = len(executed)
    else:
        pending = load_pending_actions(limit=1000)
        results["pending_before"] = len([p for p in pending if p.get("status") == "pending"])

    # 3. Calibration (recommended on every run or at least weekly)
    if run_calibration:
        print("[proactive_nightly] Running calibration...")
        from calibrate_proactive import run_calibration as _run_cal
        cal_report = _run_cal(sample_size=sample_size, use_json=False)
        results["calibration"] = {
            "calibrated_at": cal_report.get("calibrated_at"),
            "total_triggered": cal_report.get("summary", {}).get("total_triggered"),
            "drift": cal_report.get("drift"),
        }

    # 4. Summary trace (always)
    try:
        payload = build_turn_payload(
            beta_id="system",
            role="proactive_nightly",
            branch_taken="proactive_cycle",
            input_body=f"cycle executed={execute} dry={dry_run} sample={sample_size}",
            output_body=json.dumps({
                "actions_generated": results.get("actions_generated"),
                "actions_executed": results.get("actions_executed"),
                "calibration_triggered": cal_report.get("summary", {}).get("total_triggered") if run_calibration else None,
                "health_score": results.get("health_score_at_start"),
            }),
            success=True,
        )
        persist_turn_trace(payload)
    except Exception as e:
        print(f"[proactive_nightly] WARN: could not emit summary trace: {e}")

    # Persist lightweight last-run marker for /admin/agent_status and ops
    summary = {
        "last_run_at": _now(),
        "mode": results["mode"],
        "actions_generated": results.get("actions_generated", 0),
        "actions_executed": results.get("actions_executed", 0),
        "calibration": results.get("calibration"),
        "health_score_at_start": results.get("health_score_at_start"),
        "is_healthy_at_start": results.get("is_healthy_at_start"),
        "forced_dry_run_reason": results.get("forced_dry_run_reason"),
    }
    _summary_path().write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # Log the health score to the history for trend (Aprende loop)
    try:
        from action_handler import log_proactive_health_score
        log_proactive_health_score()
    except Exception:
        pass

    print(f"\n[proactive_nightly] Cycle complete. Summary written to {_summary_path()}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run full proactive cycle (Guía Agéntica)")
    parser.add_argument("--execute", action="store_true", help="Actually execute pending actions (use with care)")
    parser.add_argument("--dry-run", action="store_true", help="Force dry-run even if --execute is passed")
    parser.add_argument("--sample", type=int, default=0, help="Limit calibration sample size")
    parser.add_argument("--no-calibration", action="store_true", help="Skip calibration step")
    parser.add_argument("--json", action="store_true", help="Output final summary as JSON")
    args = parser.parse_args()

    dry = args.dry_run or not args.execute

    summary = run_proactive_cycle(
        execute=args.execute,
        dry_run=dry,
        sample_size=args.sample,
        run_calibration=not args.no_calibration,
    )

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("\nDone. See last_proactive_run.json for machine-readable output.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
