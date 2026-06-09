#!/usr/bin/env python3
"""
Placeholder / stub for real execution of proactive actions (the "último km").

Este script es un placeholder para integrar el sender real (WhatsApp, Twilio, etc.).
Actualmente solo imprime lo que se enviaría (dry-run style) y respeta el action ya preparado.

El núcleo agentic (decisión + "se corrige" + gates + logging) ya está completo.
El transporte real queda fuera del alcance del "núcleo" de la Guía.

Uso futuro (ejemplo):
  python scripts/send_proactive_action.py --action-id act-xxx

TODOs para integración real:
- Llamar al proveedor de mensajería con el "suggested_message".
- Manejar delivery receipts, retries, rate limits.
- Actualizar el action en pending/executed con "sent" status.
- Emitir traza con costo real del canal si aplica.
- Integrar con feature flag PROACTIVE_EXECUTION (ya respetado upstream).

Por ahora, el workflow y scripts siempre fuerzan dry-run por defecto en scheduled.
"""

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from action_handler import load_pending_actions


def main():
    parser = argparse.ArgumentParser(description="Stub for real proactive action sender")
    parser.add_argument("--action-id", help="Specific action_id to 'send' (dry for now)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Always dry for now (real sender TBD)")
    args = parser.parse_args()

    pending = load_pending_actions(status="pending", limit=100)
    if args.action_id:
        pending = [a for a in pending if a.get("action_id") == args.action_id]

    if not pending:
        print("No pending actions to send (or action_id not found).")
        return 0

    for a in pending:
        print(f"[STUB SENDER] Would send to {a['beta_id']}: {a.get('suggested_message','')[:100]}...")
        print(f"  action_type={a.get('action_type')} severity={a.get('severity')}")
        if args.dry_run:
            print("  (dry-run only — real sender not implemented yet)")

    print("\nNote: Real execution layer is out-of-scope for the agentic core.")
    print("The decision, health gate, feature flags, traces and preparation are complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())