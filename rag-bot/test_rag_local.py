#!/usr/bin/env python3
"""Tests del RAG local (gates + routing + confianza + prompts). Sin API key."""

import subprocess
import sys
import unittest
from pathlib import Path

from confidence_gate import decide_rag_path, score_to_confidence
from rag_retrieval_local import check_gates
from kb_pipeline import COSINE_HIGH, COSINE_MIN
from prompts import build_system_prompt
from query_preprocess import strip_command_words
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

    def test_litio_ayuno_gate(self):
        g = check_gates("tomo litio 0.42 y quiero ayuno intermitente 16:8", "longevity")
        self.assertTrue(g.triggered)
        self.assertEqual(g.code, "gate_psiquiatria")

    def test_vitamina_d_sin_gate(self):
        g = check_gates("mi vitamina D está baja, ¿qué dice la evidencia?", "longevity")
        self.assertFalse(g.triggered)

    def test_onco_fisetina_gate(self):
        g = check_gates(
            "tengo antecedente oncológico, ¿puedo empezar fisetina y quercetina?",
            "longevity",
        )
        self.assertTrue(g.triggered)
        self.assertEqual(g.code, "gate_oncologia")


class TestRouting(unittest.TestCase):
    def test_longevity_route(self):
        self.assertEqual(detect_kb_route("homocisteína alta y TMG"), "longevity")

    def test_caso0_litio_route(self):
        self.assertEqual(
            detect_kb_route("mi litio en sangre está en 0.42 mmol/L"),
            "longevity",
        )

    def test_caso0_ciatica_route(self):
        self.assertEqual(
            detect_kb_route("discopatía Pfirrmann grado IV L4-L5 y ciática"),
            "longevity",
        )

    def test_servicios_route(self):
        self.assertEqual(detect_kb_route("cuánto cuesta el HIFU"), "servicios")


class TestQueryPreprocess(unittest.TestCase):
    def test_strip_command_words(self):
        self.assertEqual(
            strip_command_words("muéstrame imagen de HIFU"),
            "HIFU",
        )
        self.assertEqual(
            strip_command_words("cuánto cuesta botox"),
            "botox",
        )
        self.assertEqual(
            strip_command_words("cuál es el precio de botox"),
            "botox",
        )

    def test_empty_after_strip_falls_back(self):
        self.assertEqual(strip_command_words("hola"), "hola")


class TestConfidenceGate(unittest.TestCase):
    def test_high_auto(self):
        v = decide_rag_path(COSINE_HIGH)
        self.assertEqual(v.path, "auto")

    def test_medium_caveat(self):
        v = decide_rag_path((COSINE_HIGH + COSINE_MIN) / 2)
        self.assertEqual(v.path, "caveat")

    def test_low_escalate(self):
        v = decide_rag_path(COSINE_MIN - 0.01)
        self.assertEqual(v.path, "escalate")

    def test_score_labels(self):
        self.assertEqual(score_to_confidence(0.75), "high")
        self.assertEqual(score_to_confidence(0.60), "medium")
        self.assertEqual(score_to_confidence(0.40), "low")


class TestPrompts(unittest.TestCase):
    def test_longevity_has_disclosure(self):
        p = build_system_prompt("longevity", confidence="medium")
        self.assertIn("DISCLOSURE", p.upper())
        self.assertIn("E1", p)
        self.assertIn("CONFIANZA", p.upper())

    def test_servicios_has_precios_rule(self):
        p = build_system_prompt("servicios")
        self.assertIn("MXN", p)

    def test_concierge_role(self):
        p = build_system_prompt("longevity", role="concierge")
        self.assertIn("CONCIERGE", p.upper())
        self.assertIn("3 líneas", p.lower())


class TestGoldenSetGates(unittest.TestCase):
    def test_golden_runner_gates_only(self):
        root = Path(__file__).resolve().parent
        proc = subprocess.run(
            [sys.executable, "golden_runner.py", "--gates-only"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()

class TestGateAvenida2LineaRusa(unittest.TestCase):
    """La línea Khavinson (péptidos rusos órgano-específicos) es Av.2.

    Hueco encontrado ago-2026: el gate cubría BPC-157/TB-500/tesamorelin pero
    NO epitalón, thymalin, semax, cortexin ni "bioreguladores" — justo la línea
    que el producto quiere impulsar, y la que más necesita derivar a médico.
    "khavinson" solo existía en PSYCH_COMPOUND, que exige contexto psiquiátrico.
    """

    RUSOS = ["quiero probar epitalón", "¿cómo funciona el epitalon?",
             "me interesan los péptidos de Khavinson", "¿el thymalin sirve?",
             "¿puedo usar semax o selank?", "¿qué dosis de cortexin?",
             "bioreguladores rusos", "endoluten", "cerluten"]
    OTROS_RX = ["¿me pongo ipamorelin?", "cjc-1295", "¿semaglutida para bajar de peso?"]
    EDUCATIVO = ["¿qué es la reprogramación Yamanaka?",
                 "¿cómo funcionan los relojes epigenéticos?",
                 "¿la espermidina activa autofagia?", "¿me conviene creatina?"]

    def test_linea_rusa_dispara_avenida_2(self):
        for q in self.RUSOS + self.OTROS_RX:
            g = check_gates(q, "longevity")
            self.assertTrue(g.triggered, f"debe derivar a médico: {q!r}")
            self.assertEqual(g.code, "avenida_2_peptido", q)

    def test_ciencia_sin_insumo_no_gatea(self):
        for q in self.EDUCATIVO:
            self.assertFalse(check_gates(q, "longevity").triggered,
                             f"pregunta educativa no debe gatear: {q!r}")
