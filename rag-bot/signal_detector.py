"""
Signal Detector — Fase 5 (Capa 6 de la Guía Agéntica Estándar).

Patrón exacto del documento:

class CobranzaSignalDetector {
  async scan(): Promise<Signal[]> {
    const moraEmergente = await db.query(/* folios con dias_atraso ∈ [1,3] */);
    ...
    return [...];
  }
}

class CobranzaAgent {
  async handleSignal(signal: Signal): Promise<Action> { ... }
}

Esto separa "ver" de "decidir".

Para Hombre Vigente (betas de longevidad / protocolo 8 semanas):
- no_activity_72h
- no_activity_7d
- stalled_onboarding (lleva >7d en onboarding sin tally completo)
- low_progress (pocos slots completados después de X días)
- missing_baseline_after_intake

Los signals se emiten; un handler decide la acción (por ahora log + trace + print).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from state_persistence import list_all_betas
from traces import build_turn_payload, persist_turn_trace


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hours_since(ts: Optional[str]) -> Optional[float]:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        last = datetime.fromisoformat(ts)
        delta = _utc_now() - last
        return delta.total_seconds() / 3600.0
    except Exception:
        return None


class BetaSignal:
    def __init__(self, beta_id: str, signal_type: str, severity: str = "medium", context: Optional[Dict] = None):
        self.beta_id = beta_id
        self.signal_type = signal_type  # e.g. "no_activity_72h"
        self.severity = severity        # low | medium | high
        self.context = context or {}
        self.detected_at = _utc_now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "beta_id": self.beta_id,
            "signal_type": self.signal_type,
            "severity": self.severity,
            "context": self.context,
            "detected_at": self.detected_at,
        }


class BetaSignalDetector:
    """
    Escanea todos los estados de beta y emite signals proactivos.
    No actúa — solo detecta.
    """

    def __init__(self, states_dir: Optional[str] = None):
        self.states_dir = states_dir

    def _load_all_betas(self) -> List[Dict[str, Any]]:
        """
        Usa list_all_betas() de la capa de persistencia.
        Esto hace que el detector sea nativo contra hv_beta_states cuando
        HV_STATE_PERSISTENCE=postgres (SSOT real según la Guía).
        """
        try:
            return list_all_betas()
        except Exception as e:
            print(f"[signal_detector] WARN: list_all_betas failed: {e}")
            return []

    def scan(self, states: Optional[List[Dict[str, Any]]] = None) -> List[BetaSignal]:
        """
        Escanea betas y emite señales.
        Si se pasa `states`, usa esa lista (útil para calibración y tests).
        Si no, carga via list_all_betas (o files fallback).
        """
        signals: List[BetaSignal] = []
        if states is not None:
            betas = states
        else:
            betas = self._load_all_betas()

        for state in betas:
            beta_id = state.get("beta_id") or "unknown"
            phase = state.get("phase", "unknown")
            slots = state.get("slots", {}) or {}
            hours = _hours_since(state.get("last_active_at"))

            if hours is not None:
                if hours > 7 * 24:
                    signals.append(BetaSignal(
                        beta_id, "no_activity_7d", "high",
                        {"hours": round(hours, 1), "phase": phase}
                    ))
                elif hours > 72:
                    signals.append(BetaSignal(
                        beta_id, "no_activity_72h", "medium",
                        {"hours": round(hours, 1), "phase": phase}
                    ))

            if phase == "onboarding" and not slots.get("tally_completo"):
                if hours is not None and hours > 5 * 24:
                    signals.append(BetaSignal(
                        beta_id, "stalled_onboarding", "high",
                        {"hours": round(hours, 1)}
                    ))

            completed = sum(1 for v in slots.values() if v)
            total = len(slots) or 1
            progress = completed / total
            if progress < 0.4 and hours is not None and hours > 10 * 24:
                signals.append(BetaSignal(
                    beta_id, "low_progress", "medium",
                    {"progress": round(progress, 2), "phase": phase}
                ))

            if slots.get("tally_completo") and not slots.get("labs_parseados"):
                if hours is not None and hours > 4 * 24:
                    signals.append(BetaSignal(
                        beta_id, "missing_labs", "medium",
                        {"hours": round(hours, 1)}
                    ))

        return signals


def handle_signal(signal: BetaSignal) -> Dict[str, Any]:
    """
    Handler de ejemplo (separado del detector, tal como recomienda la Guía).
    Por ahora: log + traza + acción mínima (en el futuro: enviar mensaje, crear tarea, etc.).
    """
    action = {
        "beta_id": signal.beta_id,
        "signal": signal.signal_type,
        "severity": signal.severity,
        "suggested_action": _suggest_action(signal),
        "handled_at": _utc_now().isoformat(),
    }

    # Emitir traza (fire-and-forget)
    try:
        payload = build_turn_payload(
            beta_id=signal.beta_id,
            branch_taken=f"signal_{signal.signal_type}",
            input_body=f"signal:{signal.signal_type}",
            output_body=action["suggested_action"],
            state_after={"signal": signal.to_dict()},
            success=True,
        )
        persist_turn_trace(payload)
    except Exception:
        pass

    # Log visible
    print(f"[signal] {signal.beta_id} → {signal.signal_type} ({signal.severity}) | {action['suggested_action']}")

    return action


def _suggest_action(signal: BetaSignal) -> str:
    if signal.signal_type == "no_activity_7d":
        return "Enviar recordatorio suave + oferta de ayuda / reenganche"
    if signal.signal_type == "no_activity_72h":
        return "Mensaje de reingreso (usar ReentryHandler) + pregunta simple"
    if signal.signal_type == "stalled_onboarding":
        return "Recordatorio específico de Tally + link directo"
    if signal.signal_type == "low_progress":
        return "Check-in motivacional + revisión de slots pendientes"
    if signal.signal_type == "missing_labs":
        return "Recordatorio de labs + instrucciones simplificadas"
    return "Revisar manualmente"


# CLI / script entry point
if __name__ == "__main__":
    detector = BetaSignalDetector()
    signals = detector.scan()
    print(f"\n[detector] {len(signals)} signals encontrados\n")
    for s in signals:
        handle_signal(s)
