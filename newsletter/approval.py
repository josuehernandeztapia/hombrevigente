"""Pulso Vigente — aprobación humana por correo + GitHub Issue.

Flujo:
  1. send-preview → Resend envía borrador al inbox del editor
  2. create-issue → Issue GitHub (responder por email a la notif de GH funciona)
  3. Comentario OK → approve + merge PR + envío Plus
  4. Comentario con texto → revise (IA) + nuevo preview por correo

Uso:
  python newsletter/approval.py send-preview newsletter/issues/2026-06-002.md
  python newsletter/approval.py create-issue newsletter/issues/2026-06-002.md --pr 42
  python newsletter/approval.py is-approved newsletter/issues/2026-06-002.md
  python newsletter/approval.py mark-approved newsletter/issues/2026-06-002.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests
import yaml

HERE = Path(__file__).parent
REPO = HERE.parent
API = "https://api.resend.com/emails"
STATE_DIR = HERE / "approvals"


def parse_issue(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError(f"{path} sin frontmatter")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def write_issue(path: Path, meta: dict, body: str) -> None:
    block = yaml.dump(meta, allow_unicode=True, default_flow_style=False).strip()
    path.write_text(f"---\n{block}\n---\n\n{body.strip()}\n", encoding="utf-8")


def is_approved(path: Path) -> bool:
    meta, _ = parse_issue(path)
    return meta.get("approved") is True


def mark_approved(path: Path) -> None:
    meta, body = parse_issue(path)
    meta["approved"] = True
    meta["approval_status"] = "approved"
    write_issue(path, meta, body)


def numero_from_path(path: Path) -> str:
    meta, _ = parse_issue(path)
    if meta.get("numero"):
        return str(meta["numero"]).zfill(3)
    m = re.search(r"-(\d+)\.md$", path.name)
    return m.group(1) if m else path.stem


def send_preview(path: Path) -> None:
    from render import render

    if os.environ.get("PULSO_MODE") == "shadow":
        print("PULSO_MODE=shadow — preview email omitido")
        return

    api_key = os.environ.get("RESEND_API_KEY")
    sender = os.environ.get("NEWSLETTER_FROM")
    to = os.environ.get("NEWSLETTER_APPROVAL_TO", "").strip()
    if not api_key or not sender:
        sys.exit("Falta RESEND_API_KEY o NEWSLETTER_FROM")
    if not to:
        sys.exit("Falta NEWSLETTER_APPROVAL_TO (tu inbox para borradores)")

    issue = render(path)
    meta, _ = parse_issue(path)
    numero = numero_from_path(path)
    rev = meta.get("approval_revision", 0)

    instructions = f"""
<div style="font-family:sans-serif;max-width:640px;margin:0 auto 24px;padding:16px;background:#1a1a1a;color:#e8e8e8;border-radius:8px;">
  <p><strong>BORRADOR Pulso Vigente Nº{numero}</strong> (revisión {rev}) — <em>no enviado a suscriptores</em></p>
  <p><strong>Para APROBAR y enviar a Plus:</strong></p>
  <ul>
    <li>Abre el <strong>issue de GitHub</strong> #{meta.get('approval_github_issue', '')} (te llega notificación por correo)</li>
    <li><strong>Responde a ese hilo</strong> (por web o respondiendo al email de GitHub) escribiendo solo: <code>OK</code></li>
  </ul>
  <p><strong>Para PEDIR CAMBIOS:</strong> responde al issue con tus notas (tono, bloques, titular, etc.). Recibirás un nuevo borrador por correo.</p>
  <p style="font-size:12px;color:#888;">Merge a main y envío solo ocurre tras OK explícito.</p>
</div>
"""

    html = instructions + issue["html"]
    subject = f"[BORRADOR Pulso Nº{numero}] {issue['subject']} — responde OK para enviar"

    r = requests.post(
        API,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "from": sender,
            "to": [to],
            "subject": subject,
            "html": html,
            "reply_to": os.environ.get("NEWSLETTER_APPROVAL_REPLY_TO", to),
        },
        timeout=30,
    )
    r.raise_for_status()
    print(f"Preview enviado a {to} · {subject}")


def save_state(path: Path, data: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    n = numero_from_path(path)
    (STATE_DIR / f"{n}.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def create_github_issue(path: Path, pr_number: int | None = None) -> int:
    meta, body = parse_issue(path)
    numero = numero_from_path(path)
    repo = os.environ.get("GITHUB_REPOSITORY", "josuehernandeztapia/hombrevigente")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("WARN: sin GITHUB_TOKEN — issue de aprobación omitido", file=sys.stderr)
        return 0

    pr_line = f"\n- PR borrador: #{pr_number}" if pr_number else ""
    issue_body = f"""## Aprobar Pulso Vigente Nº{numero}

**Responde a este hilo por correo o comenta aquí:**

- `OK` → aprueba y envía a audiencia Plus
- Cualquier otro texto → correcciones (nueva versión por email)

Archivo: `{path.as_posix()}`
{pr_line}

---
<details><summary>Vista previa (markdown)</summary>

{body[:6000]}

</details>
"""

    import json as _json

    payload = {
        "title": f"Aprobar Pulso Nº{numero}",
        "body": issue_body,
        "labels": ["pulso-approval", "newsletter"],
    }
    r = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    issue_num = r.json()["number"]
    issue_url = r.json()["html_url"]

    meta["approved"] = False
    meta["approval_status"] = "pending"
    meta["approval_github_issue"] = issue_num
    if pr_number:
        meta["approval_pr"] = pr_number
    write_issue(path, meta, body)
    save_state(path, {
        "numero": numero,
        "issue_path": path.relative_to(REPO).as_posix(),
        "github_issue": issue_num,
        "pr": pr_number,
        "status": "pending",
    })
    print(f"Issue aprobación #{issue_num} · {issue_url}")
    return issue_num


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_send = sub.add_parser("send-preview")
    p_send.add_argument("issue", type=Path)

    p_ci = sub.add_parser("create-issue")
    p_ci.add_argument("issue", type=Path)
    p_ci.add_argument("--pr", type=int, default=0)

    p_ok = sub.add_parser("mark-approved")
    p_ok.add_argument("issue", type=Path)

    p_chk = sub.add_parser("is-approved")
    p_chk.add_argument("issue", type=Path)

    args = ap.parse_args()
    path = args.issue if args.issue.is_absolute() else REPO / args.issue

    if args.cmd == "send-preview":
        send_preview(path)
    elif args.cmd == "create-issue":
        create_github_issue(path, args.pr or None)
    elif args.cmd == "mark-approved":
        mark_approved(path)
    elif args.cmd == "is-approved":
        print("yes" if is_approved(path) else "no")
        sys.exit(0 if is_approved(path) else 1)


if __name__ == "__main__":
    main()