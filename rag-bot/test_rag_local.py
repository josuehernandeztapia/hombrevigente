#!/usr/bin/env python3
"""Tests del RAG local (gates + routing). No requiere embeddings si solo corre test_gates."""

import unittest

from rag_retrieval_local import (
    check_gates,
    detect_kb_route,
    GateResult,
)


class TestGates(unittest.TestCase):
    def test_peptido_inyectable_bloqueado(self):
        g = check_gates("quiero protocolo BPC-157 inyectable para ciática", "longevity")
        self.assertTrue(g.triggered)
        self.assertEqual(g.code, "avenida_2_peptido")

    def test_litio_cerluten_gate(self):
        g = check_gates("tomo litio y quetiapina, ¿puedo usar Cerluten?", "longevity")
        self.assertTrue(g.triggered)
        self.assertEqual(g.code, "gate_psiquiatria")

    def test_vitamina_d_sin_gate(self):
        g = check_gates("mi vitamina D está baja, ¿qué dice la evidencia?", "longevity")
        self.assertFalse(g.triggered)


class TestRouting(unittest.TestCase):
    def test_longevity_route(self):
        self.assertEqual(detect_kb_route("homocisteína alta y TMG"), "longevity")

    def test_servicios_route(self):
        self.assertEqual(detect_kb_route("cuánto cuesta el HIFU"), "servicios")


if __name__ == "__main__":
    unittest.main()