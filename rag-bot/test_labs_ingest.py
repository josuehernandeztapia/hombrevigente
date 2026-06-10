"""
Tests de ingesta de labs por WhatsApp (file mode, sin red ni PDFs reales).

process_pdf y la descarga de Twilio se mockean — aquí se valida el cableado:
descarga → ingest → estado (slot labs_parseados + labs_result) → resumen, y los
caminos de fallo (sin biomarcadores, sin creds).

Run: python -m pytest rag-bot/test_labs_ingest.py -q
"""
import os
import tempfile
import unittest
from unittest.mock import patch

from whatsapp_channel import (
    ChannelSendError, download_twilio_media, is_supported_labs_media,
)


# Estructura REAL del parser (LABS_JSON_SCHEMA): key "biomarkers" + name/value/unit/flag.
# (Antes este fixture usaba "biomarcadores"/nombre/valor — formato que el parser NO
# produce — y ocultaba que labs_ingest leía la key equivocada.)
_FAKE_LABS = {
    "biomarkers": [
        {"name": "hs-CRP", "value": "0.8", "unit": "mg/L", "flag": "normal"},
        {"name": "Glucosa", "value": "110", "unit": "mg/dL", "flag": "high"},
        {"name": "HbA1c", "value": "5.9", "unit": "%", "flag": "high"},
    ],
    "extraction_method": "text",
}


class TestSupportedMedia(unittest.TestCase):
    def test_supported_types(self):
        self.assertTrue(is_supported_labs_media("application/pdf"))
        self.assertTrue(is_supported_labs_media("image/jpeg; charset=binary"))
        self.assertFalse(is_supported_labs_media("audio/ogg"))
        self.assertFalse(is_supported_labs_media(""))


class TestDownload(unittest.TestCase):
    def test_requires_creds(self):
        for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"):
            os.environ.pop(k, None)
        with self.assertRaises(ChannelSendError):
            download_twilio_media("https://api.twilio.com/x", "/tmp/x")

    def test_saves_with_extension_from_content_type(self):
        os.environ["TWILIO_ACCOUNT_SID"] = "ACtest"
        os.environ["TWILIO_AUTH_TOKEN"] = "tok"

        class _R:
            status_code = 200
            content = b"%PDF-1.4 fake"
            headers = {"Content-Type": "application/pdf"}
            text = ""

        with tempfile.TemporaryDirectory() as td:
            with patch("requests.get", return_value=_R()):
                path = download_twilio_media("https://api.twilio.com/Media/ME1", td,
                                             content_type="application/pdf", filename_stem="lab_0")
            self.assertTrue(path.endswith("lab_0.pdf"))
            self.assertEqual(open(path, "rb").read(), b"%PDF-1.4 fake")
        for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"):
            os.environ.pop(k, None)


class TestIngest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HV_STATE_PERSISTENCE"] = "files"
        os.environ["HV_BETA_STATES_DIR"] = self._tmp.name
        os.environ["HV_TRACES_DIR"] = self._tmp.name
        os.environ["HV_DECISION_LOG_ENABLED"] = "false"
        self.beta = "wa-525500000055"

    def tearDown(self):
        self._tmp.cleanup()
        for k in ("HV_BETA_STATES_DIR", "HV_TRACES_DIR"):
            os.environ.pop(k, None)

    def test_ingest_fills_slot_and_stores_result(self):
        import labs_ingest
        from state_persistence import load_state
        with patch("scripts.labs_intake_manual.process_pdf", return_value=dict(_FAKE_LABS)), \
             patch("scripts.labs_intake_manual.validate_labs_payload", return_value=[]):
            r = labs_ingest.ingest_labs_pdf(self.beta, "/tmp/lab_0.pdf")
        self.assertTrue(r["ok"])
        self.assertEqual(r["n_markers"], 3)
        self.assertEqual(r["flags"], 2)  # glucosa + HbA1c fuera de rango
        self.assertIn("biomarcadores", r["summary_text"].lower())

        state = load_state(self.beta)
        self.assertTrue((state.get("slots") or {}).get("labs_parseados"))
        self.assertIn("labs_result", state)
        self.assertEqual(len(state["labs_result"]["biomarkers"]), 3)

    def test_no_markers_does_not_fill_slot(self):
        import labs_ingest
        from state_persistence import load_state
        with patch("scripts.labs_intake_manual.process_pdf",
                   return_value={"biomarkers": [], "extraction_method": "vision"}):
            r = labs_ingest.ingest_labs_pdf(self.beta, "/tmp/empty.pdf")
        self.assertFalse(r["ok"])
        state = load_state(self.beta) or {}
        self.assertFalse((state.get("slots") or {}).get("labs_parseados"))

    def test_parser_exception_is_friendly(self):
        import labs_ingest
        with patch("scripts.labs_intake_manual.process_pdf", side_effect=RuntimeError("boom")):
            r = labs_ingest.ingest_labs_pdf(self.beta, "/tmp/x.pdf")
        self.assertFalse(r["ok"])
        self.assertIn("equipo", r["summary_text"].lower())


class TestWebhookMedia(unittest.TestCase):
    def setUp(self):
        os.environ["HV_TWILIO_VALIDATE"] = "false"
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HV_BETA_STATES_DIR"] = self._tmp.name
        os.environ["HV_INTAKE_DIR"] = self._tmp.name
        os.environ["HV_LABS_INBOX_DIR"] = self._tmp.name
        os.environ["HV_DECISION_LOG_ENABLED"] = "false"
        # No queremos que el onboarding intercepte el media en este test
        os.environ["HV_FEATURE_WA_ONBOARDING"] = "false"
        from fastapi.testclient import TestClient
        from api.main import app
        self.client = TestClient(app)

    def tearDown(self):
        self._tmp.cleanup()
        for k in ("HV_TWILIO_VALIDATE", "HV_BETA_STATES_DIR", "HV_INTAKE_DIR",
                  "HV_LABS_INBOX_DIR", "HV_FEATURE_WA_ONBOARDING"):
            os.environ.pop(k, None)

    def test_inbound_pdf_ingests_and_replies(self):
        with patch("whatsapp_channel.download_twilio_media", return_value="/tmp/lab_0.pdf"), \
             patch("labs_ingest.ingest_labs_pdf",
                   return_value={"ok": True, "n_markers": 3, "flags": 1,
                                 "summary_text": "¡Recibí tu estudio! Detecté 3 biomarcadores."}):
            r = self.client.post("/webhook/whatsapp", data={
                "From": "whatsapp:+525500000055", "Body": "",
                "NumMedia": "1",
                "MediaUrl0": "https://api.twilio.com/Media/ME1",
                "MediaContentType0": "application/pdf",
            })
        self.assertEqual(r.status_code, 200)
        self.assertIn("estudio", r.text.lower())

    def test_unsupported_media_falls_through(self):
        # audio → no es estudio → _handle_inbound_media devuelve None → sigue flujo de texto (vacío→empty)
        r = self.client.post("/webhook/whatsapp", data={
            "From": "whatsapp:+525500000056", "Body": "",
            "NumMedia": "1",
            "MediaUrl0": "https://api.twilio.com/Media/ME2",
            "MediaContentType0": "audio/ogg",
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn("<Response>", r.text)


if __name__ == "__main__":
    unittest.main()
