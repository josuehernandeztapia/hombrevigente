"""Pulso Vigente — redacción automática del número desde candidatos harvest.

Selecciona papers del archivo candidates-*.md, redacta con IA (o plantilla
fallback) siguiendo EDITORIAL.md, valida que cada PMID/DOI esté en harvest.

Uso:
  python newsletter/draft_compose.py \\
    --candidates newsletter/drafts/candidates-2026-06-08.md \\
    --out newsletter/issues/2026-06-002.md \\
    --numero 002 --fecha 2026-06-12

  --fallback-only   sin OpenAI (plantilla mecánica)
  --dry-run         no escribe archivo
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
import yaml

HERE = Path(__file__).parent
REPO = HERE.parent
EDITORIAL = HERE / "EDITORIAL.md"
EXAMPLE = HERE / "issues" / "2026-06-001.md"

TOPIC_MONOGRAPHY: dict[str, str] = {
    "hallmarks_envejecimiento": "01_hallmarks_envejecimiento.md",
    "inflammaging": "02_inflammaging.md",
    "nad_nmn_sirtuinas": "03_nad_sirtuinas.md",
    "autofagia_espermidina": "04_autofagia_spermidina.md",
    "senescencia_senoliticos": "05_senescencia_senoliticos.md",
    "epigenetica_relojes_reprogramacion": "07_reprogramacion_celular.md",
    "peptidos_bpc_tb500_ghk_tesamorelin": "08_bpc157.md",
    "glp1_metabolismo": "17_glp1_metabolismo_longevidad.md",
    "lipidos_apob": "25_biomarcadores_panel_optimizacion.md",
    "sueno": "26_lifestyle_pilares.md",
    "termico_inflamacion": "28_termografia_inflammaging.md",
    "piel_optimizacion": "12_glow_limitless_blend.md",
    "descubrimiento_farmacos_ia": "06_epigenetica_relojes_biologicos.md",
    "diseno_proteinas": "01_hallmarks_envejecimiento.md",
    "relojes_envejecimiento_ml": "06_epigenetica_relojes_biologicos.md",
    "modelos_fundacionales_biologia": "01_hallmarks_envejecimiento.md",
}

AI_TOPICS = {
    "descubrimiento_farmacos_ia",
    "diseno_proteinas",
    "relojes_envejecimiento_ml",
    "modelos_fundacionales_biologia",
}


def parse_candidates(path: Path) -> list[dict]:
    items: list[dict] = []
    topic = ""
    current: dict | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            topic = line[3:].strip()
            continue
        m = re.match(
            r"^- ([⭐•])\s+\*\*(.+?)\*\*\s+—\s+\*(.+?)\*\s+\((\d{4}-\d{2}-\d{2})\)",
            line,
        )
        if m:
            if current and current.get("pmid"):
                items.append(current)
            star, title, journal, date = m.groups()
            current = {
                "topic": topic,
                "high_impact": star == "⭐",
                "title": title.replace("&lt;", "<").replace("&gt;", ">"),
                "journal": journal,
                "date": date,
                "pmid": "",
                "doi": "",
                "link": "",
            }
            continue
        if current and "PMID" in line:
            pm = re.search(r"PMID\s+(\d+)", line)
            if pm:
                current["pmid"] = pm.group(1)
            doi_m = re.search(r"DOI\s+(\S+)", line)
            if doi_m:
                current["doi"] = doi_m.group(1)
            link_m = re.search(r"(https://\S+)", line)
            if link_m:
                current["link"] = link_m.group(1)
    if current and current.get("pmid"):
        items.append(current)
    return items


def _score(title: str, high: bool, topic: str, kind: str) -> int:
    t = title.lower()
    s = 0
    if high:
        s += 4
    if kind == "accionable":
        if any(w in t for w in ("pilot", "randomized", "clinical trial", "in vivo", "human", "older adults")):
            s += 6
        if "cohort" in t and topic in ("lipidos_apob", "glp1_metabolismo", "nad_nmn_sirtuinas"):
            s += 4
        if topic == "lipidos_apob":
            s += 8
        if any(w in t for w in ("cholesterol", "pcsk9", "ldl", "apob", "hypercholesterolemia")):
            s += 6
        if topic in ("glp1_metabolismo", "autofagia_espermidina"):
            s += 3
    elif kind == "frontera":
        if any(w in t for w in ("virus", "outbreak", "covid")):
            s -= 6
        if any(w in t for w in ("reprogramming", "senescence", "senolytic", "autophagy", "spermidine")):
            s += 5
        if any(w in t for w in ("yeast", "mice", "preclinical")):
            s += 3
        if topic in ("epigenetica_relojes_reprogramacion", "senescencia_senoliticos", "autofagia_espermidina"):
            s += 3
    elif kind == "ai":
        if topic in AI_TOPICS:
            s += 5
        if any(w in t for w in ("artificial intelligence", "machine learning", "deep learning", "llm", "multi-omics")):
            s += 4
    elif kind == "contexto":
        if any(w in t for w in ("reflection", "framework", "review", "geroscience", "translational")):
            s += 4
    return s


def pick_blocks(items: list[dict]) -> dict[str, dict]:
    used: set[str] = set()
    picks: dict[str, dict] = {}

    def best(kind: str, pool: list[dict]) -> dict | None:
        ranked = sorted(pool, key=lambda it: _score(it["title"], it["high_impact"], it["topic"], kind), reverse=True)
        for it in ranked:
            if it["pmid"] not in used:
                used.add(it["pmid"])
                return it
        return None

    actionable_pool = [i for i in items if i["topic"] not in AI_TOPICS]
    picks["accionable"] = best("accionable", actionable_pool) or items[0]
    used.add(picks["accionable"]["pmid"])

    frontera_pool = [i for i in items if i["pmid"] not in used]
    picks["frontera"] = best("frontera", frontera_pool) or frontera_pool[0]
    used.add(picks["frontera"]["pmid"])

    ai_pool = [i for i in items if i["topic"] in AI_TOPICS and i["pmid"] not in used]
    if not ai_pool:
        ai_pool = [i for i in items if i["pmid"] not in used]
    picks["ai"] = best("ai", ai_pool) or ai_pool[0]
    used.add(picks["ai"]["pmid"])

    ctx_pool = [i for i in items if i["pmid"] not in used]
    picks["contexto"] = best("contexto", ctx_pool) or ctx_pool[0]

    return picks


def evidence_level(item: dict, block: str) -> str:
    t = item["title"].lower()
    if any(w in t for w in ("yeast", "mice", "rodent", "in vitro", "preclinical")):
        return "E2"
    if "pilot" in t or "phase" in t:
        return "E3"
    if block == "accionable" and item["high_impact"]:
        return "E3"
    if "review" in t or "scoping" in t:
        return "E3"
    return "E3"


def bridge_type(block: str, item: dict, level: str) -> str:
    if block == "contexto" and "review" in item["title"].lower():
        return "C"
    if level == "E2" and block == "frontera":
        return "A"
    if block in ("accionable", "ai") and item.get("pmid"):
        return "A"
    return "C"


def allowed_ids(items: list[dict]) -> tuple[set[str], set[str]]:
    pmids = {it["pmid"] for it in items if it["pmid"]}
    dois = set()
    for it in items:
        if it.get("doi"):
            dois.add(it["doi"].lower())
            dois.add(it["doi"].split("/")[-1].lower())
    return pmids, dois


def validate_sources(body: str, items: list[dict]) -> list[str]:
    pmids, dois = allowed_ids(items)
    errors: list[str] = []
    cited_pmids = set(re.findall(r"PMID\s*(\d+)", body, re.I))
    for p in cited_pmids:
        if p not in pmids:
            errors.append(f"PMID {p} no está en candidatos harvest")
    # DOI tokens in text
    for token in re.findall(r"10\.\d{4,}/\S+", body):
        if token.lower() not in dois and token.split("/")[-1].lower() not in dois:
            # allow nejm-style ids if pmid present
            if not cited_pmids:
                errors.append(f"DOI {token[:40]} no reconocido en harvest")
    if not cited_pmids:
        errors.append("Ningún PMID citado en el borrador")
    return errors


def llm_compose(picks: dict[str, dict], numero: str, fecha: str, api_key: str) -> str:
    editorial = EDITORIAL.read_text(encoding="utf-8")[:4000]
    example = EXAMPLE.read_text(encoding="utf-8")[:2500] if EXAMPLE.exists() else ""
    payload_items = {k: v for k, v in picks.items()}

    system = (
        "Eres el redactor de Pulso Vigente (Hombre Vigente™, México). "
        "Escribes en español, tono: optimización masculina premium, riguroso, sin hype médico. "
        "NUNCA inventes PMIDs, DOIs, cifras ni estudios. Solo usa los candidatos JSON. "
        "Sin palabras: cura, trata, previene, diagnóstico, garantiza. "
        "Usa 'se asocia', 'se estudia', 'optimización', 'en investigación'. "
        "Salida: SOLO el markdown del número, empezando con --- frontmatter YAML."
    )
    user = f"""Redacta el número completo Pulso Vigente Nº{numero} ({fecha}).

