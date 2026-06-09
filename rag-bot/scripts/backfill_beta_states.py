#!/usr/bin/env python3
"""
Backfill de estados desde archivos JSON a hv_beta_states (Postgres).

Uso típico durante cutover Fase 1:
  python scripts/backfill_beta_states.py
  python scripts/backfill_beta_states.py --beta-id row-0
  python scripts/backfill_beta_states.py --dry-run

Respeta HV_STATE_PERSISTENCE y HV_DATABASE_URL.
Escribe con version=0 (bootstrap) o usa la versión actual si ya existe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from state_persistence import (
    StateVersionConflictError,
    _is_postgres_available,
    _load_from_file,
    _persistence_mode,
    _save_to_postgres,
    get_current_version,
    save_state,
)


def load_all_local_states(states_dir: Path) -> Dict[str, Dict[str, Any]]:
    states: Dict[str, Dict[str, Any]] = {}
    if not states_dir.exists():
        return states
    for p in sorted(states_dir.glob("*.json")):
        beta_id = p.stem
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            states[beta_id] = data
        except Exception as e:
            print(f"[backfill] WARN: could not load {p}: {e}")
    return states


def backfill(beta_id: str | None = None, dry_run: bool = False, force: bool = False) -> int:
    if not _is_postgres_available():
        print("ERROR: Postgres no está disponible (HV_DATABASE_URL / DATABASE_URL).", file=sys.stderr)
        return 1

    mode = _persistence_mode()
    print(f"[backfill] mode={mode}  postgres_available=True  dry_run={dry_run}")

    states_dir = Path(os.getenv("HV_BETA_STATES_DIR", "data/beta_states"))
    all_states = load_all_local_states(states_dir)

    if beta_id:
        targets = {beta_id: all_states.get(beta_id)} if beta_id in all_states else {}
    else:
        targets = {k: v for k, v in all_states.items() if v}

    if not targets:
        print("[backfill] No se encontraron estados locales para backfill.")
        return 0

    processed = 0
    for bid, state in targets.items():
        if not state:
            continue

        # Asegurar last_active_at (importante para ReentryHandler y signals)
        if "last_active_at" not in state:
            from state_persistence import _utc_now
            state["last_active_at"] = _utc_now()

        if dry_run:
            print(f"[dry-run] {bid} -> version={state.get('_state_version') or 'new'}  phase={state.get('phase')}  last_active={state.get('last_active_at')}")
            processed += 1
            continue

        current = get_current_version(bid)
        if current is not None and not force:
            print(f"[backfill] SKIP {bid} (ya existe en DB con version={current})")
            continue

        try:
            if current is None:
                # Bootstrap
                new_v = _save_to_postgres(bid, state, expected_version=None)
            else:
                new_v = _save_to_postgres(bid, state, expected_version=current)

            # Mirror al archivo si dual
            if mode == "dual":
                try:
                    save_state(bid, state, expected_version=None, also_write_file=True)
                except Exception:
                    pass

            print(f"[backfill] OK {bid} -> version={new_v}")
            processed += 1
        except StateVersionConflictError as e:
            print(f"[backfill] CONFLICT {bid}: {e}")
        except Exception as e:
            print(f"[backfill] ERROR {bid}: {e}")

    print(f"\n[backfill] Procesados: {processed}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill beta states JSON → Postgres (hv_beta_states)")
    parser.add_argument("--beta-id", help="Solo un beta específico")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Sobreescribe aunque ya exista en DB")
    args = parser.parse_args()

    return backfill(beta_id=args.beta_id, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
