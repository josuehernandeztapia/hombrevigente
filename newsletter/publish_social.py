"""Publica piezas gated de social/<numero>/ vía Ayrshare (aprobación humana implícita).

Usa unsplash_query de prompt_from_issue (o genera on-the-fly).
Instagram requiere imagen — hero local sin URL pública usa Unsplash.

Uso:
  python newsletter/publish_social.py --issue newsletter/issues/2026-06-001.md
  python newsletter/publish_social.py --issue ... --hero --tag hero-v1 --force
  python newsletter/publish_social.py --issue ... --media-url https://...
  DRY_RUN=1 python newsletter/publish_social.py ...
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import requests

from prompt_from_issue import load_prompt_artifact, visual_prompts_for_issue, write_prompt_artifact

HERE = Path(__file__).parent
API = "https://api.ayrshare.com/api/post"


def instagram_caption(numero: str) -> str:
    path = HERE / "social" / numero / "instagram-facebook.md"
    if not path.exists():
        raise FileNotFoundError(f"Falta {path}")
    raw = path.read_text(encoding="utf-8")
    m = re.search(r"## Caption\n(.*?)(?:\n\n_|$)", raw, re.S)
    if not m:
        raise ValueError("instagram-facebook.md sin sección ## Caption")
    return m.group(1).strip()


def already_posted(numero: str, platform: str) -> bool:
    marker = HERE / "social" / numero / f"instagram-facebook.posted"
    return marker.exists() and platform == "instagram"


def mark_posted(numero: str, platform: str, meta: dict) -> None:
    if platform != "instagram":
        return
    path = HERE / "social" / numero / "instagram-facebook.posted"
    lines = [
        meta.get("posted_at", ""),
        f"platform: {platform}",
        f"postUrl: {meta.get('postUrl', '')}",
        f"mediaUrl: {meta.get('mediaUrl', '')}",
        f"idempotencyKey: {meta.get('idempotencyKey', '')}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def hero_asset_path(numero: str) -> Path:
    return HERE / "assets" / f"{numero}.png"


def hero_public_url(numero: str) -> str:
    override = os.environ.get("HV_NEWSLETTER_ASSETS_BASE", "").strip().rstrip("/")
    if override:
        return f"{override}/{numero}.png"
    repo = os.environ.get("GITHUB_REPOSITORY", "josuehernandeztapia/hombrevigente")
    branch = os.environ.get("HV_NEWSLETTER_ASSETS_BRANCH", "main")
    return (
        f"https://raw.githubusercontent.com/{repo}/{branch}/"
        f"newsletter/assets/{numero}.png"
    )


def resolve_media_url(numero: str, *, media_url: str | None, use_hero: bool) -> str | None:
    if media_url:
        return media_url.strip()
    if not use_hero:
        return None
    local = hero_asset_path(numero)
    if not local.exists():
        raise FileNotFoundError(
            f"Falta {local}. Genera: python newsletter/image.py newsletter/issues/..."
        )
    return hero_public_url(numero)


def publish_instagram(
    issue_path: Path,
    *,
    force: bool = False,
    tag: str = "",
    media_url: str | None = None,
    use_hero: bool = False,
) -> bool:
    from prompt_from_issue import visual_context

    ctx = visual_context(issue_path)
    numero = ctx["numero"]
    if already_posted(numero, "instagram") and not force:
        print(f"Ya publicado en IG (social/{numero}/instagram-facebook.posted). Usa --force.")
        return False

    media = resolve_media_url(numero, media_url=media_url, use_hero=use_hero)
    unsplash = None
    if not media:
        prompts = load_prompt_artifact(issue_path)
        if not prompts or not prompts.get("unsplash_query"):
            prompts = visual_prompts_for_issue(issue_path)
            write_prompt_artifact(issue_path, prompts)
        unsplash = prompts.get("unsplash_query", "longevity abstract science")

    caption = instagram_caption(numero)
    suffix = tag or os.environ.get("PULSO_PUBLISH_TAG", "v1")
    idem = f"pulso-{numero}-ig-{suffix}"

    payload: dict = {
        "post": caption,
        "platforms": ["instagram"],
        "idempotencyKey": idem,
    }
    if media:
        payload["mediaUrls"] = [media]
    else:
        payload["unsplash"] = unsplash

    if os.environ.get("DRY_RUN") == "1":
        print(f"DRY_RUN IG Nº{numero}")
        print(f"media: {media or f'unsplash:{unsplash}'}")
        print(caption[:200], "...")
        return True

    key = os.environ.get("AYRSHARE_API_KEY")
    if not key:
        sys.exit("Falta AYRSHARE_API_KEY")

    r = requests.post(
        API,
        headers={"Authorization": f"Bearer {key}"},
        json=payload,
        timeout=90,
    )
    if r.status_code >= 300:
        print(f"Error Ayrshare {r.status_code}: {r.text[:400]}", file=sys.stderr)
        return False

    data = r.json()
    post_ids = data.get("postIds") or []
    url = post_ids[0].get("postUrl", "") if post_ids else ""
    mark_posted(
        numero,
        "instagram",
        {
            "posted_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "postUrl": url,
            "mediaUrl": media or "",
            "idempotencyKey": idem,
        },
    )
    src = media or f"unsplash:{unsplash}"
    print(f"✅ Instagram Nº{numero} · {src}")
    if url:
        print(url)
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description="Publicar social gated (Ayrshare)")
    ap.add_argument("--issue", type=Path, required=True)
    ap.add_argument("--platform", choices=["instagram"], default="instagram")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--tag", default="", help="Sufijo idempotencyKey (ej. hero-v1)")
    ap.add_argument("--media-url", default="", help="URL pública de imagen (mediaUrls)")
    ap.add_argument(
        "--hero",
        action="store_true",
        help="Usa newsletter/assets/NNN.png vía raw.githubusercontent.com (o HV_NEWSLETTER_ASSETS_BASE)",
    )
    args = ap.parse_args()
    issue = Path(args.issue)
    if not issue.is_absolute():
        for candidate in (HERE.parent / issue, HERE / issue):
            if candidate.exists():
                issue = candidate
                break
        else:
            issue = HERE.parent / issue
    if args.platform == "instagram":
        ok = publish_instagram(
            issue,
            force=args.force,
            tag=args.tag,
            media_url=args.media_url or None,
            use_hero=args.hero,
        )
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()