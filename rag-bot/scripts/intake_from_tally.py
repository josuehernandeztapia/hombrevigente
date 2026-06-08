#!/usr/bin/env python3
"""
Tally CSV export → intake_mvp0.json

En Tally: Responses → Export CSV. Usa las mismas preguntas de MVP0_Cuestionario.md.

  python scripts/intake_from_tally.py export.csv
  python scripts/intake_from_tally.py export.csv --row 0 --pipeline-row 1
  python scripts/intake_from_tally.py export.csv --all
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mvp0_lib import raw_to_intake  # noqa: E402
from mvp0_lib import parse_tally_row, load_tally_map  # noqa: E402

_ROOT = Path(__file__).resolve().parent.parent


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def main() -> None:
    parser = argparse.ArgumentParser(description="Tally CSV → intake_mvp0.json")
    parser.add_argument("csv", type=Path, help="Export CSV de Tally")
    parser.add_argument("--row", type=int, default=0, help="Índice de fila (0-based)")
    parser.add_argument("--pipeline-row", type=int, help="Número fila en tracker Pipeline")
    parser.add_argument("--all", action="store_true", help="Procesar todas las filas")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_ROOT / "data" / "intake",
        help="Directorio salida (gitignored)",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        raise SystemExit(f"CSV no encontrado: {args.csv}")

    rows = _read_csv(args.csv)
    if not rows:
        raise SystemExit("CSV vacío")

    field_map = load_tally_map()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    indices = range(len(rows)) if args.all else [args.row]
    for i in indices:
        if i >= len(rows):
            raise SystemExit(f"Fila {i} fuera de rango (hay {len(rows)} respuestas)")

        raw = parse_tally_row(rows[i], field_map)
        raw["submitted_at"] = rows[i].get("Submitted at") or rows[i].get("Fecha de envío", "")
        response_id = rows[i].get("Response ID") or rows[i].get("ID de respuesta", "")

        intake = raw_to_intake(
            raw,
            source="tally",
            pipeline_row=args.pipeline_row if not args.all else i + 1,
            response_id=response_id or None,
        )

        nombre = intake["identity"].get("nombre") or f"beta_{i}"
        slug = "".join(c if c.isalnum() else "_" for c in nombre.lower())[:40].strip("_")
        out_path = args.output_dir / f"{slug}_intake.json"
        out_path.write_text(
            json.dumps(intake, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"✓ {out_path}")
        print(f"  estado={intake['pipeline']['estado']} · stack={intake['pipeline']['stack_sugerido']}")
        if intake["screening"]["bandera_activa"]:
            print(f"  ⚠ screening: {intake['screening']['bandera_detalle']}")


if __name__ == "__main__":
    main()