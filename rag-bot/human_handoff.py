"""
human_handoff.py — STOP humano: el beta pide una persona y el bot se calla.

Por qué existe: el fallback del webhook promete "si es urgente, escribe 'humano'"
desde el día 1, y hasta ago-2026 esa palabra no tenía rama — el beta seguía
hablando con el RAG. Un usuario en screening o en crisis debe poder salir del bot.

Contrato:
- El latch es PERSISTENTE (vive en el state, SSOT). Un STOP que dura un solo
  mensaje no es un STOP: al siguiente turno el bot volvería a responder como si
  nada. Mientras esté activo: sin RAG, sin onboarding, sin LLM, sin proactivos.
- Solo un humano lo levanta (`POST /admin/handoff/resolve`, PIN). El beta no
  puede desactivarlo sin querer escribiendo cualquier cosa.
- El texto que lo disparó se guarda REDACTADO (LFPDPPP): sirve para triage, no
  para almacenar lo que la persona escribió en crisis.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Fijo y corto (regla de copy: concierge ≤3 líneas). Incluye la salida real de
# emergencia: un bot no debe ser el último recurso de alguien que se siente mal.
HANDOFF_REPLY = (
    "Listo — dejo de responder automáticamente. Una persona del equipo "
    "Hombre Vigente te escribe por este mismo chat lo antes posible.\n"
    "Si es una emergencia médica, llama al 911 o acude a urgencias."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_active(state: Optional[Dict[str, Any]]) -> bool:
    """True si el beta está en handoff (pidió humano y nadie lo ha liberado)."""
    ho = (state or {}).get("human_handoff") or {}
    return bool(ho.get("requested_at")) and not ho.get("resolved_at")


def mark(beta_id: str, trigger_text: str = "") -> Dict[str, Any]:
    """Activa el latch. Idempotente: si ya está activo conserva el timestamp
    original (importa para medir cuánto lleva esperando)."""
    from state_persistence import load_state, save_state

    state = load_state(beta_id) or {"beta_id": beta_id}
    if is_active(state):
        return state["human_handoff"]

    try:
        from decision_log import redact_for_preview
        preview = redact_for_preview(trigger_text or "")
    except Exception:
        preview = ""

    ho = {"requested_at": _now(), "resolved_at": None, "trigger_preview": preview}
    state["human_handoff"] = ho
    state.setdefault("history", []).append(
        {"at": ho["requested_at"], "note": "human_handoff_requested"}
    )
    save_state(beta_id, state)
    print(f"[handoff] beta={beta_id} pidió humano — bot en silencio hasta resolución")
    return ho


def resolve(beta_id: str, by: str = "admin") -> Optional[Dict[str, Any]]:
    """Libera el latch; el bot vuelve a responder. Devuelve None si no había."""
    from state_persistence import load_state, save_state

    state = load_state(beta_id)
    if not is_active(state):
        return None
    ho = state["human_handoff"]
    ho["resolved_at"] = _now()
    ho["resolved_by"] = by
    state.setdefault("history", []).append(
        {"at": ho["resolved_at"], "note": f"human_handoff_resolved:{by}"}
    )
    save_state(beta_id, state)
    print(f"[handoff] beta={beta_id} liberado por {by}")
    return ho
