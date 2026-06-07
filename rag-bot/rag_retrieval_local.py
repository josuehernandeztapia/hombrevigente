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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

from kb_pipeline import CONFIDENCE_WEIGHTS, TIER_WEIGHTS

load_dotenv()

DEFAULT_INDEX = Path("knowledge_base/embeddings_local.json")
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
    r"inflammaging|senolític|peptid|suplemento|25\(oh\)d|apo\s*b)\b",
    re.I,
)
INJECTABLE_PEPTIDE = re.compile(
    r"\b(bpc-?157|tb-?500|tβ-?4|thymosin|tesamorelin|peptid[oa]s?\s+inyect|"
    r"inyectable|subcutáne|magistral)\b",
    re.I,
)
PSYCH_GATE = re.compile(r"\b(litio|quetiapina|bipolar|psiquiatr)\b", re.I)
PSYCH_COMPOUND = re.compile(r"\b(cerluten|khavinson|endoluten|neuromodul)\b", re.I)
ONCO_GATE = re.compile(r"\b(oncológ|antecedente.*cáncer|cáncer activo|tumor)\b", re.I)
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

    if PSYCH_GATE.search(query) and PSYCH_COMPOUND.search(query):
        return GateResult(
            True,
            "gate_psiquiatria",
            "Con litio, quetiapina o condición psiquiátrica + neuromoduladores (p. ej. Cerluten/Khavinson), "
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
    return 0.7 * cosine + 0.3 * tier_w


def _confidence_label(score: float) -> str:
    if score >= 0.70:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def load_index(path: Path = DEFAULT_INDEX) -> Dict:
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta: python embed_kb_local.py --source all"
        )
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def embed_query(query: str) -> List[float]:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
        encoding_format="float",
    )
    return response.data[0].embedding


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
        conf = _confidence_label(combined)

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


def generate_answer(query: str, chunks: List[Dict], kb_route: str) -> str:
    from openai import OpenAI

    context = "\n\n---\n\n".join(
        f"**{c['service_name']}** — {c['section_title']}\n{c['text'][:3500]}"
        for c in chunks
    )

    if kb_route == "longevity":
        system = """Eres el Motor de Recomendación Justificada de Hombre Vigente (longevidad/wellness).
Responde SOLO con el contexto proporcionado. Cita tiers (E1–E5) cuando aparezcan.
PROHIBIDO: prescribir, dosificar, curar, tratar, diagnosticar.
Usa lenguaje educativo de optimización. Si falta evidencia, dilo explícitamente.
Disclaimer al final: información educativa, no sustituye médico."""
    else:
        system = """Eres asistente de servicios estéticos Hombre Vigente.
Responde con el contexto del Knowledge Base. Incluye precios en MXN cuando estén.
No inventes información. Audiencia: hombres 30–60 años."""

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Contexto:\n{context}\n\nPregunta: {query}"},
        ],
        temperature=0.3,
        max_tokens=800,
    )
    return response.choices[0].message.content


def rag_query_local(
    query: str,
    index_path: Path = DEFAULT_INDEX,
    kb_route: Optional[str] = None,
    top_k: int = 5,
    avenida_max: str = "1",
    use_llm: bool = True,
    verbose: bool = False,
) -> Dict:
    route = kb_route or detect_kb_route(query)
    gate = check_gates(query, route if route != "all" else "longevity")

    if gate.triggered:
        return {
            "query": query,
            "kb_route": route,
            "gate": gate.code,
            "answer": gate.message,
            "sources": [],
            "confidence": "blocked",
        }

    index = load_index(index_path)
    search_route = route if route != "all" else "all"
    chunks = retrieve(
        query,
        index,
        kb_route=search_route,
        top_k=top_k,
        avenida_max=avenida_max,
    )

    if not chunks:
        return {
            "query": query,
            "kb_route": route,
            "answer": "No encontré evidencia suficiente en el KB para responder con confianza.",
            "sources": [],
            "confidence": "low",
        }

    top_conf = chunks[0]["confidence"]
    answer = (
        generate_answer(query, chunks, route if route != "all" else chunks[0]["kb_type"])
        if use_llm and os.getenv("OPENAI_API_KEY")
        else _format_template(query, chunks, route)
    )

    result = {
        "query": query,
        "kb_route": route,
        "confidence": top_conf,
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

    if verbose:
        print(f"route={route} confidence={top_conf} chunks={len(chunks)}")
        for c in chunks[:3]:
            print(f"  - {c['service_name']} | {c['section_title']} | {c['score']:.3f}")

    return result


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
    )
    print("\n" + "=" * 60)
    print(result["answer"])
    if result.get("gate"):
        print(f"\n[GATE: {result['gate']}]")


if __name__ == "__main__":
    main()