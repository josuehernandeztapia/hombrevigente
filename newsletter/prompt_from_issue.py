"""Deriva prompts visuales (hero IA + Unsplash + slides) desde un issue Pulso.

Lee subject, TLDR y bloque Accionable; opcionalmente refina con LLM.
Salida consumida por image.py y publish_social.py.

Uso:
  python newsletter/prompt_from_issue.py newsletter/issues/2026-06-002.md
  python newsletter/prompt_from_issue.py newsletter/issues/2026-06-002.md --write
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests
import yaml

HERE = Path(__file__).parent

BRAND_TEMPLATE = (
    "Editorial hero image for a premium men's longevity brand. "
    "Near-black background (#0B0B0C), subtle warm bronze/gold accent lighting, "
    "abstract and conceptual representation of: {theme}. "
    "Minimal, sophisticated, cinematic, high-end magazine quality, masculine, "
    "scientific-but-warm mood. "
    "STRICT: no text, no words, no logos, no people, no faces, no medical imagery, "
    "no before/after, no pills shown as treatment, no clinical claims. "
    "Pure abstract/editorial art only."
)


def parse_issue(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError(f"{path} sin frontmatter YAML")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def _block_by_emoji(body: str, emoji: str) -> dict[str, str]:
    pat = rf"##\s*{re.escape(emoji)}\s*([^—\n]+)(?:\s*—\s*([^\n]+))?\n(.*?)(?=\n##\s|\n---|\Z)"
    m = re.search(pat, body, re.DOTALL)
    if not m:
        return {"headline": "", "title": "", "text": "", "lente": ""}
    category = m.group(1).strip()
    title = (m.group(2) or category).strip()
    chunk = m.group(3).strip()
    first = ""
    for line in chunk.splitlines():
        ls = line.strip()
        if ls and not ls.startswith(">") and not ls.startswith("|") and not ls.startswith("*"):
            first = ls
            break
    lente = ""
    lm = re.search(r"Lente Vigente:\*\*\s*(.+)", chunk)
    if lm:
        lente = lm.group(1).strip()
    return {"headline": title, "title": title, "text": first, "lente": lente}


def visual_context(path: Path) -> dict[str, Any]:
    meta, body = parse_issue(path)
    subject = meta.get("subject", "Pulso Vigente")
    theme_line = subject.split("—")[-1].strip() if "—" in subject else subject
    tldr = ""
    mt = re.search(r"\*\*TLDR:\*\*\s*(.+)", body)
    if mt:
        tldr = mt.group(1).strip()
    accionable = _block_by_emoji(body, "🟢")
    slides = []
    for emoji in ("🟢", "🔬", "🤖"):
        b = _block_by_emoji(body, emoji)
        if b["title"]:
            slides.append(b["title"])
    numero = str(meta.get("numero", "")).zfill(3) if meta.get("numero") else re.sub(r"\D", "", path.stem)
    return {
        "numero": numero,
        "subject": subject,
        "theme_line": theme_line,
        "tldr": tldr,
        "accionable_title": accionable["title"],
        "accionable_text": accionable["text"],
        "accionable_lente": accionable["lente"],
        "slide_headlines": slides[:3],
    }


def _hero_theme(ctx: dict[str, Any]) -> str:
    """Tema del hero anclado al bloque Accionable (🟢), no al subject ni metáforas libres."""
    title = (ctx.get("accionable_title") or "").strip()
    if title:
        return title
    return (ctx.get("theme_line") or "longevity and cellular optimization").strip()


def _fallback_prompts(ctx: dict[str, Any]) -> dict[str, Any]:
    theme = _hero_theme(ctx)
    words = re.findall(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]{4,}", f"{ctx['accionable_title']} {ctx['tldr']}")
    en_hint = " ".join(words[:6]).lower()
    unsplash = f"longevity {en_hint} abstract science".strip()[:80]
    slide_themes = [
        f"abstract editorial: {h}" for h in ctx["slide_headlines"]
    ] or [f"abstract editorial: {theme}"]
    image_prompt = BRAND_TEMPLATE.format(theme=theme)
    return {
        "theme": theme,
        "image_prompt": image_prompt,
        "unsplash_query": unsplash,
        "slide_themes": slide_themes,
        "source": "fallback",
    }


def _llm_prompts(ctx: dict[str, Any], api_key: str) -> dict[str, Any]:
    hero_theme = _hero_theme(ctx)
    system = (
        "You create visual briefs for a premium men's longevity brand (abstract editorial art). "
        "Output ONLY valid JSON with keys: unsplash_query, slide_themes. "
        "The hero image theme is FIXED from accionable_title — do NOT invent a separate theme. "
        "unsplash_query: 3-6 English keywords for stock photo search, aligned with accionable_title. "
        "slide_themes: array of 1-3 short English visual concepts for carousel slides. "
        "Never mention cure, treatment, diagnosis, or guaranteed outcomes."
    )
    user = json.dumps(
        {
            "subject": ctx["subject"],
            "tldr": ctx["tldr"],
            "accionable_title": ctx["accionable_title"],
            "accionable_summary": ctx["accionable_text"],
            "slide_headlines": ctx["slide_headlines"],
        },
        ensure_ascii=False,
    )
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": os.environ.get("PULSO_PROMPT_MODEL", "gpt-4o-mini"),
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=60,
    )
    r.raise_for_status()
    data = json.loads(r.json()["choices"][0]["message"]["content"])
    theme = hero_theme
    unsplash = str(data.get("unsplash_query") or "").strip()
    slide_themes = data.get("slide_themes") or []
    if not isinstance(slide_themes, list):
        slide_themes = [str(slide_themes)]
    slide_themes = [str(s).strip() for s in slide_themes if str(s).strip()][:3]
    if not unsplash:
        unsplash = _fallback_prompts(ctx)["unsplash_query"]
    if not slide_themes:
        slide_themes = _fallback_prompts(ctx)["slide_themes"]
    return {
        "theme": theme,
        "image_prompt": BRAND_TEMPLATE.format(theme=theme),
        "unsplash_query": unsplash,
        "slide_themes": slide_themes,
        "source": "llm",
    }


def visual_prompts_for_issue(
    path: Path,
    *,
    use_llm: bool | None = None,
) -> dict[str, Any]:
    ctx = visual_context(path)
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if use_llm is None:
        use_llm = bool(api_key) and os.environ.get("PULSO_PROMPT_FALLBACK_ONLY") != "1"
    if use_llm and api_key:
        try:
            out = _llm_prompts(ctx, api_key)
        except Exception as exc:
            print(f"WARN: LLM prompts falló ({exc}) — fallback", file=sys.stderr)
            out = _fallback_prompts(ctx)
    else:
        out = _fallback_prompts(ctx)
    out["context"] = ctx
    out["issue_path"] = path.as_posix()
    return out


def prompt_artifact_path(issue_path: Path) -> Path:
    ctx = visual_context(issue_path)
    return HERE / "assets" / f"{ctx['numero']}.prompt.json"


def write_prompt_artifact(issue_path: Path, prompts: dict[str, Any] | None = None) -> Path:
    issue_path = Path(issue_path)
    prompts = prompts or visual_prompts_for_issue(issue_path)
    out = prompt_artifact_path(issue_path)
    out.parent.mkdir(exist_ok=True)
    serializable = {k: v for k, v in prompts.items() if k != "context"}
    try:
        serializable["issue_path"] = issue_path.relative_to(HERE.parent).as_posix()
    except ValueError:
        serializable["issue_path"] = issue_path.as_posix()
    serializable["context_summary"] = {
        "numero": prompts["context"]["numero"],
        "subject": prompts["context"]["subject"],
        "accionable_title": prompts["context"]["accionable_title"],
    }
    out.write_text(json.dumps(serializable, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def load_prompt_artifact(issue_path: Path) -> dict[str, Any] | None:
    p = prompt_artifact_path(issue_path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Prompts visuales desde issue Pulso")
    ap.add_argument("issue", type=Path)
    ap.add_argument("--write", action="store_true", help="Escribe newsletter/assets/NNN.prompt.json")
    ap.add_argument("--fallback-only", action="store_true")
    ap.add_argument("--json", action="store_true", help="Solo imprime JSON")
    args = ap.parse_args()
    path = Path(args.issue)
    if not path.is_absolute():
        for candidate in (HERE.parent / path, HERE / path):
            if candidate.exists():
                path = candidate
                break
        else:
            path = HERE.parent / path
    prompts = visual_prompts_for_issue(path, use_llm=False if args.fallback_only else None)
    if args.write:
        out = write_prompt_artifact(path, prompts)
        print(f"Prompt artifact: {out}")
    if args.json or not args.write:
        payload = {k: v for k, v in prompts.items() if k != "context"}
        print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()