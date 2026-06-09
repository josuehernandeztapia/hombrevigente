"""Pulso Vigente — exporta bridges editoriales tipo A al staging RAG.

Lee la tabla *Editorial bridge* de issues/*.md y agrega entradas a
rag-bot/data/editorial-bridge-pending.json. No toca monografías ni el
knowledge loop Q&A (proceso aparte).

Uso:
  python newsletter/bridge_export.py --issue newsletter/issues/2026-06-001.md
  python newsletter/bridge_export.py --all
  python newsletter/bridge_export.py --issue ... --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).parent
REPO = HERE.parent
PENDING_PATH = REPO / "rag-bot" / "data" / "editorial-bridge-pending.json"

# topic_ssot → monografía principal (alineado a BRIDGE.md / watchlist.yml)
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
    "descubrimiento_farmacos_ia": "01_hallmarks_envejecimiento.md",
    "diseno_proteinas": "01_hallmarks_envejecimiento.md",
    "relojes_envejecimiento_ml": "06_epigenetica_relojes_biologicos.md",
    "modelos_fundacionales_biologia": "01_hallmarks_envejecimiento.md",
}

BLOCK_HEADINGS = {
    "accionable": r"##\s*🟢\s*Accionable",
    "frontera": r"##\s*🔬\s*Frontera",
    "ai × longevity": r"##\s*🤖\s*AI",
    "ai x longevity": r"##\s*🤖\s*AI",
    "contexto / voz": r"##\s*🌍\s*Contexto",
    "contexto": r"##\s*🌍\s*Contexto",
}


def parse_issue(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError(f"{path} no tiene frontmatter YAML (---).")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def parse_bridge_table(body: str) -> list[dict]:
    """Extrae filas de la tabla Editorial bridge."""
    m = re.search(
        r"##\s*Editorial bridge.*?\n\n(\|.+\|(?:\n\|[^\n]+\|)+)",
        body,
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        return []

    lines = [ln.strip() for ln in m.group(1).splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return []

    header = [c.strip().lower() for c in lines[0].strip("|").split("|")]
    rows: list[dict] = []
    for line in lines[2:]:  # skip header + separator
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        row = dict(zip(header, cells))
        rows.append(row)
    return rows


def normalize_bridge_type(raw: str) -> str | None:
    t = raw.strip()
    if not t or re.fullmatch(r"A\s*/\s*C", t, re.I):
        return None
    if re.search(r"\bA\b", t, re.I):
        return "A"
    return None


def extract_block(body: str, bloque: str) -> dict:
    key = bloque.lower().strip()
    pattern = BLOCK_HEADINGS.get(key)
    if not pattern:
        for k, pat in BLOCK_HEADINGS.items():
            if k in key or key in k:
                pattern = pat
                break
    if not pattern:
        return {}

    m = re.search(
        rf"({pattern}[^\n]*)\n(.*?)(?=\n##\s|\Z)",
        body,
        re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return {}

    heading = m.group(1).strip()
    content = m.group(2).strip()
    title = re.sub(r"^##\s*[🟢🔬🤖🌍]\s*", "", heading)
    title = re.sub(
        r"^(Accionable|Frontera|AI\s*×\s*Longevity|Contexto\s*/\s*Voz)\s*—\s*",
        "",
        title,
        flags=re.I,
    ).strip()

    fuente = ""
    fm = re.search(r"\*Fuente:\s*([^*]+)\*", content)
    if fm:
        fuente = fm.group(1).strip()

    lente = ""
    lm = re.search(r">\s*\*\*🔵 Lente Vigente:\*\*\s*(.+?)(?=\n>|\n\n|\Z)", content, re.DOTALL)
    if lm:
        lente = re.sub(r"\s+", " ", lm.group(1).strip())

    return {"title": title, "fuente": fuente, "lente": lente}


def resolve_monografia(topic: str, explicit: str) -> str:
    if explicit:
        return explicit if explicit.endswith(".md") else f"{explicit}.md"
    return TOPIC_MONOGRAPHY.get(topic, "")


def row_to_entry(
    row: dict,
    meta: dict,
    issue_path: Path,
    body: str,
) -> dict | None:
    bloque = row.get("bloque", "").strip()
    bridge_raw = row.get("bridge", "").strip()
    bridge_type = normalize_bridge_type(bridge_raw)
    if bridge_type != "A":
        return None

    topic = row.get("topic_ssot", "").strip()
    monografia = resolve_monografia(topic, row.get("monografía", row.get("monografia", "")).strip())
    pmid_doi = row.get("pmid / doi", row.get("pmid_doi", "")).strip()
    evidence = row.get("nivel e", row.get("nivel_e", row.get("evidence_level", ""))).strip().upper()

    if not topic or not pmid_doi or not evidence:
        return None
    if not re.match(r"E[1-5]$", evidence):
        return None
    if not monografia:
        return None

    numero = str(meta.get("numero", issue_path.stem.split("-")[-1])).zfill(3)
    fecha = str(meta.get("fecha", ""))[:10]
    block_ctx = extract_block(body, bloque)
    issue_rel = issue_path.relative_to(REPO).as_posix()

    entry = {
        "id": f"bridge-{issue_path.stem}-{slugify(bloque)}",
        "issue_path": issue_rel,
        "numero": numero,
        "fecha": fecha,
        "bloque": bloque,
        "bridge_type": "A",
        "topic_ssot": topic,
        "monografia": monografia,
        "pmid_doi": pmid_doi,
        "evidence_level": evidence,
        "title": block_ctx.get("title", bloque),
        "fuente": block_ctx.get("fuente", ""),
        "summary": block_ctx.get("lente", ""),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }
    return entry


def load_pending() -> list[dict]:
    if not PENDING_PATH.exists():
        return []
    try:
        return json.loads(PENDING_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"WARN: {PENDING_PATH} corrupt, treating as empty", file=sys.stderr)
        return []


def merge_pending(existing: list[dict], new_entries: list[dict]) -> tuple[list[dict], int]:
    by_id = {e["id"]: e for e in existing if e.get("id")}
    added = 0
    for entry in new_entries:
        if entry["id"] in by_id:
            continue
        by_id[entry["id"]] = entry
        added += 1
    return list(by_id.values()), added


def export_issue(path: Path) -> list[dict]:
    meta, body = parse_issue(path)
    rows = parse_bridge_table(body)
    entries = []
    for row in rows:
        entry = row_to_entry(row, meta, path, body)
        if entry:
            entries.append(entry)
    return entries


def main() -> None:
    ap = argparse.ArgumentParser(description="Exporta bridges tipo A a editorial-bridge-pending.json")
    ap.add_argument("--issue", type=Path, help="Ruta al issue (ej. newsletter/issues/2026-06-001.md)")
    ap.add_argument("--all", action="store_true", help="Escanear todos los issues/")
    ap.add_argument("--dry-run", action="store_true", help="No escribe JSON; imprime entradas")
    args = ap.parse_args()

    if not args.issue and not args.all:
        ap.error("Indica --issue o --all")

    paths: list[Path] = []
    if args.issue:
        paths = [args.issue if args.issue.is_absolute() else REPO / args.issue]
    else:
        paths = sorted((HERE / "issues").glob("*.md"))

    new_entries: list[dict] = []
    for p in paths:
        if not p.exists():
            print(f"WARN: {p} no existe", file=sys.stderr)
            continue
        found = export_issue(p)
        print(f"{p.name}: {len(found)} bridge(s) tipo A")
        new_entries.extend(found)

    if args.dry_run:
        print(json.dumps(new_entries, indent=2, ensure_ascii=False))
        return

    existing = load_pending()
    merged, added = merge_pending(existing, new_entries)
    PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)
    PENDING_PATH.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Escrito {PENDING_PATH.relative_to(REPO)} · +{added} nuevas · {len(merged)} total")

    gh = __import__("os").environ.get("GITHUB_OUTPUT")
    if gh:
        Path(gh).open("a").write(f"pending_count={len(merged)}\nadded_count={added}\n")


if __name__ == "__main__":
    main()