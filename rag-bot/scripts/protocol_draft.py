#!/usr/bin/env python3
"""
Intake + labs parseados → borrador de protocolo (MVP0_Plantilla_Protocolo.md).

Secciones 1–2: determinísticas. Secciones 3–7: gpt-4o-mini (o --no-llm plantilla mínima).

  python scripts/protocol_draft.py data/intake/caso0_intake.json
  python scripts/protocol_draft.py intake.json --labs-json data/labs_intake/lab.json
  python scripts/protocol_draft.py intake.json --no-llm
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mvp0_lib import OBJETIVO_LABELS, STACK_LABELS  # noqa: E402

_ROOT = Path(__file__).resolve().parent.parent
_LABS_SCRIPT = _ROOT / "scripts" / "labs_intake_manual.py"


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(_ROOT / ".env")


def _section_1_2(intake: dict, labs: dict | None) -> str:
    ident = intake.get("identity") or {}
    obj = intake.get("objetivos") or {}
    life = intake.get("lifestyle") or {}
    screening = intake.get("screening") or {}
    moat = intake.get("data_moat") or {}
    pipe = intake.get("pipeline") or {}

    nombre = ident.get("nombre", "[NOMBRE]")
    principal = OBJETIVO_LABELS.get(obj.get("principal", ""), obj.get("principal", ""))
    meta = obj.get("meta_8_semanas", "")
    bandera = "ninguna"
    if screening.get("bandera_activa"):
        bandera = f"requiere clearance médico por: {screening.get('bandera_detalle', 'revisar')}"

    wearable_txt = "no"
    if moat.get("wearable_usa"):
        wearable_txt = f"sí — {moat.get('wearable_dispositivo') or 'definir'}"

    lines = [
        f"## PROTOCOLO PERSONALIZADO — {nombre}",
        "",
        f"**Fecha:** {date.today().isoformat()} · **Revisado por:** ⏳ PENDIENTE — médico aliado · "
        "**Vigencia:** evaluación a 4 semanas",
        "",
    ]
    if screening.get("bandera_activa"):
        lines.extend([
            "> ⚠️ **Caso con bandera de screening.** No iniciar stack sin clearance médico. "
            "Información educativa, no prescripción.",
            "",
        ])

    lines.extend([
        "### 1. Tu punto de partida",
        f"- Edad {ident.get('edad', '[ ]')} · objetivo principal: **{principal}**",
        f"- Lo que quieres lograr en 8 semanas: *\"{meta}\"*",
        f"- Notas de tu perfil: energía {life.get('energia_1_5', '[ ]')}/5, "
        f"sueño {life.get('sueno_1_5', '[ ]')}/5, entreno {life.get('dias_entreno_semana', '[ ]')} días/sem, "
        f"dolor/molestia: {life.get('dolor_recurrente') or '[ ]'}",
        f"- Suplementos/tratamiento actual: {life.get('suplementos_actuales') or 'ninguno reportado'}",
        f"- Datos recibidos: foto {'sí' if moat.get('foto_subida') else 'no'} · "
        f"labs {'sí' if moat.get('labs_subidos') else 'no'} · wearable {wearable_txt}",
        f"- **Banderas de screening:** {bandera}",
        "",
        "### 2. Lectura rápida de tus datos",
        "- **Foto (observación):** [completar manualmente — glow/textura/postura]",
    ])

    if labs and labs.get("biomarkers"):
        lines.append("- **Labs (parse automático — validar vs PDF):**")
        priority = re.compile(
            r"litio|leptina|glucosa|hba1c|creatinina|insulina|tsh|t4|t3|crp|homociste",
            re.I,
        )
        markers = labs.get("biomarkers", [])
        flagged = [b for b in markers if b.get("flag") in ("low", "high")]
        priority_hits = [b for b in markers if priority.search(b.get("name", ""))]
        shown: list[dict] = []
        for group in (flagged, priority_hits, markers):
            for b in group:
                if b not in shown:
                    shown.append(b)
                if len(shown) >= 10:
                    break
            if len(shown) >= 10:
                break
        for b in shown:
            unit = f" {b['unit']}" if b.get("unit") else ""
            flag = b.get("flag", "unknown")
            mark = " ⚠" if flag in ("low", "high") else ""
            lines.append(
                f"  - **{b['name']}:** {b.get('value')}{unit} "
                f"(ref {b.get('ref_low', '—')}–{b.get('ref_high', '—')}){mark}"
            )
        for c in labs.get("flags_critical") or []:
            lines.append(f"  - ⚠ {c}")
    else:
        lines.append("- **Labs (si hay):** [pendiente parse o manual]")

    if moat.get("wearable_promedios_7d"):
        lines.append(f"- **Wearable:** {moat['wearable_promedios_7d']}")
    else:
        lines.append("- **Wearable (si hay):** [no reportado]")

    lines.append("- **Inconsistencias detectadas:** [revisar subjetivo vs datos]")
    lines.append("")

    stack = STACK_LABELS.get(pipe.get("stack_sugerido", ""), "Pendiente")
    lines.extend([
        f"**Stack sugerido (pre-LLM):** {stack}",
        "",
    ])
    return "\n".join(lines)


def _draft_with_llm(intake: dict, labs: dict | None, header: str) -> str:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY requerida (o usa --no-llm)")

    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    payload = {
        "intake": intake,
        "labs_summary": {
            "biomarkers": (labs or {}).get("biomarkers", [])[:15],
            "flags_critical": (labs or {}).get("flags_critical", []),
        },
    }

    prompt = f"""Eres copiloto del protocolo MVP-0 de Hombre Vigente (educativo, NO prescripción).

