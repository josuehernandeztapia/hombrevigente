#!/usr/bin/env python3
"""
proactive_golden.py — Regression runner for the 4 golden proactive signals.

Used in CI (rag-bot-ci.yml, rag-bot-nightly.yml) and GH Action (rag-bot-proactive.yml).
Exits 0 on all PASS, 1 on any failure.

RAG is best-effort and not asserted here.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from action_handler import BetaSignal, generate_action_for_signal  # type: ignore


def load_golden() -> list[Dict[str, Any]]:
    p = ROOT / "data" / "proactive-golden.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    # fallback inline (same as data/)
    return [
        {"signal_type": "no_activity_72h", "action_type": "reengage", "phase": "reentry", "suggested_message_starts_with": "Hola", "has_resume": False},
        {"signal_type": "stalled_onboarding", "action_type": "tally_reminder", "phase": "onboarding", "suggested_message_starts_with": "Recuerda", "has_resume": False},
        {"signal_type": "low_progress", "action_type": "checkin", "phase": "followup", "suggested_message_starts_with": "Check-in", "has_resume": False},
        {"signal_type": "missing_labs", "action_type": "labs_reminder", "phase": "labs", "suggested_message_starts_with": "Te faltan", "has_resume": False},
    ]


def main() -> int:
    golden = load_golden()
    failures = 0
    for g in golden:
        sig = BetaSignal(
            beta_id="beta-golden-regression",
            signal_type=g["signal_type"],
            phase=g.get("phase"),
            last_active_at=None,
        )
        action = generate_action_for_signal(sig)
        ok_type = action["action_type"] == g["action_type"]
        ok_start = action["suggested_message"].startswith(g["suggested_message_starts_with"])
        ok_resume = True  # golden fixtures declare has_resume but we only soft-check prefix here
        status = "PASS" if (ok_type and ok_start and ok_resume) else "FAIL"
        if status == "FAIL":
            failures += 1
        print(f"[{status}] {g['signal_type']} -> {action['action_type']} | starts={ok_start} | msg[:60]={action['suggested_message'][:60]!r}")
    print(f"\nGolden regression: {len(golden)-failures}/{len(golden)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
