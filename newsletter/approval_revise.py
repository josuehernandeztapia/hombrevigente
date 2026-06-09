"""Aplica correcciones del editor al borrador Pulso (LLM) y reenvía preview.

Uso:
  python newsletter/approval_revise.py newsletter/issues/2026-06-002.md "más ApoB, menos hype"
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import requests
import yaml

HERE = Path(__file__).parent
REPO = HERE.parent


def parse_issue(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, m.group(2) if m else raw


def write_issue(path: Path, meta: dict, body: str) -> None:
    block = yaml.dump(meta, allow_unicode=True, default_flow_style=False).strip()
    path.write_text(f"---\n{block}\n---\n\n{body.strip()}\n", encoding="utf-8")


def revise(path: Path, corrections: str, api_key: str) -> str:
    meta, body = parse_issue(path)
    editorial = (HERE / "EDITORIAL.md").read_text(encoding="utf-8")[:2500]

    system = (
        "Editor Pulso Vigente. Aplicas correcciones del humano al borrador markdown. "
        "Mantén estructura, PMIDs existentes, tono HV (optimización, sin cura/diagnóstico). "
        "No inventes fuentes nuevas. Devuelve SOLO el markdown completo con frontmatter ---."
    )
    user = f"""CORRECCIONES DEL EDITOR:
{corrections}

REGLAS:
{editorial[:1200]}

BORRADOR ACTUAL:
---
{yaml.dump(meta, allow_unicode=True)}---
{body}
"""

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": os.environ.get("PULSO_COMPOSE_MODEL", "gpt-4o-mini"),
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=120,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"].strip()
    content = re.sub(r"^```(?:markdown)?\n?", "", content)
    content = re.sub(r"\n?```$", "", content)
    return content.strip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("issue", type=Path)
    ap.add_argument("corrections", type=str)
    args = ap.parse_args()

    path = args.issue if args.issue.is_absolute() else REPO / args.issue
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.exit("Falta OPENAI_API_KEY")

    meta, _ = parse_issue(path)
    meta["approval_revision"] = int(meta.get("approval_revision", 0)) + 1
    meta["approved"] = False
    meta["approval_status"] = "revising"

    new_md = revise(path, args.corrections, api_key)
    # re-parse to preserve updated meta fields we set
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", new_md, re.DOTALL)
    if m:
        new_meta = yaml.safe_load(m.group(1)) or {}
        new_meta["approval_revision"] = meta["approval_revision"]
        new_meta["approved"] = False
        new_meta["approval_status"] = "revising"
        new_meta["approval_github_issue"] = meta.get("approval_github_issue")
        new_meta["approval_pr"] = meta.get("approval_pr")
        write_issue(path, new_meta, m.group(2))
    else:
        path.write_text(new_md, encoding="utf-8")

    print(f"Revisión {meta['approval_revision']} aplicada · {path.name}")

    # re-send preview
    from approval import send_preview

    send_preview(path)


if __name__ == "__main__":
    main()