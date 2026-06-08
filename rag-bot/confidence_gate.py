"""
Gating de confianza para respuestas RAG — adaptado de cmu-decision/server/confidence-gate.ts.

Tres caminos:
  - auto     → generar respuesta LLM
  - caveat   → generar con disclaimer de confianza parcial
  - escalate → no LLM; mensaje honesto "no encontré"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from kb_pipeline import COSINE_HIGH, COSINE_MIN

GatePath = Literal["auto", "caveat", "escalate"]


@dataclass
class GateVerdict:
    path: GatePath
    reason: str
    confidence: float
    label: str


def score_to_confidence(score: float) -> str:
    if score >= COSINE_HIGH:
        return "high"
    if score >= COSINE_MIN:
        return "medium"
    return "low"


def decide_rag_path(
    top_score: float,
    *,
    force_path: Optional[GatePath] = None,
) -> GateVerdict:
    if force_path:
        return GateVerdict(
            path=force_path,
            reason="forced by caller",
            confidence=top_score,
            label="",
        )

    if top_score >= COSINE_HIGH:
        return GateVerdict(
            path="auto",
            reason=f"score {top_score:.3f} ≥ COSINE_HIGH {COSINE_HIGH}",
            confidence=top_score,
            label="respuesta automática",
        )

    if top_score >= COSINE_MIN:
        return GateVerdict(
            path="caveat",
            reason=f"score {top_score:.3f} in [{COSINE_MIN}, {COSINE_HIGH})",
            confidence=top_score,
            label="respuesta con advertencia de confianza parcial",
        )

    return GateVerdict(
        path="escalate",
        reason=f"score {top_score:.3f} < COSINE_MIN {COSINE_MIN}",
        confidence=top_score,
        label="sin evidencia suficiente",
    )


NO_MATCH_MESSAGE = (
    "No encontré evidencia suficiente en el Knowledge Base para responder con confianza. "
    "¿Puedes reformular o ser más específico?"
)

CAVEAT_FOOTER = (
    "\n\n---\n"
    "_Con la evidencia disponible en nuestro KB, esta orientación es parcial. "
    "Para decisiones clínicas o de tratamiento, agenda valoración con el equipo HV._"
)