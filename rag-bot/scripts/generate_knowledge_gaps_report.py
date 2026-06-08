#!/usr/bin/env python3
"""
Genera reporte semanal de knowledge gaps.

  python scripts/generate_knowledge_gaps_report.py
  python scripts/generate_knowledge_gaps_report.py --days 14 --from-prod
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from knowledge_gap_detector import _iso_week, detect_knowledge_gaps, render_gaps_report


def _fetch_prod_gaps(*, base_url: str, pin: str, days: int) -> dict:
    url = f"{base_url.rstrip('/')}/admin/knowledge/gaps?days={days}"
    req = urllib.request.Request(url, headers={"x-admin-pin": pin})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="HV knowledge gaps report")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--from-prod", action="store_true", help="Prefer prod API")
    parser.add_argument("--out-dir", type=Path, default=Path("docs/qa"))
    args = parser.parse_args()

    report = ""
    gap_count = 0
    threshold = float(os.getenv("HV_COSINE_MIN", "0.55"))

    base_url = os.getenv("HV_RAG_API_URL", "").strip()
    pin = os.getenv("HV_ADMIN_PIN", "").strip()
    if args.from_prod and base_url and pin:
        try:
            data = _fetch_prod_gaps(base_url=base_url, pin=pin, days=args.days)
            gaps = data.get("gaps", [])
            gap_count = len(gaps)
            threshold = float(data.get("threshold") or threshold)
            report = data.get("report_md") or render_gaps_report(
                gaps, days=args.days, threshold=threshold
            )
            print(f"Fetched {gap_count} gap(s) from prod")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"WARN: prod fetch failed ({e}) — local detector", file=sys.stderr)

    if not report:
        gaps = detect_knowledge_gaps(days=args.days, gap_threshold=threshold)
        gap_count = len(gaps)
        report = render_gaps_report(gaps, days=args.days, threshold=threshold)
        print(f"Local detector: {gap_count} gap(s)")

    out = args.out_dir / f"knowledge-gaps-{_iso_week()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report.rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())