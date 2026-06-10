"""
Puente 2→3: labs parseados → Vigente Longevidad (guardado en el state, nivel B).

Cubre el mapeo de nombres crudos de labs MX → claves del Índice, la normalización de
unidades (apoB g/L↔mg/dL), y el flujo end-to-end ingest_labs_pdf → state["indice_longevidad"]
sin pegarle a OpenAI (mockeamos el parser).

Run: python -m pytest rag-bot/test_bridge_labs_indice.py -q
"""
import os
import tempfile
import unittest
from unittest.mock import patch

from indice_vigente import (
    _parse_lab_value,
    labs_result_to_longevidad_inputs,
    compute_from_labs_result,
)


def _labs_result(markers):
    return {"biomarkers": markers, "patient": {}, "lab": {}, "flags_critical": [], "notes": []}


class TestParseValue(unittest.TestCase):
    def test_variants(self):
        self.assertEqual(_parse_lab_value("95 mg/dL"), 95.0)
        self.assertEqual(_parse_lab_value("5,4"), 5.4)      # coma decimal MX
        self.assertEqual(_parse_lab_value("<0.30"), 0.30)   # límite de detección
        self.assertEqual(_parse_lab_value(88), 88.0)
        self.assertIsNone(_parse_lab_value("no detectado"))


class TestMapeoNombres(unittest.TestCase):
    def test_nombres_mx_mapean(self):
        lr = _labs_result([
            {"name": "Glucosa", "value": "88", "unit": "mg/dL", "flag": "normal"},
            {"name": "Hemoglobina glucosilada (HbA1c)", "value": "5,3", "unit": "%", "flag": "normal"},
            {"name": "Triglicéridos", "value": "85", "unit": "mg/dL", "flag": "normal"},
            {"name": "Proteína C reactiva ultrasensible", "value": "0.8", "unit": "mg/L", "flag": "normal"},
            {"name": "Homocisteína", "value": "8", "unit": "µmol/L", "flag": "normal"},
        ])
        inp = labs_result_to_longevidad_inputs(lr)
        self.assertEqual(inp["glucosa_ayuno"], 88.0)
        self.assertEqual(inp["hba1c"], 5.3)
        self.assertEqual(inp["trigliceridos"], 85.0)
        self.assertEqual(inp["hs_crp"], 0.8)
        self.assertEqual(inp["homocisteina"], 8.0)

    def test_glucosa_postprandial_no_mapea(self):
        lr = _labs_result([
            {"name": "Glucosa postprandial 2h", "value": "140", "unit": "mg/dL", "flag": "normal"},
        ])
        self.assertNotIn("glucosa_ayuno", labs_result_to_longevidad_inputs(lr))

    def test_apob_g_por_litro_se_convierte_a_mg_dl(self):
        # 1.2 g/L = 120 mg/dL → debe cruzar umbral clínico (>100), NO puntuar como óptimo
        lr = _labs_result([{"name": "Apolipoproteína B", "value": "1.2", "unit": "g/L", "flag": "high"}])
        inp = labs_result_to_longevidad_inputs(lr)
        self.assertEqual(inp["apob"], 120.0)
        res = compute_from_labs_result(lr)
        self.assertTrue(any(d["marcador"] == "apob" for d in res["derivaciones"]),
                        "apoB 120 mg/dL debe disparar derivación, no puntuar óptimo")

    def test_apob_mg_dl_se_respeta(self):
        lr = _labs_result([{"name": "Apo B", "value": "75", "unit": "mg/dL", "flag": "normal"}])
        self.assertEqual(labs_result_to_longevidad_inputs(lr)["apob"], 75.0)

    def test_marcadores_irrelevantes_se_ignoran(self):
        lr = _labs_result([{"name": "Colesterol LDL", "value": "100", "unit": "mg/dL", "flag": "normal"}])
        self.assertEqual(labs_result_to_longevidad_inputs(lr), {})


class TestComputeFromLabs(unittest.TestCase):
    def test_end_to_end_framed(self):
        lr = _labs_result([
            {"name": "Glucosa", "value": "88", "unit": "mg/dL", "flag": "normal"},
            {"name": "Apo B", "value": "70", "unit": "mg/dL", "flag": "normal"},
        ])
        res = compute_from_labs_result(lr)
        self.assertFalse(res["es_diagnostico"])
        self.assertIsNotNone(res["score"])
        self.assertEqual(res["subscores"]["metabolico"], 100.0)


class TestIngestBridge(unittest.TestCase):
    """ingest_labs_pdf debe guardar state['indice_longevidad'] tras parsear (parser mockeado)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HV_STATE_PERSISTENCE"] = "files"
        os.environ["HV_BETA_STATES_DIR"] = self._tmp.name
        os.environ["HV_TRACES_DIR"] = self._tmp.name
        os.environ["HV_DECISION_LOG_ENABLED"] = "false"

    def tearDown(self):
        self._tmp.cleanup()
        for k in ("HV_STATE_PERSISTENCE", "HV_BETA_STATES_DIR", "HV_TRACES_DIR"):
            os.environ.pop(k, None)

    def test_ingest_guarda_indice_en_state(self):
        fake_structured = _labs_result([
            {"name": "Glucosa", "value": "88", "unit": "mg/dL", "flag": "normal"},
            {"name": "Apo B", "value": "70", "unit": "mg/dL", "flag": "normal"},
        ])
        fake_structured["extraction_method"] = "text"
        import labs_ingest
        with patch("scripts.labs_intake_manual.process_pdf", return_value=fake_structured), \
             patch("scripts.labs_intake_manual.validate_labs_payload", return_value=[]):
            r = labs_ingest.ingest_labs_pdf("wa-bridge-test", "/tmp/fake.pdf")
        self.assertTrue(r["ok"])
        # el índice quedó persistido en el estado, framed, sin exponerse en el reply
        from state_persistence import load_state
        st = load_state("wa-bridge-test") or {}
        self.assertIn("indice_longevidad", st)
        self.assertFalse(st["indice_longevidad"]["es_diagnostico"])
        self.assertIsNotNone(st["indice_longevidad"]["score"])
        self.assertNotIn(str(st["indice_longevidad"]["score"]), r.get("summary_text", ""))


if __name__ == "__main__":
    unittest.main()
