"""
Estado operativo por beta (S2) — fase Pipeline + next_action + slots.

Fase 1 (Guía Agéntica Estándar):
- Persistencia dual (files + postgres) detrás de HV_STATE_PERSISTENCE.
- hv_beta_states (state_data JSONB + state_version) es el SSOT cuando el flag apunta a postgres.
- Slots: se derivan desde intake en sync/derive (modelo actual), pero se persisten tal cual en state_data.
- turn_count: se mantiene denormalizado en el state (lectura rápida). El SSOT atómico vendrá de hv_agent_traces (Fase 3).
- Política de lectura: postgres gana cuando HV_STATE_PERSISTENCE=postgres|dual y DB disponible.
  Fallback a archivos solo en error (degradación ruidosa).

La lógica de derivación de slots y compute_next_action NO cambia.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Fase 1 persistence layer (Guía Agéntica Estándar)
from state_persistence import (
    StateVersionConflictError,
    ensure_last_active,
    get_current_version,
    load_state as _persisted_load,
    save_state as _persisted_save,
)

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
    """
    Guarda el estado.

    Fase 1:
    - Si se pasa `path` explícito (tests que fuerzan directorio temporal) → comportamiento legacy en archivo.
    - En el resto de casos delega a la capa de persistencia (state_persistence.py) que respeta
      HV_STATE_PERSISTENCE y la política de lectura/escritura dual.
    """
    state_dict = state.to_dict()
    state_dict = ensure_last_active(state_dict)

    if path is not None:
        # Modo legacy forzado por tests / CLI con --path
        dest = path
        dest.parent.mkdir(parents=True, exist_ok=True)
        state.updated_at = _utc_now()
        dest.write_text(json.dumps(state_dict, ensure_ascii=False, indent=2), encoding="utf-8")
        return dest

    # Camino normal Fase 1
    try:
        # Obtenemos versión actual para optimistic lock cuando corresponda
        current_version = get_current_version(state.beta_id)
        _persisted_save(
            state.beta_id,
            state_dict,
            expected_version=current_version,
            also_write_file=False,  # el módulo de persistencia decide según el flag
        )
    except StateVersionConflictError:
        # Reintento único (patrón guía). En Fase 1 simplemente re-escribimos con la versión fresca.
        fresh_version = get_current_version(state.beta_id)
        _persisted_save(
            state.beta_id,
            state_dict,
            expected_version=fresh_version,
            also_write_file=False,
        )

    # Devolvemos un path "virtual" para compatibilidad de firma (el caller rara vez lo usa)
    return _states_dir() / f"{state.beta_id}.json"


def load_state(beta_id: str, path: Optional[Path] = None) -> Optional[BetaState]:
    """
    Carga el estado.

    Fase 1:
    - Si se pasa `path` explícito → lee solo del archivo (tests).
    - En el resto delega a la capa de persistencia (respeta HV_STATE_PERSISTENCE + política postgres-first).
    """
    if path is not None:
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return BetaState(**data)

    data = _persisted_load(beta_id)
    if data is None:
        return None

    # BetaState(**data) puede fallar si hay keys extra (ej. _state_version antigua).
    # Limpiamos keys internas conocidas.
    clean = {k: v for k, v in data.items() if not k.startswith("_")}
    try:
        return BetaState(**clean)
    except TypeError:
        # Tolerancia durante transición (campos nuevos como last_active_at ya están en el dict)
        return BetaState(**{k: v for k, v in clean.items() if k in BetaState.__dataclass_fields__})


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
    """
    Fase 2: Delega la mutación a StateManager cuando sea posible (para optimistic lock + last_active).
    Mantiene la firma legacy para compatibilidad con tests y CLI.
    """
    # Actualizamos el objeto en memoria (para callers que usan el BetaState devuelto)
    state.turn_count += increment
    state.last_channel = channel

    # Disparamos la persistencia a través de StateManager (Fase 2) — import lazy para evitar circularidad
    try:
        from state_manager import state_manager as _sm
        _sm.record_turn(state.beta_id, channel=channel, increment=increment)
    except Exception:
        # Si falla (ej. sin DB en modo files estricto), el objeto en memoria ya está actualizado
        # y la persistencia legacy (a través de save_state posterior) se encargará.
        pass

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

    # Fase 1 aclaraciones (respuestas al usuario) — actualizado:
    # 1. Modelo de slots: derivados (_slot_snapshot desde intake) pero se persisten en state_data.
    # 2. SSOT de turn_number: implementado vía next_turn_number() de hv_agent_traces (atomic query); state mantiene denormalizado para lecturas rápidas.
    # 3. Política de lectura en dual-write: postgres-first implementada en state_persistence.py (fallback solo en error).
    # 4. TRAJ-HV-005 no cubre ReentryHandler temporal → cubierto por TRAJ-HV-010 (force-old-last-active + compute_resume_message).
    return fresh