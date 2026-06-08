#!/usr/bin/env python3
"""
MVP-0 Labs intake — PDF → biomarcadores estructurados (sin BloodGPT).

Pipeline híbrido (más barato y preciso que vision-only):
  1. Texto nativo del PDF (PyMuPDF) — funciona en labs digitales mexicanos
  2. Si texto insuficiente → visión OpenAI (páginas renderizadas)
  3. Estructuración → JSON + tabla markdown para plantilla de protocolo

Modelos OpenAI recomendados (ver .env.example):
  - HV_LABS_STRUCT_MODEL=gpt-4o-mini   — texto → JSON (default)
  - HV_LABS_VISION_MODEL=gpt-4o-mini   — OCR fallback en PDFs escaneados
  - HV_LABS_VISION_FALLBACK=gpt-4o     — --high-precision para tablas difíciles

Uso:
  python scripts/labs_intake_manual.py ~/Downloads/.../Lab_Litio_7oct2025.pdf
  python scripts/labs_intake_manual.py lab.pdf --dry-run
  python scripts/labs_intake_manual.py lab.pdf --output-dir ~/HombreVigente-Caso0/
  python scripts/labs_intake_manual.py scan.pdf --force-vision --high-precision
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent

LABS_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "patient": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": ["string", "null"]},
                "age": {"type": ["string", "null"]},
                "gender": {"type": ["string", "null"]},
                "order_id": {"type": ["string", "null"]},
            },
            "required": ["name", "age", "gender", "order_id"],
        },
        "lab": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": ["string", "null"]},
                "collection_date": {"type": ["string", "null"]},
                "validation_date": {"type": ["string", "null"]},
            },
            "required": ["name", "collection_date", "validation_date"],
        },
        "biomarkers": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "string"},
                    "unit": {"type": ["string", "null"]},
                    "ref_low": {"type": ["string", "null"]},
                    "ref_high": {"type": ["string", "null"]},
                    "flag": {
                        "type": "string",
                        "enum": ["low", "high", "normal", "unknown"],
                    },
                },
                "required": ["name", "value", "unit", "ref_low", "ref_high", "flag"],
            },
        },
        "flags_critical": {
            "type": "array",
            "items": {"type": "string"},
        },
        "notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["patient", "lab", "biomarkers", "flags_critical", "notes"],
}


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(_ROOT / ".env")


def extract_text_pymupdf(pdf_path: Path) -> tuple[str, int]:
    try:
        import fitz
    except ImportError as exc:
        raise SystemExit(
            "pip install pymupdf  # requerido para extracción de PDF"
        ) from exc

    doc = fitz.open(pdf_path)
    pages = len(doc)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip(), pages


def render_pages_base64(pdf_path: Path, *, dpi: int = 150, max_pages: int = 8) -> list[str]:
    try:
        import fitz
    except ImportError as exc:
        raise SystemExit("pip install pymupdf") from exc

    doc = fitz.open(pdf_path)
    images: list[str] = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        images.append(base64.b64encode(pix.tobytes("png")).decode("ascii"))
    doc.close()
    return images


def _openai_client():
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY no configurada en .env")
    return OpenAI(api_key=api_key)


def extract_with_vision(
    pdf_path: Path,
    *,
    model: str,
    max_pages: int = 8,
) -> str:
    client = _openai_client()
    images = render_pages_base64(pdf_path, max_pages=max_pages)
    if not images:
        return ""

    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                "Extrae TODO el texto del informe de laboratorio mexicano. "
                "Preserva tablas como líneas: ESTUDIO | RESULTADO | UNIDADES | REFERENCIA. "
                "Incluye nombre paciente, fechas, notas al pie. Solo texto literal, sin interpretar."
            ),
        }
    ]
    for b64 in images:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"},
            }
        )

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        temperature=0,
        max_tokens=4096,
    )
    return (resp.choices[0].message.content or "").strip()


def structure_labs(text: str, *, model: str, source_file: str) -> dict[str, Any]:
    client = _openai_client()
    prompt = f"""Estructura este informe de laboratorio clínico (México).

