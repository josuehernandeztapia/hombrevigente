"""Pulso Vigente — publicación orgánica (carril AUTO) vía Ayrshare.

Publica posts de bajo riesgo SIN aprobación humana. Dos cerrojos de seguridad:
  1) solo publica frontmatter `lane: auto` (nunca `gated`).
  2) claim-guard: si el texto contiene lenguaje de salud (cura/trata/previene…),
     SE NIEGA a publicar y marca para revisión humana.

Uso:
  python newsletter/publish.py <post.md>          # un post
  python newsletter/publish.py --due              # todos los de queue/ con fecha<=hoy
Env: AYRSHARE_API_KEY (secret) ·  DRY_RUN=1 para no postear.
"""
from __future__ import annotations
import datetime as dt
import os
import re
import sys
from pathlib import Path
import requests
import yaml

HERE = Path(__file__).parent
QUEUE = HERE / "social" / "queue"
API = "https://api.ayrshare.com/api/post"

# Ayrshare usa estos nombres de plataforma:
PLATFORM_MAP = {"x": "twitter", "twitter": "twitter", "instagram": "instagram",
                "facebook": "facebook", "tiktok": "tiktok", "linkedin": "linkedin",
                "youtube": "youtube"}

# claim-guard: si aparece algo de esto, NO se autopublica (va a revisión humana).
RISKY = re.compile(
    r"\b(cura|curar|cura(?:n|s)|trata(?:r|miento)?|previene|prevenir|diagn[oó]stic|"
    r"garantiza|garantizado|reviert[ae]|revertir|milagro|elimina la enfermedad|"
    r"100\s?%|sana(?:r)?|adelgaza garantizado)\b",
    re.IGNORECASE,
)


def load(md: Path) -> dict:
    raw = md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    meta = yaml.safe_load(m.group(1)) if m else {}
    body = (m.group(2) if m else raw).strip()
    return {"meta": meta or {}, "text": body, "path": md}


def guard(post: dict) -> str | None:
    """Devuelve motivo de rechazo o None si pasa."""
    if post["meta"].get("lane") != "auto":
        return "lane != auto (requiere aprobación humana)"
    hit = RISKY.search(post["text"])
    if hit:
        return f"claim-guard: contiene '{hit.group(0)}' → revisión humana (compliance)"
    return None


def publish(post: dict) -> bool:
    reason = guard(post)
    if reason:
        print(f"⛔ NO publicado ({post['path'].name}): {reason}")
        return False

    platforms = [PLATFORM_MAP[p] for p in post["meta"].get("platforms", []) if p in PLATFORM_MAP]
    payload = {"post": post["text"], "platforms": platforms}
    img = post["meta"].get("image_url")
    if img:
        payload["mediaUrls"] = [img]

    if os.environ.get("DRY_RUN") == "1":
        print(f"DRY_RUN ✓ ({post['path'].name}) → {platforms}\n{post['text'][:120]}…")
        return True

    key = os.environ.get("AYRSHARE_API_KEY")
    if not key:
        sys.exit("Falta AYRSHARE_API_KEY")
    r = requests.post(API, headers={"Authorization": f"Bearer {key}"}, json=payload, timeout=30)
    if r.status_code >= 300:
        print(f"⚠️ Ayrshare error {r.status_code}: {r.text[:200]}")
        return False
    # marcador de publicado (para no repostear)
    post["path"].with_suffix(".posted").write_text(dt.datetime.utcnow().isoformat(), encoding="utf-8")
    print(f"✅ Publicado ({post['path'].name}) → {platforms}")
    return True


def due_posts() -> list[Path]:
    today = dt.date.today()
    out = []
    for p in sorted(QUEUE.glob("*.md")):
        if p.name.upper() == "README.MD" or p.with_suffix(".posted").exists():
            continue
        meta = load(p)["meta"]
        d = meta.get("date")
        if d is None:
            continue
        if (isinstance(d, dt.date) and d <= today) or (isinstance(d, str) and d <= today.isoformat()):
            out.append(p)
    return out


def main(argv: list[str]):
    if argv and argv[0] == "--due":
        posts = due_posts()
        if not posts:
            print("Sin posts due en queue/.")
            return
        for p in posts:
            publish(load(p))
    elif argv:
        publish(load(Path(argv[0])))
    else:
        sys.exit("Uso: python newsletter/publish.py <post.md> | --due")


if __name__ == "__main__":
    main(sys.argv[1:])
