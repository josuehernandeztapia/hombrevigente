"""Dispara newsletter-approval en GitHub vía repository_dispatch."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def dispatch_pulso_approval(
    issue_path: str,
    action: str,
    corrections: str | None = None,
) -> dict:
    token = os.environ.get("GITHUB_APPROVAL_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "josuehernandeztapia/hombrevigente")
    if not token:
        return {"ok": False, "error": "GITHUB_APPROVAL_TOKEN no configurado en Fly"}

    payload = {
        "event_type": "pulso-approval",
        "client_payload": {
            "issue_path": issue_path,
            "action": action,
            "corrections": corrections or "",
        },
    }
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/dispatches",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "hv-newsletter-approval",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"ok": True, "status": resp.status}
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return {"ok": False, "error": f"HTTP {e.code}: {body}"}