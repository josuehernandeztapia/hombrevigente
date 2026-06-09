#!/usr/bin/env python3
"""Tests beta_state + decision_log beta context."""

import json
import tempfile
import unittest
from pathlib import Path

from beta_state import (
    beta_id_from_intake,
    compute_next_action,
    derive_state_from_intake,
    load_state,
    save_state,
    sync_from_intake,
    transition,
)
from decision_log import RagDecisionEntry, log_rag_decision, read_decisions


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "caso0_intake_p1_entrega.json"


class TestBetaState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intake = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_beta_id_caso0(self):
        self.assertEqual(beta_id_from_intake(self.intake), "row-0")

    def test_marcado_next_action_screening(self):
        intake = dict(self.intake)
        intake["pipeline"] = {"estado": "screening", "revisado_medico": False}
        state = derive_state_from_intake(intake)
        self.assertEqual(state.perfil, "marcado")
        self.assertIn("Clearance", state.next_action)

    def test_verde_onboarding(self):
        intake = {
            "meta": {"source": "tally", "pipeline_row": 2},
            "identity": {"nombre": "Beta Test", "edad": 40, "whatsapp": "+521234567890", "ciudad": "QRO"},
            "objetivos": {"principal": "energia", "meta_8_semanas": "más energía"},
            "screening": {
                "cancer_antecedente": "no",
                "psiquiatria_tratamiento": "no",
                "cardio_renal_hepatica": "no",
                "bandera_activa": False,
            },
            "consentimiento": {"educativo_no_rx": True, "uso_datos_protocolo": True},
            "pipeline": {"estado": "onboarding"},
        }
        state = derive_state_from_intake(intake)
        self.assertEqual(state.perfil, "verde")
        self.assertEqual(state.next_action, "Ejecutar screening + asignar stack")

    def test_persist_and_transition(self):
        with tempfile.TemporaryDirectory() as tmp:
            import os

            os.environ["HV_BETA_STATES_DIR"] = tmp
            state = sync_from_intake(self.intake, persist=True)
            self.assertTrue((Path(tmp) / "row-0.json").exists())
            transition(state, "protocolo-entregado", note="test")
            save_state(state)
            loaded = load_state("row-0")
            self.assertEqual(loaded.phase, "protocolo-entregado")
            self.assertGreaterEqual(len(loaded.history), 1)

    def test_slot_overrides(self):
        state = derive_state_from_intake(
            self.intake,
            slot_overrides={"clearance_medica": True, "foto_baseline": True},
        )
        self.assertTrue(state.slots["clearance_medica"])
        self.assertTrue(state.slots["foto_baseline"])


class TestDecisionLogBetaContext(unittest.TestCase):
    def test_beta_fields_in_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "log.jsonl"
            log_rag_decision(
                RagDecisionEntry(
                    query="NMN con litio",
                    query_normalized="nmn litio",
                    kb_route="longevity",
                    gate_path="caveat",
                    beta_id="row-0",
                    turn_number=3,
                    channel="whatsapp",
                ),
                path=path,
            )
            row = read_decisions(days=7, path=path)[0]
            self.assertEqual(row["beta_id"], "row-0")
            self.assertEqual(row["turn_number"], 3)
            self.assertEqual(row["channel"], "whatsapp")


class TestProactiveGolden(unittest.TestCase):
    def test_generate_action_for_signal_deterministic(self):
        """Basic golden regression for action generation (protects Capa 5/6 logic).
        Uses data/proactive-golden.json (like RAG golden). low_progress may include optional RAG enrichment (Capa 4).
        """
        import json
        from pathlib import Path
        from signal_detector import BetaSignal
        from action_handler import generate_action_for_signal
        golden_path = Path(__file__).resolve().parent / "data" / "proactive-golden.json"
        golden = json.loads(golden_path.read_text(encoding="utf-8"))
        samples = [
            BetaSignal(beta_id="g-1", signal_type="no_activity_72h", severity="medium", context={}),
            BetaSignal(beta_id="g-2", signal_type="stalled_onboarding", severity="high", context={}),
            BetaSignal(beta_id="g-3", signal_type="low_progress", severity="low", context={}),
            BetaSignal(beta_id="g-4", signal_type="missing_labs", severity="medium", context={}),
        ]
        for i, sig in enumerate(samples):
            action = generate_action_for_signal(sig)
            g = golden[i]
            self.assertEqual(action.get("action_type"), g["action_type"])
            self.assertTrue(action.get("suggested_message", "").startswith(g["suggested_message_starts_with"]))
            self.assertEqual(bool(action.get("resume_context")), g["has_resume_context"])


if __name__ == "__main__":
    unittest.main()