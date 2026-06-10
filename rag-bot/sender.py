"""
sender.py (G2) — Real proactive sender with provider abstraction.

Replaces the previous stub-only delivery. Design goals:
- Fail-safe by default: with no feature flag / no credentials it behaves like the
  old stub (LogSender: no real delivery, status="skipped"), so existing flows and
  tests keep passing without network or secrets.
- Pluggable: WhatsAppCloudSender talks to Meta WhatsApp Cloud API (Graph), env-driven.
- Auditable: returns a SendResult with cost/receipt that the caller writes to
  hv_agent_traces (log_trace) and uses to set the pending action's final_status.

Activation:
    HV_PROACTIVE_SENDER=on            -> enables real delivery (else LogSender)
    HV_WHATSAPP_TOKEN=...             -> Meta permanent/system token
    HV_WHATSAPP_PHONE_ID=...          -> WhatsApp Business phone number id
    HV_WHATSAPP_API_VERSION=v21.0     -> Graph API version (default v21.0)

Recipient resolution order: action["to"] -> action["metadata"]["phone"] ->
state_persistence.load_state(beta_id) phone-like field. If none, status="failed".
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class SendResult:
    status: str                       # sent | failed | skipped
    provider: str
    receipt_id: Optional[str] = None
    cost_usd: float = 0.0
    model: Optional[str] = None       # not an LLM, kept for trace schema parity
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


# WhatsApp Business "marketing/utility" conversation pricing is per-country; we keep a
# conservative default that can be overridden without code changes. Used only for the
# cost factor of the health score + cost reporting, not for billing.
_DEFAULT_MSG_COST_USD = float(os.getenv("HV_WHATSAPP_MSG_COST_USD", "0.005"))


def _resolve_recipient(action: Dict[str, Any]) -> Optional[str]:
    to = action.get("to") or (action.get("metadata") or {}).get("phone")
    if to:
        return str(to)
    beta_id = action.get("beta_id")
    if not beta_id:
        return None
    try:
        from state_persistence import load_state  # lazy: avoid import cycle / hard dep
        st = load_state(beta_id) or {}
        for k in ("phone", "telefono", "whatsapp", "celular", "msisdn"):
            if st.get(k):
                return str(st[k])
    except Exception:
        pass
    return None


class LogSender:
    """Default provider: no real delivery. Mirrors the old stub behavior (safe)."""

    name = "log"

    def send(self, action: Dict[str, Any]) -> SendResult:
        to = _resolve_recipient(action) or "<unresolved>"
        print(
            "[sender:log] (no real delivery) beta=%s to=%s type=%s msg=%s"
            % (
                action.get("beta_id"),
                to,
                action.get("action_type"),
                (action.get("suggested_message") or "")[:60],
            )
        )
        return SendResult(status="skipped", provider=self.name, cost_usd=0.0,
                          meta={"reason": "sender_disabled_or_no_creds", "to": to})


class WhatsAppCloudSender:
    """Meta WhatsApp Cloud API provider (free-text within the 24h customer-care window)."""

    name = "whatsapp_cloud"

    def __init__(self) -> None:
        self.token = os.getenv("HV_WHATSAPP_TOKEN", "")
        self.phone_id = os.getenv("HV_WHATSAPP_PHONE_ID", "")
        self.api_version = os.getenv("HV_WHATSAPP_API_VERSION", "v21.0")

    def _endpoint(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}/{self.phone_id}/messages"

    def send(self, action: Dict[str, Any]) -> SendResult:
        to = _resolve_recipient(action)
        if not to:
            return SendResult(status="failed", provider=self.name,
                              error="no_recipient", meta={})
        body = action.get("suggested_message") or ""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }
        try:
            import requests  # lazy import; optional dependency
        except Exception as e:  # pragma: no cover - environment dependent
            return SendResult(status="failed", provider=self.name,
                              error=f"requests_unavailable: {e}")
        try:
            resp = requests.post(
                self._endpoint(),
                headers={"Authorization": f"Bearer {self.token}",
                         "Content-Type": "application/json"},
                json=payload,
                timeout=float(os.getenv("HV_WHATSAPP_TIMEOUT", "15")),
            )
            if resp.status_code >= 400:
                return SendResult(status="failed", provider=self.name,
                                  error=f"http_{resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            receipt = None
            msgs = data.get("messages") or []
            if msgs and isinstance(msgs, list):
                receipt = msgs[0].get("id")
            return SendResult(status="sent", provider=self.name, receipt_id=receipt,
                              cost_usd=_DEFAULT_MSG_COST_USD, meta={"to": to})
        except Exception as e:
            return SendResult(status="failed", provider=self.name, error=str(e))


def sender_enabled() -> bool:
    return os.getenv("HV_PROACTIVE_SENDER", "").strip().lower() in ("on", "1", "true", "yes")


def get_sender():
    """
    Returns the active provider. Real delivery requires BOTH the feature flag ON and
    WhatsApp credentials present; otherwise falls back to the safe LogSender.
    """
    if sender_enabled() and os.getenv("HV_WHATSAPP_TOKEN") and os.getenv("HV_WHATSAPP_PHONE_ID"):
        return WhatsAppCloudSender()
    return LogSender()


def send_action(action: Dict[str, Any]) -> SendResult:
    """Convenience: resolve provider + send a single pending action."""
    return get_sender().send(action)
