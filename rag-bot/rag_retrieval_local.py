#!/usr/bin/env python3
"""
RAG local: JSON embeddings + cosine in-memory + gates HV.
Un motor, dos rutas: servicios (ChatVigente) y longevity (Motor MVP-0).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

from beta_state import (
    beta_id_from_intake,
    derive_state_from_intake,
    load_state,
    record_turn,
    save_state,
)
from decision_log import log_from_rag_result
from frozen_context import build_frozen_context, gate_probe_text, resolve_intake
from confidence_gate import (
    CAVEAT_FOOTER,
    NO_MATCH_MESSAGE,
    decide_rag_path,
    score_to_confidence,
)
from kb_pipeline import (
    CONFIDENCE_WEIGHTS,
    COSINE_HIGH,
    COSINE_MIN,
    SCORE_COSINE_WEIGHT,
    SCORE_META_WEIGHT,
    TIER_WEIGHTS,
)
from prompts import build_system_prompt, build_user_prompt
from query_preprocess import strip_command_words

load_dotenv()

def _default_index_path() -> Path:
    raw = os.getenv("HV_EMBEDDINGS_INDEX", "knowledge_base/embeddings_local.json")
    return Path(raw)


DEFAULT_INDEX = _default_index_path()
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

SERVICIOS_HINTS = re.compile(
    r"\b(hifu|botox|fillers?|sculptra|rf\s*microneedling|láser|laser|depilación|"
    r"corte|barba|manicure|pedicure|blanqueamiento|limpieza facial|precio|cuesta|"
    r"sesión|sesiones|servicio|clínica estética)\b",
    re.I,
)
LONGEVITY_HINTS = re.compile(
    r"\b(nmn|nad\+?|resveratrol|fisetina|quercetina|spermidina|bpc-?157|tb-?500|"
    r"ghk|tesamorelin|khavinson|homocisteína|homocisteina|vitamina\s*d|omega-?3|"
    r"magnesio|coq10|tmg|wearable|hrv|ayuno|sauna|biomarcador|longevidad|"
    r"inflammaging|senolític|peptid|suplemento|25\(oh\)d|apo\s*b|"
    r"litio|leptina|ciática|ciatica|discopatía|discopatia|lumbar|radicular|"
    r"pfirrmann|resonancia|rm\s*lumbar)\b",
    re.I,
)
INJECTABLE_PEPTIDE = re.compile(
    r"\b(bpc-?157|tb-?500|tβ-?4|thymosin|tesamorelin|peptid[oa]s?\s+inyect|"
    r"inyectable|subcutáne|magistral)\b",
    re.I,
)
PSYCH_GATE = re.compile(r"\b(litio|quetiapina|bipolar|psiquiatr)\b", re.I)
PSYCH_COMPOUND = re.compile(r"\b(cerluten|khavinson|endoluten|neuromodul)\b", re.I)
PSYCH_LIFESTYLE = re.compile(r"\b(ayuno|fasting|16:8|intermitente)\b", re.I)
ONCO_GATE = re.compile(
    r"\b(oncológ\w*|antecedente\s+oncológ\w*|antecedente.*c[aá]ncer|c[aá]ncer activo|tumor|cancer)\b",
    re.I,
)
SENOLYTIC = re.compile(r"\b(senolític|fisetina|d\+q|dasatinib|quercetina)\b", re.I)


@dataclass
class GateResult:
    triggered: bool
    code: str = ""
    message: str = ""


def detect_kb_route(query: str) -> str:
    q = query.lower()
    long_score = len(LONGEVITY_HINTS.findall(q))
    serv_score = len(SERVICIOS_HINTS.findall(q))
    if long_score > serv_score:
        return "longevity"
    if serv_score > long_score:
        return "servicios"
    return "all"


def check_gates(query: str, kb_route: str) -> GateResult:
    if kb_route != "longevity" and not INJECTABLE_PEPTIDE.search(query):
        return GateResult(False)

    if INJECTABLE_PEPTIDE.search(query):
        return GateResult(
            True,
            "avenida_2_peptido",
            "Los péptidos inyectables y compuestos de Avenida 2 requieren médico responsable, "
            "prescripción y farmacia autorizada. HV no entrega protocolos Rx por este canal. "
            "Agenda valoración médica.",
        )

    if PSYCH_GATE.search(query) and (
        PSYCH_COMPOUND.search(query) or PSYCH_LIFESTYLE.search(query)
    ):
        return GateResult(
            True,
            "gate_psiquiatria",
            "Con litio, quetiapina o condición psiquiátrica + neuromoduladores o cambios de ayuno/hidratación, "
            "la decisión es exclusiva de tu psiquiatra. No ajustamos ni recomendamos por aquí.",
        )

    if ONCO_GATE.search(query) and SENOLYTIC.search(query):
        return GateResult(
            True,
            "gate_oncologia",
            "Antecedente oncológico + senolíticos/inmunomoduladores: requiere oncólogo/médico tratante "
            "antes de cualquier consideración educativa.",
        )

    return GateResult(False)


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _tier_weight(tier: str) -> float:
    return TIER_WEIGHTS.get(tier.upper(), 0.65)


def _confidence_weight(conf: str) -> float:
    return CONFIDENCE_WEIGHTS.get(conf.lower(), 0.70)


def _combined_score(cosine: float, meta: Dict) -> float:
    tier_w = _tier_weight(meta.get("evidencia_tier", "unknown"))
    if meta.get("doc_subtype") == "tarjeta":
        tier_w = max(tier_w, _confidence_weight(meta.get("confianza", "media")))
    return SCORE_COSINE_WEIGHT * cosine + SCORE_META_WEIGHT * tier_w


def load_index(path: Path = DEFAULT_INDEX) -> Dict:
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta: python embed_kb_local.py --source all"
        )
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def embed_query(query: str, *, preprocess: bool = True) -> List[float]:
    from openai import OpenAI

    text = strip_command_words(query) if preprocess else query
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        encoding_format="float",
    )
    return response.data[0].embedding


def _retrieval_backend() -> str:
    return os.getenv("HV_RETRIEVAL_BACKEND", "json").lower()


def retrieve_chunks(
    query: str,
    index: Dict,
    *,
    kb_route: str = "all",
    top_k: int = 5,
    avenida_max: str = "1",
    min_confidence: str = "medium",
) -> List[Dict]:
    if _retrieval_backend() == "pgvector":
        try:
            from pgvector_retrieval import is_pgvector_configured, retrieve_pgvector

            if is_pgvector_configured():
                return retrieve_pgvector(
                    query,
                    kb_route=kb_route,
                    top_k=top_k,
                    avenida_max=avenida_max,
                    min_confidence=min_confidence,
                )
        except Exception as e:
            print(f"[rag] pgvector fallback → json: {e}")
    return retrieve(
        query,
        index,
        kb_route=kb_route,
        top_k=top_k,
        avenida_max=avenida_max,
        min_confidence=min_confidence,
    )


def retrieve(
    query: str,
    index: Dict,
    kb_route: str = "all",
    top_k: int = 5,
    avenida_max: str = "1",
    min_confidence: str = "medium",
) -> List[Dict]:
    query_vec = embed_query(query)
    candidates: List[Dict] = []

    for chunk in index.get("chunks", []):
        meta = chunk.get("metadata", {})
        kb_type = meta.get("kb_type", "")
        if kb_route != "all" and kb_type != kb_route:
            continue
        if meta.get("has_falta_fuente"):
            continue
        if meta.get("flag_seguridad") == "alto-riesgo" and kb_route == "longevity":
            continue

        avenida = meta.get("avenida_hv", "unknown")
        if avenida_max == "1" and avenida == "2":
            continue

        emb = chunk.get("embedding")
        if not emb:
            continue

        cosine = _cosine(query_vec, emb)
        combined = _combined_score(cosine, meta)
        conf = score_to_confidence(combined)

        if kb_route == "longevity" and conf == "low":
            continue
        if min_confidence == "high" and conf != "high":
            continue

        candidates.append({
            "id": chunk["id"],
            "text": chunk["text"],
            "cosine": cosine,
            "score": combined,
            "confidence": conf,
            "service_name": meta.get("service_name", ""),
            "section_title": meta.get("section_title", ""),
            "kb_type": kb_type,
            "metadata": meta,
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]


def generate_answer(
    query: str,
    chunks: List[Dict],
    kb_route: str,
    *,
    role: str = "default",
    confidence: str = "high",
    avenida_max: str = "1",
    frozen_context: Optional[str] = None,
) -> str:
    from openai import OpenAI

    system = build_system_prompt(
        kb_route,
        role=role,
        confidence=confidence,
        avenida_max=avenida_max,
    )
    user = build_user_prompt(query, chunks, frozen_context=frozen_context)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=800,
    )
    answer = response.choices[0].message.content or ""
    if confidence == "medium" and CAVEAT_FOOTER.strip() not in answer:
        answer += CAVEAT_FOOTER
    return answer


def _attach_log(
    result: Dict,
    *,
    query_normalized: str,
    role: str,
    source: str,
    use_llm: bool,
    t0: float,
    log: bool,
    beta_id: Optional[str] = None,
    turn_number: Optional[int] = None,
    channel: Optional[str] = None,
) -> Dict:
    latency_ms = int((time.perf_counter() - t0) * 1000)
    result["latency_ms"] = latency_ms
    if beta_id:
        result["beta_id"] = beta_id
    if turn_number is not None:
        result["turn_number"] = turn_number
    if log:
        entry_id = log_from_rag_result(
            result,
            query_normalized=query_normalized,
            role=role,
            source=source,
            use_llm=use_llm,
            latency_ms=latency_ms,
            beta_id=beta_id,
            turn_number=turn_number,
            channel=channel,
        )
        if entry_id:
            result["decision_id"] = entry_id
    return result


def _beta_turn_context(
    intake: Optional[Dict],
    beta_id: Optional[str],
    channel: Optional[str],
) -> Tuple[Optional[str], Optional[int]]:
    """Incrementa turno persistido; devuelve (beta_id, turn_number)."""
    bid = beta_id
    if intake and not bid:
        bid = beta_id_from_intake(intake)
    if not bid:
        return None, None

    state = load_state(bid)
    if state is None and intake is not None:
        state = derive_state_from_intake(intake)
    if state is None:
        return bid, None

    record_turn(state, channel=channel or "cli")
    save_state(state)
    return bid, state.turn_count


def rag_query_local(
    query: str,
    index_path: Path = DEFAULT_INDEX,
    kb_route: Optional[str] = None,
    top_k: int = 5,
    avenida_max: str = "1",
    use_llm: bool = True,
    role: str = "default",
    parse: bool = False,
    verbose: bool = False,
    source: str = "cli",
    log: bool = True,
    *,
    intake: Optional[Dict] = None,
    intake_path: Optional[Path | str] = None,
    beta_id: Optional[str] = None,
    channel: Optional[str] = None,
) -> Dict:
    t0 = time.perf_counter()
    intake, beta_id = resolve_intake(intake=intake, intake_path=intake_path, beta_id=beta_id)
    frozen = build_frozen_context(intake) if intake else ""
    bid, turn_no = _beta_turn_context(intake, beta_id, channel)

    route = kb_route or detect_kb_route(query)
    query_normalized = strip_command_words(query)
    probe = gate_probe_text(query, frozen)
    gate = check_gates(probe, route if route != "all" else "longevity")

    if gate.triggered:
        out = {
            "query": query,
            "kb_route": route,
            "gate": gate.code,
            "answer": gate.message,
            "sources": [],
            "confidence": "blocked",
            "gate_path": "blocked",
            "chunks_used": 0,
        }
        if frozen:
            out["frozen_context"] = frozen
        if bid:
            out["beta_id"] = bid
        if turn_no is not None:
            out["turn_number"] = turn_no
        if parse:
            out["parse"] = {
                "query_normalized": query_normalized,
                "gate_triggered": True,
                "gate_code": gate.code,
                "has_frozen_context": bool(frozen),
            }
        return _attach_log(
            out,
            query_normalized=query_normalized,
            role=role,
            source=source,
            use_llm=use_llm,
            t0=t0,
            log=log,
            beta_id=bid,
            turn_number=turn_no,
            channel=channel,
        )

    index = load_index(index_path)
    search_route = route if route != "all" else "all"
    chunks = retrieve_chunks(
        query,
        index,
        kb_route=search_route,
        top_k=top_k,
        avenida_max=avenida_max,
    )

    if not chunks:
        out = {
            "query": query,
            "kb_route": route,
            "answer": NO_MATCH_MESSAGE,
            "sources": [],
            "confidence": "low",
            "gate_path": "escalate",
            "chunks_used": 0,
        }
        if frozen:
            out["frozen_context"] = frozen
        if bid:
            out["beta_id"] = bid
        if turn_no is not None:
            out["turn_number"] = turn_no
        if parse:
            out["parse"] = {
                "query_normalized": query_normalized,
                "detected_route": route,
                "gate_triggered": False,
                "top_score": 0.0,
                "verdict": "escalate",
                "has_frozen_context": bool(frozen),
            }
        return _attach_log(
            out,
            query_normalized=query_normalized,
            role=role,
            source=source,
            use_llm=use_llm,
            t0=t0,
            log=log,
            beta_id=bid,
            turn_number=turn_no,
            channel=channel,
        )

    top_score = chunks[0]["score"]
    top_conf = chunks[0]["confidence"]
    verdict = decide_rag_path(top_score)
    gen_route = route if route != "all" else chunks[0]["kb_type"]

    if verdict.path == "escalate":
        answer = NO_MATCH_MESSAGE
    elif use_llm and os.getenv("OPENAI_API_KEY"):
        answer = generate_answer(
            query,
            chunks,
            gen_route,
            role=role,
            confidence=top_conf,
            avenida_max=avenida_max,
            frozen_context=frozen or None,
        )
    else:
        answer = _format_template(query, chunks, route)

    result = {
        "query": query,
        "kb_route": route,
        "role": role,
        "confidence": top_conf,
        "gate_path": verdict.path,
        "gate_reason": verdict.reason,
        "thresholds": {"COSINE_HIGH": COSINE_HIGH, "COSINE_MIN": COSINE_MIN},
        "answer": answer,
        "sources": [
            {
                "service": c["service_name"],
                "section": c["section_title"],
                "score": round(c["score"], 3),
                "cosine": round(c["cosine"], 3),
                "confidence": c["confidence"],
            }
            for c in chunks
        ],
        "chunks_used": len(chunks),
    }

    if frozen:
        result["frozen_context"] = frozen
    if bid:
        result["beta_id"] = bid
    if turn_no is not None:
        result["turn_number"] = turn_no

    if parse:
        result["parse"] = {
            "query_normalized": query_normalized,
            "detected_route": route,
            "gate_triggered": False,
            "top_score": round(top_score, 4),
            "verdict": verdict.path,
            "verdict_reason": verdict.reason,
            "has_frozen_context": bool(frozen),
            "chunks": [
                {
                    "id": c["id"],
                    "service": c["service_name"],
                    "section": c["section_title"],
                    "score": round(c["score"], 4),
                    "cosine": round(c["cosine"], 4),
                    "confidence": c["confidence"],
                    "kb_type": c.get("kb_type"),
                    "tier": c.get("metadata", {}).get("evidencia_tier"),
                }
                for c in chunks
            ],
        }

    if verbose:
        print(f"route={route} confidence={top_conf} chunks={len(chunks)}")
        for c in chunks[:3]:
            print(f"  - {c['service_name']} | {c['section_title']} | {c['score']:.3f}")

    return _attach_log(
        result,
        query_normalized=query_normalized,
        role=role,
        source=source,
        use_llm=use_llm,
        t0=t0,
        log=log,
        beta_id=bid,
        turn_number=turn_no,
        channel=channel,
    )


def _format_template(query: str, chunks: List[Dict], route: str) -> str:
    lines = [f"**Consulta:** {query}\n"]
    for i, c in enumerate(chunks[:3], 1):
        excerpt = c["text"][:600].strip()
        lines.append(f"**{i}. {c['service_name']}** ({c['section_title']}, score {c['score']:.2f})\n{excerpt}\n")
    lines.append(
        "\n*Información educativa de optimización. No es diagnóstico ni tratamiento médico.*"
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="RAG local JSON + gates HV")
    parser.add_argument("query", nargs="*", help="Pregunta")
    parser.add_argument("--route", choices=["servicios", "longevity", "all"])
    parser.add_argument("--no-llm", action="store_true", help="Solo retrieval + template")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--intake", help="Ruta intake JSON (frozen context)")
    parser.add_argument("--beta-id", help="beta_id (row-0, caso0, tally-…)")
    parser.add_argument("--channel", default="cli")
    args = parser.parse_args()

    if not args.query:
        parser.error("Proporciona una pregunta")

    q = " ".join(args.query)
    result = rag_query_local(
        q,
        kb_route=args.route,
        top_k=args.top_k,
        use_llm=not args.no_llm,
        verbose=True,
        intake_path=args.intake,
        beta_id=args.beta_id,
        channel=args.channel,
        log=False,
    )
    print("\n" + "=" * 60)
    print(result["answer"])
    if result.get("gate"):
        print(f"\n[GATE: {result['gate']}]")


if __name__ == "__main__":
    main()