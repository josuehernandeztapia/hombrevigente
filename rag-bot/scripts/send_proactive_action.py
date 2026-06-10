#!/usr/bin/env python3
"""
send_proactive_action.py — STUB sender for proactive actions (out-of-scope for core agentic sprint).

This is intentionally a stub. Real implementation (WhatsApp Business API, receipts,
status update to 'sent', cost tracing to hv_agent_traces, feature flag guard) is
tracked as S-1 follow-up per AUDITORIA_CODIGO_HV_2026-06-09.md and the 2026-06 closure report.

Usage (dry): python -m rag-bot.scripts.send_proactive_action --limit 5 --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from action_handler import load_pending_actions  # type: ignore


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--dry-run", action="store_true", default=True)
    args = ap.parse_args(argv)

    pending = load_pending_actions(status="pending", limit=args.limit)
    if not pending:
        print("[STUB SENDER] No pending actions.")
        return 0

    for a in pending:
        print(
            "[STUB SENDER] Would send to beta=%s action=%s type=%s msg=%s (idemp=%s) [dry=%s]"
            % (
                a.get("beta_id"),
                a.get("action_id"),
                a.get("action_type"),
                (a.get("suggested_message") or "")[:60],
                a.get("idemp_key"),
                args.dry_run,
            )
        )
        # TODO (real WhatsApp):
        # - call provider with template or free text (respect opt-in + 24h window)
        # - wait for receipt / handle failure webhook
        # - update status in hv_pending_actions to 'sent' or 'failed'
        # - write cost trace to hv_agent_traces (normalize_model_id + PRICING)
        # - honor HV_FEATURE_PROACTIVE_SENDER or equivalent flag (default off until S-1 hardening)
    print(f"\n[STUB SENDER] {len(pending)} pending shown (no real delivery). See TODOs in file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
