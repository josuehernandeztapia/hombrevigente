"""Envía un número de Pulso Vigente vía Resend Broadcasts (a la Audience, con unsubscribe).

Uso:  python send.py newsletter/issues/2026-06-001.md
Env requeridos:
  RESEND_API_KEY          (secret)
  RESEND_AUDIENCE_PLUS    (id de audience Plus)
  RESEND_AUDIENCE_FREE    (id de audience Free, opcional)
  NEWSLETTER_FROM         (ej. "Pulso Vigente <pulso@updates.hombrevigente.com>")
  DRY_RUN=1               (opcional: crea el broadcast pero NO lo envía)
  PULSO_MODE=shadow       (ensayo: no llama API; solo valida render)
  FORCE_RESEND=1          (opcional: reenvía aunque ya conste en approvals/*.json)
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import requests
from render import render

API = "https://api.resend.com"
HERE = Path(__file__).parent
STATE_DIR = HERE / "approvals"


def _audience_id(audiencia: str) -> str:
    key = "RESEND_AUDIENCE_FREE" if audiencia == "free" else "RESEND_AUDIENCE_PLUS"
    aid = os.environ.get(key)
    if not aid:
        sys.exit(f"Falta env {key}")
    return aid


def _state_path(path: Path) -> Path:
    from approval import numero_from_path

    return STATE_DIR / f"{numero_from_path(path)}.json"


def _already_sent(path: Path) -> str | None:
    sp = _state_path(path)
    if not sp.exists():
        return None
    sent_at = json.loads(sp.read_text(encoding="utf-8")).get("sent_at")
    return sent_at if sent_at else None


def _record_sent(path: Path, broadcast_id: str) -> None:
    from approval import numero_from_path

    STATE_DIR.mkdir(exist_ok=True)
    sp = _state_path(path)
    state = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    state.update({
        "numero": numero_from_path(path),
        "issue_path": path.relative_to(HERE.parent).as_posix()
        if path.is_relative_to(HERE.parent)
        else path.as_posix(),
        "sent_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "broadcast_id": broadcast_id,
    })
    sp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def main(md_path: str):
    path = Path(md_path)
    if not path.is_absolute():
        path = HERE.parent / path

    sent_at = _already_sent(path)
    if sent_at and os.environ.get("FORCE_RESEND") != "1":
        print(f"Ya enviado ({sent_at}) — omitido. Usa FORCE_RESEND=1 para repetir.")
        return

    issue = render(path)

    if os.environ.get("FORCE_SEND") != "1":
        from approval import is_approved
        if not is_approved(path):
            print(f"No aprobado ({path.name}) — envío omitido. Comenta OK en el issue de aprobación.")
            return

    if os.environ.get("PULSO_MODE") == "shadow":
        print("PULSO_MODE=shadow — render OK, sin llamar Resend.")
        print("Subject:", issue["subject"])
        return

    api_key = os.environ.get("RESEND_API_KEY")
    sender = os.environ.get("NEWSLETTER_FROM")
    if not api_key or not sender:
        sys.exit("Falta RESEND_API_KEY o NEWSLETTER_FROM")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # 1) crear broadcast
    r = requests.post(f"{API}/broadcasts", headers=headers, json={
        "audience_id": _audience_id(issue["audiencia"]),
        "from": sender,
        "subject": issue["subject"],
        "html": issue["html"],
    }, timeout=30)
    r.raise_for_status()
    bid = r.json()["id"]
    print("Broadcast creado:", bid, "·", issue["subject"])

    # 2) enviar (a menos que DRY_RUN)
    if os.environ.get("DRY_RUN") == "1":
        print("DRY_RUN=1 — broadcast creado pero NO enviado.")
        return
    s = requests.post(f"{API}/broadcasts/{bid}/send", headers=headers, timeout=30)
    s.raise_for_status()
    _record_sent(path, bid)
    print("Enviado ✓")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python send.py <ruta_al_numero.md>")
    main(sys.argv[1])
