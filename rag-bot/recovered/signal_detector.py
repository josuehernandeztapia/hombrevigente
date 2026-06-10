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

------------------------------------------------------------------------------
RECOVERED SOURCE (G6/b). The original .py was lost; only cpython-311 bytecode
survived. pycdc (Decompyle++) recovers 3.11 .pyc only partially, so this module
was reconstructed faithfully from the bytecode via marshal+dis: all thresholds,
signal types, severities and context shapes are taken verbatim from co_consts.
The two original hard imports (state_persistence.list_all_betas, traces.*) are
guarded so the module imports and scan() runs standalone even if those deps are
absent. Review before wiring into the live path.
------------------------------------------------------------------------------
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Original: `from state_persistence import list_all_betas`. Guarded — fall back to
# scan_all_states (current name) or empty so the module always imports.
try:
    from state_persistence import list_all_betas as _list_all_betas  # type: ignore
except Exception:
    try:
        from state_persistence import scan_all_states as _list_all_betas  # type: ignore
    except Exception:
        _list_all_betas = None  # type: ignore

# Original: `from traces import build_turn_payload, persist_turn_trace` (orphan module).
try:
    from traces import build_turn_payload, persist_turn_trace  # type: ignore
except Exception:
    build_turn_payload = None  # type: ignore
    persist_turn_trace = None  # type: ignore


def _utc_now():
    return datetime.now(timezone.utc)


def _hours_since(ts: Optional[str]) -> Optional[float]:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        last = datetime.fromisoformat(ts)
        delta = _utc_now() - last
        return delta.total_seconds() / 3600
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
        """
        Usa list_all_betas() de la capa de persistencia.
        Esto hace que el detector sea nativo contra hv_beta_states cuando
        HV_STATE_PERSISTENCE=postgres (SSOT real según la Guía).
        """
        if _list_all_betas is None:
            return []
        try:
            return _list_all_betas()
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
        betas = states if states is not None else self._load_all_betas()
        for state in betas:
            beta_id = state.get("beta_id") or "unknown"
            phase = state.get("phase", "unknown")
            slots = state.get("slots", {}) or {}
            hours = _hours_since(state.get("last_active_at"))

            # Inactividad
            if hours is not None:
                if hours > 168:  # 7d
                    signals.append(BetaSignal(beta_id, "no_activity_7d", "high",
                                              {"hours": round(hours, 1), "phase": phase}))
                elif hours > 72:  # 72h
                    signals.append(BetaSignal(beta_id, "no_activity_72h", "medium",
                                              {"hours": round(hours, 1), "phase": phase}))

            # Onboarding estancado: en onboarding, sin tally completo, >120h
            if phase == "onboarding" and not slots.get("tally_completo"):
                if hours is not None and hours > 120:
                    signals.append(BetaSignal(beta_id, "stalled_onboarding", "high",
                                              {"hours": round(hours, 1)}))

            # Progreso bajo: <40% de slots completados y >240h
            completed = sum(1 for v in slots.values() if v)
            total = len(slots) or 1
            progress = completed / total
            if progress < 0.4:
                if hours is not None and hours > 240:
                    signals.append(BetaSignal(beta_id, "low_progress", "medium",
                                              {"progress": round(progress, 2), "phase": phase}))

            # Labs faltantes: tally completo pero labs no parseados y >96h
            if slots.get("tally_completo") and not slots.get("labs_parseados"):
                if hours is not None and hours > 96:
                    signals.append(BetaSignal(beta_id, "missing_labs", "medium",
                                              {"hours": round(hours, 1)}))
        return signals


def _suggest_action(signal: "BetaSignal") -> str:
    return {
        "no_activity_7d": "Enviar recordatorio suave + oferta de ayuda / reenganche",
        "no_activity_72h": "Mensaje de reingreso (usar ReentryHandler) + pregunta simple",
        "stalled_onboarding": "Recordatorio específico de Tally + link directo",
        "low_progress": "Check-in motivacional + revisión de slots pendientes",
        "missing_labs": "Recordatorio de labs + instrucciones simplificadas",
    }.get(signal.signal_type, "Revisar manualmente")


def handle_signal(signal: "BetaSignal") -> Dict[str, Any]:
    """
    Handler de ejemplo (separado del detector, tal como recomienda la Guía).
    Por ahora: log + traza + acción mínima (en el futuro: enviar mensaje, crear tarea, etc.).
    """
    suggested_action = _suggest_action(signal)
    record = {
        "beta_id": signal.beta_id,
        "signal": signal.signal_type,
        "severity": signal.severity,
        "suggested_action": suggested_action,
        "handled_at": _utc_now().isoformat(),
    }
    # Best-effort trace (orphan `traces` module guarded above).
    try:
        if build_turn_payload is not None and persist_turn_trace is not None:
            payload = build_turn_payload(
                beta_id=signal.beta_id,
                branch_taken=f"signal_{signal.signal_type}",
                input_body=f"signal:{signal.signal_type}",
                output_body=suggested_action,
                state_after=signal.to_dict(),
                success=True,
            )
            persist_turn_trace(payload)
    except Exception as e:
        print(f"[signal] trace failed: {e}")
    print(f"[signal] {signal.signal_type} → {suggested_action} "
          f"({signal.severity}) | {signal.beta_id}")
    return record
