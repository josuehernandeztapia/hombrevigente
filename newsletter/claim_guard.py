"""
claim_guard.py — regla de compliance COFEPRIS, sin dependencias.

Vive aparte de publish.py a propósito: es la barrera que decide si un texto
puede autopublicarse, y no debe arrastrar yaml/requests para poder evaluarse.
Así se puede correr contra cualquier superficie (newsletter, redes, el landing,
el corpus) y testear en cualquier entorno.

Regla: en español el claim vive en la RAÍZ, no en la forma exacta. El bug que
motivó extraer esto (ago-2026): el patrón cerraba con \\b, así que
`diagn[oó]stic\\b` nunca matcheaba "diagnóstico" — tras "stic" viene "o".
El término más sensible pasaba libre hacia autopublicación.

Criterio de diseño: preferir el falso positivo (va a revisión humana) sobre el
falso negativo (se publica un claim clínico). Pero sin frenar copy legítimo —
por eso los verbos con uso no-clínico quedan enumerados en vez de abiertos.
"""
from __future__ import annotations

import re
from typing import List

RISKY = re.compile(
    r"\b(?:"
    # Verbos donde TODA conjugación es claim → raíz abierta.
    r"garantiz\w*|"                    # garantiza, garantizamos, garantizado…
    r"diagn[oó]stic\w*|diagnostic\w*|"  # diagnóstico/a/os, diagnosticamos…
    r"preven\w*|previen\w*|"           # prevenir/prevención/preventivo + previene
    r"revert\w*|reviert\w*|reversi[oó]n\w*|"
    r"milagro\w*|"
    # Enumerados: la raíz abierta daría falsos positivos ("curaduría", "sangre").
    # "curado/a" queda FUERA a propósito: en el copy de marca significa
    # seleccionado ("arsenal de servicios curado") — el anglicismo de *curated*.
    r"cura(?:r|n|s|mos|ci[oó]n|tiv[oa]s?)?|"
    r"trata(?:r|mos|mient[oa]s?)?|"
    r"sana(?:r|n|mos|ci[oó]n)?|"
    r"elimina la enfermedad|adelgaza garantizado"
    r")\b"
    # Símbolos aparte: tras "%" no hay límite de palabra, así que dentro del
    # grupo anterior "100 % efectivo" se fugaba.
    r"|100\s?%",
    re.IGNORECASE,
)


def find_claims(text: str) -> List[str]:
    """Todos los claims encontrados (para auditar una superficie completa)."""
    return [m.group(0) for m in RISKY.finditer(text or "")]


def first_claim(text: str) -> str | None:
    """El primer claim, o None si el texto pasa. Lo que usa el guard de publish."""
    m = RISKY.search(text or "")
    return m.group(0) if m else None