REGLAS EDITORIALES (resumen):
{editorial[:2000]}

EJEMPLO DE ESTILO (referencia, no copies hechos):
{example[:1500]}

CANDIDATOS ASIGNADOS (única fuente permitida):
{json.dumps(payload_items, indent=2, ensure_ascii=False)}

ESTRUCTURA OBLIGATORIA:
- frontmatter: numero, fecha, subject (curiosity-gap con cifra), preheader, audiencia: plus, approved: false, approval_status: pending
- TLDR una línea
- ## 🟢 Accionable — [titular] + párrafo + Lente Vigente + *Fuente: journal, PMID x*
- ## 🔬 Frontera — [titular] + ...
- ## 🤖 AI × Longevity — [titular] + ...
- ## 🌍 Contexto / Voz — [titular] + ...
- Para ti miembro Plus + Bottom line
- Tabla Editorial bridge (4 filas) con topic_ssot, monografía, pmid/doi, nivel E, bridge A o C
- Disclaimer al pie

Para bridge: usa topic del candidato; monografía según mapa HV; nivel E2 preclínico, E3 piloto/review, E4 ensayo humano si aplica."""

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": os.environ.get("PULSO_COMPOSE_MODEL", "gpt-4o-mini"),
            "temperature": 0.4,
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


def fallback_compose(picks: dict[str, dict], numero: str, fecha: str) -> str:
    a, f, ai, c = picks["accionable"], picks["frontera"], picks["ai"], picks["contexto"]
    subj = f"Pulso Vigente Nº{numero} — {a['title'][:55]}"
    pre = f"{a['journal']} · {f['title'][:40]} · IA×longevidad"

    def block(emoji, label, item: dict, lente: str) -> str:
        return (
            f"## {emoji} {label} — {item['title'][:80]}\n"
            f"Publicado en *{item['journal']}* ({item['date']}). "
            f"Metadatos verificados Europe PMC (PMID {item['pmid']}).\n\n"
            f"> **🔵 Lente Vigente:** {lente}\n"
            f"> *Fuente: {item['journal']} {item['date'][:4]}, PMID {item['pmid']}.*\n"
        )

    def bridge_row(name: str, item: dict, block_key: str) -> str:
        lvl = evidence_level(item, block_key)
        bt = bridge_type(block_key, item, lvl)
        mono = TOPIC_MONOGRAPHY.get(item["topic"], "")
        ref = item.get("doi", "").split("/")[-1] if item.get("doi") else f"PMID {item['pmid']}"
        return f"| {name} | {item['topic']} | {mono} | {ref} | {lvl} | {bt} |"

    body = f"""---
