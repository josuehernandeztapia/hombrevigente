"""Pulso Vigente — harvester de candidatos.

Cosecha papers recientes de Europe PMC para los temas del watchlist, los puntúa
y escribe un archivo de CANDIDATOS VERIFICADOS (PMID/DOI reales, metadatos de la
fuente — sin fabricación posible). El editor humano elige y escribe el "lente
Vigente". NO escribe el número final ni inventa nada.

Uso:  python newsletter/harvest.py [--days 30] [--per-topic 4]
Salida: newsletter/drafts/candidates-YYYY-MM-DD.md
"""
from __future__ import annotations
import argparse
import datetime as dt
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests
import yaml

HERE = Path(__file__).parent
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UA = {"User-Agent": "PulsoVigente-harvester/1.0 (contacto@hombrevigente.com)"}

# Temas del watchlist -> términos de búsqueda Europe PMC
TOPIC_QUERIES = {
    "hallmarks_envejecimiento": '("hallmarks of aging" OR geroscience)',
    "inflammaging": '(inflammaging OR "inflamm-aging")',
    "nad_nmn_sirtuinas": '("nicotinamide mononucleotide" OR "NAD+" OR sirtuin) AND aging',
    "autofagia_espermidina": '(spermidine OR autophagy) AND (aging OR longevity)',
    "senescencia_senoliticos": '(senolytic OR "cellular senescence") AND (aging OR lifespan)',
    "epigenetica_relojes_reprogramacion": '("epigenetic clock" OR "partial reprogramming" OR "epigenetic reprogramming") AND aging',
    "peptidos_bpc_tb500_ghk_tesamorelin": '("BPC-157" OR "thymosin beta 4" OR "GHK-Cu" OR tesamorelin)',
    "glp1_metabolismo": '(semaglutide OR tirzepatide OR "GLP-1") AND (aging OR longevity OR metabolic)',
    "lipidos_apob": '(ApoB OR PCSK9 OR "LDL cholesterol") AND (cardiovascular OR atherosclerosis)',
    "sueno": '(sleep) AND (longevity OR healthspan OR inflammation)',
    "termico_inflamacion": '(thermography OR "infrared thermal imaging") AND (inflammation OR skin)',
    "piel_optimizacion": '("skin aging" OR photoaging) AND (intervention OR treatment)',
    # AI x longevity
    "descubrimiento_farmacos_ia": '("artificial intelligence" OR "machine learning" OR "deep learning") AND "drug discovery" AND (aging OR longevity OR senescence)',
    "diseno_proteinas": '("protein design" OR AlphaFold OR RFdiffusion) AND (therapeutic OR aging)',
    "relojes_envejecimiento_ml": '("aging clock" OR "biological age") AND ("machine learning" OR "deep learning")',
    "modelos_fundacionales_biologia": '("foundation model" OR "large language model") AND (biology OR genomics)',
}

HIGH_IMPACT = {
    "n engl j med", "nature", "science", "cell", "lancet", "jama",
    "nature aging", "nature medicine", "cell metab", "cell metabolism",
    "aging cell", "geroscience", "elife", "nat aging", "nat med",
}


def load_watchlist() -> dict:
    p = HERE / "watchlist.yml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def search_topic(terms: str, since: str, until: str, page_size: int = 12) -> list[dict]:
    q = f'({terms}) AND (FIRST_PDATE:[{since} TO {until}]) AND SRC:MED'
    url = f"{EPMC}?query={quote(q)}&format=json&pageSize={page_size}&resultType=lite"
    try:
        r = requests.get(url, headers=UA, timeout=30)
        r.raise_for_status()
        return r.json().get("resultList", {}).get("result", [])
    except Exception as e:  # noqa: BLE001
        print(f"  WARN topic query falló: {e}", file=sys.stderr)
        return []


def score(item: dict) -> int:
    s = 0
    jr = (item.get("journalTitle") or "").lower()
    if any(h in jr for h in HIGH_IMPACT):
        s += 3
    # tipo de evidencia
    pt = (item.get("pubType") or "").lower()
    if "randomized controlled trial" in pt or "clinical trial" in pt:
        s += 2
    if "review" in pt:
        s += 1
    # recencia
    d = item.get("firstPublicationDate") or ""
    try:
        days_old = (dt.date.today() - dt.date.fromisoformat(d)).days
        s += max(0, 3 - days_old // 10)
    except Exception:  # noqa: BLE001
        pass
    return s


def fmt(item: dict) -> str:
    pmid = item.get("pmid", "")
    doi = item.get("doi", "")
    title = (item.get("title") or "").rstrip(".")
    jr = item.get("journalTitle", "")
    date = item.get("firstPublicationDate", "")
    auth = item.get("authorString", "")
    link = f"https://europepmc.org/abstract/MED/{pmid}" if pmid else (f"https://doi.org/{doi}" if doi else "")
    tag = "⭐" if any(h in jr.lower() for h in HIGH_IMPACT) else "•"
    src = f"PMID {pmid}" + (f" · DOI {doi}" if doi else "")
    return f"- {tag} **{title}** — *{jr}* ({date}). {auth[:60]}\n  - {src} · {link}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--per-topic", type=int, default=4)
    args = ap.parse_args()

    wl = load_watchlist()
    enabled = set(wl.get("temas_ssot", [])) | set(wl.get("beat_ai_longevity", []))
    topics = {k: v for k, v in TOPIC_QUERIES.items() if not enabled or k in enabled}

    until = dt.date.today().isoformat()
    since = (dt.date.today() - dt.timedelta(days=args.days)).isoformat()

    lines = [
        f"# Candidatos Pulso Vigente — {until}",
        "",
        f"Ventana: últimos {args.days} días · fuente: Europe PMC (metadatos verificados).",
        "⭐ = journal de alto impacto. Elige, verifica el abstract y escribe el lente Vigente.",
        "",
        "> Regla de hierro: solo entra al número lo que tú confirmes. Esto es materia prima, no el número final.",
        "",
    ]
    total = 0
    for topic, terms in topics.items():
        results = search_topic(terms, since, until)
        ranked = sorted(results, key=score, reverse=True)[: args.per_topic]
        if not ranked:
            continue
        lines.append(f"## {topic}")
        for it in ranked:
            lines.append(fmt(it))
            total += 1
        lines.append("")
        time.sleep(0.6)  # cortesía con Europe PMC

    if total == 0:
        lines.append("_Sin candidatos en la ventana. Amplía --days o revisa manualmente la prensa de industria._")

    out_dir = HERE / "drafts"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"candidates-{until}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Escrito {out} · {total} candidatos")
    # expone la ruta para el workflow
    gh = __import__("os").environ.get("GITHUB_OUTPUT")
    if gh:
        Path(gh).open("a").write(f"candidates={out.relative_to(HERE.parent)}\n")


if __name__ == "__main__":
    main()
