#!/usr/bin/env python3
"""
Coherencia de topics del Pulso: watchlist.yml ↔ harvest ↔ draft_compose ↔ bridge_export.

Por qué existe: un topic vive en CUATRO lugares (la lista de activos en
watchlist.yml, la query en harvest.TOPIC_QUERIES y el mapeo a monografía en
draft_compose.TOPIC_MONOGRAPHY y bridge_export.TOPIC_MONOGRAPHY). El 03-sep-2026
se añadió `bioreguladores_peptidicos` solo a dos de ellos y el harvest del jueves
lo filtró en silencio: el watchlist no lo listaba. Este test hace que el drift
sea un fallo de CI, no un descubrimiento a la semana siguiente.

Sin dependencias (CI no tiene pyyaml): el watchlist se lee con regex y los dicts
de Python con `ast`, sin importar los módulos.

Run: python -m pytest rag-bot/test_newsletter_topics.py -q
"""
import ast
import re
import unittest
from pathlib import Path

NEWSLETTER = Path(__file__).resolve().parent.parent / "newsletter"
KB_LONGEVITY = Path(__file__).resolve().parent / "knowledge_base" / "longevity"


def _dict_literal(path: Path, name: str) -> dict:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == name for t in targets) and node.value is not None:
                return ast.literal_eval(node.value)
    raise AssertionError(f"{name} no encontrado en {path.name}")


def _watchlist_enabled() -> set:
    """Lee las listas planas `temas_ssot` y `beat_ai_longevity` línea a línea.

    Una clave sin sangría cierra la sección; así un `- item` de otra lista
    (journals, voces…) nunca se cuela.
    """
    enabled, section, vistas = set(), None, set()
    for raw in (NEWSLETTER / "watchlist.yml").read_text(encoding="utf-8").splitlines():
        line = re.sub(r"#.*", "", raw).rstrip()
        if not line.strip():
            continue
        if not line[0].isspace():                      # clave de nivel superior
            section = line.split(":")[0].strip()
            vistas.add(section)
            continue
        if section in ("temas_ssot", "beat_ai_longevity"):
            item = line.strip()
            if item.startswith("- "):
                enabled.add(item[2:].strip())
    assert {"temas_ssot", "beat_ai_longevity"} <= vistas, "secciones de topics no encontradas en watchlist.yml"
    return enabled


class TestTopicsCoherentes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enabled = _watchlist_enabled()
        cls.queries = _dict_literal(NEWSLETTER / "harvest.py", "TOPIC_QUERIES")
        cls.mono_compose = _dict_literal(NEWSLETTER / "draft_compose.py", "TOPIC_MONOGRAPHY")
        cls.mono_bridge = _dict_literal(NEWSLETTER / "bridge_export.py", "TOPIC_MONOGRAPHY")

    def test_todo_topic_activo_tiene_query(self):
        faltan = self.enabled - set(self.queries)
        self.assertFalse(faltan, f"en watchlist pero sin query en harvest: {sorted(faltan)}")

    def test_toda_query_esta_activa_en_watchlist(self):
        # Una query que el watchlist no lista NUNCA corre — así se perdió Khavinson.
        faltan = set(self.queries) - self.enabled
        self.assertFalse(faltan, f"query definida pero filtrada por watchlist.yml: {sorted(faltan)}")

    def test_todo_topic_tiene_monografia_en_ambos_mapas(self):
        for nombre, mapa in (("draft_compose", self.mono_compose), ("bridge_export", self.mono_bridge)):
            faltan = set(self.queries) - set(mapa)
            self.assertFalse(faltan, f"sin monografía destino en {nombre}: {sorted(faltan)}")

    def test_los_dos_mapas_coinciden(self):
        comunes = set(self.mono_compose) & set(self.mono_bridge)
        distintos = {t for t in comunes if self.mono_compose[t] != self.mono_bridge[t]}
        self.assertFalse(distintos, f"draft_compose y bridge_export mandan a monografías distintas: {sorted(distintos)}")

    def test_las_monografias_destino_existen(self):
        for mapa in (self.mono_compose, self.mono_bridge):
            for topic, fname in mapa.items():
                self.assertTrue((KB_LONGEVITY / fname).exists(), f"{topic} → {fname} no existe en el corpus")

    def test_linea_khavinson_cerrada(self):
        t = "bioreguladores_peptidicos"
        self.assertIn(t, self.enabled)
        self.assertIn("epitalon", self.queries[t].lower())
        self.assertEqual(self.mono_compose[t], "20_khavinson_marco_biorreguladores.md")


if __name__ == "__main__":
    unittest.main()
