#!/usr/bin/env python3
"""
MVP-0 Concierge manual — consulta hv-rag-api y formatea respuesta para WhatsApp.

Uso:
  python scripts/concierge_mvp.py "¿cuánto cuesta HIFU?"
  python scripts/concierge_mvp.py --api-url https://hv-rag-api.fly.dev "aceptan amex"
  echo "pregunta del cliente" | python scripts/concierge_mvp.py

Copia el bloque "→ WhatsApp" y pégalo al cliente. El decision_log en prod
registra source=api (o concierge si usas POST con role).
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


def _query_api(
    *,
    api_url: str,
    question: str,
    role: str,
    use_llm: bool,
) -> dict:
    url = f"{api_url.rstrip('/')}/rag/query"
    body = json.dumps(
        {"query": question, "role": role, "use_llm": use_llm}
    ).encode("utf-8")
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

    result = _query_api(
        api_url=args.api_url,
        question=question,
        role=args.role,
        use_llm=not args.no_llm,
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print("─" * 50)
    print(f"Cliente: {question}")
    print(f"Ruta: {result.get('kb_route')} · {result.get('gate_path')} · {result.get('confidence')}")
    if result.get("decision_id"):
        print(f"decision_id: {result['decision_id']}")
    print("─" * 50)
    print("\n→ WhatsApp (copiar):\n")
    print(_format_whatsapp(result))


if __name__ == "__main__":
    main()