"""
vendor_quality.py — Criterio de selección de proveedor (Av.2) como CÓDIGO.

Convierte el embudo de Calidad_Suministro_Peptidos.md en una rúbrica ejecutable.
NO scrapea: tú alimentas los datos (data/vendor_quality.json); esto puntúa y decide.

Embudo de 3 pasos:
  1. CRIBA        — ¿se somete a testeo independiente? (Finnrick fuerte; Janoshik débil)
  2. CALIFICACIÓN — COA por lote (+ endotoxinas/esterilidad si inyectable)
  3. VERIFICACIÓN — el LOTE que vas a usar fue testeado (no negociable)

Principio rector: un buen ranking NO sustituye testear el lote. Por eso la criba
sola nunca abre el gate Av.2; los 3 pasos + firma del médico (externa) lo hacen.

Ref: estrategia_2026/Calidad_Suministro_Peptidos.md · rag-bot/docs/AI_Second_Opinion_Spec.md

AUTO-FETCH (diferido — recon 2026-06, robots.txt):
  - Finnrick: robots PERMITE público (invita a crawlers IA), pero DISALLOW /api/.
    Si algún día auto-fetcheas: "Researcher data access" (legítimo) > páginas públicas
    (Next.js server-rendered → fetch+Cheerio, sin headless). Nunca /api/.
  - Janoshik: robots PROHÍBE bots (ai-train=no). NO scrapear; usar solo como LAB
    (destino de muestra, paso 3), no como fuente de datos.
  Hoy: el registro se llena a mano (este archivo no hace red). Construir auto-fetch
  solo cuando evalúes vendors de forma recurrente (Av.2 a escala).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Días tras los cuales un test de lote se considera viejo (re-testear).
LOTE_TEST_TTL_DIAS = 365


@dataclass
class Vendor:
    name: str
    inyectable: bool = False               # inyectable → exige endotoxinas + esterilidad
    # Paso 1 — criba (fuentes de ranking)
    en_finnrick: Optional[bool] = None     # independiente → señal FUERTE
    finnrick_ok: Optional[bool] = None     # resultados aceptables en Finnrick
    en_janoshik: Optional[bool] = None     # vendor-submitted → señal DÉBIL (sesgo selección)
    # Paso 2 — calificación (por vendor)
    coa_por_lote: bool = False
    endotoxinas: Optional[bool] = None     # solo aplica si inyectable
    esterilidad: Optional[bool] = None     # solo aplica si inyectable
    iso_17025_lab: bool = False            # bonus de rigor
    # Paso 3 — verificación (por lote)
    ultimo_lote_testeado: Optional[Dict[str, Any]] = None  # {lab, fecha, lote, resultado}
    notas: str = ""


def _dias_desde(fecha_iso: Optional[str]) -> Optional[int]:
    if not fecha_iso:
        return None
    try:
        f = datetime.fromisoformat(str(fecha_iso).replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - f).days
    except Exception:
        return None


def _criba(v: Vendor) -> Dict[str, Any]:
    """Paso 1: ¿se somete a testeo independiente? Finnrick fuerte; Janoshik débil; nada → fail."""
    if v.en_finnrick and v.finnrick_ok:
        return {"pass": True, "fuerza": "fuerte", "razon": "Finnrick independiente con resultados OK"}
    if v.en_finnrick and v.finnrick_ok is False:
        return {"pass": False, "fuerza": "negativa", "razon": "Finnrick con resultados fallidos → descartar"}
    if v.en_janoshik:
        return {"pass": True, "fuerza": "debil",
                "razon": "Solo Janoshik (vendor-submitted, sesgo de selección) — no suficiente para confiar"}
    return {"pass": False, "fuerza": "nula", "razon": "No aparece en testeo independiente (ej. Exoma)"}


def _calificacion(v: Vendor) -> Dict[str, Any]:
    """Paso 2: COA por lote (+ endotoxinas/esterilidad si inyectable)."""
    faltantes: List[str] = []
    if not v.coa_por_lote:
        faltantes.append("COA por lote")
    if v.inyectable:
        if not v.endotoxinas:
            faltantes.append("prueba de endotoxinas (inyectable)")
        if not v.esterilidad:
            faltantes.append("prueba de esterilidad (inyectable)")
    return {"pass": not faltantes, "faltantes": faltantes, "iso_17025": v.iso_17025_lab}


def _verificacion(v: Vendor) -> Dict[str, Any]:
    """Paso 3: el lote a usar fue testeado por un lab independiente y está vigente."""
    lote = v.ultimo_lote_testeado or {}
    if not lote.get("lab"):
        return {"pass": False, "razon": "Sin test de lote — NO usar en protocolo Av.2"}
    dias = _dias_desde(lote.get("fecha"))
    if dias is not None and dias > LOTE_TEST_TTL_DIAS:
        return {"pass": False, "razon": f"Test de lote viejo ({dias}d > {LOTE_TEST_TTL_DIAS}d) — re-testear"}
    if str(lote.get("resultado", "")).lower() in ("fail", "fallo", "rechazado"):
        return {"pass": False, "razon": "El lote testeado FALLÓ → descartar lote"}
    return {"pass": True, "razon": f"Lote {lote.get('lote','?')} testeado en {lote.get('lab')}"}


def evaluate(v: Vendor) -> Dict[str, Any]:
    """
    Aplica el embudo. gate_av2 = los 3 pasos en verde. La firma del médico responsable
    es un paso EXTERNO (no automatizable): gate_av2=True habilita la decisión, no la sustituye.
    """
    criba = _criba(v)
    cal = _calificacion(v)
    ver = _verificacion(v)
    gate = bool(criba["pass"] and cal["pass"] and ver["pass"])

    faltantes: List[str] = []
    if not criba["pass"]:
        faltantes.append(f"criba: {criba['razon']}")
    elif criba["fuerza"] == "debil":
        faltantes.append("criba débil (solo Janoshik) — preferir un vendor con historial en Finnrick")
    faltantes += [f"calificación: falta {x}" for x in cal["faltantes"]]
    if not ver["pass"]:
        faltantes.append(f"verificación: {ver['razon']}")

    return {
        "vendor": v.name,
        "inyectable": v.inyectable,
        "criba": criba,
        "calificacion": cal,
        "verificacion": ver,
        "gate_av2": gate,
        "faltantes": faltantes,
        "siguiente_paso": (
            "Listo para decisión del médico responsable (firma)" if gate
            else (faltantes[0] if faltantes else "revisar")
        ),
    }


# ------------------------------------------------------------------
# Registro (data/vendor_quality.json) — SSOT de decisiones de proveedor
# ------------------------------------------------------------------

def _registry_path() -> Path:
    return Path(os.getenv("HV_VENDOR_REGISTRY", "data/vendor_quality.json"))


def load_registry() -> List[Vendor]:
    p = _registry_path()
    if not p.exists():
        return []
    raw = json.loads(p.read_text(encoding="utf-8"))
    items = raw.get("vendors", raw) if isinstance(raw, dict) else raw
    return [Vendor(**{k: v for k, v in d.items() if k in Vendor.__dataclass_fields__}) for d in items]


def evaluate_registry() -> List[Dict[str, Any]]:
    return [evaluate(v) for v in load_registry()]


if __name__ == "__main__":
    import sys
    results = evaluate_registry()
    if not results:
        print("Registro vacío. Crea data/vendor_quality.json con {\"vendors\":[...]}.")
        sys.exit(0)
    for r in results:
        estado = "✅ gate Av.2 OK (→ firma médico)" if r["gate_av2"] else "⛔ no pasa"
        print(f"\n{r['vendor']} {'(inyectable)' if r['inyectable'] else ''} — {estado}")
        for f in r["faltantes"]:
            print(f"   • {f}")
