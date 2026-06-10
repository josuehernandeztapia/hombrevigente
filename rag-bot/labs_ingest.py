"""
labs_ingest.py — Ingesta de estudios (labs) al estado del beta.

Pieza 2 del intake WhatsApp-nativo: cuando el beta manda un PDF/imagen de labs por
el hilo, esto los parsea (process_pdf de labs_intake_manual: texto PyMuPDF → visión
OpenAI fallback → biomarcadores estructurados), guarda el resultado en el estado y
marca el slot `labs_parseados`. Reusable fuera de WhatsApp (CLI, futura app).

El resultado estructurado (PII de salud) se guarda en state["labs_result"]; el slot
booleano `labs_parseados` avanza la máquina de fases (screening → protocolo).
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ingest_labs_pdf(beta_id: str, pdf_path: str, *, dry_run: bool = False) -> Dict[str, Any]:
    """
    Parsea el PDF/imagen y, si hay biomarcadores, marca labs_parseados + guarda el
    resultado en el estado. Devuelve un resumen liviano (no expone PII en el reply):
    {"ok", "n_markers", "flags", "method", "summary_text"}.
    Nunca lanza hacia el caller (el webhook degrada con un mensaje amable).
    """
    try:
        from scripts.labs_intake_manual import process_pdf, validate_labs_payload
    except Exception as e:
        return {"ok": False, "error": f"labs parser no disponible: {e}",
                "summary_text": "No pude procesar el estudio ahora. El equipo lo revisará."}

    struct_model = os.getenv("HV_LABS_STRUCT_MODEL", "gpt-4o-mini")
    vision_model = os.getenv("HV_LABS_VISION_MODEL", "gpt-4o-mini")
    min_text_chars = int(os.getenv("HV_LABS_MIN_TEXT_CHARS", "400"))

    from pathlib import Path
    try:
        structured = process_pdf(
            Path(pdf_path),
            struct_model=struct_model,
            vision_model=vision_model,
            min_text_chars=min_text_chars,
            force_vision=False,
            dry_run=dry_run,
        )
    except Exception as e:
        return {"ok": False, "error": f"parse falló: {e}",
                "summary_text": "Tu estudio llegó pero no pude leerlo automáticamente; "
                                "el equipo lo revisará a mano. 🙌"}

    if dry_run:
        return {"ok": True, "dry_run": True, "method": structured.get("extraction_method"),
                "summary_text": "(dry-run) estudio recibido."}

    markers = structured.get("biomarcadores") or structured.get("markers") or []
    n = len(markers) if isinstance(markers, list) else 0
    warnings = []
    try:
        warnings = validate_labs_payload(structured)
    except Exception:
        pass

    if n == 0:
        return {"ok": False, "n_markers": 0, "method": structured.get("extraction_method"),
                "summary_text": "Recibí el archivo pero no detecté biomarcadores claros. "
                                "¿Puedes reenviarlo más nítido o en PDF? Si no, el equipo lo revisa."}

    # Persistir: resultado estructurado en estado + slot labs_parseados.
    try:
        from state_persistence import load_state, save_state, get_current_version
        state = load_state(beta_id) or {"beta_id": beta_id}
        state["labs_result"] = {**structured, "_ingested_at": _utc_now(),
                                "_source_path": os.path.basename(pdf_path)}
        try:
            save_state(beta_id, state, expected_version=get_current_version(beta_id) or 0)
        except Exception:
            save_state(beta_id, state)
    except Exception as e:
        print(f"[labs_ingest] WARN persist labs_result({beta_id}): {e}")

    try:
        from state_manager import state_manager as sm
        sm.fill_slot(beta_id, "labs_parseados", True)
    except Exception as e:
        print(f"[labs_ingest] WARN fill_slot({beta_id}): {e}")

    flagged = [m for m in markers if isinstance(m, dict) and m.get("flag") not in (None, "", "normal", "ok")]
    summary = (f"¡Recibí tu estudio! Detecté {n} biomarcadores"
               + (f", {len(flagged)} fuera de rango para revisar con tu médico." if flagged
                  else " dentro de lo esperado.")
               + " Los uso para personalizar tu protocolo (esto no es diagnóstico).")
    return {"ok": True, "n_markers": n, "flags": len(flagged),
            "method": structured.get("extraction_method"),
            "warnings": warnings, "summary_text": summary}
