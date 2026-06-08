#!/usr/bin/env python3
"""
intake_mvp0.json → fila CSV para hoja Pipeline (Google Sheets).

Copia la línea TSV en la siguiente fila vacía de Pipeline.

  python scripts/tracker_pipeline_row.py data/intake/juan_intake.json
  python scripts/tracker_pipeline_row.py data/intake/juan_intake.json --tsv
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mvp0_lib import PIPELINE_COLUMNS, intake_to_pipeline_row  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Intake JSON → fila Pipeline tracker")
    parser.add_argument("intake_json", type=Path)
    parser.add_argument("--tsv", action="store_true", help="Tab-separated (pegar en Sheets)")
    parser.add_argument("--notes", default="", help="Texto extra columna Notas")
    args = parser.parse_args()

    intake = json.loads(args.intake_json.read_text(encoding="utf-8"))
    row = intake_to_pipeline_row(intake)
    if args.notes:
        row["Notas"] = args.notes

    buf = io.StringIO()
    if args.tsv:
        writer = csv.writer(buf, delimiter="\t", lineterminator="\n")
        writer.writerow([row.get(c, "") for c in PIPELINE_COLUMNS])
    else:
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow(PIPELINE_COLUMNS)
        writer.writerow([row.get(c, "") for c in PIPELINE_COLUMNS])

    print(buf.getvalue().rstrip())
    print(f"\n# Pega en Google Sheets → hoja Pipeline (fila vacía)", file=sys.stderr)


if __name__ == "__main__":
    main()