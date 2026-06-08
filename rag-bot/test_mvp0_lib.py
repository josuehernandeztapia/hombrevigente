#!/usr/bin/env python3
"""Tests pipeline MVP-0 (sin API)."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT / "scripts"))
from mvp0_lib import (  # noqa: E402
    derive_screening,
    intake_to_pipeline_row,
    load_tally_map,
    merge_labs_into_intake,
    parse_tally_row,
    raw_to_intake,
    route_profile,
    suggest_stack,
)
from labs_intake_manual import validate_labs_payload  # noqa: E402


class TestMvp0Lib(unittest.TestCase):
    def test_suggest_stack_wolverine(self):
        self.assertEqual(suggest_stack("recuperacion_dolor", ["estetica"]), "wolverine")

    def test_screening_litio(self):
        tally_map = load_tally_map()
        raw = {
            "psiquiatria_tratamiento": "Sí",
            "medicacion_cronica": "Litio carbonato",
            "cancer_antecedente": "No",
            "cardio_renal_hepatica": "No",
        }
        s = derive_screening(raw, tally_map)
        self.assertTrue(s["bandera_activa"])
        self.assertIn("psiquiatría", s["bandera_detalle"])

    def test_route_verde(self):
        intake = {
            "identity": {"nombre": "Beta Verde"},
            "screening": {"bandera_activa": False},
            "pipeline": {"stack_sugerido": "glow"},
        }
        r = route_profile(intake)
        self.assertEqual(r["perfil"], "verde")
        self.assertEqual(r["entrega"], "MVP0_Entrega_Verde.md")

    def test_route_marcado_caso0(self):
        intake = json.loads(
            (_ROOT / "fixtures" / "caso0_intake_p1_entrega.json").read_text(encoding="utf-8")
        )
        r = route_profile(intake)
        self.assertEqual(r["perfil"], "marcado")
        self.assertIn("MVP0_Entrega_Marcado", r["entrega"])

    def test_caso0_fixture_pipeline_row(self):
        intake = json.loads(
            (_ROOT / "fixtures" / "caso0_intake.json").read_text(encoding="utf-8")
        )
        row = intake_to_pipeline_row(intake)
        self.assertEqual(row["#"], 0)
        self.assertIn("SÍ", row["Bandera screening"])
        self.assertEqual(row["Stack asignado"], "Wolverine")

    def test_tally_csv_roundtrip(self):
        import csv

        csv_path = _ROOT / "fixtures" / "tally_export_sample.csv"
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            row = next(csv.DictReader(f))
        field_map = load_tally_map()
        raw = parse_tally_row(row, field_map)
        intake = raw_to_intake(raw, source="tally", pipeline_row=1)
        self.assertEqual(intake["objetivos"]["principal"], "recuperacion_dolor")
        self.assertTrue(intake["screening"]["bandera_activa"])

    def test_merge_labs_into_intake(self):
        intake = json.loads(
            (_ROOT / "fixtures" / "caso0_intake.json").read_text(encoding="utf-8")
        )
        labs = _ROOT / "fixtures" / "caso0_labs_metabolico.json"
        merged = merge_labs_into_intake(intake, labs, root=_ROOT)
        self.assertIn("fixtures/caso0_labs_metabolico.json", merged["data_moat"]["labs_parse_json"])
        self.assertTrue(merged["data_moat"]["labs_subidos"])

    def test_validate_labs_fixture(self):
        data = json.loads(
            (_ROOT / "fixtures" / "caso0_labs_metabolico.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_labs_payload(data), [])
        self.assertTrue(validate_labs_payload({"biomarkers": []}))

    def test_intake_from_tally_script(self):
        proc = subprocess.run(
            [
                sys.executable,
                "scripts/intake_from_tally.py",
                "fixtures/tally_export_sample.csv",
                "--output-dir",
                "/tmp/hv-mvp0-test-intake",
            ],
            cwd=_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()