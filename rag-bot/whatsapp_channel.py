"""
whatsapp_channel.py — Canal WhatsApp vía Twilio (Día 1 del plan WhatsApp-nativo).

Piezas:
- normalize_phone / lookup_beta_by_phone / phone_for_beta: mapeo E.164 ↔ beta_id.
  Fuentes: registry opcional data/wa_contacts.json ({"+52...": "beta-id"}) y los
  intakes en HV_INTAKE_DIR (identity.whatsapp). Número desconocido → beta_id
  determinístico "wa-<dígitos>" (bootstrap de lead; state_manager crea el estado).
- validate_twilio_signature: X-Twilio-Signature (HMAC-SHA1 base64 del URL + params
  ordenados, firmado con el auth token) — stdlib, sin SDK de Twilio.
- send_whatsapp: POST a la API de mensajes de Twilio (requests). Texto libre
  (ventana 24h) o template aprobado vía content_sid/content_variables.
- twiml_reply: respuesta inline al webhook (no consume API ni requiere creds).

Env:
  TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_WHATSAPP_FROM ("whatsapp:+1...")
  HV_TWILIO_VALIDATE=false  → salta validación de firma (solo dev/tests)
  HV_INTAKE_DIR (default data/intake) / HV_WA_CONTACTS (default data/wa_contacts.json)
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
from xml.sax.saxutils import escape

TWILIO_API = "https://api.twilio.com/2010-04-01"
# WhatsApp corta cuerpos >1600 chars; dejamos margen.
MAX_BODY_CHARS = 1500


class ChannelSendError(Exception):
    """El envío vía Twilio falló (HTTP != 2xx o sin credenciales)."""


def twilio_configured() -> bool:
    return bool(
        os.getenv("TWILIO_ACCOUNT_SID")
        and os.getenv("TWILIO_AUTH_TOKEN")
        and os.getenv("TWILIO_WHATSAPP_FROM")
    )


# ------------------------------------------------------------------
# Teléfonos ↔ betas
# ------------------------------------------------------------------

def normalize_phone(raw: str) -> str:
    """'whatsapp:+52 442-100-0000' → '+524421000000'. Sin dígitos → ''."""
    digits = re.sub(r"\D", "", raw or "")
    return f"+{digits}" if digits else ""


def _contacts_path() -> Path:
    return Path(os.getenv("HV_WA_CONTACTS", "data/wa_contacts.json"))


def _intake_dir() -> Path:
    return Path(os.getenv("HV_INTAKE_DIR", "data/intake"))


def _iter_intakes():
    base = _intake_dir()
    if not base.exists():
        return
    for p in sorted(base.glob("*.json")):
        try:
            yield p, json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue


def lookup_beta_by_phone(phone: str) -> Optional[str]:
    """Registry primero, luego intakes (identity.whatsapp). None si no hay match."""
    phone = normalize_phone(phone)
    if not phone:
        return None
    try:
        reg = json.loads(_contacts_path().read_text(encoding="utf-8"))
        for k, v in reg.items():
            if normalize_phone(k) == phone and v:
                return str(v)
    except Exception:
        pass
    for path, intake in _iter_intakes() or []:
        ident = (intake.get("identity") or {})
        if normalize_phone(ident.get("whatsapp", "")) == phone:
            beta = (intake.get("meta") or {}).get("beta_id")
            return str(beta) if beta else path.stem.replace("_intake", "")
    return None


def beta_id_for_phone(phone: str) -> str:
    """beta_id conocido o bootstrap determinístico 'wa-<dígitos>' para leads."""
    known = lookup_beta_by_phone(phone)
    if known:
        return known
    return f"wa-{normalize_phone(phone).lstrip('+')}"


def phone_for_beta(beta_id: str) -> Optional[str]:
    """Inverso (para el sender proactivo): registry, luego intakes."""
    try:
        reg = json.loads(_contacts_path().read_text(encoding="utf-8"))
        for k, v in reg.items():
            if str(v) == beta_id:
                return normalize_phone(k)
    except Exception:
        pass
    for path, intake in _iter_intakes() or []:
        beta = (intake.get("meta") or {}).get("beta_id") or path.stem.replace("_intake", "")
        if str(beta) == beta_id:
            p = normalize_phone((intake.get("identity") or {}).get("whatsapp", ""))
            if p:
                return p
    # bootstrap ids llevan el número embebido
    if beta_id.startswith("wa-") and beta_id[3:].isdigit():
        return f"+{beta_id[3:]}"
    return None


# ------------------------------------------------------------------
# Firma de Twilio (X-Twilio-Signature)
# ------------------------------------------------------------------

def validate_twilio_signature(url: str, params: Dict[str, str], signature: str,
                              auth_token: Optional[str] = None) -> bool:
    """Esquema oficial: base64(HMAC-SHA1(url + Σ key+value ordenados, auth_token))."""
    token = auth_token or os.getenv("TWILIO_AUTH_TOKEN", "")
    if not token or not signature:
        return False
    payload = url + "".join(k + params[k] for k in sorted(params))
    digest = hmac.new(token.encode(), payload.encode("utf-8"), hashlib.sha1).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)


# ------------------------------------------------------------------
# Envío (proactivo / fuera del ciclo request-reply)
# ------------------------------------------------------------------

def send_whatsapp(to_phone: str, body: str = "", *,
                  content_sid: Optional[str] = None,
                  content_variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Envía por la Messages API de Twilio. Texto libre solo entra en ventana de 24h;
    para mensajes iniciados por el bot usa content_sid (template aprobado por Meta).
    Lanza ChannelSendError si no hay creds o Twilio responde error — el caller
    decide si la acción queda pending (sí: ver execute_pending_action).
    """
    import requests  # lazy: file-mode/tests no lo requieren

    sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    token = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_ = os.getenv("TWILIO_WHATSAPP_FROM", "")
    if not (sid and token and from_):
        raise ChannelSendError("Twilio no configurado (TWILIO_ACCOUNT_SID/AUTH_TOKEN/WHATSAPP_FROM)")

    to = normalize_phone(to_phone)
    if not to:
        raise ChannelSendError(f"Teléfono destino inválido: {to_phone!r}")

    data: Dict[str, str] = {
        "From": from_ if from_.startswith("whatsapp:") else f"whatsapp:{from_}",
        "To": f"whatsapp:{to}",
    }
    if content_sid:
        data["ContentSid"] = content_sid
        if content_variables:
            data["ContentVariables"] = json.dumps(content_variables, ensure_ascii=False)
    else:
        data["Body"] = (body or "")[:MAX_BODY_CHARS]

    resp = requests.post(
        f"{TWILIO_API}/Accounts/{sid}/Messages.json",
        data=data, auth=(sid, token), timeout=30,
    )
    if resp.status_code // 100 != 2:
        raise ChannelSendError(f"Twilio {resp.status_code}: {resp.text[:300]}")
    out = resp.json()
    return {"sid": out.get("sid"), "status": out.get("status"), "to": to}


# ------------------------------------------------------------------
# Respuesta inline al webhook (TwiML)
# ------------------------------------------------------------------

def twiml_reply(text: str) -> str:
    body = escape((text or "").strip()[:MAX_BODY_CHARS])
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{body}</Message></Response>'


def twiml_empty() -> str:
    return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
