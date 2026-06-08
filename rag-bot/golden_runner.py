#!/usr/bin/env python3
"""
Ejecuta golden-set HV y reporta pass/fail.

  python golden_runner.py --gates-only     # sin API key (CI rápido)
  python golden_runner.py --full           # retrieval + gates (requiere OPENAI_API_KEY)
  python golden_runner.py --full --llm       # incluye generación LLM (lento, costoso)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from rag_retrieval_local import (
    check_gates,
    detect_kb_route,
    rag_query_local,
)

load_dotenv()

GOLDEN_PATH = Path("data/golden-set-hv-rag.json")


def load_golden() -> List[Dict]:
    if not GOLDEN_PATH.exists():
        raise FileNotFoundError(
            f"{GOLDEN_PATH} missing. Run: python scripts/sync_golden_set.py"
        )
    data = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    return data["scenarios"]


def _text_blob(result: Dict) -> str:
    parts = [result.get("answer", "")]
    for s in result.get("sources", []):
        parts.append(str(s.get("service", "")))
        parts.append(str(s.get("section", "")))
    return " ".join(parts).lower()


def eval_gate_scenario(scenario: Dict) -> tuple[bool, str]:
    q = scenario["question"]
    route = detect_kb_route(q)
    gate = check_gates(q, route if route != "all" else "longevity")
    parsed = scenario["parsed"]

    if parsed.get("no_gate"):
        if gate.triggered:
            return False, f"gate triggered unexpectedly: {gate.code}"
        return True, "no gate (expected)"

    expected = parsed.get("expected_gate")
    if expected:
        if not gate.triggered:
            return False, "gate not triggered"
        if gate.code != expected:
            return False, f"gate {gate.code} != {expected}"
        blob = gate.message.lower()
        for term in parsed.get("must_contain_any", []):
            alts = re.split(r"\s+o\s+", term, flags=re.I)
            if not any(a.strip().lower() in blob for a in alts):
                return False, f"gate message missing: {term}"
        return True, f"gate {gate.code}"

    return True, "gate check skipped"


def eval_routing_scenario(scenario: Dict) -> tuple[bool, str]:
    q = scenario["question"]
    route = detect_kb_route(q)
    expected = scenario["parsed"].get("expected_route") or scenario["parsed"].get("expected_route")
    if not expected:
        return True, f"route={route}"
    if route != expected:
        return False, f"route {route} != {expected}"
    return True, f"route={route}"


def eval_retrieval_scenario(scenario: Dict, *, use_llm: bool) -> tuple[bool, str]:
    result = rag_query_local(scenario["question"], use_llm=use_llm, log=False)
    parsed = scenario["parsed"]
    blob = _text_blob(result)

    if parsed.get("expected_route"):
        if result.get("kb_route") != parsed["expected_route"]:
            return False, f"kb_route {result.get('kb_route')} != {parsed['expected_route']}"

    gp = result.get("gate_path") or result.get("gate", "blocked")
    if parsed.get("expected_gate_path_any"):
        if gp not in parsed["expected_gate_path_any"]:
            return False, f"gate_path {gp} not in {parsed['expected_gate_path_any']}"
    elif parsed.get("expected_gate_path"):
        if parsed["expected_gate_path"] == "escalate":
            if gp != "escalate":
                return False, f"gate_path {gp} expected escalate"
        elif gp != parsed["expected_gate_path"]:
            return False, f"gate_path {gp} != {parsed['expected_gate_path']}"

    for term in parsed.get("must_contain_any", []):
        # split OR terms like "homocisteína o TMG"
        alts = re.split(r"\s+o\s+", term, flags=re.I)
        if not any(a.strip().lower() in blob for a in alts):
            return False, f"missing trait: {term}"

    for term in parsed.get("must_not_contain", []):
        if term.lower() in blob:
            return False, f"forbidden trait present: {term}"

    if "sources vacíos" in " ".join(scenario.get("expected_traits", [])).lower():
        if result.get("sources"):
            return False, "expected empty sources"

    if result.get("gate_path") == "escalate" or not result.get("sources"):
        if "escalate" in " ".join(scenario.get("expected_traits", [])).lower():
            return True, "escalated as expected"

    return True, f"conf={result.get('confidence')} path={result.get('gate_path')}"


def run_scenario(scenario: Dict, *, full: bool, use_llm: bool) -> tuple[bool, str]:
    mode = scenario.get("mode", "retrieval")

    if mode == "gate":
        return eval_gate_scenario(scenario)
    if mode == "routing":
        return eval_routing_scenario(scenario)
    if mode == "retrieval":
        if not full:
            return eval_routing_scenario(scenario)
        return eval_retrieval_scenario(scenario, use_llm=use_llm)

    return False, f"unknown mode {mode}"


def main():
    parser = argparse.ArgumentParser(description="HV golden-set runner")
    parser.add_argument("--gates-only", action="store_true", help="Solo gate + routing")
    parser.add_argument("--full", action="store_true", help="Retrieval completo")
    parser.add_argument("--llm", action="store_true", help="Generar respuestas LLM")
    parser.add_argument("--id", help="Correr un solo escenario por ID")
    args = parser.parse_args()

    full = args.full
    if not args.gates_only and not args.full:
        args.gates_only = True

    if full and not os.getenv("OPENAI_API_KEY"):
        print("ERROR: --full requiere OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)

    scenarios = load_golden()
    if args.id:
        scenarios = [s for s in scenarios if s["id"] == args.id]
        if not scenarios:
            print(f"ID {args.id} not found", file=sys.stderr)
            sys.exit(1)

    passed = failed = 0
    failures: List[Dict[str, Any]] = []

    for sc in scenarios:
        if not full and sc["id"].startswith(("P-", "T-")):
            continue
        ok, detail = run_scenario(sc, full=full, use_llm=args.llm)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {sc['id']} ({sc['criticality']}) {sc['title'][:40]} — {detail}")
        if ok:
            passed += 1
        else:
            failed += 1
            failures.append({"id": sc["id"], "detail": detail, "criticality": sc["criticality"]})

    print(f"\n{passed}/{passed + failed} passed")
    if failures:
        p0_fail = [f for f in failures if f["criticality"] == "P0"]
        if p0_fail:
            print(f"P0 FAILURES: {[f['id'] for f in p0_fail]}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()