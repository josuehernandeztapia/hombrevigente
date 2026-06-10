"""
signal_detector.py — Capa 6 de la Guía Agéntica Estándar: separa "ver" de "decidir".

Emite BetaSignal a partir del estado de cada beta; un handler (action_handler) decide
la acción. Señales y umbrales (verbatim del diseño original, ver recovered/README.md):
- no_activity_7d        inactividad > 168h            (high)
- no_activity_72h       inactividad > 72h             (medium)
- stalled_onboarding    onboarding, sin tally, > 120h (high)
- low_progress          <40% de slots y > 240h        (medium)
- missing_labs          tally hecho, labs no, > 96h   (medium)

LIVE/WIRED version. The faithful bytecode reconstruction lives in
recovered/signal_detector.py. The only delta here vs that archive: each signal's
`context` carries `last_active_at` so it can bridge to action_handler.BetaSignal
(which uses it for the TRAJ-HV-010 resume bands). Thresholds/types are unchanged.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from state_persistence import list_all_betas as _list_all_betas  # type: ignore
except Exception:
    try:
        from state_persistence import scan_all_states as _list_all_betas  # type: ignore
    except Exception:
        _list_all_betas = None  # type: ignore


def _utc_now():
    return datetime.now(timezone.utc)


def _hours_since(ts: Optional[str]) -> Optional[float]:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        last = datetime.fromisoformat(ts)
        return (_utc_now() - last).total_seconds() / 3600
    except Exception:
        return None


class BetaSignal:
    def __init__(self, beta_id: str, signal_type: str, severity: str = "medium",
                 context: Optional[Dict] = None):
        self.beta_id = beta_id
        self.signal_type = signal_type
        self.severity = severity
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
    def __init__(self, states_dir: Optional[str] = None):
        self.states_dir = states_dir

    def _load_all_betas(self) -> List[Dict[str, Any]]:
        if _list_all_betas is None:
            return []
        try:
            return _list_all_betas()
        except Exception as e:
            print(f"[signal_detector] WARN: list_all_betas failed: {e}")
            return []

    def scan(self, states: Optional[List[Dict[str, Any]]] = None) -> List[BetaSignal]:
        """Escanea betas y emite señales. `states` opcional (tests/calibración)."""
        signals: List[BetaSignal] = []
        betas = states if states is not None else self._load_all_betas()
        for state in betas:
            beta_id = state.get("beta_id") or "unknown"
            phase = state.get("phase", "unknown")
            slots = state.get("slots", {}) or {}
            la = state.get("last_active_at")
            hours = _hours_since(la)

            def ctx(**extra: Any) -> Dict[str, Any]:
                # last_active_at always carried for the action_handler bridge.
                return {"last_active_at": la, "phase": phase, **extra}

            if hours is not None:
                if hours > 168:
                    signals.append(BetaSignal(beta_id, "no_activity_7d", "high",
                                              ctx(hours=round(hours, 1))))
                elif hours > 72:
                    signals.append(BetaSignal(beta_id, "no_activity_72h", "medium",
                                              ctx(hours=round(hours, 1))))

            if phase == "onboarding" and not slots.get("tally_completo"):
                if hours is not None and hours > 120:
                    signals.append(BetaSignal(beta_id, "stalled_onboarding", "high",
                                              ctx(hours=round(hours, 1))))

            completed = sum(1 for v in slots.values() if v)
            total = len(slots) or 1
            progress = completed / total
            if progress < 0.4:
                if hours is not None and hours > 240:
                    signals.append(BetaSignal(beta_id, "low_progress", "medium",
                                              ctx(progress=round(progress, 2))))

            if slots.get("tally_completo") and not slots.get("labs_parseados"):
                if hours is not None and hours > 96:
                    signals.append(BetaSignal(beta_id, "missing_labs", "medium",
                                              ctx(hours=round(hours, 1))))
        return signals


def _suggest_action(signal: "BetaSignal") -> str:
    return {
        "no_activity_7d": "Enviar recordatorio suave + oferta de ayuda / reenganche",
        "no_activity_72h": "Mensaje de reingreso (usar ReentryHandler) + pregunta simple",
        "stalled_onboarding": "Recordatorio específico de Tally + link directo",
        "low_progress": "Check-in motivacional + revisión de slots pendientes",
        "missing_labs": "Recordatorio de labs + instrucciones simplificadas",
    }.get(signal.signal_type, "Revisar manualmente")
