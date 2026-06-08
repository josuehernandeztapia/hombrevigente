"""
Estado operativo por beta (S2) — fase Pipeline + next_action + slots.

Persistencia JSON en data/beta_states/{beta_id}.json (no PHI clínico).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PHASES = (
    "lead",
    "onboarding",
    "screening",
    "protocolo-entregado",
    "semana-1",
    "semana-2",
    "semana-3",
    "semana-4",
    "feedback",
    "escalate-humano",
)

WEEK_PHASES = {"semana-1", "semana-2", "semana-3", "semana-4"}


def _norm_phase(estado: str | None) -> str:
    return (estado or "").strip().replace("_", "-")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _states_dir() -> Path:
    raw = os.getenv("HV_BETA_STATES_DIR", "data/beta_states")
    return Path(raw)


def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (s or "").strip().lower())
    return s.strip("-") or "beta"


def beta_id_from_intake(intake: dict[str, Any]) -> str:
    meta = intake.get("meta") or {}
    if meta.get("pipeline_row") is not None:
        return f"row-{meta['pipeline_row']}"
    if meta.get("tally_response_id"):
        return f"tally-{meta['tally_response_id']}"
    nombre = (intake.get("identity") or {}).get("nombre") or ""
    if meta.get("source") == "caso0":
        return "caso0"
    return _slug(nombre) or "beta"


@dataclass
class BetaState:
    beta_id: str
    phase: str
    next_action: str
    slots: Dict[str, bool] = field(default_factory=dict)
    pipeline_row: Optional[int] = None
    tally_response_id: Optional[str] = None
    perfil: Optional[str] = None
    turn_count: int = 0
    last_channel: Optional[str] = None
    updated_at: str = field(default_factory=_utc_now)
    history: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _slot_snapshot(intake: dict[str, Any], *, overrides: Optional[dict[str, bool]] = None) -> dict[str, bool]:
    screening = intake.get("screening") or {}
    moat = intake.get("data_moat") or {}
    pipe = intake.get("pipeline") or {}
    ident = intake.get("identity") or {}
    lifestyle = intake.get("lifestyle") or {}

    slots = {
        "tally_completo": bool(ident.get("nombre") and intake.get("objetivos")),
        "clearance_medica": (
            not screening.get("bandera_activa") or bool(pipe.get("revisado_medico"))
        ),
        "protocolo_entregado": _norm_phase(pipe.get("estado")) in (
            "protocolo-entregado",
            *WEEK_PHASES,
            "feedback",
        ),
        "foto_baseline": bool(moat.get("foto_subida")),
        "labs_parseados": bool(moat.get("labs_subidos") or moat.get("labs_parse_json")),
        "baseline_subjetivo": bool(
            lifestyle.get("energia_1_5") is not None and lifestyle.get("sueno_1_5") is not None
        ),
        "checkin_semana_actual": False,
    }
    if overrides:
        slots.update(overrides)
    return slots


def compute_next_action(intake: dict[str, Any], phase: str, slots: dict[str, bool]) -> str:
    screening = intake.get("screening") or {}
    marcado = bool(screening.get("bandera_activa"))

    if phase == "lead":
        return "Enviar invitación Gate A + link Tally"
    if phase == "onboarding":
        if not slots.get("tally_completo"):
            return "Completar Tally (8 min)"
        return "Ejecutar screening + asignar stack"
    if phase == "screening":
        if marcado and not slots.get("clearance_medica"):
            return "Clearance médico (psiq/onco según bandera) antes de protocolo"
        if not slots.get("labs_parseados"):
            return "Subir labs PDF → labs_intake_manual.py"
        return "Redactar protocolo + revisión médico aliado"
    if phase == "protocolo-entregado":
        missing = []
        if not slots.get("protocolo_entregado"):
            missing.append("entregar mensaje #4")
        if not slots.get("foto_baseline"):
            missing.append("foto baseline")
        if not slots.get("baseline_subjetivo"):
            missing.append("subjetivo día 0")
        if missing:
            return "Cerrar baseline: " + ", ".join(missing)
        return "Lifestyle A + introducción gradual C1 si clearance OK"
    if phase in WEEK_PHASES:
        week = phase.split("-")[1]
        return f"Check-in semana {week} (mensaje #5) + diario 1–5"
    if phase == "feedback":
        return "Encuesta cierre beta + intención de pago + Gate A siguiente"
    if phase == "escalate-humano":
        return "Fundador/médico: resolver bandera o adverse event"
    return "Revisar Pipeline manualmente"


def derive_state_from_intake(
    intake: dict[str, Any],
    *,
    slot_overrides: Optional[dict[str, bool]] = None,
) -> BetaState:
    meta = intake.get("meta") or {}
    pipe = intake.get("pipeline") or {}
    screening = intake.get("screening") or {}
    marcado = bool(screening.get("bandera_activa"))
    perfil = "marcado" if marcado else "verde"
    phase = _norm_phase(pipe.get("estado")) or ("screening" if marcado else "onboarding")
    if phase not in PHASES:
        phase = "onboarding"

    slots = _slot_snapshot(intake, overrides=slot_overrides)
    beta_id = beta_id_from_intake(intake)

    return BetaState(
        beta_id=beta_id,
        phase=phase,
        next_action=compute_next_action(intake, phase, slots),
        slots=slots,
        pipeline_row=meta.get("pipeline_row"),
        tally_response_id=meta.get("tally_response_id"),
        perfil=perfil,
        updated_at=_utc_now(),
    )


def save_state(state: BetaState, path: Optional[Path] = None) -> Path:
    dest = path or (_states_dir() / f"{state.beta_id}.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    state.updated_at = _utc_now()
    dest.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return dest


def load_state(beta_id: str, path: Optional[Path] = None) -> Optional[BetaState]:
    dest = path or (_states_dir() / f"{beta_id}.json")
    if not dest.exists():
        return None
    data = json.loads(dest.read_text(encoding="utf-8"))
    return BetaState(**data)


def transition(
    state: BetaState,
    new_phase: str,
    *,
    note: str = "",
) -> BetaState:
    if new_phase not in PHASES:
        raise ValueError(f"Fase inválida: {new_phase}")
    old = state.phase
    state.history.append(
        {
            "at": _utc_now(),
            "from_phase": old,
            "to_phase": new_phase,
            "note": note,
        }
    )
    state.phase = new_phase
    return state


def record_turn(
    state: BetaState,
    *,
    channel: str = "cli",
    increment: int = 1,
) -> BetaState:
    state.turn_count += increment
    state.last_channel = channel
    return state


def sync_from_intake(
    intake: dict[str, Any],
    *,
    channel: str = "cli",
    slot_overrides: Optional[dict[str, bool]] = None,
    persist: bool = True,
) -> BetaState:
    beta_id = beta_id_from_intake(intake)
    existing = load_state(beta_id)
    fresh = derive_state_from_intake(intake, slot_overrides=slot_overrides)

    if existing:
        fresh.turn_count = existing.turn_count
        fresh.history = list(existing.history)
        fresh.last_channel = existing.last_channel
        if existing.phase != fresh.phase:
            fresh.history.append(
                {
                    "at": _utc_now(),
                    "from_phase": existing.phase,
                    "to_phase": fresh.phase,
                    "note": "sync desde intake",
                }
            )

    fresh = record_turn(fresh, channel=channel)
    if persist:
        save_state(fresh)
    return fresh