numero: "{numero}"
fecha: {fecha}
subject: "{subj}"
preheader: "{pre}"
audiencia: plus
approved: false
approval_status: pending
compose: auto-fallback
---

**TLDR:** Tres señales de la semana en longevidad — y qué puedes optimizar hoy con evidencia verificable.

---

{block("🟢", "Accionable", a, "Dato con evidencia reciente. Mide, contextualiza con tu médico y optimiza hábitos con señal (Av.1). No es prescripción.")}

{block("🔬", "Frontera", f, "Investigación activa — etiquetado como frontera, no terapia disponible. HV educa; no vende lo que aún está en laboratorio.")}

{block("🤖", "AI × Longevity", ai, "La IA acelera el descubrimiento; el gate sigue siendo evidencia en humanos. Hype con sustancia.")}

{block("🌍", "Contexto / Voz", c, "Panorama del campo: traducción de gerociencia y prioridades de investigación global.")}

---

**🟢 Para ti, miembro Plus:** revisa qué marcador o hábito de esta semana encaja con tu Diagnóstico Vigente. ¿Lo agregamos a tu panel?

**Bottom line:** la frontera avanza; tu ventaja es medir y optimizar lo que ya tiene señal. Eso es estar Vigente.

---

## Editorial bridge (auto — verificar antes de merge)

