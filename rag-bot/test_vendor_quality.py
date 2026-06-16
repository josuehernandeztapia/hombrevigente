"""Tests del criterio de selección de proveedor (Av.2). Sin red — pura lógica."""
import unittest
from datetime import datetime, timezone, timedelta

from vendor_quality import Vendor, evaluate, _criba


def _ago(days):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


class TestCriba(unittest.TestCase):
    def test_finnrick_ok_es_fuerte(self):
        c = _criba(Vendor("X", en_finnrick=True, finnrick_ok=True))
        self.assertTrue(c["pass"]); self.assertEqual(c["fuerza"], "fuerte")

    def test_finnrick_fallido_descarta(self):
        c = _criba(Vendor("X", en_finnrick=True, finnrick_ok=False))
        self.assertFalse(c["pass"]); self.assertEqual(c["fuerza"], "negativa")

    def test_janoshik_solo_es_debil_no_suficiente(self):
        c = _criba(Vendor("X", en_janoshik=True))
        self.assertTrue(c["pass"]); self.assertEqual(c["fuerza"], "debil")

    def test_sin_testeo_independiente_falla(self):
        c = _criba(Vendor("Exoma"))
        self.assertFalse(c["pass"]); self.assertEqual(c["fuerza"], "nula")


class TestGate(unittest.TestCase):
    def _full(self, **kw):
        base = dict(
            name="V", inyectable=True, en_finnrick=True, finnrick_ok=True,
            coa_por_lote=True, endotoxinas=True, esterilidad=True,
            ultimo_lote_testeado={"lab": "MZ Biolabs", "fecha": _ago(30), "lote": "L1", "resultado": "pass"},
        )
        base.update(kw)
        return evaluate(Vendor(**base))

    def test_proveedor_completo_pasa_gate(self):
        self.assertTrue(self._full()["gate_av2"])

    def test_buen_ranking_sin_lote_testeado_NO_pasa(self):
        # El núcleo del criterio: ranking ≠ confianza. Sin test de lote, no hay gate.
        r = self._full(ultimo_lote_testeado=None)
        self.assertFalse(r["gate_av2"])
        self.assertTrue(any("verificación" in f for f in r["faltantes"]))

    def test_inyectable_sin_endotoxinas_NO_pasa(self):
        r = self._full(endotoxinas=False)
        self.assertFalse(r["gate_av2"])
        self.assertTrue(any("endotoxinas" in f for f in r["faltantes"]))

    def test_lote_viejo_no_pasa(self):
        r = self._full(ultimo_lote_testeado={"lab": "Janoshik", "fecha": _ago(400), "lote": "L9", "resultado": "pass"})
        self.assertFalse(r["gate_av2"])

    def test_lote_fallido_no_pasa(self):
        r = self._full(ultimo_lote_testeado={"lab": "ACS", "fecha": _ago(10), "lote": "L2", "resultado": "fail"})
        self.assertFalse(r["gate_av2"])

    def test_janoshik_como_lab_de_verificacion_es_valido(self):
        # Janoshik vale como DESTINO de muestra (paso 3), aunque sea débil como fuente.
        r = self._full(en_finnrick=False, finnrick_ok=None, en_janoshik=True,
                       ultimo_lote_testeado={"lab": "Janoshik", "fecha": _ago(5), "lote": "L3", "resultado": "pass"})
        # criba débil pero los 3 pasos en verde → gate abre (con nota de criba débil)
        self.assertTrue(r["verificacion"]["pass"])

    def test_no_inyectable_no_exige_endotoxinas(self):
        r = self._full(inyectable=False, endotoxinas=None, esterilidad=None)
        self.assertTrue(r["gate_av2"])


class TestRegistry(unittest.TestCase):
    def test_exoma_seed_falla_criba(self):
        import os, json, tempfile
        from vendor_quality import evaluate_registry
        # usa el registro real del repo (Exoma seed)
        from vendor_quality import load_registry
        vendors = {v.name: v for v in load_registry()}
        if "Exoma" in vendors:
            r = evaluate(vendors["Exoma"])
            self.assertFalse(r["gate_av2"])
            self.assertFalse(r["criba"]["pass"])


if __name__ == "__main__":
    unittest.main()
