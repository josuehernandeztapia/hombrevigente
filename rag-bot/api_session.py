"""
api_session.py — sesiones de la app (JSON), sin passwords.

Por qué existe: hasta ahora todo lo que el producto expone sale por TwiML en
`/webhook/whatsapp`. Un front (la app v2 diseñada en design/handoff) necesita
JSON e identidad propia. Este módulo da lo segundo.

Modelo de identidad: WhatsApp YA autentica al beta (Twilio firma el inbound y el
número mapea a un beta_id). Así que la app no inventa credenciales: el beta pide
acceso por su hilo y recibe un token de sesión firmado. Cero passwords que
robar, cero base de credenciales que cuidar — y coherente con el producto
WhatsApp-nativo.

Patrón HMAC calcado de newsletter/approval_token.py, que ya lleva meses en
producción firmando los links de aprobación del Pulso.

Fail-closed: sin HV_APP_SESSION_SECRET no se emite ni se acepta ningún token.
Un endpoint de datos de salud no debe degradar a "sin auth" por falta de config.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Optional

DEFAULT_TTL_HOURS = 720  # 30 días: la app es de uso recurrente, no una sesión bancaria


def _secret() -> str:
    s = os.environ.get("HV_APP_SESSION_SECRET", "").strip()
    if not s:
        raise ValueError("HV_APP_SESSION_SECRET no configurado")
    return s


def session_configured() -> bool:
    """True si la app puede emitir sesiones (para reportarlo sin filtrar el secreto)."""
    return bool(os.environ.get("HV_APP_SESSION_SECRET", "").strip())


def _sign(beta_id: str, exp: int) -> str:
    return hmac.new(
        _secret().encode(),
        f"{beta_id}|{exp}".encode(),
        hashlib.sha256,
    ).hexdigest()


def issue_token(beta_id: str, *, ttl_hours: int = DEFAULT_TTL_HOURS) -> str:
    """Token de sesión para un beta. Formato: <beta_id>.<exp>.<sig>"""
    if not beta_id:
        raise ValueError("beta_id requerido")
    exp = int(time.time()) + int(ttl_hours) * 3600
    return f"{beta_id}.{exp}.{_sign(beta_id, exp)}"


def verify_token(token: str) -> Optional[str]:
    """Devuelve el beta_id si el token es válido y vigente; None si no.

    Nunca lanza: un token corrupto es un 401, no un 500.
    """
    if not token:
        return None
    try:
        beta_id, exp_s, sig = token.rsplit(".", 2)
        exp = int(exp_s)
    except (ValueError, AttributeError):
        return None
    if exp < int(time.time()):
        return None
    try:
        expected = _sign(beta_id, exp)
    except ValueError:
        return None  # secreto no configurado → nada es válido
    if not hmac.compare_digest(expected, sig):
        return None
    return beta_id