| bloque | topic_ssot | monografía | pmid / doi | nivel E | bridge |
|--------|------------|------------|------------|---------|--------|
{bridge_row("Accionable", a, "accionable")}
{bridge_row("Frontera", f, "frontera")}
{bridge_row("AI × Longevity", ai, "ai")}
{bridge_row("Contexto / Voz", c, "contexto")}

- **A** = patch a monografía SSOT · **C** = solo Pulso/redes

---

*Pulso Vigente es información educativa de optimización y bienestar. No es diagnóstico ni tratamiento médico.*
"""
    return body


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--numero", required=True)
    ap.add_argument("--fecha", required=True)
    ap.add_argument("--fallback-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cand_path = args.candidates if args.candidates.is_absolute() else REPO / args.candidates
    out_path = args.out if args.out.is_absolute() else REPO / args.out

    items = parse_candidates(cand_path)
    if len(items) < 4:
        sys.exit(f"Insuficientes candidatos ({len(items)}); amplía harvest --days")

    picks = pick_blocks(items)
    api_key = os.environ.get("OPENAI_API_KEY")

    if args.fallback_only or not api_key:
        if not api_key and not args.fallback_only:
            print("WARN: sin OPENAI_API_KEY — usando fallback", file=sys.stderr)
        draft = fallback_compose(picks, args.numero, args.fecha)
        mode = "fallback"
    else:
        try:
            draft = llm_compose(picks, args.numero, args.fecha, api_key)
            mode = "llm"
        except Exception as e:  # noqa: BLE001
            print(f"WARN: LLM falló ({e}) — fallback", file=sys.stderr)
            draft = fallback_compose(picks, args.numero, args.fecha)
            mode = "fallback"

    errors = validate_sources(draft, items)
    if errors:
        print("Validación falló:", "; ".join(errors), file=sys.stderr)
        if mode == "llm":
            print("Reintentando con fallback…", file=sys.stderr)
            draft = fallback_compose(picks, args.numero, args.fecha)
            errors = validate_sources(draft, items)
        if errors:
            sys.exit(f"Draft inválido: {errors}")

    if args.dry_run:
        print(draft[:2000])
        print(f"\n… ({len(draft)} chars) · mode={mode} · OK")
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(draft, encoding="utf-8")
    try:
        shown = out_path.relative_to(REPO)
    except ValueError:
        shown = out_path
    print(f"Escrito {shown} · mode={mode} · {len(items)} candidatos")

    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        Path(gh).open("a").write(f"issue_path={out_path.relative_to(REPO)}\ncompose_mode={mode}\n")


if __name__ == "__main__":
    main()