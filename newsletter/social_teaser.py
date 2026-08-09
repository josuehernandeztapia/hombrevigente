#!/usr/bin/env python3
"""
Auto-encola un teaser lane:auto al aprobar un Pulso.

Puente Pulso → redes SIN pasos extra del owner: el anuncio del número (sin
claims de salud — solo "ya salió") entra al carril AUTO y social-auto lo
publica en su siguiente corrida. El paquete social con ciencia (social/NNN/)
sigue siendo carril GATED. El claim-guard de publish.py aplica igual al
teaser: si un subject algún día trae lenguaje de claim, se frena solo.

Uso: python newsletter/social_teaser.py newsletter/issues/2026-07-009.md
Idempotente: si el teaser del número ya existe, no hace nada.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

QUEUE_DIR = Path(__file__).resolve().parent / "social" / "queue"


def build_teaser(issue_path: Path) -> Path | None:
    raw = issue_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", raw, re.S)
    if not m:
        print(f"[teaser] sin frontmatter en {issue_path} — omitido")
        return None
    meta = yaml.safe_load(m.group(1)) or {}
    numero = str(meta.get("numero", "")).strip()
    subject = str(meta.get("subject", "")).strip()
    if not numero or not subject:
        print("[teaser] frontmatter sin numero/subject — omitido")
        return None

    # "Pulso Vigente Nº008 — Título" → "Título"
    title = re.sub(r"^Pulso Vigente\s+N[º°]\s*\d+\s*[—-]\s*", "", subject).strip()
    today = datetime.now(timezone.utc).date().isoformat()
    dest = QUEUE_DIR / f"{today}-pulso-{numero}-teaser.md"
    if dest.exists():
        print(f"[teaser] ya existe {dest.name} — idempotente, nada que hacer")
        return dest

    body = f"""---
lane: auto
platforms: [instagram, facebook, x]
date: {today}
image_url: ""
---
📬 Ya salió Pulso Vigente Nº{numero}

{title}

Ciencia de longevidad verificada — papers reales, cero humo — cada semana en tu correo.

#HombreVigente #longevidad #PulsoVigente
"""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, encoding="utf-8")
    print(f"[teaser] encolado {dest.name} (lane:auto — sale en la próxima corrida social)")
    return dest


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: social_teaser.py <ruta-issue.md>")
    build_teaser(Path(sys.argv[1]))
