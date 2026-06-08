#!/usr/bin/env python3
"""
Simula tráfico RAG → decision_log (para gaps detector y knowledge loop).

  python scripts/simulate_traffic.py
  python scripts/simulate_traffic.py --count 40 --seed 42
  python scripts/simulate_traffic.py --synthetic-only
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from decision_log import RagDecisionEntry, log_rag_decision
from rag_retrieval_local import rag_query_local

GOLDEN_PATH = _ROOT / "data" / "golden-set-hv-rag.json"

SYNTHETIC_GAPS = [
    ("¿aceptan criptomonedas?", "criptomonedas pago", "all", "escalate", 0.22, 0),
    ("horario del costco cerca", "horario costco", "all", "escalate", 0.18, 0),
    ("precio bitcoin hoy", "precio bitcoin", "all", "escalate", 0.25, 0),
    ("¿venden seguros de auto?", "seguros auto", "all", "escalate", 0.31, 0),
    ("cuánto cuesta un Tesla", "precio tesla", "all", "escalate", 0.28, 0),
    ("¿tienen vacuna COVID?", "vacuna covid", "servicios", "escalate", 0.35, 0),
    ("¿horario del lounge?", "horario lounge", "servicios", "caveat", 0.52, 2),
    ("¿aceptan AMEX?", "aceptan amex", "servicios", "caveat", 0.48, 1),
]

SOURCES = ("api", "whatsapp", "cli", "concierge")


def _load_golden_questions(*, gate_only: bool = False) -> list[str]:
    if not GOLDEN_PATH.exists():
        return []
    data = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    scenarios = data.get("scenarios", [])
    if gate_only:
        scenarios = [s for s in scenarios if s.get("mode") == "gate"]
    return [s["question"] for s in scenarios if s.get("question")]


def _log_synthetic(
    *,
    log_path: Path,
    rng: random.Random,
    spread_days: int,
) -> int:
    n = 0
    for _ in range(rng.randint(2, 4)):
        q, q_norm, route, gate_path, score, chunks = rng.choice(SYNTHETIC_GAPS)
        ts = datetime.now(timezone.utc) - timedelta(
            hours=rng.randint(0, spread_days * 24)
        )
        entry = RagDecisionEntry(
            query=q,
            query_normalized=q_norm,
            kb_route=route,
            gate_path=gate_path,
            role=rng.choice(("default", "concierge")),
            top_score=score,
            confidence="low" if score < 0.55 else "medium",
            chunks_used=chunks,
            source=rng.choice(SOURCES),
            use_llm=False,
            timestamp=ts.isoformat(),
        )
        log_rag_decision(entry, path=log_path)
        n += 1
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description="Simula tráfico RAG en decision_log")
    parser.add_argument("--count", type=int, default=30, help="Queries reales a ejecutar")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--log-path", type=Path, default=_ROOT / "data" / "decision_log.jsonl")
    parser.add_argument("--synthetic-only", action="store_true")
    parser.add_argument("--llm", action="store_true", help="Usar LLM (requiere API key)")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    args.log_path.parent.mkdir(parents=True, exist_ok=True)

    real_n = 0
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    if not args.synthetic_only:
        if not has_key:
            print("WARN: sin OPENAI_API_KEY — solo gates + synthetic", file=sys.stderr)
        pool = _load_golden_questions(gate_only=not has_key)
        if has_key:
            pool += [
                "¿cuánto cuesta HIFU?",
                "qué es homocisteína",
                "botox entrecejo precio",
                "NMN dosis recomendada",
                "depilación láser piernas",
            ]
        if not pool:
            print("WARN: sin preguntas — solo synthetic", file=sys.stderr)
        else:
            index_ok = (_ROOT / "knowledge_base" / "embeddings_local.json").exists()
            needs_index = has_key
            if needs_index and not index_ok:
                print("WARN: sin índice JSON — saltando queries reales", file=sys.stderr)
            else:
                for _ in range(args.count):
                    q = rng.choice(pool)
                    try:
                        rag_query_local(
                            q,
                            use_llm=args.llm and has_key,
                            log=True,
                            source=rng.choice(SOURCES),
                            role=rng.choice(("default", "concierge")),
                        )
                        real_n += 1
                    except Exception as e:
                        print(f"WARN: query failed ({q[:40]}…): {e}", file=sys.stderr)

    synth_n = _log_synthetic(log_path=args.log_path, rng=rng, spread_days=7)
    min_synth = max(3, args.count // 5)
    while synth_n < min_synth:
        synth_n += _log_synthetic(log_path=args.log_path, rng=rng, spread_days=7)
    total = real_n + synth_n
    print(f"Simulated traffic: {real_n} live queries + {synth_n} synthetic gaps → {args.log_path}")
    print(f"Next: python knowledge_gap_detector.py --write-report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())