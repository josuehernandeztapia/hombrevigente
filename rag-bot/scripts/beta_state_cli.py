#!/usr/bin/env python3
"""CLI — estado operativo por beta (fase + next_action)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from beta_state import (  # noqa: E402
    beta_id_from_intake,
    derive_state_from_intake,
    load_state,
    save_state,
    sync_from_intake,
    transition,
)


def _load_intake(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_show(args: argparse.Namespace) -> int:
    if args.intake:
        intake = _load_intake(Path(args.intake))
        state = derive_state_from_intake(intake)
    else:
        state = load_state(args.beta_id)
        if not state:
            print(f"No existe estado para {args.beta_id}", file=sys.stderr)
            return 1
    print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    intake = _load_intake(Path(args.intake))
    overrides = {}
    if args.foto:
        overrides["foto_baseline"] = True
    if args.baseline:
        overrides["baseline_subjetivo"] = True
    if args.clearance:
        overrides["clearance_medica"] = True
    state = sync_from_intake(
        intake,
        channel=args.channel,
        slot_overrides=overrides or None,
        persist=not args.dry_run,
    )
    print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    state = load_state(args.beta_id)
    if not state:
        print(f"No existe estado para {args.beta_id}", file=sys.stderr)
        return 1
    transition(state, args.phase, note=args.note or "")
    if args.intake:
        intake = _load_intake(Path(args.intake))
        derived = derive_state_from_intake(intake)
        state.next_action = derived.next_action
        state.slots = derived.slots
        state.perfil = derived.perfil
    save_state(state)
    print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="HV beta state (MVP-0)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_show = sub.add_parser("show", help="Mostrar estado")
    p_show.add_argument("--intake", help="Derivar desde intake JSON")
    p_show.add_argument("--beta-id", help="Leer persistido")
    p_show.set_defaults(func=cmd_show)

    p_sync = sub.add_parser("sync", help="Sincronizar desde intake → data/beta_states/")
    p_sync.add_argument("intake", help="Ruta intake JSON")
    p_sync.add_argument("--channel", default="cli")
    p_sync.add_argument("--foto", action="store_true")
    p_sync.add_argument("--baseline", action="store_true")
    p_sync.add_argument("--clearance", action="store_true")
    p_sync.add_argument("--dry-run", action="store_true")
    p_sync.set_defaults(func=cmd_sync)

    p_adv = sub.add_parser("advance", help="Cambiar fase manualmente")
    p_adv.add_argument("beta_id")
    p_adv.add_argument("phase")
    p_adv.add_argument("--note", default="")
    p_adv.add_argument("--intake", help="Recalcular next_action desde intake")
    p_adv.set_defaults(func=cmd_advance)

    args = parser.parse_args()
    if args.cmd == "show" and not args.intake and not args.beta_id:
        parser.error("show requiere --intake o --beta-id")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())