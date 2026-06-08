#!/usr/bin/env python3
"""
Knowledge Loop HV — procesa promotions pendientes.

Lee data/knowledge-promotions-pending.json y:
  1. Agrega P/R a knowledge_base/FAQ_PROMOTED.md
  2. Agrega escenario al golden-set MD
  3. Vacía entradas aplicadas del JSON pendiente

Formato de cada promotion:
  {
    "id": "promo-001",
    "question": "...",
    "answer": "...",
    "kb_route": "longevity|servicios",
    "from_log_id": "optional",
    "target_section": "FAQ_PROMOTED"
  }

Uso:
  python scripts/process_knowledge_promotions.py
  python scripts/process_knowledge_promotions.py --dry-run
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_pendings(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"WARN: {path} corrupt, treating as empty", file=sys.stderr)
        return []


def append_faq(faq_path: Path, question: str, answer: str, kb_route: str) -> bool:
    src = faq_path.read_text(encoding="utf-8")
    if f"P: {question}" in src:
        return True
    block = (
        f"\n## {question[:60]}\n\n"
        f"**Ruta KB:** {kb_route}\n"
        f"**Promovido:** {datetime.now(timezone.utc).isoformat()}\n\n"
        f"P: {question}\n"
        f"R: {answer}\n"
    )
    faq_path.write_text(src.rstrip() + block + "\n", encoding="utf-8")
    return True


def next_promo_id(golden_md: Path, prefix: str = "P") -> str:
    if not golden_md.exists():
        return f"{prefix}-001"
    ids = re.findall(rf"###\s+({prefix}-\d{{3}}):", golden_md.read_text())
    n = max((int(x.split("-")[1]) for x in ids), default=0) + 1
    return f"{prefix}-{n:03d}"


def append_golden(golden_md: Path, scenario_id: str, promo: dict) -> None:
    q, a = promo["question"], promo["answer"]
    route = promo.get("kb_route", "longevity")
    block = (
        f"\n\n### {scenario_id}: pregunta auto-promovida\n\n"
        f"**Pregunta:** `{q}`\n"
        f"**Topic:** auto-promoted\n"
        f"**Modo:** retrieval\n"
        f"**Ruta esperada:** {route}\n"
        f"**Respuesta esperada:**\n"
        f"- kb_route {route}\n"
        f"- source o answer menciona fragmento de la respuesta promovida\n"
        f"**Criticidad:** P1\n"
        f"**Notas:** Auto-generated log_id={promo.get('from_log_id', '?')} "
        f"{datetime.now(timezone.utc).isoformat()}\n"
    )
    golden_md.write_text(golden_md.read_text(encoding="utf-8") + block, encoding="utf-8")


def main():
    root = Path(__file__).resolve().parent.parent
    pendings_path = root / "data" / "knowledge-promotions-pending.json"
    faq_path = root / "knowledge_base" / "FAQ_PROMOTED.md"
    golden_md = root / "docs" / "qa" / "golden-set-hv-rag.md"
    dry_run = "--dry-run" in sys.argv

    pendings = load_pendings(pendings_path)
    if not pendings:
        print("No pending promotions. Exit 0.")
        return

    print(f"Processing {len(pendings)} promotion(s)...")
    applied: list[dict] = []
    failed: list[dict] = []

    for promo in pendings:
        pid = promo.get("id", "?")
        q = promo.get("question", "").strip()
        a = promo.get("answer", "").strip()
        if not q or not a:
            failed.append({"id": pid, "reason": "missing question or answer"})
            continue
        if dry_run:
            print(f"  [dry-run] would apply {pid}: {q[:50]}...")
            applied.append(promo)
            continue
        try:
            append_faq(faq_path, q, a, promo.get("kb_route", "longevity"))
            sid = next_promo_id(golden_md, "P")
            append_golden(golden_md, sid, promo)
            print(f"  OK {pid} → FAQ + golden {sid}")
            applied.append(promo)
        except Exception as e:
            failed.append({"id": pid, "reason": str(e)})
            print(f"  FAIL {pid}: {e}")

    if not dry_run and applied:
        remaining = [p for p in pendings if p.get("id") not in {a.get("id") for a in applied}]
        pendings_path.write_text(json.dumps(remaining, indent=2) + "\n", encoding="utf-8")
        print(f"Cleared {len(applied)} applied, {len(remaining)} remain.")
        print("Next: python scripts/sync_golden_set.py && python embed_kb_local.py --source all")

    print(f"Done. Applied: {len(applied)}, Failed: {len(failed)}")


if __name__ == "__main__":
    main()