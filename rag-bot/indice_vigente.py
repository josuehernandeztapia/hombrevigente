"""
indice_vigente.py — Motor del Vigente Longevidad (contrato: docs/Metodologia_Indice_Vigente.md).

Implementa §3–§7 de la spec para la vertiente Longevidad (la Estética viene de CV/IR,
fuera de alcance hoy). Diseño clave — **framing forzado por código**, no por copy:

- El score NUNCA se devuelve "desnudo": `compute_indice_longevidad` retorna siempre un
  dict con {score, etiqueta, disclaimer, es_diagnostico:False, ilustrativo:True,
  preliminar, completitud, subscores, derivaciones}. No hay forma de obtener el número
  sin su marco.
- **Doble umbral (cortafuegos COFEPRIS §6):** un marcador que cruza su umbral clínico
  NO puntúa como "malo" — se omite del score y emite una bandera de derivación (Ruta B).
  El índice nunca afirma una enfermedad.
- **Degradación (§7):** se calcula solo con los subscores presentes, re-normalizando
  pesos. Regla dura: si solo hay autorreporte (Comportamiento), el resultado es
  `preliminar` y no se emite como número "duro".
- **headline_text()** produce el texto seguro (pasa por claim-guard) para que la UI no
  arme su propio string y se salga del marco.

Bandas y PMIDs: verbatim de la spec §4/§11 (Europe PMC, 2026-06-09). Los cutoffs son los
de las guías citadas; cambiar una banda obliga a subir METODOLOGIA_VERSION.

NO es diagnóstico ni consejo médico. La vertiente Longevidad requiere revisión COFEPRIS
antes de exponerse a usuarios reales (hoy: nivel interno / ilustrativo).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

METODOLOGIA_VERSION = "0.1.0-ilustrativo"

DISCLAIMER = (
    "Información de optimización y bienestar con metodología documentada. "
    "No es diagnóstico ni sustituye la valoración de un médico. Modelo en validación."
)
ETIQUETA = "indicativo de optimización (ilustrativo · modelo en validación)"

# Vocabulario que jamás debe acompañar al índice (mismo espíritu que el claim-guard
# del newsletter). Si aparece en un texto de salida, headline_text lo rechaza.
_CLAIM_GUARD = re.compile(
    r"\b(diagn[oó]stic\w*|enfermedad|cura\w*|trata\w*|prevskip|padece\w*|"
    r"prediabet\w*|diabet\w*|dislipidemi\w*|patolog\w*)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Banda:
    """Banda de un marcador. `lower_better`: óptimo bajo (glucosa); si False, banda
    central (sueño 7–9h). Score 100 en óptima, interpola 90→50 en sub-óptima, y al
    cruzar `clinico` NO puntúa → derivación."""
    marcador: str
    unidad: str
    subscore: str
    optimo: float          # frontera de banda óptima
    suboptimo: float       # frontera de sub-óptima (antes del umbral clínico)
    clinico: float         # cruzar esto dispara derivación (no puntúa)
    pmid: str
    fuente: str
    lower_better: bool = True
    # Para bandas centrales (lower_better=False): mínimos espejo.
    optimo_lo: Optional[float] = None
    clinico_lo: Optional[float] = None


# §4 — bandas con fuente verificada (§11). Cutoffs de las guías citadas.
BANDAS: Dict[str, Banda] = {
    # Metabólico (35%)
    "glucosa_ayuno": Banda("glucosa_ayuno", "mg/dL", "metabolico", 90, 99, 100,
                           "33298413", "ADA 2021 Classification & Diagnosis of Diabetes"),
    "hba1c": Banda("hba1c", "%", "metabolico", 5.4, 5.6, 5.7,
                   "33298413", "ADA 2021"),
    "apob": Banda("apob", "mg/dL", "metabolico", 80, 100, 100.0001,
                  "31504418", "ESC/EAS 2019 dyslipidaemias (Mach); causalidad Ference 28444290"),
    "trigliceridos": Banda("trigliceridos", "mg/dL", "metabolico", 90, 149, 150,
                           "31504418", "ESC/EAS 2019"),
    # Inflamación (25%)
    "hs_crp": Banda("hs_crp", "mg/L", "inflamacion", 1.0, 3.0, 3.0001,
                    "12551853", "Ridker hs-CRP en prevención CV"),
    "homocisteina": Banda("homocisteina", "µmol/L", "inflamacion", 9, 12, 15,
                          "12446535", "Wald 12446535 · Clarke 20937919"),
    # Recuperación (25%) — wearable
    "fc_reposo": Banda("fc_reposo", "lpm", "recuperacion", 60, 75, 85,
                       "26598376", "Zhang FC reposo y mortalidad (meta)"),
    "sueno_horas": Banda("sueno_horas", "h", "recuperacion", 9, 7, 6,
                         "20469800", "Cappuccio 20469800 · Irwin 26140821",
                         lower_better=False, optimo_lo=7, clinico_lo=6),
    # NOTA: HRV (rMSSD) requiere tabla de percentiles por edad/sexo (Shaffer 29034226).
    # Sin esa tabla NO inventamos cutoff → se acepta como dato informativo pero no puntúa
    # (ver compute: marcadores sin banda se ignoran sin penalizar). Pendiente: tabla ref.
}

# Pesos declarados (§3) — heurística versionada, no calibrada.
SUBSCORE_PESOS = {
    "metabolico": 0.35,
    "inflamacion": 0.25,
    "recuperacion": 0.25,
    "comportamiento": 0.15,
}
_MIN_SENALES_DURAS = 1  # al menos 1 subscore objetivo (no solo autorreporte) → §7


# ------------------------------------------------------------------
# Normalización por marcador (§5) + doble umbral (§6)
# ------------------------------------------------------------------

def _score_marcador(b: Banda, valor: float) -> Dict[str, Any]:
    """
    Devuelve {'score': 0-100|None, 'derivacion': {...}|None}.
    Si cruza umbral clínico → score=None + derivación (no puntúa como "malo").
    """
    deriva = (
        valor >= b.clinico if b.lower_better
        else (b.clinico_lo is not None and valor < b.clinico_lo)
    )
    if deriva:
        return {
            "score": None,
            "derivacion": {
                "marcador": b.marcador,
                "valor": valor,
                "unidad": b.unidad,
                "umbral_clinico": b.clinico if b.lower_better else b.clinico_lo,
                "mensaje": "Este valor amerita valoración médica.",
                "ruta": "B",
                "fuente_pmid": b.pmid,
            },
        }

    if b.lower_better:
        if valor <= b.optimo:
            score = 100.0
        else:
            # interpola 90 (en óptimo) → 50 (en clínico)
            frac = (valor - b.optimo) / max(b.clinico - b.optimo, 1e-9)
            score = max(50.0, 90.0 - frac * 40.0)
    else:
        # banda central: óptima entre optimo_lo y optimo
        if b.optimo_lo is not None and b.optimo_lo <= valor <= b.optimo:
            score = 100.0
        else:
            # zona sub-óptima entre clinico_lo y optimo_lo → 50..90
            lo, hi = (b.clinico_lo or 0), (b.optimo_lo or b.optimo)
            frac = (valor - lo) / max(hi - lo, 1e-9)
            score = max(50.0, min(90.0, 50.0 + frac * 40.0))
    return {"score": round(score, 1), "derivacion": None}


def _subscore(marcadores: Dict[str, float]) -> Dict[str, Any]:
    """Promedia los scores de los marcadores presentes; recolecta derivaciones."""
    scores: List[float] = []
    derivaciones: List[Dict[str, Any]] = []
    usados: List[str] = []
    for nombre, valor in marcadores.items():
        b = BANDAS.get(nombre)
        if b is None or valor is None:
            continue
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            continue
        r = _score_marcador(b, valor)
        if r["derivacion"]:
            derivaciones.append(r["derivacion"])
        if r["score"] is not None:
            scores.append(r["score"])
            usados.append(nombre)
    if not scores:
        return {"score": None, "derivaciones": derivaciones, "marcadores": usados}
    return {
        "score": round(sum(scores) / len(scores), 1),
        "derivaciones": derivaciones,
        "marcadores": usados,
    }


def _frame(score: Optional[float], *, preliminar: bool, subscores: Dict[str, Any],
           derivaciones: List[Dict[str, Any]], completitud: Dict[str, Any]) -> Dict[str, Any]:
    """Envoltorio ÚNICO de salida — el número nunca sale sin su marco (framing-as-code)."""
    return {
        "metodologia_version": METODOLOGIA_VERSION,
        "vertiente": "longevidad",
        "score": score,                 # None si no hay señales duras suficientes
        "etiqueta": ETIQUETA,
        "es_diagnostico": False,
        "ilustrativo": True,
        "disclaimer": DISCLAIMER,
        "preliminar": preliminar,
        "completitud": completitud,
        "subscores": subscores,
        "derivaciones": derivaciones,   # banderas Ruta B (doble umbral)
    }


# ------------------------------------------------------------------
# API pública
# ------------------------------------------------------------------

def compute_indice_longevidad(
    labs: Optional[Dict[str, float]] = None,
    wearable: Optional[Dict[str, float]] = None,
    cuestionario: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Vigente Longevidad (0–100) desde labs/wearable/cuestionario. Siempre framed.

    labs: {glucosa_ayuno, hba1c, apob, trigliceridos, hs_crp, homocisteina}
    wearable: {fc_reposo, sueno_horas}  (HRV pendiente de tabla de percentiles)
    cuestionario: {sueno, ejercicio, estres, alcohol} cada 0–100 (autorreporte)
    """
    labs = labs or {}
    wearable = wearable or {}
    cuestionario = cuestionario or {}

    metab = {k: labs[k] for k in ("glucosa_ayuno", "hba1c", "apob", "trigliceridos") if k in labs}
    inflam = {k: labs[k] for k in ("hs_crp", "homocisteina") if k in labs}
    recup = {k: wearable[k] for k in ("fc_reposo", "sueno_horas") if k in wearable}

    subscores: Dict[str, Any] = {}
    derivaciones: List[Dict[str, Any]] = []

    for nombre, marcadores in (("metabolico", metab), ("inflamacion", inflam), ("recuperacion", recup)):
        if marcadores:
            r = _subscore(marcadores)
            derivaciones.extend(r["derivaciones"])
            if r["score"] is not None:
                subscores[nombre] = r["score"]
            elif r["derivaciones"]:
                # todos sus marcadores derivaron → subscore no puntúa pero queda registrado
                subscores[nombre] = None

    # Comportamiento (autorreporte) — escala directa 0–100
    if cuestionario:
        vals = [float(v) for v in cuestionario.values() if isinstance(v, (int, float))]
        if vals:
            subscores["comportamiento"] = round(sum(vals) / len(vals), 1)

    # subscores objetivos presentes (excluye comportamiento) = señales "duras"
    duros = [k for k in ("metabolico", "inflamacion", "recuperacion") if subscores.get(k) is not None]
    total_señales = 4
    faltan = [k for k in SUBSCORE_PESOS if k not in subscores or subscores.get(k) is None]
    completitud = {
        "senales_presentes": len([k for k in subscores if subscores.get(k) is not None]),
        "senales_totales": total_señales,
        "faltan": faltan,
        "senales_duras": len(duros),
    }

    # §7 — regla dura: sin señales objetivas, no se emite número duro (preliminar).
    puntuables = {k: v for k, v in subscores.items() if v is not None}
    preliminar = len(duros) < _MIN_SENALES_DURAS
    if not puntuables or preliminar:
        return _frame(None, preliminar=True, subscores=subscores,
                      derivaciones=derivaciones, completitud=completitud)

    # Agregación con re-normalización de pesos al subconjunto presente (§5/§7).
    peso_total = sum(SUBSCORE_PESOS[k] for k in puntuables)
    score = sum(SUBSCORE_PESOS[k] * v for k, v in puntuables.items()) / peso_total
    return _frame(round(score, 1), preliminar=False, subscores=subscores,
                  derivaciones=derivaciones, completitud=completitud)


