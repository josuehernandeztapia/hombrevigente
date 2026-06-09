#!/usr/bin/env python3
"""
Bridge editorial HV — aplica patches tipo A a monografías longevity.

Lee rag-bot/data/editorial-bridge-pending.json (staging de bridge_export.py)
y agrega sección *Evidencia reciente (Pulso Nº…)* en cada monografía.
No toca FAQ_PROMOTED ni knowledge-promotions-pending.json.

Uso:
  python scripts/process_editorial_bridge.py
  python scripts/process_editorial_bridge.py --dry-run
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SECTION_MARKER = "### Evidencia reciente (Pulso"
INSERT_BEFORE = (
    "## ⚠️ Límites",
    "## 📖 FAQ",
    "## 🔗 Integración",
    "## 🏷️ Plantilla",
)


def load_pendings(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"WARN: {path} corrupt, treating as empty", file=sys.stderr)
        return []


def build_bullet(entry: dict) -> str:
    numero = entry.get("numero", "???")
    fecha = entry.get("fecha", "")[:10]
    title = entry.get("title", "Sin título").strip()
    pmid_doi = entry.get("pmid_doi", "").strip()
    level = entry.get("evidence_level", "E3")
    summary = entry.get("summary", "").strip()
    fuente = entry.get("fuente", "").strip()

    journal_year = fuente if fuente else "fuente verificada"
    lines = [
        f"- **{title}** — *{journal_year}*. {pmid_doi} · {level}.",
    ]
    if summary:
        lines.append(f"  - {summary}")
    if level in ("E1", "E2"):
        lines.append("  - Límite: en investigación / preclínico; no establece efecto en personas.")
    return "\n".join(lines)


def build_section_header(numero: str, fecha: str) -> str:
    return f"### Evidencia reciente (Pulso Nº{numero} · {fecha})"


def already_present(content: str, pmid_doi: str) -> bool:
    key = pmid_doi.lower().replace(" ", "")
    return key in content.lower().replace(" ", "")


def insert_patch(mono_path: Path, entry: dict, dry_run: bool) -> bool:
    pmid_doi = entry.get("pmid_doi", "").strip()
    if not pmid_doi:
        return False

    if not mono_path.exists():
        print(f"  FAIL {entry.get('id')}: monografía no existe {mono_path.name}")
        return False

    content = mono_path.read_text(encoding="utf-8")
    if already_present(content, pmid_doi):
        print(f"  SKIP {entry.get('id')}: {pmid_doi} ya en {mono_path.name}")
        return True

    numero = entry.get("numero", "???")
    fecha = entry.get("fecha", "")[:10]
    header = build_section_header(numero, fecha)
    bullet = build_bullet(entry)

    if SECTION_MARKER in content:
        # Append bullet to existing Pulso section for this issue
        issue_marker = f"Pulso Nº{numero}"
        if issue_marker in content:
            pattern = rf"({re.escape(header)}.*?)(?=\n### Evidencia reciente|\n## |\Z)"
            m = re.search(pattern, content, re.DOTALL)
            if m:
                new_content = content[: m.end()] + "\n" + bullet + content[m.end() :]
            else:
                new_content = content.rstrip() + f"\n\n{header}\n{bullet}\n"
        else:
            new_content = content.rstrip() + f"\n\n{header}\n{bullet}\n"
    else:
        block = f"\n\n{header}\n{bullet}\n"
        inserted = False
        for anchor in INSERT_BEFORE:
            idx = content.find(anchor)
            if idx != -1:
                new_content = content[:idx].rstrip() + block + "\n" + content[idx:]
                inserted = True
                break
        if not inserted:
            new_content = content.rstrip() + block

    if dry_run:
        print(f"  [dry-run] would patch {mono_path.name} ← {entry.get('id')}")
        return True

    mono_path.write_text(new_content, encoding="utf-8")
    print(f"  OK {entry.get('id')} → {mono_path.name}")
    return True


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    pendings_path = root / "data" / "editorial-bridge-pending.json"
    longevity_dir = root / "knowledge_base" / "longevity"
    dry_run = "--dry-run" in sys.argv

    pendings = [p for p in load_pendings(pendings_path) if p.get("bridge_type") == "A"]
    if not pendings:
        print("No pending editorial bridges. Exit 0.")
        return

    print(f"Processing {len(pendings)} bridge(s)...")
    applied: list[dict] = []
    failed: list[dict] = []

    for entry in pendings:
        mono = entry.get("monografia", "").strip()
        if not mono:
            failed.append({"id": entry.get("id"), "reason": "missing monografia"})
            continue
        mono_path = longevity_dir / mono
        try:
            if insert_patch(mono_path, entry, dry_run):
                applied.append(entry)
            else:
                failed.append({"id": entry.get("id"), "reason": "insert failed"})
        except Exception as e:  # noqa: BLE001
            failed.append({"id": entry.get("id"), "reason": str(e)})
            print(f"  FAIL {entry.get('id')}: {e}")

    if not dry_run and applied:
        remaining = [p for p in load_pendings(pendings_path) if p.get("id") not in {a.get("id") for a in applied}]
        pendings_path.write_text(json.dumps(remaining, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Cleared {len(applied)} applied, {len(remaining)} remain.")
        print("Next: rag-bot-nightly.yml re-embede tras merge.")

    print(f"Done. Applied: {len(applied)}, Failed: {len(failed)}")


if __name__ == "__main__":
    main()