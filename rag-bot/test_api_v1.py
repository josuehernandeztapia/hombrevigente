#!/usr/bin/env python3
"""
API de producto /api/v1/* — la superficie JSON que consume la PWA.

Lo que estos tests protegen: que la app NO sea una puerta trasera. WhatsApp y la
PWA son dos renderizados del mismo motor, así que la app tiene que respetar
exactamente las mismas barreras: auth real, STOP humano, gates clínicos, el
Índice siempre con su marco, y el consentimiento como paso 0 del onboarding.

Run: python -m pytest rag-bot/test_api_v1.py -q
"""
import os
import tempfile
import unittest
from unittest.mock import patch


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HV_APP_SESSION_SECRET"] = "secreto-de-prueba"
        os.environ["HV_BETA_STATES_DIR"] = self._tmp.name
        os.environ["HV_INTAKE_DIR"] = self._tmp.name
        os.environ["HV_STATE_PERSISTENCE"] = "files"
        os.environ["HV_DECISION_LOG_ENABLED"] = "false"
        os.environ["HV_TRACES_DIR"] = self._tmp.name
        from fastapi.testclient import TestClient
        from api.main import app
        self.client = TestClient(app)
        from api_session import issue_token
        self.beta = "wa-525500001111"
        self.auth = {"Authorization": f"Bearer {issue_token(self.beta)}"}

    def tearDown(self):
        self._tmp.cleanup()
        for k in ("HV_APP_SESSION_SECRET", "HV_BETA_STATES_DIR", "HV_INTAKE_DIR",
                  "HV_STATE_PERSISTENCE", "HV_TRACES_DIR"):
            os.environ.pop(k, None)


class TestAuth(_Base):
    """Son datos de salud: sin sesión válida no se entra, y no se degrada."""

    def test_sin_token_401(self):
        for path in ("/api/v1/me", "/api/v1/indice"):
            self.assertEqual(self.client.get(path).status_code, 401, path)
        self.assertEqual(
            self.client.post("/api/v1/chat", json={"message": "hola"}).status_code, 401)

    def test_token_basura_401(self):
        for t in ("Bearer x", "Bearer a.b.c", "Basic abc", ""):
            r = self.client.get("/api/v1/me", headers={"Authorization": t})
            self.assertEqual(r.status_code, 401, t)

    def test_token_firmado_con_otro_secreto_401(self):
        from api_session import issue_token
        os.environ["HV_APP_SESSION_SECRET"] = "otro-secreto"
        ajeno = issue_token(self.beta)
        os.environ["HV_APP_SESSION_SECRET"] = "secreto-de-prueba"
        r = self.client.get("/api/v1/me", headers={"Authorization": f"Bearer {ajeno}"})
        self.assertEqual(r.status_code, 401)

    def test_token_expirado_401(self):
        from api_session import issue_token
        r = self.client.get("/api/v1/me",
                            headers={"Authorization": f"Bearer {issue_token(self.beta, ttl_hours=-1)}"})
        self.assertEqual(r.status_code, 401)

    def test_token_valido_200(self):
        r = self.client.get("/api/v1/me", headers=self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["beta_id"], self.beta)


class TestMismoMotorQueWhatsApp(_Base):
    """La PWA no puede esquivar lo que WhatsApp respeta."""

    def test_chat_respeta_el_stop_humano(self):
        from human_handoff import mark
        mark(self.beta, "humano")
        with patch("api.main._run_query",
                   side_effect=AssertionError("el STOP no debe llamar al RAG")):
            r = self.client.post("/api/v1/chat", json={"message": "¿qué es el NAD+?"},
                                 headers=self.auth)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["tipo"], "handoff_humano")

    def test_pedir_humano_desde_la_app_activa_el_latch(self):
        from human_handoff import is_active
        from state_persistence import load_state
        r = self.client.post("/api/v1/chat", json={"message": "quiero hablar con una persona"},
                             headers=self.auth)
        self.assertEqual(r.json()["tipo"], "handoff_humano")
        self.assertTrue(is_active(load_state(self.beta)),
                        "el latch debe quedar activo también para WhatsApp")

    def test_onboarding_empieza_por_consentimiento(self):
        r = self.client.post("/api/v1/onboarding", json={"message": "hola"}, headers=self.auth)
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["step"], "consent_educativo")
        self.assertEqual(body["field"]["kind"], "consent")
        self.assertNotIn("reply", body, "el texto de WhatsApp no va a la PWA")

    def test_onboarding_devuelve_estructura_para_renderizar(self):
        self.client.post("/api/v1/onboarding", json={"message": "hola"}, headers=self.auth)
        for msg in ("sí", "sí", "Juan Pérez", "44", "Querétaro", "78", "175"):
            r = self.client.post("/api/v1/onboarding", json={"message": msg}, headers=self.auth)
        body = r.json()
        self.assertEqual(body["field"]["kind"], "enum", "debe llegar al objetivo (enum)")
        self.assertTrue(body["field"]["options"], "un enum sin opciones no se puede pintar")
        self.assertIn("label", body["field"]["options"][0])
        self.assertIn("total", body["progress"])

    def test_el_mismo_estado_avanza_por_ambos_canales(self):
        """Continuidad: empieza en la app, sigue en WhatsApp, mismo paso."""
        from onboarding_flow import start_or_advance
        self.client.post("/api/v1/onboarding", json={"message": "hola"}, headers=self.auth)
        self.client.post("/api/v1/onboarding", json={"message": "sí"}, headers=self.auth)
        # ...ahora por el motor de WhatsApp, sin reiniciar nada:
        out = start_or_advance(self.beta, "sí")
        self.assertEqual(out["step"], "nombre",
                         "WhatsApp debe retomar donde la app dejó el guion")


class TestIndiceConMarco(_Base):
    """El número nunca sale desnudo — tampoco por la app."""

    def test_sin_labs_devuelve_marco_con_score_none(self):
        body = self.client.get("/api/v1/indice", headers=self.auth).json()
        self.assertIsNone(body["score"])
        self.assertFalse(body["es_diagnostico"])
        self.assertTrue(body["ilustrativo"])
        self.assertIn("disclaimer", body)

    def test_el_marco_siempre_acompaña_al_numero(self):
        body = self.client.get("/api/v1/indice", headers=self.auth).json()
        for campo in ("etiqueta", "disclaimer", "es_diagnostico", "ilustrativo",
                      "metodologia_version", "derivaciones"):
            self.assertIn(campo, body, f"falta {campo}: el score no puede ir solo")


class TestSesion(_Base):
    """Emitir sesión no puede ser tan fácil como escribir un número."""

    def test_sin_twilio_ni_pin_no_entrega_token(self):
        r = self.client.post("/api/v1/session", json={"phone": "+525500001111"})
        self.assertIn(r.status_code, (401, 403),
                      "un formulario no basta para obtener acceso a datos de salud")

    def test_con_pin_ops_si_entrega(self):
        os.environ["HV_ADMIN_PIN"] = "pin-test"
        try:
            r = self.client.post("/api/v1/session?pin=pin-test", json={"phone": "+525500001111"})
            self.assertEqual(r.status_code, 200)
            self.assertIn("token", r.json())
        finally:
            os.environ.pop("HV_ADMIN_PIN", None)


if __name__ == "__main__":
    unittest.main()