# ------------------------------------------------------------------
# Puente labs → inputs del Índice (mapea nombres MX + normaliza unidades)
# ------------------------------------------------------------------

# clave del Índice → patrones (regex) sobre el nombre crudo del biomarcador del lab MX.
_LAB_SYNONYMS: Dict[str, List[str]] = {
    "glucosa_ayuno": [r"glucosa"],  # se excluye postprandial/curva abajo
    "hba1c": [r"hemoglobina\s+glucosilada", r"glucohemoglobina", r"hba1c", r"\ba1c\b"],
    "apob": [r"apolipoprote[ií]na\s*b", r"\bapo\s*b\b", r"\bapob\b"],
    "trigliceridos": [r"triglic[eé]ridos"],
    "hs_crp": [r"prote[ií]na\s*c\s*reactiva", r"hs[\s-]?crp", r"\bpcr\s*(ultra|us|hs)", r"\bpcr\b"],
    "homocisteina": [r"homociste[ií]na"],
}
# nombres que invalidan un match de glucosa (no es ayuno).
_GLUCOSA_EXCLUDE = re.compile(r"post|2\s*h|curva|carga|tolerancia", re.IGNORECASE)


def _parse_lab_value(value: Any) -> Optional[float]:
    """'95 mg/dL' / '5,4' / '<0.30' → float. None si no hay número."""
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    s = value.strip().replace(",", ".")
    m = re.search(r"[-+]?\d*\.?\d+", s)
    return float(m.group()) if m else None


