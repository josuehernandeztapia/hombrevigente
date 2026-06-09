"""
StateManager — Fase 2 de la Guía Agéntica Estándar (Capa 3).

Implementa la API central del state machine resumible con:
- Optimistic locking vía state_version (con reintento único en conflicto)
- fill_slot idempotente (mismo valor → no genera write)
- last_active_at actualizado en toda mutación (dentro del state_data)
- Uso de la capa de persistencia de Fase 1 (soporta files/postgres/dual)
- Lógica de slots y next_action delegada a beta_state (derivación preservada)

Aún no incluye ReentryHandler completo (eso es Fase 4).

Respeta las aclaraciones previas (puntos del usuario):
- Slots: derivados en sync/derive, pero persistidos en state_data.
- turn_count: denormalizado aquí para lecturas rápidas; SSOT atómico vía next_turn_number() de hv_agent_traces (implementado).
- Lecturas/escrituras van por la política de state_persistence (postgres-first en dual-write).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from beta_state import (
    PHASES,
    WEEK_PHASES,
    BetaState,
    compute_next_action,
    derive_state_from_intake,
    _norm_phase,
    _slot_snapshot,
)
from state_persistence import (
    StateVersionConflictError,
    ensure_last_active,
    get_current_version,
    load_state,
    next_turn_number,
    save_state,
)

# Fase 3: traces para mutaciones del state machine
try:
    from traces import build_turn_payload, persist_turn_trace
except Exception:
    build_turn_payload = lambda **k: {}
    persist_turn_trace = lambda p: None

# Fase 4: ReentryHandler
from reentry import compute_resume_message, get_resume_context, compute_hours_away


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateManager:
    """
    StateManager central (inspirado directamente en el sketch de la Guía).

    Uso típico:
        sm = StateManager()
        state, version = sm.get_state(beta_id)
        state = sm.fill_slot(beta_id, "foto_baseline", True, expected_version=version)
        state = sm.record_turn(beta_id, channel="whatsapp")
    """

    def get_state(self, beta_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Devuelve (state_dict, current_version).
        El state_dict es el contenido de state_data (sin la clave interna de versión).
        turn_count se mantiene sincronizado con el SSOT de traces en mutaciones.
        """
        data = load_state(beta_id) or {}
        version = data.pop("_state_version", None)
        if version is None:
            version = get_current_version(beta_id) or 0
        # Best-effort: si traces tienen turn más alto, el próximo record_turn lo corregirá
        # (evitamos side-effect en get puro; el authoritative se fuerza en record_turn/transition)
        return data, int(version)

    def _ensure_state_dict(
        self,
        beta_id: str,
        intake: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], int]:
        """
        Carga estado existente o deriva uno fresco desde intake si se provee.
        """
        state, version = self.get_state(beta_id)
        if state:
            return state, version

        if intake:
            fresh = derive_state_from_intake(intake).to_dict()
            fresh = ensure_last_active(fresh)
            return fresh, 0

        # Estado vacío mínimo
        return {
            "beta_id": beta_id,
            "phase": "onboarding",
            "next_action": "Completar Tally (8 min)",
            "slots": {},
            "turn_count": 0,
            "history": [],
        }, 0

    def fill_slot(
        self,
        beta_id: str,
        slot: str,
        value: bool,
        *,
        expected_version: Optional[int] = None,
        intake: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Idempotente: si el slot ya tiene exactamente ese valor, NO escribe (no bumpea versión).
        Actualiza last_active_at solo si hay cambio real.
        """
        state, current_version = self._ensure_state_dict(beta_id, intake)
        if expected_version is None:
            expected_version = current_version

        slots: Dict[str, bool] = dict(state.get("slots", {}))
        if slots.get(slot) == value:
            # Idempotente según guía: mismo (slot, value) → no genera write
            return state

        slots[slot] = value
        state["slots"] = slots

        # Recomputar next_action con la lógica existente (derivada)
        phase = state.get("phase", "onboarding")
        # Reconstruimos un intake mínimo para compute_next_action (evitamos acoplamiento fuerte)
        intake_like = {"pipeline": {"estado": phase}}
        state["next_action"] = compute_next_action(intake_like, phase, slots)

        state = ensure_last_active(state)

        try:
            new_version = save_state(
                beta_id, state, expected_version=expected_version
            )
            state["_state_version"] = new_version
            return state
        except StateVersionConflictError:
            # Un solo reintento (patrón recomendado en la Guía)
            fresh_version = get_current_version(beta_id) or 0
            new_version = save_state(
                beta_id, state, expected_version=fresh_version
            )
            state["_state_version"] = new_version
            return state

    def transition(
        self,
        beta_id: str,
        target_phase: str,
        *,
        expected_version: Optional[int] = None,
        force: bool = False,
        note: str = "",
        intake: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Cambia de fase.
        - force=True permite saltos que normalmente bloquearía (equivalente al admin endpoint de la guía).
        - Actualiza history y last_active_at.
        """
        if target_phase not in PHASES:
            raise ValueError(f"Fase inválida: {target_phase}")

        state, current_version = self._ensure_state_dict(beta_id, intake)
        if expected_version is None:
            expected_version = current_version

        if not force:
            # Precondición básica (se puede enriquecer con min_required_to_continue en Fase 2+)
            # Por ahora permitimos forward transitions libremente (como en el código actual)
            pass

        old_phase = state.get("phase")
        state["phase"] = target_phase

        history = list(state.get("history", []))
        history.append(
            {
                "at": _utc_now(),
                "from_phase": old_phase,
                "to_phase": target_phase,
                "note": note or "transition",
            }
        )
        state["history"] = history

        # Recomputar next_action
        slots = state.get("slots", {})
        intake_like = {"pipeline": {"estado": target_phase}}
        state["next_action"] = compute_next_action(intake_like, target_phase, slots)

        state = ensure_last_active(state)

        try:
            new_version = save_state(
                beta_id, state, expected_version=expected_version
            )
            state["_state_version"] = new_version

            # Fase 3 trace con turn SSOT
            try:
                tnum = next_turn_number(beta_id)
                payload = build_turn_payload(
                    beta_id=beta_id,
                    turn_number=tnum,
                    role="concierge",
                    phase=target_phase,
                    branch_taken="state_transition",
                    input_body=f"phase:{old_phase}→{target_phase}",
                    state_before={"phase": old_phase},
                    state_after=state,
                    success=True,
                )
                persist_turn_trace(payload)
            except Exception:
                pass

            return state
        except StateVersionConflictError:
            fresh_version = get_current_version(beta_id) or 0
            new_version = save_state(
                beta_id, state, expected_version=fresh_version
            )
            state["_state_version"] = new_version
            return state

    def record_turn(
        self,
        beta_id: str,
        *,
        channel: str = "cli",
        increment: int = 1,
        expected_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Incrementa el contador de turnos y actualiza last_channel + last_active_at.
        Usa next_turn_number de traces como SSOT atómico (Guía Capa 2).
        El state mantiene denormalizado turn_count para lecturas rápidas.
        """
        state, current_version = self.get_state(beta_id)
        if not state:
            state = {
                "beta_id": beta_id,
                "phase": "onboarding",
                "next_action": "",
                "slots": {},
                "turn_count": 0,
                "history": [],
            }
            current_version = 0

        if expected_version is None:
            expected_version = current_version

        # SSOT atómico desde traces (punto 2 del usuario / Guía)
        authoritative_turn = next_turn_number(beta_id)
        state["turn_count"] = authoritative_turn
        state["last_channel"] = channel
        state = ensure_last_active(state)

        try:
            new_version = save_state(
                beta_id, state, expected_version=expected_version
            )
            state["_state_version"] = new_version

            # Trace con el turn_number autoritativo
            try:
                payload = build_turn_payload(
                    beta_id=beta_id,
                    turn_number=authoritative_turn,
                    role="concierge",
                    phase=state.get("phase"),
                    branch_taken="record_turn",
                    input_body=f"channel:{channel}",
                    state_after=state,
                    success=True,
                )
                persist_turn_trace(payload)
            except Exception:
                pass

            return state
        except StateVersionConflictError:
            fresh_version = get_current_version(beta_id) or 0
            new_version = save_state(
                beta_id, state, expected_version=fresh_version
            )
            state["_state_version"] = new_version
            return state

    def get_suggested_next_action(self, beta_id: str) -> str:
        """Devuelve el next_action calculado desde el estado actual."""
        state, _ = self.get_state(beta_id)
        phase = state.get("phase", "onboarding")
        slots = state.get("slots", {})
        intake_like = {"pipeline": {"estado": phase}}
        return compute_next_action(intake_like, phase, slots)

    def resume_conversation(
        self,
        beta_id: str,
        hours_away: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fase 4 — ReentryHandler (patrón exacto de la Guía).
        Devuelve {band, text} o None si el usuario regresó hace <24h.
        """
        state, _ = self.get_state(beta_id)
        if not state:
            return None
        return compute_resume_message(state, hours_away=hours_away)

    # Helper de conveniencia (útil para callers)
    def sync_from_intake(
        self,
        intake: Dict[str, Any],
        *,
        channel: str = "cli",
        slot_overrides: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """
        Mantiene compatibilidad con el flujo actual de sync.
        Deriva el estado fresco (slots derivados) y lo persiste vía fill/transition si es necesario.
        """
        beta_id = intake.get("meta", {}).get("tally_response_id") or "unknown"
        # Por simplicidad en Fase 2 usamos derive + record_turn
        fresh = derive_state_from_intake(intake, slot_overrides=slot_overrides).to_dict()
        fresh = ensure_last_active(fresh)

        # Guardamos el estado derivado (bootstrap o sync)
        current_v = get_current_version(beta_id) or 0
        try:
            save_state(beta_id, fresh, expected_version=current_v)
        except StateVersionConflictError:
            fresh_v = get_current_version(beta_id) or 0
            save_state(beta_id, fresh, expected_version=fresh_v)

        # Registramos el turno
        return self.record_turn(beta_id, channel=channel)


# Instancia singleton para uso simple (puede inyectarse después)
state_manager = StateManager()
