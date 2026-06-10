"""
Tests del onboarding conversacional determinístico (file mode, sin red).

Cubre: consentimiento como paso 0, recolección secuencial, validación, gate de
screening (cáncer/psiquiatría → bandera → fase screening), rechazo de consentimiento
(abortar sin capturar), y persistencia del progreso entre mensajes.

Run: python -m pytest rag-bot/test_onboarding_flow.py -q
"""
import os
import tempfile
import unittest

import onboarding_flow as of
from state_persistence import load_state


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HV_STATE_PERSISTENCE"] = "files"
        os.environ["HV_BETA_STATES_DIR"] = self._tmp.name
        os.environ["HV_TRACES_DIR"] = self._tmp.name
        os.environ["HV_DECISION_LOG_ENABLED"] = "false"
        os.environ.pop("HV_ONBOARDING_LLM_TONE", None)
        self.beta = "wa-525500000099"

    def tearDown(self):
        self._tmp.cleanup()
        for k in ("HV_BETA_STATES_DIR", "HV_TRACES_DIR"):
            os.environ.pop(k, None)

    def feed(self, messages):
        out = None
        for m in messages:
            out = of.start_or_advance(self.beta, m)
        return out


class TestHappyPath(_Base):
    def test_full_flow_completes_and_syncs_state(self):
        # 1er mensaje arranca (no consume); luego respondemos cada paso.
        first = of.start_or_advance(self.beta, "hola")
        self.assertEqual(first["status"], "in_progress")
        self.assertIn("educativa", first["reply"].lower())

        out = self.feed([
            "sí",            # consent_educativo
            "sí",            # consent_datos
            "Juan Josué",    # nombre
            "44",            # edad
            "Querétaro",     # ciudad
            "78",            # peso_kg
            "175",           # estatura_cm
            "5",             # objetivo_principal -> longevidad
            "Sentirme con más energía",  # meta_8_semanas
            "1",             # cancer -> no
            "1",             # psiquiatria -> no
            "1",             # cardio -> no
        ])
        self.assertEqual(out["status"], "completed")
        self.assertIn("estudios", out["reply"].lower())

        state = load_state(self.beta)
        self.assertEqual(state["onboarding"]["status"], "completed")
        # intake sincronizado → sin bandera entra en fase onboarding + tally_completo
        self.assertEqual(state.get("phase"), "onboarding")
        self.assertTrue((state.get("slots") or {}).get("tally_completo"))

    def test_progress_persists_between_messages(self):
        of.start_or_advance(self.beta, "hola")
        of.start_or_advance(self.beta, "sí")  # consent_educativo
        st = load_state(self.beta)
        self.assertEqual(st["onboarding"]["idx"], 1)  # avanzó a consent_datos
        self.assertTrue(of.is_onboarding_active(st))


class TestGate(_Base):
    def test_cancer_yes_raises_bandera_and_routes_to_screening(self):
        of.start_or_advance(self.beta, "hola")
        out = self.feed([
            "sí", "sí", "Pedro", "50", "CDMX", "90", "180",
            "2",   # objetivo recuperacion_dolor
            "Recuperar movilidad",
            "2",   # cancer -> SÍ  (gate)
            "1",   # psiq -> no
            "1",   # cardio -> no
        ])
        self.assertEqual(out["status"], "completed")
        self.assertIn("médica", out["reply"].lower())
        state = load_state(self.beta)
        # La bandera se observa como fase 'screening' (deriva a médico, no protocolo directo).
        self.assertEqual(state.get("phase"), "screening")
        self.assertEqual(state["onboarding"]["raw"].get("cancer_antecedente"), "si")


class TestConsentAndValidation(_Base):
    def test_consent_rejected_aborts_without_capturing(self):
        of.start_or_advance(self.beta, "hola")
        out = of.start_or_advance(self.beta, "no")  # rechaza consent_educativo
        self.assertEqual(out["status"], "aborted")
        state = load_state(self.beta)
        self.assertEqual(state["onboarding"]["status"], "aborted")
        # no se capturó nada de salud
        self.assertNotIn("nombre", state["onboarding"]["raw"])
        self.assertIsNone(state.get("phase"))

    def test_invalid_int_reasks(self):
        of.start_or_advance(self.beta, "hola")
        of.start_or_advance(self.beta, "sí")
        of.start_or_advance(self.beta, "sí")
        of.start_or_advance(self.beta, "Ana")        # nombre
        out = of.start_or_advance(self.beta, "cuarenta")  # edad inválida
        self.assertIn("número", out["reply"].lower())
        self.assertEqual(out["status"], "in_progress")
        self.assertEqual(out["step"], "edad")  # no avanzó

    def test_enum_accepts_keyword_and_number(self):
        of.start_or_advance(self.beta, "hola")
        self.feed(["sí", "sí", "Ana", "30", "Monterrey", "60", "165"])
        out = of.start_or_advance(self.beta, "longevidad")  # por palabra, no número
        self.assertEqual(out["status"], "in_progress")
        self.assertEqual(out["step"], "meta_8_semanas")  # avanzó


if __name__ == "__main__":
    unittest.main()
