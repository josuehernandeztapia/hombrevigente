"""Pulso Vigente — hero IA por número.

Genera una imagen editorial de marca (negro premium + acento bronce, abstracta,
SIN texto, SIN personas, SIN imaginería médica) a partir del tema del número.
Prompts derivados de prompt_from_issue.py (TLDR + Accionable + LLM opcional).
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

from prompt_from_issue import visual_context, visual_prompts_for_issue, write_prompt_artifact

HERE = Path(__file__).parent


def _resolve_issue(md_path: str) -> Path:
    issue = Path(md_path)
    if issue.is_absolute():
        return issue
    for candidate in (HERE.parent / issue, HERE / issue):
        if candidate.exists():
            return candidate
    return HERE.parent / issue


def main(md_path: str):
    issue = _resolve_issue(md_path)

    prompts = visual_prompts_for_issue(issue)
    artifact = write_prompt_artifact(issue, prompts)
    prompt = prompts["image_prompt"]
    ctx = visual_context(issue)
    theme = prompts["theme"]

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY no configurado — no se genera imagen.")
        print(f"Prompt artifact: {artifact}")
        print("Prompt que se usaría:\n" + prompt)
        print(f"Unsplash sugerido: {prompts['unsplash_query']}")
        return

    numero = ctx["numero"] or re.sub(r"\D", "", issue.stem) or issue.stem
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
    print(f"Prompt artifact: {artifact}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python newsletter/image.py <ruta_al_numero.md>")
    main(sys.argv[1])