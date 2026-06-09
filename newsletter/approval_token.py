"""Tokens HMAC para links de aprobación Pulso (un clic en email)."""
from __future__ import annotations

import hmac
import hashlib
import os
import time
from urllib.parse import quote


def _secret() -> str:
    s = os.environ.get("NEWSLETTER_APPROVAL_SECRET", "").strip()
    if not s:
        raise ValueError("NEWSLETTER_APPROVAL_SECRET no configurado")
    return s


def make_token(issue_path: str, action: str, ttl_hours: int = 96) -> str:
    exp = int(time.time()) + ttl_hours * 3600
    sig = hmac.new(
        _secret().encode(),
        f"{issue_path}|{action}|{exp}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{exp}.{sig}"


def verify_token(issue_path: str, action: str, token: str) -> bool:
    try:
        exp_s, sig = token.split(".", 1)
        exp = int(exp_s)
    except ValueError:
        return False
    if exp < int(time.time()):
        return False
    expected = hmac.new(
        _secret().encode(),
        f"{issue_path}|{action}|{exp}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, sig)


def approval_url(issue_path: str, action: str = "approve") -> str:
    base = os.environ.get("NEWSLETTER_APPROVAL_BASE_URL", "https://hv-rag-api.fly.dev").rstrip("/")
    token = make_token(issue_path, action)
    return f"{base}/newsletter/approve?issue={quote(issue_path)}&action={action}&token={token}"