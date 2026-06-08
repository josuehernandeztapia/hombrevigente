#!/usr/bin/env python3
"""
MVP-0 Concierge manual — consulta hv-rag-api o RAG local y formatea respuesta para WhatsApp.

Uso:
  python scripts/concierge_mvp.py "¿cuánto cuesta HIFU?"
  python scripts/concierge_mvp.py --local --beta-id row-0 "¿puedo tomar NMN?"
  python scripts/concierge_mvp.py --local --intake fixtures/caso0_intake_p1_entrega.json "ayuno 16:8"
  python scripts/concierge_mvp.py --api-url https://hv-rag-api.fly.dev --beta-id row-0 "pregunta"

Copia el bloque "→ WhatsApp" y pégalo al cliente. El decision_log registra beta_id + turn si hay intake.
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
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _query_api(
    *,
    api_url: str,
    question: str,
    role: str,
    use_llm: bool,
    beta_id: str | None,
    channel: str | None,
) -> dict:
    url = f"{api_url.rstrip('/')}/rag/query"
    payload: dict = {"query": question, "role": role, "use_llm": use_llm}
    if beta_id:
        payload["beta_id"] = beta_id
    if channel:
        payload["channel"] = channel
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"API HTTP {e.code}: {detail}") from e


def _query_local(
    *,
    question: str,
    role: str,
    use_llm: bool,
    intake_path: str | None,
    beta_id: str | None,
    channel: str | None,
) -> dict:
    from rag_retrieval_local import rag_query_local

    return rag_query_local(
        question,
        role=role,
        use_llm=use_llm,
        intake_path=intake_path,
        beta_id=beta_id,
        channel=channel or "whatsapp",
        source="concierge",
        parse=True,
    )


def _format_whatsapp(result: dict) -> str:
    answer = (result.get("answer") or "").strip()
    path = result.get("gate_path", "?")
    conf = result.get("confidence", "?")

    lines = [answer]
    if path == "escalate":
        lines.append(
            "\n_(Si necesitas confirmación con el equipo, te conectamos en un momento.)_"
        )
    elif path == "caveat":
        lines.append("\n_(Información orientativa — confirma en recepción si aplica.)_")
    elif path == "blocked":
        lines.append("\n_(Por tu seguridad, esto requiere valoración con nuestro médico.)_")

    footer = f"\n\n— Concierge HV · conf={conf} · path={path}"
    return "".join(lines) + footer


def main() -> None:
    parser = argparse.ArgumentParser(description="MVP-0 concierge → WhatsApp paste")
    parser.add_argument("question", nargs="?", help="Pregunta del cliente")
    parser.add_argument(
        "--api-url",
        default=os.getenv("HV_RAG_API_URL", "https://hv-rag-api.fly.dev"),
    )
    parser.add_argument("--local", action="store_true", help="RAG local (sin Fly)")
    parser.add_argument("--intake", help="Intake JSON → frozen context")
    parser.add_argument("--beta-id", help="row-0, caso0, tally-gbAO6Yl")
    parser.add_argument("--channel", default="whatsapp")
    parser.add_argument("--role", default="concierge", choices=["concierge", "default"])
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Sin LLM (rápido pero respuesta cruda con chunks)",
    )
    parser.add_argument("--json", action="store_true", help="Salida JSON cruda")
    args = parser.parse_args()

    question = args.question
    if not question:
        question = sys.stdin.read().strip()
    if not question:
        print("ERROR: pregunta vacía", file=sys.stderr)
        raise SystemExit(1)

    if args.local:
        result = _query_local(
            question=question,
            role=args.role,
            use_llm=not args.no_llm,
            intake_path=args.intake,
            beta_id=args.beta_id,
            channel=args.channel,
        )
    else:
        result = _query_api(
            api_url=args.api_url,
            question=question,
            role=args.role,
            use_llm=not args.no_llm,
            beta_id=args.beta_id,
            channel=args.channel,
        )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print("─" * 50)
    print(f"Cliente: {question}")
    print(f"Ruta: {result.get('kb_route')} · {result.get('gate_path')} · {result.get('confidence')}")
    if result.get("beta_id"):
        print(f"beta: {result['beta_id']} · turn {result.get('turn_number', '?')}")
    if result.get("decision_id"):
        print(f"decision_id: {result['decision_id']}")
    print("─" * 50)
    print("\n→ WhatsApp (copiar):\n")
    print(_format_whatsapp(result))


if __name__ == "__main__":
    main()