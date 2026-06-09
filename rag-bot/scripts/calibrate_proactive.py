#!/usr/bin/env python3
"""
Calibration script for the proactive layer (Fase 6 / Capa 6 de la Guía Agéntica Estándar).

Toma una muestra de betas actuales, corre el detector + action handler actual,
y reporta qué señales/acciones se generarían hoy.

Si existe una calibración previa (data/proactive_calibration.json), compara y reporta drift.

Uso:
  python scripts/calibrate_proactive.py
  python scripts/calibrate_proactive.py --sample 20 --json
  HV_STATE_PERSISTENCE=postgres python scripts/calibrate_proactive.py

Se puede correr semanalmente vía GitHub Action (patrón ya usado en rag-bot-nightly).

Emite trazas de la propia calibración para auditoría.
"""

import argparse
import difflib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from state_persistence import list_all_betas
from signal_detector import BetaSignalDetector
from action_handler import generate_action_for_signal
from traces import build_turn_payload, persist_turn_trace


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _calibration_path() -> Path:
    base = Path(os.getenv("HV_CALIBRATION_DIR", "data"))
    base.mkdir(parents=True, exist_ok=True)
    return base / "proactive_calibration.json"


def load_previous_calibration() -> Dict[str, Any]:
    path = _calibration_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_calibration(report: Dict[str, Any]) -> None:
    path = _calibration_path()
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def run_calibration(sample_size: int = 0, use_json: bool = False) -> Dict[str, Any]:
    """
    Corre la calibración actual.
    sample_size=0 significa "todas las betas disponibles".
    """
    detector = BetaSignalDetector()
    all_betas = list_all_betas()

    if sample_size > 0:
        betas = all_betas[:sample_size]
    else:
        betas = all_betas

    # Use the injected-states path for controlled, reproducible calibration
    signals = detector.scan(states=betas)

    current_results: List[Dict[str, Any]] = []

    for sig in signals:
        action = generate_action_for_signal(sig)  # pure generation, no side effects

        current_results.append({
            "beta_id": sig.beta_id,
            "signal_type": sig.signal_type,
            "severity": sig.severity,
            "action_type": action.get("action_type"),
            "suggested_message_preview": (action.get("suggested_message") or "")[:120],
            "suggested_message": action.get("suggested_message") or "",
        })

    # Build report
    report = {
        "calibrated_at": _now(),
        "sample_size": len(betas),
        "signals_and_actions": current_results,
        "summary": {
            "total_triggered": len(current_results),
            "by_severity": {},
            "unique_betas": len({r["beta_id"] for r in current_results}),
        },
    }

    # Simple severity count
    for r in current_results:
        sev = r["severity"]
        report["summary"]["by_severity"][sev] = report["summary"]["by_severity"].get(sev, 0) + 1

    # Drift detection vs previous (Guía "Aprende": presence + content)
    previous = load_previous_calibration()
    if previous:
        prev_actions = { (a["beta_id"], a["signal_type"], a.get("action_type")) for a in previous.get("signals_and_actions", []) }
        curr_actions = { (r["beta_id"], r["signal_type"], r.get("action_type")) for r in current_results }

        added = curr_actions - prev_actions
        removed = prev_actions - curr_actions

        # Message/content drift for overlapping (beta,signal,action) – richer output comparison per Guía (re-corre y compara output)
        common = prev_actions & curr_actions
        message_changes = 0
        msg_examples = []
        similarities = []
        prev_map = { (a["beta_id"], a["signal_type"], a.get("action_type")): a.get("suggested_message","") for a in previous.get("signals_and_actions", []) }
        curr_map = { (r["beta_id"], r["signal_type"], r.get("action_type")): r.get("suggested_message","") for r in current_results }
        for key in common:
            pmsg = prev_map.get(key, "")
            cmsg = curr_map.get(key, "")
            if pmsg and cmsg:
                if pmsg != cmsg:
                    message_changes += 1
                    if len(msg_examples) < 3:
                        msg_examples.append({"key": key, "prev": pmsg[:80], "curr": cmsg[:80]})
                # Semantic-ish similarity using difflib (0-1)
                ratio = difflib.SequenceMatcher(None, pmsg, cmsg).ratio()
                similarities.append(ratio)
        avg_similarity = round(sum(similarities) / len(similarities), 4) if similarities else 1.0
        significant_message_drift = sum(1 for s in similarities if s < 0.85)

        report["drift"] = {
            "added": len(added),
            "removed": len(removed),
            "added_examples": list(added)[:5],
            "removed_examples": list(removed)[:5],
            "message_changes": message_changes,
            "message_examples": msg_examples,
            "avg_message_similarity": avg_similarity,
            "significant_message_drift": significant_message_drift,
        }
    else:
        report["drift"] = {"note": "no previous calibration found — this is the baseline"}

    # Persist this run as new baseline
    save_calibration(report)

    # Emit a trace for the calibration itself (observability)
    try:
        payload = build_turn_payload(
            beta_id="system",
            role="calibration",
            branch_taken="proactive_calibration",
            input_body=f"calibrated {len(betas)} betas, found {len(current_results)} signals/actions",
            output_body=json.dumps(report["summary"]),
            success=True,
        )
        persist_turn_trace(payload)
    except Exception:
        pass

    # Log the health score to the history (Aprende loop)
    try:
        from action_handler import log_proactive_health_score
        log_proactive_health_score()
    except Exception:
        pass

    if use_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"\n[calibrate_proactive] Calibrated at {report['calibrated_at']}")
        print(f"  Sample: {report['sample_size']} betas")
        print(f"  Triggered: {report['summary']['total_triggered']} (unique betas: {report['summary']['unique_betas']})")
        if "drift" in report and "note" not in report["drift"]:
            print(f"  Drift vs previous: +{report['drift']['added']} / -{report['drift']['removed']}")
            if report['drift'].get('message_changes', 0) > 0 or report['drift'].get('significant_message_drift', 0) > 0:
                print(f"    + message content drift: changes={report['drift']['message_changes']}, significant={report['drift']['significant_message_drift']}, avg_similarity={report['drift']['avg_message_similarity']} (richer Aprende)")
        print(f"  Baseline saved to { _calibration_path() }")

    if os.getenv("HV_STATE_PERSISTENCE") != "postgres":
        print("\n[Guía] Para SSOT real y calibración confiable en prod: "
              "HV_STATE_PERSISTENCE=postgres.")

    return report


def main():
    parser = argparse.ArgumentParser(description="Calibrate proactive signals & actions (Guía Agéntica)")
    parser.add_argument("--sample", type=int, default=0, help="Limit number of betas to calibrate (0 = all)")
    parser.add_argument("--json", action="store_true", help="Output full report as JSON")
    args = parser.parse_args()

    run_calibration(sample_size=args.sample, use_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
