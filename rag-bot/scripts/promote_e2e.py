#!/usr/bin/env python3
"""
Promote E2E — gap → pending → FAQ + golden P-xxx → sync → embed → verify.

Flujo completo del knowledge loop en un solo comando (local o prod API).

  # Local
  python scripts/promote_e2e.py \\
    --question "¿Aceptan AMEX?" \\
    --answer "Sí, aceptamos Visa, Mastercard y AMEX." \\
    --kb-route servicios

  # Desde primer gap del log local
  python scripts/promote_e2e.py --from-gap --answer "..." --kb-route servicios

  # Prod API (staging en Fly; luego procesa en repo)
  python scripts/promote_e2e.py --api-url https://hv-rag-api.fly.dev \\
    --pin "$HV_ADMIN_PIN" --question "..." --answer "..."

  python scripts/promote_e2e.py --dry-run ...
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from knowledge_gap_detector import detect_knowledge_gaps
from knowledge_promote import load_pending, submit_promotion

PENDING_PATH = _ROOT / "data" / "knowledge-promotions-pending.json"
GOLDEN_MD = _ROOT / "docs" / "qa" / "golden-set-hv-rag.md"


def _run(cmd: list[str], *, dry_run: bool, cwd: Path = _ROOT) -> None:
    printable = " ".join(cmd)
    if dry_run:
        print(f"  [dry-run] would run: {printable}")
        return
    print(f"  → {printable}")
    r = subprocess.run(cmd, cwd=cwd, check=False)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def _submit_via_api(
    *,
    api_url: str,
    pin: str,
    question: str,
    answer: str,
    kb_route: str,
    from_log_id: Optional[str],
    notes: Optional[str],
    dry_run: bool,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "question": question,
        "answer": answer,
        "kb_route": kb_route,
        "target_section": "FAQ_PROMOTED",
    }
    if from_log_id:
        body["from_log_id"] = from_log_id
    if notes:
        body["notes"] = notes

    if dry_run:
        print(f"  [dry-run] POST {api_url.rstrip('/')}/admin/knowledge/promote")
        return {"success": True, "promotion": {"id": "dry-run"}}

    url = f"{api_url.rstrip('/')}/admin/knowledge/promote"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-admin-pin": pin,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            payload["status_code"] = resp.status
            return payload
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: promote API HTTP {e.code}: {detail}", file=sys.stderr)
        raise SystemExit(1) from e


def _submit_local(
    *,
    question: str,
    answer: str,
    kb_route: str,
    from_log_id: Optional[str],
    notes: Optional[str],
    pending_path: Path,
    dry_run: bool,
) -> Dict[str, Any]:
    if dry_run:
        print(f"  [dry-run] submit_promotion: {question[:50]}...")
        return {"success": True, "promotion": {"id": "dry-run"}}

    result = submit_promotion(
        question=question,
        answer=answer,
        kb_route=kb_route,
        from_log_id=from_log_id,
        notes=notes,
        path=pending_path,
    )
    if not result.get("success"):
        print(f"ERROR: {result.get('error')}", file=sys.stderr)
        raise SystemExit(result.get("status_code", 1))
    return result


def _latest_promo_id(golden_md: Path) -> Optional[str]:
    if not golden_md.exists():
        return None
    ids = re.findall(r"###\s+(P-\d{3}):", golden_md.read_text(encoding="utf-8"))
    return ids[-1] if ids else None


def _promoted_questions(faq_path: Path, golden_md: Path) -> set[str]:
    promoted: set[str] = set()
    if faq_path.exists():
        for m in re.finditer(r"^P:\s*(.+)$", faq_path.read_text(encoding="utf-8"), re.M):
            promoted.add(m.group(1).strip().lower())
    if golden_md.exists():
        for m in re.finditer(r"\*\*Pregunta:\*\*\s*`([^`]+)`", golden_md.read_text(encoding="utf-8")):
            if m.group(1).strip():
                promoted.add(m.group(1).strip().lower())
    return promoted


def _knowledge_promotable_gaps(
    gaps: list[Dict[str, Any]],
    *,
    already_promoted: set[str],
    gap_match: Optional[str],
) -> list[Dict[str, Any]]:
    """Excluye gates de seguridad (blocked) y preguntas ya promovidas."""
    out: list[Dict[str, Any]] = []
    needle = (gap_match or "").strip().lower()
    for g in gaps:
        paths = set(g.get("gate_paths") or [])
        if paths <= {"blocked"} or paths == {"blocked"}:
            continue
        q = (g.get("question") or "").strip()
        if q.lower() in already_promoted:
            continue
        if needle and needle not in q.lower():
            continue
        out.append(g)
    return out


def _resolve_from_gap(
    *,
    gap_index: int,
    days: int,
    log_path: Optional[Path],
    gap_match: Optional[str],
) -> tuple[str, Optional[str], str]:
    raw = detect_knowledge_gaps(days=days, log_path=log_path, max_gaps=50)
    gaps = _knowledge_promotable_gaps(
        raw,
        already_promoted=_promoted_questions(
            _ROOT / "knowledge_base" / "FAQ_PROMOTED.md",
            GOLDEN_MD,
        ),
        gap_match=gap_match,
    )
    if not gaps:
        print("ERROR: no knowledge-promotable gaps (only safety gates?)", file=sys.stderr)
        raise SystemExit(1)
    if gap_index >= len(gaps):
        print(f"ERROR: --gap-index {gap_index} out of range ({len(gaps)} gaps)", file=sys.stderr)
        raise SystemExit(1)
    g = gaps[gap_index]
    question = g["question"]
    log_id = (g.get("log_ids") or [None])[0]
    routes = g.get("kb_routes") or ["longevity"]
    kb_route = "servicios" if "servicios" in routes else routes[0]
    if kb_route == "all":
        kb_route = "longevity"
    print(f"Gap #{gap_index}: {question!r} (freq={g['frequency']}, routes={routes})")
    return question, log_id, kb_route


def main() -> None:
    parser = argparse.ArgumentParser(description="HV knowledge promote E2E")
    parser.add_argument("--question", help="Pregunta a promover")
    parser.add_argument("--answer", help="Respuesta autoritativa (requerida salvo --dry-run)")
    parser.add_argument("--kb-route", default="longevity", choices=["servicios", "longevity", "all"])
    parser.add_argument("--from-log-id", help="entry_id del decision_log (idempotencia)")
    parser.add_argument("--notes")
    parser.add_argument("--from-gap", action="store_true", help="Usar gap del log (requiere --answer)")
    parser.add_argument("--gap-index", type=int, default=0)
    parser.add_argument("--gap-match", help="Filtrar gap por substring (ej. amex)")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--log-path", type=Path, help="Ruta decision_log.jsonl")
    parser.add_argument("--api-url", help="POST promote a prod; process sigue en repo local")
    parser.add_argument("--pin", help="HV_ADMIN_PIN (API)")
    parser.add_argument("--pending-path", type=Path, default=PENDING_PATH)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-embed", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    parser.add_argument("--pgvector", action="store_true", help="Re-embed Neon si HV_DATABASE_URL")
    args = parser.parse_args()

    if args.api_url and not args.pin:
        print("ERROR: --api-url requiere --pin", file=sys.stderr)
        raise SystemExit(1)

    question = args.question
    from_log_id = args.from_log_id
    kb_route = args.kb_route

    if args.from_gap:
        if not args.answer and not args.dry_run:
            print("ERROR: --from-gap requiere --answer", file=sys.stderr)
            raise SystemExit(1)
        question, gap_log_id, kb_route = _resolve_from_gap(
            gap_index=args.gap_index,
            days=args.days,
            log_path=args.log_path,
            gap_match=args.gap_match,
        )
        from_log_id = from_log_id or gap_log_id

    if not question:
        print("ERROR: --question o --from-gap requerido", file=sys.stderr)
        raise SystemExit(1)
    if not args.answer and not args.dry_run:
        print("ERROR: --answer requerido", file=sys.stderr)
        raise SystemExit(1)

    before_promo_id = _latest_promo_id(GOLDEN_MD)
    pending_before = len(load_pending(args.pending_path))

    print("1/5 Submit promotion")
    if args.api_url:
        result = _submit_via_api(
            api_url=args.api_url,
            pin=args.pin or "",
            question=question,
            answer=args.answer or "(dry-run)",
            kb_route=kb_route,
            from_log_id=from_log_id,
            notes=args.notes,
            dry_run=args.dry_run,
        )
    else:
        result = _submit_local(
            question=question,
            answer=args.answer or "(dry-run)",
            kb_route=kb_route,
            from_log_id=from_log_id,
            notes=args.notes,
            pending_path=args.pending_path,
            dry_run=args.dry_run,
        )
    promo_id = (result.get("promotion") or {}).get("id", "?")
    print(f"   promotion id: {promo_id}")

    if args.api_url and not args.dry_run:
        print("   (API mode: fetch pending from prod before process, or copy pending JSON locally)")
        fetch_cmd = [
            "curl", "-sL",
            "-H", f"x-admin-pin: {args.pin}",
            f"{args.api_url.rstrip('/')}/admin/knowledge/pending",
            "-o", str(args.pending_path),
        ]
        _run(fetch_cmd, dry_run=False)
        try:
            data = json.loads(args.pending_path.read_text(encoding="utf-8"))
            promotions = data.get("promotions", data if isinstance(data, list) else [])
            args.pending_path.write_text(
                json.dumps(promotions, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"   fetched {len(promotions)} pending from prod")
        except (json.JSONDecodeError, OSError) as e:
            print(f"WARN: could not parse pending fetch: {e}", file=sys.stderr)

    print("2/5 Process pending → FAQ + golden")
    proc_cmd = [sys.executable, "scripts/process_knowledge_promotions.py"]
    if args.dry_run:
        proc_cmd.append("--dry-run")
    _run(proc_cmd, dry_run=args.dry_run)

    print("3/5 Sync golden-set MD → JSON")
    sync_cmd = [sys.executable, "scripts/sync_golden_set.py", "--validate"]
    _run(sync_cmd, dry_run=args.dry_run)

    if not args.skip_embed:
        print("4/5 Re-embed local index")
        if not args.dry_run and not os.getenv("OPENAI_API_KEY"):
            print("WARN: OPENAI_API_KEY missing — skip embed (use --skip-embed to silence)", file=sys.stderr)
        else:
            _run([sys.executable, "embed_kb_local.py", "--source", "all"], dry_run=args.dry_run)
            if args.pgvector and os.getenv("HV_DATABASE_URL"):
                _run([sys.executable, "embed_kb_pgvector.py", "--source", "all"], dry_run=args.dry_run)
    else:
        print("4/5 Re-embed (skipped)")

    new_promo_id = _latest_promo_id(GOLDEN_MD)
    if not args.dry_run and new_promo_id == before_promo_id and pending_before < len(load_pending(args.pending_path)):
        print("WARN: golden P-id unchanged — process may have failed partially", file=sys.stderr)

    if not args.skip_verify and new_promo_id and not args.dry_run:
        print(f"5/5 Verify golden {new_promo_id}")
        if not os.getenv("OPENAI_API_KEY"):
            print("WARN: skip --full verify (no OPENAI_API_KEY); routing-only", file=sys.stderr)
            _run(
                [sys.executable, "golden_runner.py", "--gates-only", "--id", new_promo_id],
                dry_run=False,
            )
        else:
            _run(
                [sys.executable, "golden_runner.py", "--full", "--id", new_promo_id],
                dry_run=False,
            )
    else:
        print("5/5 Verify (skipped)")

    print("\nDone. promote_e2e OK")
    if new_promo_id and new_promo_id != before_promo_id:
        print(f"New golden scenario: {new_promo_id}")


if __name__ == "__main__":
    main()