def labs_result_to_longevidad_inputs(labs_result: Dict[str, Any]) -> Dict[str, float]:
    """
    Convierte el `structured` del parser (biomarkers crudos del lab MX) en los inputs
    nombrados que espera compute_indice_longevidad. Mapea por sinónimos y normaliza
    unidades donde es ambiguo (apoB g/L↔mg/dL). Marcadores no reconocidos se ignoran.
    """
    markers = (labs_result.get("biomarkers") or labs_result.get("biomarcadores")
               or labs_result.get("markers") or [])
    out: Dict[str, float] = {}
    for m in markers:
        if not isinstance(m, dict):
            continue
        name = (m.get("name") or "").lower()
        val = _parse_lab_value(m.get("value"))
        unit = (m.get("unit") or "").lower()
        if not name or val is None:
            continue
        for key, patterns in _LAB_SYNONYMS.items():
            if key in out:
                continue  # primer match gana
            if key == "glucosa_ayuno" and _GLUCOSA_EXCLUDE.search(name):
                continue
            if any(re.search(p, name) for p in patterns):
                # apoB: g/L (0.X) → mg/dL (×100). Heurística por unidad o magnitud.
                if key == "apob" and ("g/l" in unit or (val < 10 and "mg" not in unit)):
                    val = val * 100.0
                out[key] = val
                break
    return out


