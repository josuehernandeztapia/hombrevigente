"""Verificación de tokens de aprobación Pulso (misma lógica que newsletter/approval_token.py)."""
from __future__ import annotations

import hashlib
import hmac
import os
import time


def verify_token(issue_path: str, action: str, token: str) -> bool:
    secret = os.environ.get("NEWSLETTER_APPROVAL_SECRET", "").strip()
    if not secret:
        return False
    try:
        exp_s, sig = token.split(".", 1)
        exp = int(exp_s)
    except ValueError:
        return False
    if exp < int(time.time()):
        return False
    expected = hmac.new(
        secret.encode(),
        f"{issue_path}|{action}|{exp}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, sig)