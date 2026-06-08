#!/usr/bin/env python3
"""
Expande golden-set con escenarios T-xxx derivados del decision_log (tráfico real).

Agrupa consultas por query_normalized, prioriza frecuencia y retrieval exitoso
(auto/caveat con chunks), excluye preguntas ya cubiertas en G/L/S/P.

  python scripts/expand_golden_from_log.py
  python scripts/expand_golden_from_log.py --days 14 --max 5 --min-frequency 2
  python scripts/expand_golden_from_log.py --dry-run
  python scripts/expand_golden_from_log.py && python scripts/sync_golden_set.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from decision_log import read_decisions
from kb_pipeline import COSINE_MIN
from knowledge_gap_detector import _cluster_key, is_gap_row
from query_preprocess import strip_command_words

GOLDEN_MD_PATH = _ROOT / "docs" / "qa" / "golden-set-hv-rag.md"
GOLDEN_JSON_PATH = _ROOT / "data" / "golden-set-hv-rag.json"
TRAFFIC_SECTION = "## Tráfico real (T)"


def _normalize_question(q: str) -> str:
    return strip_command_words(q).lower().strip()


def _load_existing_questions(*, golden_md: Path, golden_json: Path) -> Set[str]:
    existing: Set[str] = set()
    if golden_json.exists():
        data = json.loads(golden_json.read_text(encoding="utf-8"))
        for sc in data.get("scenarios", []):
            existing.add(_normalize_question(sc.get("question", "")))
    if golden_md.exists():
        for m in re.finditer(r"\*\*Pregunta:\*\*\s*`([^`]+)`", golden_md.read_text(encoding="utf-8")):
            existing.add(_normalize_question(m.group(1)))
    return existing


def _next_traffic_id(content: str) -> str:
    ids = re.findall(r"###\s+(T-\d{3}):", content)
    n = max((int(x.split("-")[1]) for x in ids), default=0) + 1
    return f"T-{n:03d}"


def _dominant(counter: Counter) -> str | None:
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def _service_keyword(service: str | None) -> str | None:
    if not service:
        return None
    s = service.strip()
    if not s:
        return None
    head = re.split(r"\s*[—(\[]", s)[0].strip()
    return head if len(head) >= 3 else s[:40]


def cluster_traffic(
    rows: List[Dict[str, Any]],
    *,
    gap_threshold: float,
    include_gaps: bool = False,
) -> Dict[str, Dict[str, Any]]:
    clusters: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "question": "",
            "frequency": 0,
            "kb_routes": Counter(),
            "gate_paths": Counter(),
            "top_services": Counter(),
            "max_score": 0.0,
            "gap_hits": 0,
            "success_hits": 0,
        }
    )

    for row in rows:
        is_gap = is_gap_row(row, gap_threshold=gap_threshold)
        gate_path = row.get("gate_path", "")
        if is_gap and not include_gaps:
            continue
        if gate_path == "blocked":
            continue

        q_display = (row.get("query") or row.get("query_normalized") or "").strip()
        q_norm = row.get("query_normalized") or q_display
        key = _cluster_key(q_norm)
        if not key or len(key) < 4:
            continue

        c = clusters[key]
        if not c["question"] or len(q_display) > len(c["question"]):
            c["question"] = q_display
        c["frequency"] += 1
        c["kb_routes"][row.get("kb_route", "all")] += 1
        c["gate_paths"][gate_path] += 1
        svc = row.get("top_service")
        if svc:
            kw = _service_keyword(str(svc))
            if kw:
                c["top_services"][kw] += 1
        score = row.get("top_score")
        if score is not None:
            c["max_score"] = max(c["max_score"], float(score))
        if is_gap:
            c["gap_hits"] += 1
        elif gate_path in ("auto", "caveat") and int(row.get("chunks_used") or 0) > 0:
            c["success_hits"] += 1

    return clusters


def pick_candidates(
    clusters: Dict[str, Dict[str, Any]],
    existing: Set[str],
    *,
    min_frequency: int,
    max_add: int,
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for key, c in clusters.items():
        if c["frequency"] < min_frequency:
            continue
        if _normalize_question(c["question"]) in existing:
            continue
        if c["success_hits"] == 0 and c["gap_hits"] > 0:
            continue
        candidates.append({**c, "cluster_key": key})

    candidates.sort(
        key=lambda x: (-x["success_hits"], -x["frequency"], -x["max_score"]),
    )
    return candidates[:max_add]


def _resolve_kb_route(counter: Counter) -> str:
    route = _dominant(counter)
    if route in ("servicios", "longevity"):
        return route
    if counter.get("servicios", 0) >= counter.get("longevity", 0) and counter.get("servicios"):
        return "servicios"
    return "longevity"


def _gate_path_trait(counter: Counter) -> str:
    paths = [p for p, _ in counter.most_common() if p in ("auto", "caveat", "escalate")]
    if not paths:
        return "gate_path auto o caveat"
    if len(paths) == 1:
        return f"gate_path {paths[0]}"
    if set(paths) <= {"auto", "caveat"}:
        return "gate_path auto o caveat"
    return f"gate_path {paths[0]}"


def format_scenario_block(scenario_id: str, cand: Dict[str, Any]) -> str:
    q = cand["question"]
    route = _resolve_kb_route(cand["kb_routes"])
    gate_trait = _gate_path_trait(cand["gate_paths"])
    svc = _dominant(cand["top_services"])
    traits = [
        f"- kb_route {route}",
        f"- {gate_trait}",
    ]
    if svc:
        traits.append(f"- source contiene {svc}")
    topic = f"traffic-{cand['cluster_key'][:40]}"

    return (
        f"\n### {scenario_id}: tráfico real\n\n"
        f"**Pregunta:** `{q}`\n"
        f"**Topic:** {topic}\n"
        f"**Modo:** retrieval\n"
        f"**Ruta esperada:** {route}\n"
        f"**Respuesta esperada:**\n"
        + "\n".join(traits)
        + "\n"
        f"**Criticidad:** P1\n"
        f"**Notas:** Auto from log freq={cand['frequency']} "
        f"success={cand['success_hits']} {datetime.now(timezone.utc).isoformat()}\n"
    )


def ensure_traffic_section(md_text: str) -> str:
    if TRAFFIC_SECTION in md_text:
        return md_text
    return md_text.rstrip() + f"\n\n---\n\n{TRAFFIC_SECTION}\n"


def append_scenarios(
    golden_md: Path,
    candidates: List[Dict[str, Any]],
    *,
    dry_run: bool,
) -> List[str]:
    if not candidates:
        return []

    content = golden_md.read_text(encoding="utf-8") if golden_md.exists() else ""
    content = ensure_traffic_section(content)
    added_ids: List[str] = []

    for cand in candidates:
        sid = _next_traffic_id(content)
        block = format_scenario_block(sid, cand)
        if dry_run:
            print(f"  [dry-run] would add {sid}: {cand['question'][:60]}...")
        else:
            content += block
        added_ids.append(sid)

    if not dry_run:
        golden_md.write_text(content, encoding="utf-8")

    return added_ids


def main() -> None:
    parser = argparse.ArgumentParser(description="Expand golden set from decision_log traffic")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--log-path", type=Path, help="decision_log.jsonl")
    parser.add_argument("--golden-md", type=Path, default=GOLDEN_MD_PATH)
    parser.add_argument("--min-frequency", type=int, default=2)
    parser.add_argument("--max", type=int, default=5, dest="max_add")
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--include-gaps", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    threshold = args.threshold if args.threshold is not None else COSINE_MIN
    log_path = args.log_path or (_ROOT / "data" / "decision_log.jsonl")
    rows = read_decisions(days=args.days, path=log_path)
    if not rows:
        print(f"No decisions in last {args.days}d ({log_path}). Exit 0.")
        return

    existing = _load_existing_questions(
        golden_md=args.golden_md,
        golden_json=GOLDEN_JSON_PATH,
    )
    clusters = cluster_traffic(rows, gap_threshold=threshold, include_gaps=args.include_gaps)
    candidates = pick_candidates(
        clusters,
        existing,
        min_frequency=args.min_frequency,
        max_add=args.max_add,
    )

    if not candidates:
        print("No new traffic candidates (all covered or below min-frequency). Exit 0.")
        return

    print(f"Candidates ({len(candidates)}):")
    for c in candidates:
        print(
            f"  - {c['question'][:70]} "
            f"(freq={c['frequency']}, success={c['success_hits']}, "
            f"route={_resolve_kb_route(c['kb_routes'])})"
        )

    added = append_scenarios(args.golden_md, candidates, dry_run=args.dry_run)
    if args.dry_run:
        print(f"Dry-run: would add {len(added)} scenario(s).")
    else:
        print(f"Added {len(added)} scenario(s): {', '.join(added)}")
        print("Next: python scripts/sync_golden_set.py --validate")


if __name__ == "__main__":
    main()