"""Pulso Vigente — hero IA por número.

Genera una imagen editorial de marca (negro premium + acento bronce, abstracta,
SIN texto, SIN personas, SIN imaginería médica) a partir del tema del número.
API: OpenAI Images (gpt-image-1). Degrada con gracia si no hay OPENAI_API_KEY
(imprime el prompt y termina, sin romper el flujo).

Uso: python newsletter/image.py newsletter/issues/2026-06-001.md
Env: OPENAI_API_KEY (secret)
"""
from __future__ import annotations
import base64
import os
import re
import sys
from pathlib import Path
import requests
import yaml

HERE = Path(__file__).parent

# Prompt de marca — guardrails de compliance incrustados.
BRAND = (
    "Editorial hero image for a premium men's longevity brand. "
    "Near-black background (#0B0B0C), subtle warm bronze/gold accent lighting, "
    "abstract and conceptual representation of: {theme}. "
    "Minimal, sophisticated, cinematic, high-end magazine quality, masculine, "
    "scientific-but-warm mood. "
    "STRICT: no text, no words, no logos, no people, no faces, no medical imagery, "
    "no before/after, no pills shown as treatment, no clinical claims. "
    "Pure abstract/editorial art only."
)


def theme_from_issue(md_path: Path) -> str:
    raw = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", raw, re.DOTALL)
    meta = yaml.safe_load(m.group(1)) if m else {}
    subj = meta.get("subject", "longevity science")
    # quita "Pulso Vigente Nº00X —"
    return subj.split("—")[-1].strip() or "longevity and optimization"


def main(md_path: str):
    issue = Path(md_path)
    theme = theme_from_issue(issue)
    prompt = BRAND.format(theme=theme)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY no configurado — no se genera imagen.")
        print("Prompt que se usaría:\n" + prompt)
        return

    numero = re.sub(r"\D", "", issue.stem) or issue.stem
    out_dir = HERE / "assets"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{numero}.png"

    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "gpt-image-1", "prompt": prompt, "size": "1536x1024", "n": 1},
        timeout=120,
    )
    r.raise_for_status()
    b64 = r.json()["data"][0]["b64_json"]
    out.write_bytes(base64.b64decode(b64))
    print(f"Hero escrito en {out} · tema: {theme}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python newsletter/image.py <ruta_al_numero.md>")
    main(sys.argv[1])
