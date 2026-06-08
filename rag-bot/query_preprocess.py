"""
Preprocesamiento de queries antes de embed — CMU PR #444 stripCommandWords.
"""

from __future__ import annotations

import re

# Patrones globales (reemplazan en cualquier posición, no solo prefijo)
STRIP_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bmu[eé]strame\b", re.I),
    re.compile(r"\bens[eé]ñame\b", re.I),
    re.compile(r"\bd[eé]jame\s+ver\b", re.I),
    re.compile(r"\bimagen\s+de\b", re.I),
    re.compile(r"\bfoto\s+de\b", re.I),
    re.compile(r"\bfotograf[ií]a\s+de\b", re.I),
    re.compile(r"\bla\s+imagen\s+(?:de\s+)?", re.I),
    re.compile(r"\bla\s+foto\s+(?:de\s+)?", re.I),
    re.compile(r"\bcu[aá]nto\s+vale\b", re.I),
    re.compile(r"\bcu[aá]nto\s+cuesta\b", re.I),
    re.compile(r"\bcu[aá]l\s+es\s+el\s+precio\s+de\b", re.I),
    re.compile(r"\bel\s+precio\s+de\b", re.I),
    re.compile(r"\bcosto\s+de\b", re.I),
    re.compile(r"\bprecio\s+de\b", re.I),
    re.compile(r"\bprecio\s+del\b", re.I),
    re.compile(r"\bqu[eé]\s+(?:es|son|significa)\b", re.I),
    re.compile(r"\bexpl[ií]came\b", re.I),
    re.compile(r"\bcu[eé]ntame\b", re.I),
    re.compile(r"\bquiero\s+saber\b", re.I),
    re.compile(r"\bme\s+puedes\b", re.I),
    re.compile(r"\bpodr[ií]as\b", re.I),
    re.compile(r"\bpor\s+favor\b", re.I),
    re.compile(r"\bgracias\b", re.I),
]

WHITESPACE = re.compile(r"\s+")


def strip_command_words(query: str) -> str:
    """Normaliza query para embedding: quita comandos conversacionales."""
    clean = query.strip()
    for pattern in STRIP_PATTERNS:
        clean = pattern.sub(" ", clean)
    clean = WHITESPACE.sub(" ", clean).strip()
    return clean or query.strip()