"""
Feature Flags — Capa 5 / production checklist de la Guía Agéntica Estándar.

Patrón exacto recomendado:
- Default ON (seguro).
- Deshabilitar con env var HV_FEATURE_XXX=false (sin redeploy, rollback en <5s).
- Usar para branches nuevos, gates, y "se corrige" fácil.

Uso:
    from feature_flags import is_enabled, list_active_flags

    if is_enabled("PROACTIVE_EXECUTION"):
        # código real

    flags = list_active_flags()  # para /admin/health y ops

Agregar nuevo flag: simplemente usar is_enabled("NUEVO_NOMBRE") en el código.
El flag aparecerá automáticamente en list_active_flags() si se consulta.
"""

from __future__ import annotations

import os
from typing import Dict, List


def _normalize(val: str) -> bool:
    v = (val or "").strip().lower()
    if v in ("0", "false", "no", "off", "disabled", "disable"):
        return False
    return True


def is_enabled(name: str, default: bool = True) -> bool:
    """
    Devuelve True si el feature está habilitado.
    Env var: HV_FEATURE_{NAME} (ej. HV_FEATURE_PROACTIVE_EXECUTION=false)
    Default es True (ON) para que todo nuevo feature sea seguro por defecto.
    """
    env_name = f"HV_FEATURE_{name.upper().replace('-', '_')}"
    raw = os.getenv(env_name)
    if raw is None:
        return default
    return _normalize(raw)


def list_active_flags() -> Dict[str, bool]:
    """
    Devuelve el estado de los flags conocidos + cualquier HV_FEATURE_* que esté seteado.
    Útil para /admin/agent_status, health, y ops visibility.
    """
    known = [
        "PROACTIVE_EXECUTION",
        "HEALTH_GATE",
        "RAG_LLM",
        "CALIBRATION",
        "PROACTIVE_NIGHTLY",
    ]

    flags: Dict[str, bool] = {}
    for name in known:
        flags[name] = is_enabled(name)

    # También escanear cualquier HV_FEATURE_ extra que el usuario haya puesto
    for key, val in os.environ.items():
        if key.startswith("HV_FEATURE_"):
            flag_name = key[len("HV_FEATURE_"):]
            if flag_name not in flags:
                flags[flag_name] = _normalize(val)

    return dict(sorted(flags.items()))


def require_enabled(name: str, default: bool = True) -> None:
    """Helper para fallar explícitamente si un flag crítico está apagado."""
    if not is_enabled(name, default):
        raise RuntimeError(f"Feature flag '{name}' is disabled (HV_FEATURE_{name}=false)")


# Ejemplos de uso en el código (comentados para referencia):
# if is_enabled("PROACTIVE_EXECUTION"):
#     ... real send ...
#
# if is_enabled("HEALTH_GATE"):
#     ... aplicar el is_healthy gate ...
#
# if is_enabled("RAG_LLM"):
#     use_llm = use_llm and is_enabled("RAG_LLM")