Completa las secciones 3–7 del protocolo en markdown español, continuando este borrador ya escrito.
NO repitas secciones 1–2. Mantén tono conservador si hay banderas de screening.

Reglas:
- Lenguaje educativo: sin "cura", "tratamiento médico", "medicamento recetado por HV"
- Avenida 2 (péptidos inyectables): solo "con validación médica + magistral"
- Si litio/psiquiatría/oncología: énfasis en no auto-experimentar
- Stack oral con dosis orientativas de KB (NMN, magnesio, etc.) — no Rx
- Incluir disclaimer §7 completo

Datos JSON:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Borrador existente (secciones 1–2):
---
{header}
---

Escribe desde ### 3. Tu enfoque hasta el checklist final (### Checklist antes de enviar)."""

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2500,
    )
    tail = (resp.choices[0].message.content or "").strip()
    return header + "\n" + tail


def _minimal_tail(intake: dict) -> str:
    pipe = intake.get("pipeline") or {}
    stack = STACK_LABELS.get(pipe.get("stack_sugerido", ""), "Combinación")
    screening = intake.get("screening") or {}
    extra = ""
    if screening.get("bandera_activa"):
        extra = "\n> ⚠️ No iniciar hasta clearance médico.\n"

    return f"""### 3. Tu enfoque (mapeo objetivo → intervención)

**Tu stack recomendado:** {stack} — [completar razón con LLM o manual]

### 4. Protocolo (8 semanas)

**Fundamentos lifestyle:** [sueño / nutrición / movimiento / estrés]

**Stack oral (diario):** [completar con médico]

**Stack avanzado (Av.2 — solo con médico):** [completar]
{extra}
### 5. Qué medir
- Foto semanal · diario 1–5 · labs 4–6 sem si aplica

### 6. Calendario de la semana (ejemplo)
- [completar]

### 7. Seguridad y disclaimers
- Información educativa, no diagnóstico ni prescripción.
- Validar con profesional de salud antes de iniciar.
- Revisado por: **[médico — pendiente]**

### Checklist antes de enviar
- [ ] Screening revisado
- [ ] Revisado por médico aliado
"""


def main() -> None:
    _load_dotenv()
    parser = argparse.ArgumentParser(description="Intake → borrador protocolo")
    parser.add_argument("intake_json", type=Path)
    parser.add_argument("--labs-json", type=Path, help="Salida de labs_intake_manual.py")
    parser.add_argument("--output", type=Path, help="Archivo .md de salida")
    parser.add_argument("--no-llm", action="store_true", help="Solo secciones 1–2 + plantilla")
    args = parser.parse_args()

    intake = json.loads(args.intake_json.read_text(encoding="utf-8"))
    labs = None
    if args.labs_json and args.labs_json.exists():
        labs = json.loads(args.labs_json.read_text(encoding="utf-8"))

    header = _section_1_2(intake, labs)
    if args.no_llm:
        doc = header + _minimal_tail(intake)
    else:
        doc = _draft_with_llm(intake, labs, header)

    nombre = (intake.get("identity") or {}).get("nombre", "beta")
    slug = "".join(c if c.isalnum() else "_" for c in nombre.lower())[:40].strip("_")
    out = args.output or (_ROOT / "data" / "protocols" / f"{slug}_protocolo_borrador.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc + "\n", encoding="utf-8")
    print(f"✓ {out}")
    print(f"  {len(doc.splitlines())} líneas · revisar + médico antes de enviar")


if __name__ == "__main__":
    main()