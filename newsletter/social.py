"""Pulso Vigente — atomizador social.

Toma un número (.md) y genera un 'social pack' por plataforma en
newsletter/social/<numero>/: X (hilo), Instagram/Facebook (carrusel + caption),
LinkedIn (post), TikTok (guion). Es ESTRUCTURAL: arma los borradores desde el
contenido del número; el humano pule y VERIFICA antes de publicar.

Uso: python newsletter/social.py newsletter/issues/2026-06-001.md
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
import yaml

HERE = Path(__file__).parent
HASHTAGS = "#longevidad #optimización #saludmasculina #biohacking #HombreVigente"
CTA = "Suscríbete a Pulso Vigente → hombrevigente.com"
WARN = "<!-- REVISAR Y VERIFICAR FUENTES ANTES DE PUBLICAR. Sigue EDITORIAL.md. -->\n"


def parse(md_path: Path) -> dict:
    raw = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    meta = yaml.safe_load(m.group(1)) if m else {}
    body = m.group(2) if m else raw

    tldr = ""
    mt = re.search(r"\*\*TLDR:\*\*\s*(.+)", body)
    if mt:
        tldr = mt.group(1).strip()

    bottom = ""
    mb = re.search(r"\*\*Bottom line:\*\*\s*(.+)", body)
    if mb:
        bottom = mb.group(1).strip()

    blocks = []
    for bm in re.finditer(r"^##\s+(.+?)\n(.*?)(?=^##\s|\n---|\Z)", body, re.DOTALL | re.MULTILINE):
        head = bm.group(1).strip()
        text = bm.group(2).strip()
        # primer párrafo (sin la cita > lente ni la fuente)
        first = ""
        for line in text.splitlines():
            ls = line.strip()
            if ls and not ls.startswith(">") and not ls.startswith("*"):
                first = ls
                break
        source = ""
        ms = re.search(r"\*Fuente:\s*(.+?)\*", text)
        if ms:
            source = ms.group(1).strip()
        lente = ""
        ml = re.search(r"Lente Vigente:\*\*\s*(.+)", text)
        if ml:
            lente = ml.group(1).strip()
        # titulo limpio (sin emoji ni "Categoría —")
        title = re.sub(r"^[^\w]*\w+\s+—\s+", "", head)
        title = re.sub(r"^[\W_]+", "", head).split("—")[-1].strip() or head
        blocks.append({"head": head, "title": title, "text": first, "source": source, "lente": lente})

    return {
        "numero": meta.get("numero", ""),
        "subject": meta.get("subject", "Pulso Vigente"),
        "tldr": tldr,
        "bottom": bottom,
        "blocks": blocks,
    }


def build_x(d: dict) -> str:
    out = [WARN, f"# X / Twitter — hilo (Nº{d['numero']})\n"]
    out.append(f"1/ {d['subject'].split('—')[-1].strip()}\n\n{d['tldr']}\n")
    n = 2
    for b in d["blocks"]:
        if "[slot" in b["text"].lower() or not b["text"]:
            continue
        src = f"\nFuente: {b['source']}" if b["source"] else ""
        out.append(f"{n}/ {b['title']}\n{b['text'][:230]}{src}\n")
        n += 1
    out.append(f"{n}/ {d['bottom']}\n\n{CTA}\n")
    out.append("\n_Nota: cada tweet ≤280 car. Acorta donde haga falta. Adjunta el hero del número._")
    return "\n".join(out)


def build_ig_fb(d: dict) -> str:
    slides = [f"**Slide 1 (portada):** PULSO VIGENTE Nº{d['numero']}\n{d['subject'].split('—')[-1].strip()}"]
    i = 2
    for b in d["blocks"]:
        if "[slot" in b["text"].lower() or not b["text"]:
            continue
        slides.append(f"**Slide {i}:** {b['title']}\n{b['text'][:160]}")
        i += 1
    slides.append(f"**Slide {i} (cierre):** {d['bottom'][:140]}\n→ {CTA}")
    caption = f"{d['tldr']}\n\n{d['bottom']}\n\n{CTA}\n\n{HASHTAGS}"
    return (
        f"{WARN}# Instagram / Facebook — carrusel (Nº{d['numero']})\n\n"
        + "\n\n".join(slides)
        + "\n\n---\n## Caption\n"
        + caption
        + "\n\n_Diseña los slides con el hero + acento bronce. Cita la fuente en el slide correspondiente._"
    )


def build_linkedin(d: dict) -> str:
    paras = [d["tldr"], ""]
    for b in d["blocks"]:
        if "[slot" in b["text"].lower() or not b["text"]:
            continue
        src = f" (Fuente: {b['source']})" if b["source"] else ""
        paras.append(f"▸ {b['title']}. {b['text']}{src}")
    paras += ["", d["bottom"], "", CTA, "", HASHTAGS]
    return f"{WARN}# LinkedIn — post (Nº{d['numero']})\n\n" + "\n".join(paras)


def build_tiktok(d: dict) -> str:
    beats = []
    for b in d["blocks"][:3]:
        if "[slot" in b["text"].lower() or not b["text"]:
            continue
        beats.append(f"- **{b['title']}** — {b['text'][:120]}")
    return (
        f"{WARN}# TikTok / Reels — guion (Nº{d['numero']})\n\n"
        f"**Gancho (0-3s):** {d['tldr'][:120]}\n\n"
        f"**Desarrollo (3 beats):**\n" + "\n".join(beats) + "\n\n"
        f"**Cierre/CTA:** {d['bottom'][:120]}\n→ {CTA}\n\n"
        "_Formato: hablado a cámara (Caso #1) o texto-en-movimiento. 20-40s. "
        "Disclaimer en pantalla: 'Información educativa, no diagnóstico médico.'_"
    )


def main(md_path: str):
    d = parse(Path(md_path))
    out_dir = HERE / "social" / str(d["numero"])
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "x-thread.md": build_x(d),
        "instagram-facebook.md": build_ig_fb(d),
        "linkedin.md": build_linkedin(d),
        "tiktok-script.md": build_tiktok(d),
    }
    for name, content in files.items():
        (out_dir / name).write_text(content, encoding="utf-8")
    print(f"Social pack escrito en {out_dir} · {len(files)} piezas")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python newsletter/social.py <ruta_al_numero.md>")
    main(sys.argv[1])
