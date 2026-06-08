#!/usr/bin/env python3
"""
Pipeline MVP-0 secuencial: Tally/intake → labs → protocolo → fila tracker.

  # Caso completo desde Tally CSV + PDF labs:
  python scripts/mvp0_pipeline.py --tally-csv export.csv --labs-pdf lab.pdf --pipeline-row 1

  # Caso #0 desde fixture + labs ya parseados:
  python scripts/mvp0_pipeline.py --intake fixtures/caso0_intake.json \\
    --labs-pdf ~/Downloads/longevity/Estudios_Medicos/Lab_Completo_Metabolico_7oct2025.pdf

  # Solo intake → tracker (sin labs):
  python scripts/mvp0_pipeline.py --tally-csv export.csv --skip-labs --skip-protocol
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = Path(__file__).resolve().parent


def _run(cmd: list[str], *, step: str) -> None:
    print(f"\n── {step} ──")
    proc = subprocess.run(cmd, cwd=_ROOT)
    if proc.returncode != 0:
        raise SystemExit(f"Falló: {step} (exit {proc.returncode})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Orquestador pipeline MVP-0")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--tally-csv", type=Path, help="Export CSV Tally")
    src.add_argument("--intake", type=Path, help="intake_mvp0.json existente")

    parser.add_argument("--tally-row", type=int, default=0)
    parser.add_argument("--pipeline-row", type=int, help="Fila # en tracker Pipeline")
    parser.add_argument("--labs-pdf", type=Path, help="PDF laboratorio para parse")
    parser.add_argument("--labs-json", type=Path, help="JSON labs ya parseado (saltar OCR)")
    parser.add_argument("--output-dir", type=Path, default=_ROOT / "data" / "mvp0_runs")
    parser.add_argument("--skip-labs", action="store_true")
    parser.add_argument("--skip-protocol", action="store_true")
    parser.add_argument("--no-llm", action="store_true", help="Protocolo sin LLM")
    parser.add_argument("--tracker-notes", default="", help="Notas columna Pipeline")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    intake_dir = args.output_dir / "intake"
    labs_dir = args.output_dir / "labs"
    proto_dir = args.output_dir / "protocols"
    for d in (intake_dir, labs_dir, proto_dir):
        d.mkdir(parents=True, exist_ok=True)

    intake_path: Path

    if args.tally_csv:
        cmd = [
            sys.executable,
            str(_SCRIPTS / "intake_from_tally.py"),
            str(args.tally_csv),
            "--row",
            str(args.tally_row),
            "--output-dir",
            str(intake_dir),
        ]
        if args.pipeline_row is not None:
            cmd.extend(["--pipeline-row", str(args.pipeline_row)])
        _run(cmd, step="1/4 Intake desde Tally")
        intakes = sorted(intake_dir.glob("*_intake.json"))
        if not intakes:
            raise SystemExit("No se generó intake JSON")
        intake_path = intakes[-1]
    else:
        intake_path = args.intake.resolve()
        if not intake_path.exists():
            raise SystemExit(f"Intake no encontrado: {intake_path}")
        dest = intake_dir / intake_path.name
        dest.write_text(intake_path.read_text(encoding="utf-8"), encoding="utf-8")
        intake_path = dest
        print(f"\n── 1/4 Intake ──\n✓ {intake_path}")

    labs_json_path = args.labs_json
    if not args.skip_labs:
        if args.labs_pdf:
            _run(
                [
                    sys.executable,
                    str(_SCRIPTS / "labs_intake_manual.py"),
                    str(args.labs_pdf.resolve()),
                    "--output-dir",
                    str(labs_dir),
                ],
                step="2/4 Labs parse",
            )
            labs_json_path = sorted(labs_dir.glob("*.json"))[-1]
        elif labs_json_path and not Path(labs_json_path).exists():
            raise SystemExit(f"Labs JSON no encontrado: {labs_json_path}")
        elif not labs_json_path:
            print("\n── 2/4 Labs parse ──\n⏭ sin PDF (usa --labs-pdf o --labs-json)")
            labs_json_path = None

        if labs_json_path:
            from scripts.mvp0_lib import merge_labs_into_intake

            intake = json.loads(intake_path.read_text(encoding="utf-8"))
            merged = merge_labs_into_intake(
                intake, Path(labs_json_path), root=_ROOT
            )
            intake_path.write_text(
                json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"\n── 2/4 Labs merge ──\n✓ labs_parse_json → {merged['data_moat']['labs_parse_json']}")
    else:
        print("\n── 2/4 Labs parse ──\n⏭ skip")

    if not args.skip_protocol:
        cmd = [
            sys.executable,
            str(_SCRIPTS / "protocol_draft.py"),
            str(intake_path),
            "--output",
            str(proto_dir / intake_path.stem.replace("_intake", "_protocolo_borrador.md")),
        ]
        if labs_json_path and Path(labs_json_path).exists():
            cmd.extend(["--labs-json", str(labs_json_path)])
        if args.no_llm:
            cmd.append("--no-llm")
        _run(cmd, step="3/4 Protocolo borrador")
    else:
        print("\n── 3/4 Protocolo ──\n⏭ skip")

    tracker_cmd = [
        sys.executable,
        str(_SCRIPTS / "tracker_pipeline_row.py"),
        str(intake_path),
        "--tsv",
    ]
    if args.tracker_notes:
        tracker_cmd.extend(["--notes", args.tracker_notes])

    print("\n── 4/4 Tracker Pipeline (copiar TSV) ──")
    subprocess.run(tracker_cmd, cwd=_ROOT)

    manifest = {
        "intake": str(intake_path),
        "labs_json": str(labs_json_path) if labs_json_path else None,
        "protocol_dir": str(proto_dir),
        "output_dir": str(args.output_dir),
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\n✓ Pipeline completo → {args.output_dir}")
    print(f"  manifest: {manifest_path}")


if __name__ == "__main__":
    main()