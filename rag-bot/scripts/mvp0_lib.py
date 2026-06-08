"""Utilidades compartidas del pipeline MVP-0 (intake → labs → protocolo → tracker)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
_SCHEMA_PATH = _ROOT / "schemas" / "intake_mvp0.json"
_TALLY_MAP_PATH = _ROOT / "schemas" / "tally_field_map.json"

OBJETIVO_LABELS = {
    "energia": "Más energía / menos fatiga",
    "recuperacion_dolor": "Recuperación / dolor / lesión",
    "estetica": "Estética (piel, glow, composición corporal)",
    "grasa_visceral": "Bajar grasa (sobre todo abdominal)",
    "longevidad": "Longevidad / prevención",
    "rendimiento": "Rendimiento físico/mental",
}

STACK_LABELS = {
    "glow": "Glow",
    "wolverine": "Wolverine",
    "metabolic": "Metabolic Longevity",
    "combinacion": "Combinación",
    "pendiente": "Pendiente",
}

PIPELINE_ESTADO = {
    "screening": "screening",
    "onboarding": "onboarding",
    "protocolo-entregado": "protocolo-entregado",
}


def load_tally_map() -> dict[str, Any]:
    return json.loads(_TALLY_MAP_PATH.read_text(encoding="utf-8"))


def _norm_header(h: str) -> str:
    return re.sub(r"\s+", " ", (h or "").strip().lower())


def match_tally_column(headers: list[str], aliases: list[str]) -> str | None:
    norm_headers = {_norm_header(h): h for h in headers if h}
    for alias in aliases:
        key = _norm_header(alias)
        for nh, orig in norm_headers.items():
            if key in nh or nh in key:
                return orig
    return None


def parse_tally_row(row: dict[str, str], field_map: dict[str, Any]) -> dict[str, str]:
    """Devuelve dict campo_interno → valor crudo del CSV."""
    headers = list(row.keys())
    out: dict[str, str] = {}
    for field, aliases in field_map["columns"].items():
        col = match_tally_column(headers, aliases)
        if col:
            val = (row.get(col) or "").strip()
            if val:
                out[field] = val
    return out


def _parse_int(val: str | None, default: int | None = None) -> int | None:
    if not val:
        return default
    m = re.search(r"\d+", str(val))
    return int(m.group()) if m else default


def _parse_float(val: str | None) -> float | None:
    if not val:
        return None
    m = re.search(r"[\d.]+", str(val).replace(",", "."))
    return float(m.group()) if m else None


def _map_si_no(val: str, tally_map: dict) -> str:
    low = (val or "").strip().lower()
    return tally_map.get("si_no_map", {}).get(low, low.replace(" ", "_")[:32] or "no")


def _map_objetivo(text: str, tally_map: dict) -> str:
    low = (text or "").lower()
    for fragment, code in tally_map.get("objetivo_map", {}).items():
        if fragment in low:
            return code
    return "longevidad"


def _map_objetivos_list(text: str, tally_map: dict) -> list[str]:
    if not text:
        return []
    parts = re.split(r"[,;|\n]+", text)
    codes: list[str] = []
    for p in parts:
        code = _map_objetivo(p, tally_map)
        if code not in codes:
            codes.append(code)
    return codes


def _truthy_upload(val: str) -> bool:
    low = (val or "").lower()
    if not low:
        return False
    if low in ("no", "false", "0", "—", "-"):
        return False
    return bool(low) and low not in ("n/a", "na")


def derive_screening(raw: dict[str, str], tally_map: dict) -> dict[str, Any]:
    cancer = _map_si_no(raw.get("cancer_antecedente", ""), tally_map)
    psiq = _map_si_no(raw.get("psiquiatria_tratamiento", ""), tally_map)
    cardio = _map_si_no(raw.get("cardio_renal_hepatica", ""), tally_map)
    embarazo = (raw.get("embarazo_menor") or "").lower()
    embarazo_flag = any(
        x in embarazo for x in ("embarazo", "lactancia", "menor", "sí", "si", "checked")
    )

    detalles: list[str] = []
    if cancer in ("si", "prefiero_hablarlo"):
        detalles.append("antecedente oncológico")
    if psiq in ("si", "prefiero_hablarlo"):
        detalles.append("psiquiatría/medicación (litio, etc.)")
    if cardio == "si":
        detalles.append("cardio/renal/hepática")
    if embarazo_flag:
        detalles.append("embarazo/lactancia/menor de edad")

    med = (raw.get("medicacion_cronica") or "").lower()
    if "litio" in med or "quetiapina" in med or "bipolar" in med:
        if "psiquiatría" not in " ".join(detalles):
            detalles.append("psiquiatría (medicación crónica)")

    return {
        "cancer_antecedente": cancer if cancer else "no",
        "psiquiatria_tratamiento": psiq if psiq else "no",
        "cardio_renal_hepatica": cardio if cardio else "no",
        "medicacion_cronica": raw.get("medicacion_cronica", ""),
        "alergias": raw.get("alergias", ""),
        "embarazo_lactancia_menor": embarazo_flag,
        "medico_cabecera": _map_si_no(raw.get("medico_cabecera", ""), tally_map),
        "bandera_activa": bool(detalles),
        "bandera_detalle": "; ".join(detalles) if detalles else "",
    }


def suggest_stack(objetivo_principal: str, secundarios: list[str]) -> str:
    if objetivo_principal == "recuperacion_dolor":
        return "wolverine"
    if objetivo_principal == "estetica":
        return "glow" if "recuperacion_dolor" not in secundarios else "combinacion"
    if objetivo_principal == "grasa_visceral":
        return "metabolic"
    if objetivo_principal in ("energia", "longevidad", "rendimiento"):
        if "recuperacion_dolor" in secundarios:
            return "combinacion"
        return "combinacion" if len(secundarios) > 1 else "combinacion"
    return "combinacion"


def raw_to_intake(
    raw: dict[str, str],
    *,
    source: str = "tally",
    pipeline_row: int | None = None,
    response_id: str | None = None,
) -> dict[str, Any]:
    tally_map = load_tally_map()
    principal = _map_objetivo(raw.get("objetivo_principal", ""), tally_map)
    secundarios = _map_objetivos_list(raw.get("objetivos_secundarios", ""), tally_map)
    screening = derive_screening(raw, tally_map)
    stack = suggest_stack(principal, secundarios)

    foto = _truthy_upload(raw.get("foto_subida", ""))
    labs = _truthy_upload(raw.get("labs_subidos", ""))
    wearable_text = (raw.get("wearable_usa") or "").lower()
    wearable = wearable_text.startswith("sí") or wearable_text.startswith("si") or (
        "oura" in wearable_text or "whoop" in wearable_text or "apple" in wearable_text
    )

    estado = "screening" if screening["bandera_activa"] else "onboarding"

    intake: dict[str, Any] = {
        "meta": {
            "submitted_at": raw.get("submitted_at")
            or datetime.now(timezone.utc).isoformat(),
            "source": source,
        },
        "identity": {
            "nombre": raw.get("nombre", "").strip(),
            "edad": _parse_int(raw.get("edad")),
            "whatsapp": raw.get("whatsapp", "").strip(),
            "ciudad": raw.get("ciudad", "").strip(),
            "peso_kg": _parse_float(raw.get("peso_kg")),
            "estatura_cm": _parse_int(raw.get("estatura_cm")),
        },
        "objetivos": {
            "principal": principal,
            "secundarios": secundarios,
            "meta_8_semanas": raw.get("meta_8_semanas", "").strip(),
            "urgencia_1_5": _parse_int(raw.get("urgencia_1_5")),
        },
        "lifestyle": {
            "energia_1_5": _parse_int(raw.get("energia_1_5")),
            "sueno_1_5": _parse_int(raw.get("sueno_1_5")),
            "dias_entreno_semana": _parse_int(raw.get("dias_entreno_semana"), 0),
            "dolor_recurrente": raw.get("dolor_recurrente", "").strip(),
            "suplementos_actuales": raw.get("suplementos_actuales", "").strip(),
        },
        "screening": screening,
        "data_moat": {
            "foto_subida": foto,
            "labs_subidos": labs,
            "wearable_usa": wearable,
            "wearable_dispositivo": raw.get("wearable_dispositivo", "").strip(),
            "wearable_promedios_7d": raw.get("wearable_promedios_7d", "").strip(),
        },
        "consentimiento": {
            "educativo_no_rx": _truthy_upload(raw.get("consent_educativo", "yes")),
            "uso_datos_protocolo": _truthy_upload(raw.get("consent_datos", "yes")),
            "anonimo_mejora_producto": _truthy_upload(raw.get("consent_anonimo", "")),
            "feedback_4_semanas": _truthy_upload(raw.get("consent_feedback", "")),
        },
        "pipeline": {
            "estado": estado,
            "stack_sugerido": stack,
            "revisado_medico": False,
        },
    }
    if response_id:
        intake["meta"]["tally_response_id"] = response_id
    if pipeline_row is not None:
        intake["meta"]["pipeline_row"] = pipeline_row
    return intake


def intake_to_pipeline_row(intake: dict[str, Any]) -> dict[str, Any]:
    ident = intake.get("identity") or {}
    obj = intake.get("objetivos") or {}
    screening = intake.get("screening") or {}
    moat = intake.get("data_moat") or {}
    pipe = intake.get("pipeline") or {}

    principal_label = OBJETIVO_LABELS.get(obj.get("principal", ""), obj.get("principal", ""))
    sec_labels = [OBJETIVO_LABELS.get(s, s) for s in obj.get("secundarios") or []]
    objetivo_txt = principal_label
    if sec_labels:
        objetivo_txt += " + " + " + ".join(sec_labels[:3])

    bandera = "No"
    if screening.get("bandera_activa"):
        bandera = f"SÍ — {screening.get('bandera_detalle', 'revisar')}"

    stack = STACK_LABELS.get(pipe.get("stack_sugerido", ""), pipe.get("stack_sugerido", ""))

    return {
        "#": intake.get("meta", {}).get("pipeline_row", ""),
        "Nombre": ident.get("nombre", ""),
        "WhatsApp": ident.get("whatsapp", ""),
        "Edad": ident.get("edad", ""),
        "Ciudad": ident.get("ciudad", ""),
        "Objetivo principal": objetivo_txt,
        "Estado": pipe.get("estado", "onboarding"),
        "Bandera screening": bandera,
        "Datos: foto": "Sí" if moat.get("foto_subida") else "No",
        "Datos: labs": "Sí" if moat.get("labs_subidos") else "No",
        "Datos: wearable": (
            f"Sí — {moat.get('wearable_dispositivo')}"
            if moat.get("wearable_usa")
            else "No"
        ),
        "Stack asignado": stack,
        "Fecha entrega": "",
        "Revisado x médico": "Pendiente" if not pipe.get("revisado_medico") else "Sí",
        "Notas": "",
    }


def route_profile(intake: dict[str, Any]) -> dict[str, Any]:
    """
    Triage MVP-0: verde (Av.1 rápida) vs marcado (clearance médico).
    Los docs son rutas relativas a estrategia_2026/ en el repo HV.
    """
    screening = intake.get("screening") or {}
    marcado = bool(screening.get("bandera_activa"))
    nombre = (intake.get("identity") or {}).get("nombre") or "beta"

    if marcado:
        return {
            "perfil": "marcado",
            "bandera": screening.get("bandera_detalle", ""),
            "ux": "routing médico · bloques A/B/C1/C2/D con porqué",
            "docs": [
                "MVP0_Caso0_Clearance_Psiquiatra.md",  # adaptar por tipo bandera
                "MVP0_Template_Beta.md",
            ],
            "entrega": "MVP0_Entrega_Marcado.md",
            "mensaje_wa": "script #3 bandera + clearance antes de stack",
            "estado_pipeline": "screening",
            "nota": f"Perfil marcado ({screening.get('bandera_detalle', '')}). No usar plantilla verde.",
        }

    stack = (intake.get("pipeline") or {}).get("stack_sugerido", "combinacion")
    return {
        "perfil": "verde",
        "bandera": None,
        "ux": "rápido · Av.1 · stack orientativo, empieza hoy",
        "docs": ["MVP0_Entrega_Verde.md", "MVP0_Template_Beta.md"],
        "entrega": "MVP0_Entrega_Verde.md",
        "mensaje_wa": "script #4 verde",
        "estado_pipeline": "onboarding",
        "stack_sugerido": stack,
        "nota": f"Perfil verde para {nombre}. Sin muro de advertencias clínico.",
    }


def merge_labs_into_intake(
    intake: dict[str, Any],
    labs_path: Path,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    """Adjunta ruta labs parseados a data_moat (copia superficial del intake)."""
    root = root or _ROOT
    labs_path = labs_path.resolve()
    try:
        rel = labs_path.relative_to(root.resolve())
        stored = str(rel).replace("\\", "/")
    except ValueError:
        stored = str(labs_path)

    out = json.loads(json.dumps(intake))
    moat = out.setdefault("data_moat", {})
    moat["labs_parse_json"] = stored
    moat["labs_subidos"] = True
    return out


PIPELINE_COLUMNS = [
    "#",
    "Nombre",
    "WhatsApp",
    "Edad",
    "Ciudad",
    "Objetivo principal",
    "Estado",
    "Bandera screening",
    "Datos: foto",
    "Datos: labs",
    "Datos: wearable",
    "Stack asignado",
    "Fecha entrega",
    "Revisado x médico",
    "Notas",
]