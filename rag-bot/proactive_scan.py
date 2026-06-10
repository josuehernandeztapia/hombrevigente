"""
proactive_scan.py — Wiring layer: signal_detector (ver) -> action_handler (decidir).

Bridges the two BetaSignal shapes:
  signal_detector.BetaSignal(beta_id, signal_type, severity, context, detected_at)
    -> action_handler.BetaSignal(beta_id, signal_type, phase, last_active_at, metadata)

then runs generate_and_persist_for_signal for each (C1-protected persist + dry-run
execute). This replaces hand-injected signals: the proactive loop now derives its
input from the detector over hv_beta_states (postgres SSOT) or file states.

CLI:
  python rag-bot/proactive_scan.py            # scan + persist + dry-run execute
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from signal_detector import BetaSignalDetector, BetaSignal as DetectorSignal  # type: ignore
from action_handler import BetaSignal as ActionSignal, generate_and_persist_for_signal  # type: ignore


def adapt(sig: "DetectorSignal") -> ActionSignal:
    """Detector signal -> action_handler signal (carries phase + last_active_at + severity)."""
    ctx = dict(sig.context or {})
    return ActionSignal(
        beta_id=sig.beta_id,
        signal_type=sig.signal_type,
        phase=ctx.get("phase"),
        last_active_at=ctx.get("last_active_at"),
        metadata={**ctx, "severity": sig.severity, "detected_at": sig.detected_at},
    )


def scan_and_generate(
    states: Optional[List[Dict[str, Any]]] = None,
    *,
    dry_run: bool = True,
) -> List[Dict[str, Any]]:
    """Detect signals, adapt, and generate+persist (dry-run execute by default)."""
    detector = BetaSignalDetector()
    signals = detector.scan(states)
    results: List[Dict[str, Any]] = []
    for sig in signals:
        results.append(generate_and_persist_for_signal(adapt(sig), dry_run=dry_run))
    return results


def main(argv: Optional[list] = None) -> int:
    results = scan_and_generate(dry_run=True)
    by_type: Dict[str, int] = {}
    for r in results:
        at = (r.get("action") or {}).get("action_type", "unknown")
        by_type[at] = by_type.get(at, 0) + 1
    print(f"[proactive-scan] {len(results)} signal(s) -> actions: "
          f"{json.dumps(by_type, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
