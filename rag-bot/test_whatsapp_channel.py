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
    send_whatsapp,
    twiml_reply,
    validate_twilio_signature,
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
