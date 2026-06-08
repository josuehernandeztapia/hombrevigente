#!/usr/bin/env python3
"""
Intake JSON → ruta verde vs marcado (triage MVP-0).

  python scripts/mvp0_route.py fixtures/caso0_intake_p1_entrega.json
  python scripts/mvp0_route.py data/intake/juan_intake.json --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mvp0_lib import route_profile  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Triage verde vs marcado")
    parser.add_argument("intake_json", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    intake = json.loads(args.intake_json.read_text(encoding="utf-8"))
    route = route_profile(intake)

    if args.json:
        print(json.dumps(route, ensure_ascii=False, indent=2))
        return

    print(f"Perfil: {route['perfil'].upper()}")
    if route.get("bandera"):
        print(f"Bandera: {route['bandera']}")
    print(f"UX: {route['ux']}")
    print(f"Estado Pipeline sugerido: {route['estado_pipeline']}")
    print(f"Entrega: estrategia_2026/{route['entrega']}")
    print("Docs:")
    for d in route["docs"]:
        print(f"  - estrategia_2026/{d}")
    print(f"\n{route['nota']}")


if __name__ == "__main__":
    main()