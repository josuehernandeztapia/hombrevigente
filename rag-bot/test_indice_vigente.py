"""
Tests del Vigente Longevidad (contrato: docs/Metodologia_Indice_Vigente.md).
Sin red ni deps externas — lógica pura.

Run: python -m pytest rag-bot/test_indice_vigente.py -q
"""
import unittest

from indice_vigente import (
    BANDAS,
    DISCLAIMER,
    compute_indice_longevidad,
    headline_text,
)


class TestNormalizacion(unittest.TestCase):
    def test_optimo_da_100(self):
        r = compute_indice_longevidad(labs={"glucosa_ayuno": 85, "apob": 70})
        self.assertEqual(r["subscores"]["metabolico"], 100.0)

    def test_suboptimo_entre_50_y_90(self):
        r = compute_indice_longevidad(labs={"glucosa_ayuno": 95})  # 90–99 sub-óptima
        s = r["subscores"]["metabolico"]
        self.assertTrue(50 <= s < 100, f"esperaba sub-óptima, got {s}")

    def test_banda_central_sueno(self):
        # 8h dentro de 7–9 → óptimo
        r = compute_indice_longevidad(wearable={"sueno_horas": 8})
        self.assertEqual(r["subscores"]["recuperacion"], 100.0)


class TestDobleUmbral(unittest.TestCase):
    def test_valor_clinico_no_puntua_y_deriva(self):
        # glucosa 130 ≥126 (DM) → NO puntúa, emite derivación Ruta B
        r = compute_indice_longevidad(labs={"glucosa_ayuno": 130})
        self.assertEqual(len(r["derivaciones"]), 1)
        d = r["derivaciones"][0]
        self.assertEqual(d["marcador"], "glucosa_ayuno")
        self.assertEqual(d["ruta"], "B")
        self.assertIn("médica", d["mensaje"])
        # el índice nunca afirma enfermedad: solo bandera, no "diagnóstico"
        self.assertNotIn("diabet", str(r).lower())

    def test_sueno_bajo_deriva(self):
        # <6h crónico → bandera (banda central, lado bajo)
        r = compute_indice_longevidad(wearable={"sueno_horas": 5})
        self.assertTrue(any(x["marcador"] == "sueno_horas" for x in r["derivaciones"]))

    def test_marcador_clinico_se_excluye_del_score(self):
        # glucosa óptima + apob clínico → metabólico puntúa solo con glucosa, apob deriva
        r = compute_indice_longevidad(labs={"glucosa_ayuno": 85, "apob": 130})
        self.assertEqual(r["subscores"]["metabolico"], 100.0)  # solo glucosa
        self.assertTrue(any(d["marcador"] == "apob" for d in r["derivaciones"]))


class TestDegradacion(unittest.TestCase):
    def test_renormaliza_con_subconjunto(self):
        # solo metabólico presente → score == subscore metabólico (peso re-normalizado a 1)
        r = compute_indice_longevidad(labs={"glucosa_ayuno": 85})
        self.assertEqual(r["score"], r["subscores"]["metabolico"])
        self.assertFalse(r["preliminar"])
        self.assertEqual(r["completitud"]["senales_duras"], 1)

    def test_solo_comportamiento_es_preliminar_sin_numero(self):
        # §7 regla dura: autorreporte solo → preliminar, score None
        r = compute_indice_longevidad(cuestionario={"sueno": 80, "ejercicio": 70})
        self.assertTrue(r["preliminar"])
        self.assertIsNone(r["score"])
        self.assertIn("comportamiento", r["subscores"])

    def test_sin_datos_es_preliminar(self):
        r = compute_indice_longevidad()
        self.assertTrue(r["preliminar"])
        self.assertIsNone(r["score"])

    def test_completitud_reporta_faltantes(self):
        r = compute_indice_longevidad(labs={"glucosa_ayuno": 85})
        self.assertIn("recuperacion", r["completitud"]["faltan"])
        self.assertIn("comportamiento", r["completitud"]["faltan"])


class TestFramingAsCode(unittest.TestCase):
    def test_score_nunca_sale_desnudo(self):
        r = compute_indice_longevidad(labs={"glucosa_ayuno": 85})
        for k in ("etiqueta", "disclaimer", "es_diagnostico", "ilustrativo",
                  "metodologia_version", "completitud"):
            self.assertIn(k, r)
        self.assertFalse(r["es_diagnostico"])
        self.assertTrue(r["ilustrativo"])
        self.assertEqual(r["disclaimer"], DISCLAIMER)

    def test_headline_preliminar_no_da_numero(self):
        r = compute_indice_longevidad(cuestionario={"sueno": 80})
        txt = headline_text(r)
        # no expone un número de score, y reafirma el marco (no-diagnóstico) vía disclaimer
        self.assertIsNone(r["score"])
        self.assertIn("no es diagnóstico", txt.lower())
        self.assertIn("sube tus estudios", txt.lower())

    def test_headline_con_score_incluye_disclaimer(self):
        r = compute_indice_longevidad(labs={"glucosa_ayuno": 85, "apob": 70})
        txt = headline_text(r)
        self.assertIn(str(r["score"]), txt)
        self.assertIn("no es diagnóstico", txt.lower())

    def test_headline_menciona_derivacion(self):
        r = compute_indice_longevidad(labs={"glucosa_ayuno": 85, "hs_crp": 5.0})
        txt = headline_text(r)
        self.assertIn("médico", txt.lower())


class TestBandasIntegridad(unittest.TestCase):
    def test_todas_las_bandas_tienen_pmid(self):
        for nombre, b in BANDAS.items():
            self.assertTrue(b.pmid and b.pmid.isdigit(), f"{nombre} sin PMID válido")
            self.assertTrue(b.fuente, f"{nombre} sin fuente")


if __name__ == "__main__":
    unittest.main()
