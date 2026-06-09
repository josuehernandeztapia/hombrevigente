#!/usr/bin/env python3
"""
Script para correr el detector de señales proactivas (Fase 5 / Capa 6 de la Guía).

Uso:
  python scripts/detect_beta_signals.py
  python scripts/detect_beta_signals.py --json
  HV_STATE_PERSISTENCE=postgres python scripts/detect_beta_signals.py

Emite signals + los maneja (por ahora log + traces).
"""

import argparse
import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from signal_detector import BetaSignalDetector
from action_handler import handle_signal_to_action, run_detect_and_act, load_pending_actions


def main():
    parser = argparse.ArgumentParser(description="HV Beta Signal Detector + Action Handler (proactivo)")
    parser.add_argument("--json", action="store_true", help="Salida en JSON")
    parser.add_argument("--states-dir", help="Override del directorio de estados (útil en tests)")
    parser.add_argument("--pending", action="store_true", help="Mostrar acciones pendientes en vez de escanear")
    args = parser.parse_args()

    if args.pending:
        actions = load_pending_actions(limit=50)
        if args.json:
            print(json.dumps({"count": len(actions), "pending_actions": actions}, ensure_ascii=False, indent=2))
        else:
            print(f"\n[pending_actions] {len(actions)} acciones pendientes\n")
            for a in actions:
                print(f"- {a.get('beta_id')} | {a.get('action_type')} | {a.get('suggested_message','')[:70]}...")
        return 0

    # Full detect + act pipeline (recommended)
    results = run_detect_and_act()

    # Strong Guía warning
    mode = os.getenv("HV_STATE_PERSISTENCE", "files")
    if mode != "postgres" and os.getenv("ENVIRONMENT") == "production":
        print("[WARN] Guía Agéntica: Postgres debe ser el SSOT en producción. "
              "Setea HV_STATE_PERSISTENCE=postgres + HV_DATABASE_URL.")

    if args.json:
        print(json.dumps({
            "count": len(results),
            "actions": results,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"\n[detect_beta_signals] {len(results)} señales procesadas → acciones generadas.\n")
        if not results:
            print("Sin señales en esta corrida. El agente está tranquilo.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
