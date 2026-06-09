"""
ReentryHandler — Fase 4 (Capa 3 de la Guía Agéntica Estándar).

Implementación directa del patrón recomendado:

function computeResumeMessage(state, hoursAway) {
  if (hoursAway < 24) return null;
  if (hoursAway < 72)  return { band: "24h-72h", text: `Retomamos. Estás en ${phase}. Falta ${missing.join(", ")}.` };
  if (hoursAway < 168) return { band: "3d-7d",   text: `Tu trámite está en ${phase} con ${pct}% de avance. ¿Continuamos?` };
  return                       { band: "7d+",    text: `Tu trámite quedó pausado en ${phase}. Si quieres retomarlo, dime.` };
}

Se usa last_active_at (garantizado dentro del state_data desde Fase 1/2).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _parse_last_active(state: Dict[str, Any]) -> Optional[datetime]:
    ts = state.get("last_active_at")
    if not ts:
        return None
    try:
        # Soporta ISO con o sin Z
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def compute_hours_away(state: Dict[str, Any]) -> Optional[float]:
    """Devuelve horas desde last_active_at (None si no hay dato)."""
    last = _parse_last_active(state)
    if not last:
        return None
    now = datetime.now(timezone.utc)
    delta = now - last
    return delta.total_seconds() / 3600.0


def _calculate_progress(state: Dict[str, Any]) -> Optional[int]:
    """Porcentaje muy simple basado en slots completados (para la banda 3d-7d)."""
    slots = state.get("slots", {}) or {}
    if not slots:
        return None
    completed = sum(1 for v in slots.values() if v)
    total = len(slots)
    if total == 0:
        return None
    return int((completed / total) * 100)


def _get_missing_slots(state: Dict[str, Any]) -> list[str]:
    """Devuelve lista de slots pendientes (para la banda 24h-72h)."""
    slots = state.get("slots", {}) or {}
    # Mapeo amigable (puede refinarse)
    friendly = {
        "tally_completo": "completar Tally",
        "clearance_medica": "clearance médico",
        "protocolo_entregado": "entregar protocolo",
        "foto_baseline": "subir foto baseline",
        "labs_parseados": "subir/parsear labs",
        "baseline_subjetivo": "completar subjetivo día 0",
        "checkin_semana_actual": "check-in de la semana",
    }
    missing = []
    for key, val in slots.items():
        if not val:
            missing.append(friendly.get(key, key))
    return missing


def compute_resume_message(state: Dict[str, Any], hours_away: Optional[float] = None) -> Optional[Dict[str, Any]]:
    """
    Devuelve un mensaje de reingreso según las bandas exactas de la Guía.
    Si hours_away es None, lo calcula desde last_active_at.
    """
    if hours_away is None:
        hours_away = compute_hours_away(state)

    if hours_away is None or hours_away < 24:
        return None

    phase = state.get("phase", "onboarding")
    missing = _get_missing_slots(state)
    pct = _calculate_progress(state)

    if hours_away < 72:
        text = f"Retomamos. Estás en {phase}."
        if missing:
            text += f" Falta {', '.join(missing)}."
        return {"band": "24h-72h", "text": text}

    if hours_away < 168:
        text = f"Tu trámite está en {phase}"
        if pct is not None:
            text += f" con {pct}% de avance"
        text += ". ¿Continuamos?"
        return {"band": "3d-7d", "text": text}

    # 7d+
    text = f"Tu trámite quedó pausado en {phase}."
    if missing:
        text += f" Falta {', '.join(missing)}."
    text += " Si quieres retomarlo, dime."
    return {"band": "7d+", "text": text}


def get_resume_context(state: Dict[str, Any]) -> Optional[str]:
    """Devuelve solo el texto del mensaje de resume (útil para frozen_context o respuesta)."""
    msg = compute_resume_message(state)
    return msg["text"] if msg else None