def compute_from_labs_result(labs_result: Dict[str, Any], *,
                             wearable: Optional[Dict[str, float]] = None,
                             cuestionario: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Atajo del puente 2→3: structured del parser → Vigente Longevidad framed."""
    return compute_indice_longevidad(
        labs=labs_result_to_longevidad_inputs(labs_result),
        wearable=wearable, cuestionario=cuestionario,
    )


def headline_text(resultado: Dict[str, Any]) -> str:
    """
    Texto seguro para UI/WhatsApp. El claim-guard valida la parte VARIABLE (donde
    podría colarse vocabulario no-compliant por un cambio futuro o un valor inyectado);
    el DISCLAIMER y la ETIQUETA son boilerplate fijo y auditado (usan "no es diagnóstico"
    en negación, legítimo) y se anexan exentos.
    """
    if resultado.get("preliminar") or resultado.get("score") is None:
        comp = resultado.get("completitud", {})
        cuerpo = ("Aún no podemos calcular tu Vigente Longevidad como número confiable "
                  f"(tenemos {comp.get('senales_duras', 0)} de 3 señales objetivas). "
                  "Sube tus estudios para activarlo.")
    else:
        n_der = len(resultado.get("derivaciones", []))
        extra = (f" Detectamos {n_der} valor(es) que conviene revisar con un médico."
                 if n_der else "")
        cuerpo = (f"Tu Vigente Longevidad es {resultado['score']} "
                  f"({ETIQUETA}).{extra}")
    if _CLAIM_GUARD.search(cuerpo):
        raise ValueError("claim-guard: el texto variable del índice contiene vocabulario no permitido")
    return f"{cuerpo} {DISCLAIMER}"
