#!/usr/bin/env python3
"""
Detecta knowledge gaps desde decision_log — patrón CMU knowledge-gap-detector.ts.

Preguntas con score < threshold o gate_path escalate/blocked → candidatas a promover.

  python knowledge_gap_detector.py
  python knowledge_gap_detector.py --days 14 --threshold 0.55 --write-report
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from decision_log import read_decisions
from kb_pipeline import COSINE_MIN
from query_preprocess import strip_command_words


def _iso_week(d: Optional[datetime] = None) -> str:
    d = d or datetime.now(timezone.utc)
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def _cluster_key(query_normalized: str) -> str:
    return strip_command_words(query_normalized).lower().strip()


def is_gap_row(
    row: Dict[str, Any],
    *,
    gap_threshold: float,
) -> bool:
    gate_path = row.get("gate_path", "")
    if gate_path in ("escalate", "blocked"):
        return True
    chunks = int(row.get("chunks_used") or 0)
    if chunks == 0:
        return True
    score = row.get("top_score")
    if score is not None and float(score) < gap_threshold:
        return True
    return False


def detect_knowledge_gaps(
    *,
    days: int = 7,
    gap_threshold: Optional[float] = None,
    min_frequency: int = 1,
    max_gaps: int = 20,
    log_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    threshold = gap_threshold if gap_threshold is not None else COSINE_MIN
    rows = read_decisions(days=days, path=log_path)
    clusters: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "question": "",
            "variants": set(),
            "log_ids": [],
            "frequency": 0,
            "max_score": 0.0,
            "gate_paths": set(),
            "kb_routes": set(),
            "first_seen": None,
            "last_seen": None,
        }
    )

    for row in rows:
        if not is_gap_row(row, gap_threshold=threshold):
            continue
        q_norm = row.get("query_normalized") or row.get("query", "")
        key = _cluster_key(q_norm)
        if not key:
            continue
        c = clusters[key]
        if not c["question"]:
            c["question"] = q_norm
        c["variants"].add(row.get("query", q_norm))
        c["log_ids"].append(row.get("entry_id"))
        c["frequency"] += 1
        score = row.get("top_score")
        if score is not None:
            c["max_score"] = max(c["max_score"], float(score))
        c["gate_paths"].add(row.get("gate_path", "?"))
        c["kb_routes"].add(row.get("kb_route", "all"))
        ts = row.get("timestamp")
        if ts:
            if c["first_seen"] is None or ts < c["first_seen"]:
                c["first_seen"] = ts
            if c["last_seen"] is None or ts > c["last_seen"]:
                c["last_seen"] = ts

    gaps: List[Dict[str, Any]] = []
    for key, c in clusters.items():
        if c["frequency"] < min_frequency:
            continue
        gaps.append({
            "question": c["question"],
            "cluster_key": key,
            "frequency": c["frequency"],
            "max_score": round(c["max_score"], 4),
            "gap_threshold": threshold,
            "gate_paths": sorted(c["gate_paths"]),
            "kb_routes": sorted(c["kb_routes"]),
            "variants": sorted(c["variants"])[:5],
            "log_ids": [x for x in c["log_ids"] if x][:10],
            "first_seen": c["first_seen"],
            "last_seen": c["last_seen"],
        })

    gaps.sort(key=lambda g: (-g["frequency"], g["max_score"]))
    return gaps[:max_gaps]


def render_gaps_report(gaps: List[Dict[str, Any]], *, days: int, threshold: float) -> str:
    lines = [
        f"# HV Knowledge Gaps — {_iso_week()}",
        "",
        f"Ventana: últimos **{days}** días · threshold score < **{threshold}**",
        f"Gaps detectados: **{len(gaps)}**",
        "",
    ]
    if not gaps:
        lines.append("_Sin gaps en la ventana._")
        return "\n".join(lines)

    for i, g in enumerate(gaps, 1):
        lines.extend([
            f"## {i}. {g['question'][:80]}",
            "",
            f"- **Frecuencia:** {g['frequency']}",
            f"- **Max score:** {g['max_score']}",
            f"- **Rutas KB:** {', '.join(g['kb_routes'])}",
            f"- **Gate paths:** {', '.join(g['gate_paths'])}",
            f"- **Variantes:** {', '.join(g['variants'][:3])}",
            "",
        ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="HV knowledge gap detector")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--max-gaps", type=int, default=20)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args()

    threshold = args.threshold if args.threshold is not None else COSINE_MIN
    gaps = detect_knowledge_gaps(
        days=args.days,
        gap_threshold=threshold,
        max_gaps=args.max_gaps,
    )

    if args.json:
        print(json.dumps(gaps, indent=2, ensure_ascii=False))
    else:
        print(render_gaps_report(gaps, days=args.days, threshold=threshold))

    if args.write_report:
        out = Path("docs/qa") / f"knowledge-gaps-{_iso_week()}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            render_gaps_report(gaps, days=args.days, threshold=threshold) + "\n",
            encoding="utf-8",
        )
        print(f"\nWrote {out}", flush=True)


if __name__ == "__main__":
    main()