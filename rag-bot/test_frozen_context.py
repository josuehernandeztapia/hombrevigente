#!/usr/bin/env python3
"""Tests frozen context + gates con perfil intake."""

import json
import tempfile
import unittest
from pathlib import Path

from frozen_context import build_frozen_context, gate_probe_text, resolve_intake
from rag_retrieval_local import check_gates

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "caso0_intake_p1_entrega.json"


class TestFrozenContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intake = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_build_contains_bandera(self):
        block = build_frozen_context(self.intake)
        self.assertIn("BANDERA screening", block)
        self.assertIn("litio", block.lower())

    def test_resolve_by_beta_id(self):
        intake, bid = resolve_intake(beta_id="row-0")
        self.assertIsNotNone(intake)
        self.assertEqual(bid, "row-0")

    def test_gate_nmn_sin_litio_en_pregunta(self):
        """S5: la pregunta no dice litio; el perfil sí."""
        frozen = build_frozen_context(self.intake)
        probe = gate_probe_text("¿puedo empezar NMN esta semana?", frozen)
        g = check_gates(probe, "longevity")
        self.assertFalse(g.triggered)

    def test_gate_ayuno_con_perfil_litio(self):
        frozen = build_frozen_context(self.intake)
        probe = gate_probe_text("¿puedo hacer ayuno 16:8?", frozen)
        g = check_gates(probe, "longevity")
        self.assertTrue(g.triggered)
        self.assertEqual(g.code, "gate_psiquiatria")

    def test_rag_local_beta_id_no_llm(self):
        import os

        from rag_retrieval_local import rag_query_local

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HV_BETA_STATES_DIR"] = tmp
            result = rag_query_local(
                "¿puedo hacer ayuno 16:8?",
                beta_id="row-0",
                use_llm=False,
                log=False,
                channel="whatsapp",
            )
            self.assertEqual(result.get("gate_path"), "blocked")
            self.assertEqual(result.get("beta_id"), "row-0")
            self.assertIn("frozen_context", result)
            self.assertEqual(result.get("turn_number"), 1)


if __name__ == "__main__":
    unittest.main()