Reglas:
- Extrae SOLO biomarcadores con valor numérico o cualitativo explícito.
- flag: "low" si resultado < ref_low, "high" si > ref_high, "normal" si en rango, "unknown" si no hay ref.
- flags_critical: banderas clínicas obvias (ej. litio subterapéutico, glucosa muy alta) en español, tono educativo.
- No diagnostiques ni prescribas.
- Archivo fuente: {source_file}

Texto del laboratorio:
---
{text[:24000]}
"""

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "labs_intake",
                "strict": True,
                "schema": LABS_JSON_SCHEMA,
            },
        },
    )
    raw = resp.choices[0].message.content or "{}"
    data = json.loads(raw)
    return data


def validate_labs_payload(data: dict[str, Any]) -> list[str]:
    """Validación estructural sin OpenAI — para CI / trajectories."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be object"]
    for key in LABS_JSON_SCHEMA["required"]:
        if key not in data:
            errors.append(f"missing {key}")
    biomarkers = data.get("biomarkers")
    if not isinstance(biomarkers, list):
        errors.append("biomarkers must be array")
    elif not biomarkers:
        errors.append("biomarkers empty")
    else:
        for i, b in enumerate(biomarkers):
            if not isinstance(b, dict):
                errors.append(f"biomarkers[{i}] not object")
                continue
            for req in ("name", "value", "flag"):
                if req not in b:
                    errors.append(f"biomarkers[{i}] missing {req}")
    patient = data.get("patient")
    if patient is not None and not isinstance(patient, dict):
        errors.append("patient must be object")
    return errors


def flag_emoji(flag: str) -> str:
    return {"low": "🔴 Bajo", "high": "🔴 Alto", "normal": "OK", "unknown": "—"}.get(
        flag, "—"
    )


def render_markdown_table(data: dict[str, Any]) -> str:
    patient = data.get("patient") or {}
    lab = data.get("lab") or {}
    lines = [
        "# Labs parseados — MVP-0",
        "",
        f"**Paciente:** {patient.get('name') or '—'} · **Orden:** {patient.get('order_id') or '—'}",
        f"**Laboratorio:** {lab.get('name') or '—'} · **Toma:** {lab.get('collection_date') or '—'}",
        "",
        "| Marcador | Resultado | Ref. | Flag |",
        "|----------|-----------|------|------|",
    ]
    for b in data.get("biomarkers") or []:
        ref = ""
        if b.get("ref_low") or b.get("ref_high"):
            ref = f"{b.get('ref_low') or '—'} – {b.get('ref_high') or '—'}"
        unit = b.get("unit") or ""
        val = b.get("value") or "—"
        if unit:
            val = f"{val} {unit}".strip()
        lines.append(
            f"| {b.get('name', '—')} | {val} | {ref} | {flag_emoji(b.get('flag', 'unknown'))} |"
        )

    critical = data.get("flags_critical") or []
    if critical:
        lines.extend(["", "## Banderas críticas", ""])
        for c in critical:
            lines.append(f"- {c}")

    notes = data.get("notes") or []
    if notes:
        lines.extend(["", "## Notas del informe", ""])
        for n in notes:
            lines.append(f"- {n}")

    lines.append("")
    lines.append(
        "_Información educativa. Interpretación clínica: solo con profesional de salud._"
    )
    return "\n".join(lines)


def render_protocol_snippet(data: dict[str, Any]) -> str:
    """Bloque §2 para MVP0_Plantilla_Protocolo.md."""
    highlights: list[str] = []
    for b in data.get("biomarkers") or []:
        if b.get("flag") in ("low", "high"):
            unit = f" {b['unit']}" if b.get("unit") else ""
            highlights.append(
                f"**{b['name']}** {b.get('value')}{unit} ({flag_emoji(b['flag'])})"
            )
    critical = data.get("flags_critical") or []
    lines = ["**Labs (parse automático — revisar antes de enviar):**"]
    if highlights:
        lines.append("- Destacados: " + "; ".join(highlights[:8]))
    else:
        lines.append("- Sin banderas fuera de rango detectadas automáticamente.")
    if critical:
        lines.append("- Crítico: " + "; ".join(critical[:5]))
    lines.append("- _Validar manualmente contra PDF original._")
    return "\n".join(lines)


