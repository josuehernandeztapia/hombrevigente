"""
onboarding_flow.py — Onboarding conversacional por WhatsApp (determinístico).

Reemplaza el intake por Tally: el beta completa el cuestionario MVP-0 conversando
en el mismo hilo de WhatsApp. El GUION es fijo (garantiza que se llenen todos los
slots requeridos y respeta el orden de compliance); el LLM solo se usaría para
reformular el tono (seam _phrase(), OFF por default vía HV_ONBOARDING_LLM_TONE).

Contrato (la metodología manda sobre el handler):
- Paso 0 = CONSENTIMIENTO (LFPDPPP) antes de cualquier dato de salud. Si el beta
  no acepta, el flujo se aborta sin capturar nada.
- Las preguntas de screening (cáncer / psiquiatría / cardio-renal-hepática) son los
  gates: una respuesta "sí" levanta bandera → el intake derivado entra en fase
  'screening' (deriva a médico), nunca protocolo directo.
- Al completar: raw_to_intake(...) → sync_from_intake(beta_id) → estado/slots
  derivados (incl. tally_completo). De ahí, piece 2 pedirá los estudios (labs).

Progreso por beta en state["onboarding"] = {idx, raw, status}. Persistencia vía
state_persistence (load_state/save_state) — el mismo SSOT (files o postgres).
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from state_persistence import load_state, save_state, get_current_version

_AVISO_URL = os.getenv("HV_PRIVACY_URL", "https://hombrevigente.com/aviso-privacidad")

# Cada paso: key (clave raw para raw_to_intake) · kind · prompt · (options para enum).
# El ORDEN importa: consentimiento primero (compliance), luego identidad, objetivos, screening.
STEPS: List[Dict[str, Any]] = [
    {"key": "consent_educativo", "kind": "consent",
     "prompt": ("Bienvenido a Hombre Vigente. Antes de empezar, lo importante: esto es "
                "información *educativa de optimización* — **no** sustituye consulta médica "
                "ni es una receta. ¿Estás de acuerdo en continuar bajo esa base? (responde *sí* o *no*)")},
    {"key": "consent_datos", "kind": "consent",
     "prompt": (f"Para armar tu protocolo personalizado necesito guardar tus respuestas y datos "
                f"de salud, tratados conforme a nuestro Aviso de Privacidad: {_AVISO_URL}. "
                f"¿Me autorizas a usarlos con ese fin? (*sí* / *no*)")},
    {"key": "nombre", "kind": "text", "prompt": "Perfecto. ¿Cómo te llamas? (nombre y apellido)"},
    {"key": "edad", "kind": "int", "prompt": "¿Qué edad tienes?"},
    {"key": "ciudad", "kind": "text", "prompt": "¿En qué ciudad estás?"},
    {"key": "peso_kg", "kind": "number", "prompt": "¿Tu peso aproximado en kg?"},
    {"key": "estatura_cm", "kind": "int", "prompt": "¿Tu estatura en cm?"},
    {"key": "objetivo_principal", "kind": "enum",
     "prompt": "¿Cuál es tu objetivo principal? Elige uno (responde el número):",
     "options": [
         ("1", "energia", "Energía / vitalidad"),
         ("2", "recuperacion_dolor", "Recuperación / dolor"),
         ("3", "estetica", "Estética / piel"),
         ("4", "grasa_visceral", "Grasa visceral / metabólico"),
         ("5", "longevidad", "Longevidad / prevención"),
         ("6", "rendimiento", "Rendimiento físico"),
     ]},
    {"key": "meta_8_semanas", "kind": "text",
     "prompt": "En una frase: ¿qué te gustaría lograr en las próximas 8 semanas?"},
    {"key": "cancer_antecedente", "kind": "enum",
     "prompt": "Unas de salud (importan para tu seguridad). ¿Antecedente de cáncer? Responde el número:",
     "options": [("1", "no", "No"), ("2", "si", "Sí"), ("3", "prefiero_hablarlo", "Prefiero hablarlo")]},
    {"key": "psiquiatria_tratamiento", "kind": "enum",
     "prompt": "¿Tratamiento psiquiátrico o medicación tipo litio/bipolar? Responde el número:",
     "options": [("1", "no", "No"), ("2", "si", "Sí"), ("3", "prefiero_hablarlo", "Prefiero hablarlo")]},
    {"key": "cardio_renal_hepatica", "kind": "enum",
     "prompt": "¿Condición cardiaca, renal o hepática diagnosticada? Responde el número:",
     "options": [("1", "no", "No"), ("2", "si", "Sí")]},
]

_AFFIRM = {"si", "sí", "s", "sip", "claro", "acepto", "ok", "okay", "dale", "1", "yes"}
_NEGATE = {"no", "n", "nel", "negativo", "2"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _phrase(text: str) -> str:
    """Seam para tono LLM (OFF por default). Determinístico = devuelve el guion tal cual."""
    if os.getenv("HV_ONBOARDING_LLM_TONE", "false").strip().lower() in ("1", "true", "yes"):
        try:
            from rag_retrieval_local import _llm_rephrase  # type: ignore
            return _llm_rephrase(text)  # pragma: no cover (hook futuro)
        except Exception:
            return text
    return text


def _enum_options_text(step: Dict[str, Any]) -> str:
    return "\n".join(f"  {num}) {label}" for num, _val, label in step["options"])


def _parse_enum(step: Dict[str, Any], msg: str) -> Optional[str]:
    m = msg.strip().lower()
    for num, val, label in step["options"]:
        if m == num or m == val or m == label.lower() or m in label.lower().split(" / "):
            return val
    return None


def _validate(step: Dict[str, Any], msg: str):
    """Devuelve (ok, valor_normalizado | mensaje_de_error)."""
    raw = (msg or "").strip()
    kind = step["kind"]
    if not raw:
        return False, "No te entendí, ¿me lo repites?"
    if kind == "consent":
        if raw.lower() in _AFFIRM:
            return True, "yes"
        if raw.lower() in _NEGATE:
            return True, "no"
        return False, "Responde *sí* o *no*, por favor."
    if kind == "int":
        digits = "".join(c for c in raw if c.isdigit())
        if not digits:
            return False, "Necesito un número, ¿me lo mandas así (ej. 44)?"
        return True, digits
    if kind == "number":
        cleaned = raw.replace(",", ".")
        try:
            float("".join(c for c in cleaned if c.isdigit() or c == "."))
        except Exception:
            return False, "Necesito un número (ej. 78 o 78.5)."
        return True, "".join(c for c in cleaned if c.isdigit() or c == ".")
    if kind == "enum":
        val = _parse_enum(step, raw)
        if val is None:
            return False, "Elige una de las opciones (responde el número)."
        return True, val
    return True, raw


def is_onboarding_active(state: Optional[Dict[str, Any]]) -> bool:
    ob = (state or {}).get("onboarding") or {}
    return ob.get("status") == "in_progress"


def should_start_onboarding(state: Optional[Dict[str, Any]]) -> bool:
    """Lead nuevo: sin onboarding previo y sin tally completo todavía."""
    s = state or {}
    ob = s.get("onboarding") or {}
    if ob.get("status") in ("in_progress", "completed", "aborted"):
        return ob.get("status") == "in_progress"
    slots = s.get("slots") or {}
    return not slots.get("tally_completo")


def _prompt_for(step: Dict[str, Any]) -> str:
    base = step["prompt"]
    if step["kind"] == "enum":
        base = base + "\n" + _enum_options_text(step)
    return _phrase(base)


def start_or_advance(beta_id: str, message: str) -> Dict[str, Any]:
    """
    Procesa un mensaje del beta dentro del onboarding. Devuelve
    {"reply": str, "status": in_progress|completed|aborted, "step": key}.
    El webhook envía `reply` como respuesta de WhatsApp.
    """
    state = load_state(beta_id) or {"beta_id": beta_id}
    ob = state.get("onboarding")

    # Arranque
    if not ob or ob.get("status") != "in_progress":
        ob = {"idx": 0, "raw": {}, "status": "in_progress", "started_at": _utc_now()}
        state["onboarding"] = ob
        _persist(beta_id, state)
        return {"reply": _prompt_for(STEPS[0]), "status": "in_progress", "step": STEPS[0]["key"]}

    idx = ob["idx"]
    step = STEPS[idx]
    ok, result = _validate(step, message)
    if not ok:
        return {"reply": _phrase(result + "\n\n" + _prompt_for(step)),
                "status": "in_progress", "step": step["key"]}

    # Consentimiento rechazado → abortar sin capturar datos de salud.
    if step["kind"] == "consent" and result == "no":
        ob["status"] = "aborted"
        ob["aborted_at"] = _utc_now()
        _persist(beta_id, state)
        return {"reply": _phrase(
            "Entendido, no guardamos nada. Cuando quieras retomar, escríbeme y empezamos de nuevo. 👋"),
            "status": "aborted", "step": step["key"]}

    ob["raw"][step["key"]] = result
    ob["idx"] = idx + 1

    # ¿Terminó el guion?
    if ob["idx"] >= len(STEPS):
        return _finalize(beta_id, state, ob)

    _persist(beta_id, state)
    return {"reply": _prompt_for(STEPS[ob["idx"]]), "status": "in_progress",
            "step": STEPS[ob["idx"]]["key"]}


def _finalize(beta_id: str, state: Dict[str, Any], ob: Dict[str, Any]) -> Dict[str, Any]:
    """Construye el intake, lo sincroniza al estado y cierra el onboarding."""
    from scripts.mvp0_lib import raw_to_intake  # lazy: evita acoplar import en carga
    from state_manager import state_manager as sm

    raw = dict(ob["raw"])
    raw["submitted_at"] = _utc_now()
    raw["whatsapp"] = (state.get("identity") or {}).get("whatsapp") or _phone_hint(beta_id)

    intake = raw_to_intake(raw, source="whatsapp", response_id=beta_id)
    intake.setdefault("meta", {})["tally_response_id"] = beta_id  # bind explícito

    bandera = bool((intake.get("screening") or {}).get("bandera_activa"))
    try:
        sm.sync_from_intake(intake, channel="whatsapp")
    except Exception as e:
        print(f"[onboarding] WARN sync_from_intake({beta_id}): {e}")

    ob["status"] = "completed"
    ob["completed_at"] = _utc_now()
    # Re-cargar el estado derivado por sync y re-anexar el bloque onboarding (no perderlo).
    fresh = load_state(beta_id) or state
    fresh["onboarding"] = ob
    _persist(beta_id, fresh)

    if bandera:
        reply = ("¡Gracias! Con lo que me cuentas, antes de cualquier protocolo necesitamos una "
                 "**valoración médica** (es por tu seguridad). Te conecto con el equipo para agendarla. "
                 "Mientras, si quieres ir adelantando tus estudios recientes (labs en PDF), puedes enviarlos aquí.")
    else:
        reply = ("¡Listo, gracias! Ya tengo tu perfil. Siguiente paso: si tienes **estudios de "
                 "laboratorio recientes**, mándamelos por aquí (PDF o foto) para personalizar mejor "
                 "tu protocolo. Si no, no te preocupes — seguimos con lo que tenemos.")
    return {"reply": _phrase(reply), "status": "completed", "step": "done"}


def _phone_hint(beta_id: str) -> str:
    """beta bootstrap 'wa-<dígitos>' → '+<dígitos>'."""
    if beta_id.startswith("wa-") and beta_id[3:].isdigit():
        return "+" + beta_id[3:]
    return ""


def _persist(beta_id: str, state: Dict[str, Any]) -> None:
    try:
        save_state(beta_id, state, expected_version=get_current_version(beta_id) or 0)
    except Exception as e:
        # Reintento sin versión (bootstrap / conflicto suave) — no perder el progreso.
        try:
            save_state(beta_id, state)
        except Exception as e2:
            print(f"[onboarding] WARN persist({beta_id}): {e} / {e2}")
