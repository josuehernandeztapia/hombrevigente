#!/usr/bin/env python3
"""
Sync golden-set-hv-rag.md → data/golden-set-hv-rag.json

  python scripts/sync_golden_set.py
  python scripts/sync_golden_set.py --validate
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROFILE_PREFIX = {"G": "gate", "L": "longevity", "S": "servicios", "P": "promoted"}


def field(block: str, name: str, multiline: bool = False):
    if multiline:
        pattern = rf"\*\*{re.escape(name)}:\*\*\n((?:[-•].*\n?)+)"
        m = re.search(pattern, block)
        if m:
            return [b.strip() for b in re.findall(r"[-•]\s*(.+)", m.group(1))]
        return None
    pattern = rf"\*\*{re.escape(name)}:\*\*\s*`?(.+?)`?\s*(?:\n|$)"
    m = re.search(pattern, block)
    return m.group(1).strip() if m else None


def parse_scenario_block(block: str) -> dict | None:
    header_match = re.match(r"^###\s+([GLSP]-\d{3}):\s+(.+?)\n", block)
    if not header_match:
        return None

    scenario_id = header_match.group(1).strip()
    title = header_match.group(2).strip()
    profile = PROFILE_PREFIX.get(scenario_id[0])
    if not profile:
        return None

    question = field(block, "Pregunta")
    topic = field(block, "Topic")
    mode = field(block, "Modo")
    expected_route = field(block, "Ruta esperada")
    expected = field(block, "Respuesta esperada", multiline=True)
    criticality = field(block, "Criticidad")

    if not question or not criticality:
        return None

    question = question.strip("`").strip()
    if criticality.startswith("P"):
        criticality = criticality.split()[0].strip()

    traits = expected or []
    parsed_traits = {
        "must_contain_any": [],
        "must_not_contain": [],
        "expected_gate": None,
        "no_gate": False,
        "expected_route": expected_route,
        "expected_gate_path": None,
        "expected_gate_path_any": None,
    }

    for t in traits:
        low = t.lower()
        if low.startswith("gate "):
            parsed_traits["expected_gate"] = t.split("gate", 1)[1].strip()
        elif "no debe activar gate" in low:
            parsed_traits["no_gate"] = True
        elif low.startswith("kb_route "):
            parsed_traits["expected_route"] = t.split("kb_route", 1)[1].strip()
        elif low.startswith("gate_path "):
            rest = t.split("gate_path", 1)[1].strip()
            if " o " in rest.lower():
                parsed_traits["expected_gate_path_any"] = [
                    x.strip() for x in re.split(r"\s+o\s+", rest, flags=re.I)
                ]
            else:
                parsed_traits["expected_gate_path"] = rest.split()[0]
        elif low.startswith("no "):
            parsed_traits["must_not_contain"].append(t[3:].strip())
        elif low.startswith("source contiene "):
            parsed_traits["must_contain_any"].append(t.split("contiene", 1)[1].strip())
        elif low.startswith("answer o source menciona "):
            parsed_traits["must_contain_any"].append(t.split("menciona", 1)[1].strip())
        elif low.startswith("menciona "):
            parsed_traits["must_contain_any"].append(t.split("menciona", 1)[1].strip())
        else:
            parsed_traits["must_contain_any"].append(t)

    return {
        "id": scenario_id,
        "profile": profile,
        "title": title,
        "question": question,
        "topic": topic,
        "mode": mode or "retrieval",
        "expected_traits": traits,
        "parsed": parsed_traits,
        "criticality": criticality,
    }


def parse_md(md_path: Path) -> list[dict]:
    content = md_path.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^###\s+[GLSP]-\d{3}:)", content, flags=re.MULTILINE)
    scenarios = []
    for block in blocks:
        if not re.match(r"^###\s+[GLSP]-\d{3}:", block):
            continue
        parsed = parse_scenario_block(block)
        if parsed:
            scenarios.append(parsed)
    return scenarios


def main():
    root = Path(__file__).resolve().parent.parent
    md_path = root / "docs" / "qa" / "golden-set-hv-rag.md"
    json_path = root / "data" / "golden-set-hv-rag.json"

    if not md_path.exists():
        print(f"ERROR: {md_path} not found", file=sys.stderr)
        sys.exit(1)

    scenarios = parse_md(md_path)
    if len(scenarios) < 20:
        print(f"WARN: expected 20 scenarios, got {len(scenarios)}", file=sys.stderr)

    payload = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_md": "docs/qa/golden-set-hv-rag.md",
        "total_scenarios": len(scenarios),
        "scenarios": scenarios,
    }

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(scenarios)} scenarios → {json_path}")

    if "--validate" in sys.argv:
        ids = [s["id"] for s in scenarios]
        assert len(ids) == len(set(ids)), "duplicate scenario IDs"
        p0 = sum(1 for s in scenarios if s["criticality"] == "P0")
        print(f"Validate OK: {len(scenarios)} scenarios, {p0} P0")


if __name__ == "__main__":
    main()