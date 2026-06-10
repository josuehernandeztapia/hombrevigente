#!/usr/bin/env python3
"""
send_proactive_action.py (G2) — Proactive sender CLI.

No longer a stub. Drives the real delivery path:
  load pending -> execute_pending_action (idemp C1 -> health gate -> sender) -> trace.

Delivery is defense-in-depth gated and remains safe by default:
  * --send is OFF by default (dry-run: marks dry_run_executed, no delivery).
  * Even with --send, real WhatsApp delivery requires HV_PROACTIVE_SENDER=on AND
    HV_WHATSAPP_TOKEN/HV_WHATSAPP_PHONE_ID; otherwise the LogSender no-ops (status 'skipped').
  * The health gate still blocks real sends when ssot!=postgres or score<70 (unless --force).

Usage:
  python rag-bot/scripts/send_proactive_action.py --limit 5            # dry-run (safe)
  HV_PROACTIVE_SENDER=on HV_WHATSAPP_TOKEN=... HV_WHATSAPP_PHONE_ID=... \
      python rag-bot/scripts/send_proactive_action.py --limit 5 --send  # real delivery
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from action_handler import execute_all_pending  # type: ignore


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Proactive sender (dry-run by default).")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--send", action="store_true", default=False,
                    help="Attempt real delivery (still gated by sender flag + creds + health).")
    ap.add_argument("--force", action="store_true", default=False,
                    help="Bypass the health gate (break-glass only).")
    args = ap.parse_args(argv)

    dry_run = not args.send
    results = execute_all_pending(limit=args.limit, dry_run=dry_run, force=args.force)

    counts: dict[str, int] = {}
    for r in results:
        s = r.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1

    mode = "DRY-RUN" if dry_run else "SEND"
    print(f"[sender:{mode}] processed {len(results)} action(s): "
          f"{json.dumps(counts, ensure_ascii=False)}")
    if not args.send:
        print("[sender] dry-run only — pass --send (with HV_PROACTIVE_SENDER=on + WhatsApp creds) to deliver.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
