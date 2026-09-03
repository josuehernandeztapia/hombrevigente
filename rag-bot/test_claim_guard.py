#!/usr/bin/env python3
"""Claim-guard de publicación — candado de compliance COFEPRIS.

Por qué existe este archivo: hasta ago-2026 el patrón cerraba el grupo con `\\b`,
así que `diagn[oó]stic\\b` NUNCA matcheaba "diagnóstico" (tras "stic" viene "o",
carácter de palabra). El término más sensible — y el que motiva el guard — pasaba
libre; solo se bloqueaba la forma inglesa "diagnostic". Igual con "tratamientos",
"curación", "prevención", "sanación" y "100 % efectivo".

La regla en español: el claim vive en la raíz, no en la forma exacta. Un falso
positivo cuesta una revisión humana; un falso negativo publica un claim clínico.

Run: python -m pytest rag-bot/test_claim_guard.py -q
"""
import importlib.util
import unittest
from pathlib import Path

_PUBLISH = Path(__file__).resolve().parent.parent / "newsletter" / "publish.py"


def _risky():
    """Carga RISKY sin importar el módulo completo (evita deps de red)."""
    spec = importlib.util.spec_from_file_location("_pub_guard", _PUBLISH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.RISKY


class TestClaimGuardBloquea(unittest.TestCase):
    """Lo que NUNCA debe autopublicarse sin ojo humano."""

    CLAIMS = [
        # El agujero histórico: todas las formas españolas de diagnóstico.
        "un diagnóstico preciso", "diagnóstica tu edad biológica",
        "diagnosticar el envejecimiento", "diagnósticos personalizados",
        # Curación / tratamiento
        "esto cura el cáncer", "curación garantizada", "efecto curativo",
        "tratamiento para la diabetes", "tratamientos disponibles",
        # Prevención
        "previene la enfermedad", "prevención del alzheimer", "efecto preventivo",
        # Reversión / garantías / absolutos
        "revierte el daño celular", "reversión del envejecimiento",
        "resultados garantizados", "te garantizamos resultados",
        "curamos el insomnio", "tratamos la fatiga", "prevenimos el deterioro",
        "100% efectivo", "100 % efectivo",
        "sanación natural", "producto milagroso", "es un milagro",
    ]

    def test_todos_los_claims_se_bloquean(self):
        risky = _risky()
        fugas = [c for c in self.CLAIMS if not risky.search(c)]
        self.assertEqual(fugas, [], f"claims que se publicarían solos: {fugas}")


class TestClaimGuardNoEstorba(unittest.TestCase):
    """Lo que SÍ debe poder autopublicarse: el lenguaje editorial de HV."""

    LEGITIMOS = [
        "información educativa de optimización",
        "se asocia con un mejor perfil lipídico",
        "en investigación preclínica, no disponible como intervención",
        "consulta con tu médico antes de cambiar tu protocolo",
        "no sustituye consulta ni diagnóstico médico"[:32],  # sin la palabra
        "curaduría de contenido científico",
        # Caso real del landing: aquí "curado" = seleccionado, no curación.
        "nuestro arsenal de servicios está curado bajo una sola premisa",
        "valoración objetiva con el Índice Vigente",
        "mide tu ApoB, no solo tu LDL-C",
        "entrenamiento de resistencia y zona 2",
    ]

    def test_no_hay_falsos_positivos(self):
        risky = _risky()
        marcados = [(t, risky.search(t).group(0)) for t in self.LEGITIMOS
                    if risky.search(t)]
        self.assertEqual(marcados, [], f"falsos positivos (frenan publicación válida): {marcados}")


if __name__ == "__main__":
    unittest.main()