def process_pdf(
    pdf_path: Path,
    *,
    struct_model: str,
    vision_model: str,
    min_text_chars: int,
    force_vision: bool,
    dry_run: bool,
) -> dict[str, Any]:
    raw_text, pages = extract_text_pymupdf(pdf_path)
    method = "text"
    vision_used = None

    if force_vision or len(raw_text) < min_text_chars:
        if dry_run:
            print(
                f"WARN: texto corto ({len(raw_text)} chars, {pages} págs) — "
                "usaría visión sin --dry-run",
                file=sys.stderr,
            )
        else:
            vision_used = vision_model
            raw_text = extract_with_vision(pdf_path, model=vision_model)
            method = "vision"

    result: dict[str, Any] = {
        "source_file": str(pdf_path),
        "pages": pages,
        "text_chars": len(raw_text),
        "extraction_method": method,
        "models_used": {"struct": struct_model, "vision": vision_used},
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "raw_text_preview": raw_text[:500],
    }

    if dry_run:
        result["dry_run"] = True
        return result

    structured = structure_labs(
        raw_text, model=struct_model, source_file=pdf_path.name
    )
    structured["_meta"] = {
        "extraction_method": method,
        "models_used": result["models_used"],
        "source_file": pdf_path.name,
        "extracted_at": result["extracted_at"],
    }
    return structured


def main() -> None:
    _load_dotenv()

    parser = argparse.ArgumentParser(description="MVP-0 labs PDF → JSON + markdown")
    parser.add_argument("pdf", type=Path, help="Ruta al PDF de laboratorio")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directorio de salida (default: rag-bot/data/labs_intake/)",
    )
    parser.add_argument(
        "--struct-model",
        default=os.getenv("HV_LABS_STRUCT_MODEL", "gpt-4o-mini"),
    )
    parser.add_argument(
        "--vision-model",
        default=os.getenv("HV_LABS_VISION_MODEL", "gpt-4o-mini"),
    )
    parser.add_argument(
        "--high-precision",
        action="store_true",
        help=f"Visión con {os.getenv('HV_LABS_VISION_FALLBACK', 'gpt-4o')} en lugar de mini",
    )
    parser.add_argument(
        "--force-vision",
        action="store_true",
        help="OCR por visión aunque el PDF tenga texto embebido",
    )
    parser.add_argument(
        "--min-text-chars",
        type=int,
        default=400,
        help="Umbral mínimo de chars antes de activar visión",
    )
    parser.add_argument("--dry-run", action="store_true", help="Solo extracción de texto, sin API")
    parser.add_argument("--json", action="store_true", help="Imprimir JSON a stdout")
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF no encontrado: {args.pdf}")

    vision_model = args.vision_model
    if args.high_precision:
        vision_model = os.getenv("HV_LABS_VISION_FALLBACK", "gpt-4o")

    data = process_pdf(
        args.pdf.resolve(),
        struct_model=args.struct_model,
        vision_model=vision_model,
        min_text_chars=args.min_text_chars,
        force_vision=args.force_vision,
        dry_run=args.dry_run,
    )

    if args.json or args.dry_run:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        if args.dry_run:
            return

    stem = re.sub(r"[^\w\-]+", "_", args.pdf.stem)[:60]
    out_dir = args.output_dir or (_ROOT / "data" / "labs_intake")
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"
    snippet_path = out_dir / f"{stem}_protocol_snippet.txt"

    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    md_path.write_text(render_markdown_table(data), encoding="utf-8")
    snippet_path.write_text(render_protocol_snippet(data) + "\n", encoding="utf-8")

    print(f"✓ JSON  → {json_path}")
    print(f"✓ MD    → {md_path}")
    print(f"✓ §2    → {snippet_path}")
    print(f"  método={data['_meta']['extraction_method']} · "
          f"biomarcadores={len(data.get('biomarkers', []))}")
    if data.get("flags_critical"):
        print(f"  ⚠ banderas: {', '.join(data['flags_critical'][:3])}")


if __name__ == "__main__":
    main()