"""Envía un número de Pulso Vigente vía Resend Broadcasts (a la Audience, con unsubscribe).

Uso:  python send.py newsletter/issues/2026-06-001.md
Env requeridos:
  RESEND_API_KEY          (secret)
  RESEND_AUDIENCE_PLUS    (id de audience Plus)
  RESEND_AUDIENCE_FREE    (id de audience Free, opcional)
  NEWSLETTER_FROM         (ej. "Pulso Vigente <pulso@updates.hombrevigente.com>")
  DRY_RUN=1               (opcional: crea el broadcast pero NO lo envía)
  PULSO_MODE=shadow       (ensayo: no llama API; solo valida render)
"""
import os
import sys
from pathlib import Path
import requests
from render import render

API = "https://api.resend.com"


def _audience_id(audiencia: str) -> str:
    key = "RESEND_AUDIENCE_FREE" if audiencia == "free" else "RESEND_AUDIENCE_PLUS"
    aid = os.environ.get(key)
    if not aid:
        sys.exit(f"Falta env {key}")
    return aid


def main(md_path: str):
    issue = render(Path(md_path))

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
    print("Enviado ✓")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python send.py <ruta_al_numero.md>")
    main(sys.argv[1])
