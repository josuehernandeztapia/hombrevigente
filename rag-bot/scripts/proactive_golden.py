#!/usr/bin/env python3
"""
Proactive Golden Regression Runner (Capa 6 Aprende + production checklist).

Loads data/proactive-golden.json and runs generate_action_for_signal on sample signals,
asserting stable action_type, suggested_message prefix, and resume_context.
This protects the proactive "agente" (Capa 5) logic from regressions, mirroring
the RAG golden-runner.

Usage:
  python scripts/proactive_golden.py
  (exits non-zero on failure for CI/nightly)

Run as part of CI (proactive-smoke) and scheduled nightly for continuous Aprende.
"""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from signal_detector import BetaSignal
from action_handler import generate_action_for_signal


def main() -> int:
    golden_path = Path(__file__).resolve().parent.parent / "data" / "proactive-golden.json"
    if not golden_path.exists():
        print(f"ERROR: {golden_path} not found")
        return 2

    golden = json.loads(golden_path.read_text(encoding="utf-8"))

    samples = [
        BetaSignal(beta_id="golden-1", signal_type="no_activity_72h", severity="medium", context={}),
        BetaSignal(beta_id="golden-2", signal_type="stalled_onboarding", severity="high", context={}),
        BetaSignal(beta_id="golden-3", signal_type="low_progress", severity="low", context={}),
        BetaSignal(beta_id="golden-4", signal_type="missing_labs", severity="medium", context={}),
    ]

    if len(samples) != len(golden):
        print(f"ERROR: sample count {len(samples)} != golden count {len(golden)}")
        return 1

    for i, sig in enumerate(samples):
        action = generate_action_for_signal(sig)
        g = golden[i]

        if action.get("action_type") != g["action_type"]:
            print(f"FAIL: action_type mismatch for {sig.signal_type}: got {action.get('action_type')} expected {g['action_type']}")
            return 1

        if not action.get("suggested_message", "").startswith(g["suggested_message_starts_with"]):
            print(f"FAIL: message prefix mismatch for {sig.signal_type}")
            return 1

        if bool(action.get("resume_context")) != g["has_resume_context"]:
            print(f"FAIL: has_resume_context mismatch for {sig.signal_type}")
            return 1

    print("Proactive golden regression PASSED (all samples match baseline)")
    return 0


if __name__ == "__main__":
    sys.exit(main())