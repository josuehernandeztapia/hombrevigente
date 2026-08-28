"""
Tests del canal WhatsApp (Twilio) — sin red ni credenciales reales.

Cubre: normalización/lookup de teléfonos, validación de firma Twilio (vector
calculado con el mismo esquema oficial), webhook inbound (TwiML + record_turn),
y el sender real en execute_pending_action (flag REAL_SENDER, fallo → pending).

Run: python -m pytest rag-bot/test_whatsapp_channel.py -q
"""
import base64
import hashlib
import hmac
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from whatsapp_channel import (
    ChannelSendError,
    beta_id_for_phone,
    normalize_phone,
    phone_for_beta,
    pii_scope,
    purge_expired_media,
    send_whatsapp,
    twiml_reply,
    validate_twilio_signature,
    wants_human,
)


class TestPhones(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HV_INTAKE_DIR"] = self._tmp.name
        os.environ["HV_WA_CONTACTS"] = str(Path(self._tmp.name) / "wa_contacts.json")
        intake = {
            "meta": {"beta_id": "caso0"},
            "identity": {"nombre": "Juan", "whatsapp": "+524421000000"},
        }
        (Path(self._tmp.name) / "caso0_intake.json").write_text(
            json.dumps(intake), encoding="utf-8"
        )

    def tearDown(self):
        self._tmp.cleanup()
        os.environ.pop("HV_INTAKE_DIR", None)
        os.environ.pop("HV_WA_CONTACTS", None)

    def test_normalize(self):
        self.assertEqual(normalize_phone("whatsapp:+52 442-100-0000"), "+524421000000")
        self.assertEqual(normalize_phone(""), "")

    def test_lookup_by_intake_and_reverse(self):
        self.assertEqual(beta_id_for_phone("whatsapp:+524421000000"), "caso0")
        self.assertEqual(phone_for_beta("caso0"), "+524421000000")

    def test_unknown_phone_bootstraps_deterministic_id(self):
        self.assertEqual(beta_id_for_phone("+525599887766"), "wa-525599887766")
        self.assertEqual(phone_for_beta("wa-525599887766"), "+525599887766")

    def test_registry_wins(self):
        Path(os.environ["HV_WA_CONTACTS"]).write_text(
            json.dumps({"+524421000000": "beta-registry"}), encoding="utf-8"
        )
        self.assertEqual(beta_id_for_phone("+524421000000"), "beta-registry")


class TestSignature(unittest.TestCase):
    def test_valid_and_invalid(self):
        token = "secret-token"
        url = "https://hv-rag-api.fly.dev/webhook/whatsapp"
        params = {"From": "whatsapp:+521234567890", "Body": "hola"}
        payload = url + "".join(k + params[k] for k in sorted(params))
        sig = base64.b64encode(
            hmac.new(token.encode(), payload.encode(), hashlib.sha1).digest()
        ).decode()
        self.assertTrue(validate_twilio_signature(url, params, sig, token))
        self.assertFalse(validate_twilio_signature(url, params, "bad" + sig, token))
        self.assertFalse(validate_twilio_signature(url, params, "", token))


class TestWebhook(unittest.TestCase):
    def setUp(self):
        os.environ["HV_TWILIO_VALIDATE"] = "false"  # firma cubierta en TestSignature
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HV_BETA_STATES_DIR"] = self._tmp.name
        os.environ["HV_INTAKE_DIR"] = self._tmp.name
        os.environ["HV_DECISION_LOG_ENABLED"] = "false"
        from fastapi.testclient import TestClient
        from api.main import app
        self.client = TestClient(app)

    def tearDown(self):
        self._tmp.cleanup()
        for k in ("HV_TWILIO_VALIDATE", "HV_BETA_STATES_DIR", "HV_INTAKE_DIR"):
            os.environ.pop(k, None)

    def test_inbound_replies_twiml_and_records_turn(self):
        r = self.client.post(
            "/webhook/whatsapp",
            data={"From": "whatsapp:+525511122233", "Body": "hola, ¿qué es HIFU?"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("application/xml", r.headers["content-type"])
        self.assertIn("<Response><Message>", r.text)
        # record_turn debió bootstrapear el estado del lead wa-…
        state_file = Path(self._tmp.name) / "wa-525511122233.json"
        self.assertTrue(state_file.exists(), "webhook must bootstrap beta state")
        state = json.loads(state_file.read_text())
        self.assertEqual(state.get("last_channel"), "whatsapp")

    def test_missing_signature_rejected_when_validation_on(self):
        os.environ["HV_TWILIO_VALIDATE"] = "true"
        os.environ["TWILIO_AUTH_TOKEN"] = "tok"
        try:
            r = self.client.post(
                "/webhook/whatsapp", data={"From": "whatsapp:+5255", "Body": "x"}
            )
            self.assertEqual(r.status_code, 403)
        finally:
            os.environ["HV_TWILIO_VALIDATE"] = "false"
            os.environ.pop("TWILIO_AUTH_TOKEN", None)


class TestWantsHuman(unittest.TestCase):
    """Detección del STOP. Conservadora: mejor un falso positivo (una persona
    lee un mensaje de más) que un falso negativo (alguien en crisis atrapado)."""

    def test_escala(self):
        for txt in ("humano", "HUMANO", "  Humano.  ", "agente", "ayuda", "urgente",
                    "quiero hablar con un humano", "necesito hablar con alguien",
                    "me pueden comunicar con una persona", "hablar con el equipo",
                    "prefiero hablar con un doctor", "SOS"):
            self.assertTrue(wants_human(txt), f"debió escalar: {txt!r}")

    def test_no_escala(self):
        for txt in ("", "hola", "¿qué es HIFU?", "quiero saber de péptidos",
                    "el cuerpo humano necesita proteína",
                    "me interesa el enfoque humano de la clínica",
                    "mi meta es sentirme mejor", "35", "sí"):
            self.assertFalse(wants_human(txt), f"NO debió escalar: {txt!r}")


class TestHumanHandoffWebhook(unittest.TestCase):
    """El fallback promete 'escribe humano' — aquí se prueba que lo cumple."""

    def setUp(self):
        os.environ["HV_TWILIO_VALIDATE"] = "false"
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HV_BETA_STATES_DIR"] = self._tmp.name
        os.environ["HV_INTAKE_DIR"] = self._tmp.name
        os.environ["HV_STATE_PERSISTENCE"] = "files"
        os.environ["HV_DECISION_LOG_ENABLED"] = "false"
        os.environ["HV_TRACES_DIR"] = self._tmp.name
        from fastapi.testclient import TestClient
        from api.main import app
        self.client = TestClient(app)
        self.phone = "whatsapp:+525599988877"
        self.beta = "wa-525599988877"

    def tearDown(self):
        self._tmp.cleanup()
        for k in ("HV_TWILIO_VALIDATE", "HV_BETA_STATES_DIR", "HV_INTAKE_DIR",
                  "HV_STATE_PERSISTENCE", "HV_TRACES_DIR"):
            os.environ.pop(k, None)

    def _post(self, body):
        return self.client.post("/webhook/whatsapp",
                                data={"From": self.phone, "Body": body})

    def test_humano_responde_handoff_sin_llamar_al_rag(self):
        from human_handoff import HANDOFF_REPLY
        # Si el RAG se invoca, el test truena: el STOP no debe gastar LLM.
        with patch("api.main._run_query",
                   side_effect=AssertionError("STOP no debe llamar al RAG")):
            r = self._post("humano")
        self.assertEqual(r.status_code, 200)
        self.assertIn(HANDOFF_REPLY.split("\n")[0][:40], r.text)
        self.assertIn("911", r.text, "debe ofrecer la salida real de emergencia")

    def test_latch_persiste_en_mensajes_siguientes(self):
        self._post("quiero hablar con una persona")
        # Un STOP que dura un solo turno no es un STOP.
        with patch("api.main._run_query",
                   side_effect=AssertionError("el latch debe seguir activo")):
            r = self._post("¿y qué opinas del NAD+?")
        self.assertEqual(r.status_code, 200)
        self.assertIn("911", r.text)

    def test_resolve_devuelve_el_bot(self):
        from human_handoff import is_active, resolve
        from state_persistence import load_state
        self._post("humano")
        self.assertTrue(is_active(load_state(self.beta)))
        resolve(self.beta, by="test")
        self.assertFalse(is_active(load_state(self.beta)))
        # Ya liberado, el flujo normal vuelve. Apagamos el onboarding para aislar
        # el camino RAG (si no, el guion determinístico conduce — es un lead sin
        # intake — y eso ya lo cubre test_onboarding_flow).
        os.environ["HV_FEATURE_WA_ONBOARDING"] = "false"
        try:
            with patch("api.main._run_query", return_value={"answer": "respuesta normal"}):
                r = self._post("¿qué es HIFU?")
        finally:
            os.environ.pop("HV_FEATURE_WA_ONBOARDING", None)
        self.assertIn("respuesta normal", r.text)
        self.assertNotIn("911", r.text, "el handoff ya no debe estar activo")

    def test_cron_no_escribe_a_beta_en_handoff(self):
        from human_handoff import mark
        import action_handler
        mark(self.beta, "humano")
        out = action_handler.execute_pending_action({
            "beta_id": self.beta,
            "action_id": "act-handoff-1",
            "idemp_key": f"{self.beta}:no_activity_7d:followup:h0",
            "signal": {"signal_type": "no_activity_7d"},
            "action_type": "reengage",
            "suggested_message": "Hola, retomemos.",
            "status": "pending",
        }, force=True)  # ni el override de ops atropella el STOP
        self.assertEqual(out.get("status"), "blocked_by_human_handoff")


class TestLabsPII(unittest.TestCase):
    """El beta_id de un lead ES su teléfono; no debe quedar en disco junto a
    sus estudios de salud (LFPDPPP), ni quedarse ahí para siempre."""

    def test_scope_no_contiene_digitos_del_telefono(self):
        beta = "wa-525511122233"
        scope = pii_scope(beta)
        self.assertNotIn("525511122233", scope)
        self.assertNotIn(beta, scope)
        self.assertFalse(any(c.isdigit() and c in "525511122233"[:6] for c in scope[:2]))
        self.assertTrue(scope.startswith("b-"))

    def test_scope_es_estable_y_distinto_por_beta(self):
        self.assertEqual(pii_scope("wa-1"), pii_scope("wa-1"))
        self.assertNotEqual(pii_scope("wa-1"), pii_scope("wa-2"))

    def test_salt_cambia_el_scope(self):
        os.environ["HV_PII_SALT"] = "salt-a"
        a = pii_scope("wa-525511122233")
        os.environ["HV_PII_SALT"] = "salt-b"
        b = pii_scope("wa-525511122233")
        os.environ.pop("HV_PII_SALT", None)
        self.assertNotEqual(a, b, "el salt debe entrar al hash")

    def test_purga_borra_viejos_y_conserva_recientes(self):
        import time
        with tempfile.TemporaryDirectory() as tmp:
            old = Path(tmp) / "b-abc" / "lab_0.pdf"
            old.parent.mkdir(parents=True)
            old.write_bytes(b"%PDF-viejo")
            os.utime(old, (time.time() - 90000, time.time() - 90000))  # ~25h
            fresh = Path(tmp) / "b-def" / "lab_0.pdf"
            fresh.parent.mkdir(parents=True)
            fresh.write_bytes(b"%PDF-nuevo")

            removed = purge_expired_media(tmp, ttl_hours=24)

            self.assertEqual(removed, 1)
            self.assertFalse(old.exists(), "el estudio > TTL debe desaparecer")
            self.assertTrue(fresh.exists(), "el reciente se conserva")


class TestPublicHealth(unittest.TestCase):
    """El health público es liveness, no telemetría: no debe ser un mapa."""

    def setUp(self):
        from fastapi.testclient import TestClient
        from api.main import app
        self.client = TestClient(app)

    def test_health_no_filtra_ops(self):
        body = self.client.get("/api/health").json()
        self.assertEqual(set(body), {"status", "index_loaded", "openai_configured"})
        for leaked in ("pending_signals", "feature_flags", "beta_states_dir",
                       "ssot", "state_persistence", "pending_actions"):
            self.assertNotIn(leaked, body, f"/api/health no debe exponer {leaked}")

    def test_detalle_operativo_sigue_disponible_con_pin(self):
        os.environ["HV_ADMIN_PIN"] = "pin-test"
        try:
            r = self.client.get("/admin/agent_status", headers={"x-admin-pin": "pin-test"})
            self.assertEqual(r.status_code, 200)
            runtime = r.json().get("runtime", {})
            self.assertIn("pending_signals", runtime)
            self.assertIn("feature_flags", runtime)
            self.assertIn("beta_fixture_row_0", runtime)
        finally:
            os.environ.pop("HV_ADMIN_PIN", None)

    def test_health_sin_pin_sigue_siendo_publico(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn(r.json()["status"], ("ok", "degraded"))


class TestRealSender(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ.update({
            "HV_STATE_PERSISTENCE": "files",
            "HV_PENDING_ACTIONS_DIR": self._tmp.name,
            "HV_TRACES_DIR": self._tmp.name,
            "HV_BETA_STATES_DIR": self._tmp.name,
            "HV_INTAKE_DIR": self._tmp.name,
            "HV_DECISION_LOG_ENABLED": "false",
        })

    def tearDown(self):
        self._tmp.cleanup()
        for k in ("HV_FEATURE_REAL_SENDER", "TWILIO_ACCOUNT_SID",
                  "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM"):
            os.environ.pop(k, None)

    def _pending_action(self, suffix="s1"):
        return {
            "beta_id": "wa-525500000001",
            "action_id": f"act-{suffix}",
            "idemp_key": f"wa-525500000001:no_activity_72h:followup:{suffix}",
            "signal": {"signal_type": "no_activity_72h"},
            "action_type": "reengage",
            "suggested_message": "Hola, retomemos tu protocolo.",
            "status": "pending",
        }

    def test_flag_off_keeps_simulated_path(self):
        from action_handler import execute_pending_action
        r = execute_pending_action(self._pending_action("off"), dry_run=False, force=True)
        self.assertEqual(r.get("status"), "executed")  # simulado, como antes

    def test_send_failure_leaves_action_pending(self):
        os.environ["HV_FEATURE_REAL_SENDER"] = "true"
        # Twilio sin configurar → ChannelSendError → send_failed, NO executed
        from action_handler import execute_pending_action, is_idemp_already_executed
        a = self._pending_action("fail")
        r = execute_pending_action(a, dry_run=False, force=True)
        self.assertEqual(r.get("status"), "send_failed")
        self.assertFalse(is_idemp_already_executed(a["idemp_key"]))

    def test_send_success_marks_executed_with_receipt(self):
        os.environ["HV_FEATURE_REAL_SENDER"] = "true"
        os.environ["TWILIO_ACCOUNT_SID"] = "ACtest"
        os.environ["TWILIO_AUTH_TOKEN"] = "tok"
        os.environ["TWILIO_WHATSAPP_FROM"] = "whatsapp:+14155238886"

        class _Resp:
            status_code = 201
            text = "{}"
            @staticmethod
            def json():
                return {"sid": "SM123", "status": "queued"}

        from action_handler import execute_pending_action
        with patch("requests.post", return_value=_Resp()) as mock_post:
            r = execute_pending_action(self._pending_action("ok"), dry_run=False, force=True)
        self.assertEqual(r.get("status"), "executed")
        self.assertEqual(r.get("delivery", {}).get("sid"), "SM123")
        sent = mock_post.call_args.kwargs.get("data") or mock_post.call_args[1].get("data")
        self.assertEqual(sent["To"], "whatsapp:+525500000001")

    def test_send_whatsapp_requires_creds(self):
        with self.assertRaises(ChannelSendError):
            send_whatsapp("+5255", "hola")


class TestTwiml(unittest.TestCase):
    def test_escapes_and_truncates(self):
        xml = twiml_reply("<b>hola & adiós</b>" + "x" * 2000)
        self.assertIn("&lt;b&gt;hola &amp; adiós&lt;/b&gt;", xml)
        self.assertLess(len(xml), 1700)


if __name__ == "__main__":
    unittest.main()
