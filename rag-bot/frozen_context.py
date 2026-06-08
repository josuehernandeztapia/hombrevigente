"""
Contexto congelado del intake (S5) — perfil beta para gates + prompt RAG.
Sin PHI en logs: el bloque va al LLM; decision_log usa beta_id + turn.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Tuple

from beta_state import beta_id_from_intake

_ROOT = Path(__file__).resolve().parent

_BETA_INTAKE_PATHS: dict[str, Path] = {
    "row-0": _ROOT / "fixtures" / "caso0_intake_p1_entrega.json",
    "caso0": _ROOT / "fixtures" / "caso0_intake_p1_entrega.json",
    "tally-gbAO6Yl": _ROOT / "data" / "mvp0_runs" / "caso0_gbAO6Yl" / "intake" / "juan_josue_hernandez_intake.json",
}


def _find_tally_intake(tally_id: str) -> Optional[Path]:
    run_dir = _ROOT / "data" / "mvp0_runs" / f"caso0_{tally_id}" / "intake"
    if not run_dir.is_dir():
        return None
    for p in sorted(run_dir.glob("*_intake.json")):
        return p
    return None


def resolve_intake_path(beta_id: str) -> Optional[Path]:
    if beta_id in _BETA_INTAKE_PATHS:
        p = _BETA_INTAKE_PATHS[beta_id]
        return p if p.exists() else None
    if beta_id.startswith("tally-"):
        return _find_tally_intake(beta_id[6:])
    custom = _ROOT / "data" / "intake" / f"{beta_id}.json"
    if custom.exists():
        return custom
    return None


def load_intake_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_intake(
    *,
    intake: Optional[dict[str, Any]] = None,
    intake_path: Optional[Path | str] = None,
    beta_id: Optional[str] = None,
) -> Tuple[Optional[dict[str, Any]], Optional[str]]:
    """Devuelve (intake, beta_id)."""
    if intake is not None:
        return intake, beta_id or beta_id_from_intake(intake)

    if intake_path:
        p = Path(intake_path)
        if not p.is_absolute():
            p = _ROOT / p
        if p.exists():
            data = load_intake_json(p)
            return data, beta_id or beta_id_from_intake(data)

    if beta_id:
        p = resolve_intake_path(beta_id)
        if p:
            data = load_intake_json(p)
            return data, beta_id

    return None, beta_id


def build_frozen_context(intake: dict[str, Any]) -> str:
    """Resumen estructurado para gates y prompt (sin rutas privadas)."""
    ident = intake.get("identity") or {}
    obj = intake.get("objetivos") or {}
    life = intake.get("lifestyle") or {}
    screen = intake.get("screening") or {}
    moat = intake.get("data_moat") or {}
    pipe = intake.get("pipeline") or {}

    lines = [
        f"Nombre: {ident.get('nombre', '?')}",
        f"Edad: {ident.get('edad', '?')} · Ciudad: {ident.get('ciudad', '?')}",
        f"Objetivo 8 sem: {obj.get('principal', '?')} — {obj.get('meta_8_semanas', '')}",
    ]
    if life.get("suplementos_actuales"):
        lines.append(f"Medicación/suplementos actuales: {life['suplementos_actuales']}")
    if screen.get("medicacion_cronica"):
        lines.append(f"Medicación crónica (screening): {screen['medicacion_cronica']}")
    if screen.get("bandera_activa"):
        lines.append(f"BANDERA screening: {screen.get('bandera_detalle', 'activa')}")
    else:
        lines.append("BANDERA screening: no")
    if life.get("dolor_recurrente"):
        lines.append(f"Dolor recurrente: {life['dolor_recurrente']}")
    if life.get("energia_1_5") is not None:
        lines.append(f"Subjetivo intake: energía {life['energia_1_5']}/5 · sueño {life.get('sueno_1_5', '?')}/5")
    moat_bits = []
    if moat.get("foto_subida"):
        moat_bits.append("foto")
    if moat.get("labs_subidos") or moat.get("labs_parse_json"):
        moat_bits.append("labs")
    if moat.get("wearable_usa"):
        moat_bits.append("wearable")
    if moat_bits:
        lines.append(f"Data moat: {', '.join(moat_bits)}")
    if pipe.get("estado"):
        lines.append(f"Fase pipeline: {pipe['estado']}")
    return "\n".join(lines)


def gate_probe_text(query: str, frozen: str = "") -> str:
    """Texto combinado para regex de gates (pregunta + perfil)."""
    if not frozen:
        return query
    return f"{query}\n---\nPERFIL:\n{frozen}"