# Índice Vigente — Metodología (spec / fundamento)

> **Estado:** borrador de spec · 2026-06-09. **Los scores son ilustrativos / "modelo en validación"** hasta que se calibre con datos reales (COMPLIANCE §0). Este documento es el **contrato** del que cuelga el código y la UI: define bandas, umbrales, fórmulas, degradación y derivación. No es consejo legal; la vertiente Longevidad debe revisarse con asesoría COFEPRIS antes de operar con usuarios reales.

---

## 0. Principios (lo que hace defendible al índice)

1. **No predictivo, no diagnóstico.** Es un índice de **optimización/bienestar con metodología documentada**. No predice outcomes ni diagnostica enfermedad.
2. **Transparente y desglosable.** Todo número se puede abrir a sus componentes y cada componente a su fuente. Sin caja negra.
3. **Bandas con fuente.** La normalización de cada marcador se ancla a referencias publicadas (guías/papers), no a cutoffs inventados.
4. **Doble umbral.** Cada marcador tiene banda de optimización (puntúa) y umbral clínico (deriva a médico, no puntúa). Este es el cortafuegos de compliance.
5. **Validez de constructo, no predictiva.** Hoy se defiende que mide lo que dice con marcadores aceptados y dirección correcta; la validación predictiva es un paso futuro dependiente de datos.

---

## 1. Arquitectura — dos índices separados

```
ÍNDICE VIGENTE (marca)
├── Vigente Estético (0–100)      "cómo te lees"     → fuentes imagen (CV / IR)
└── Vigente Longevidad (0–100)    "cómo estás dentro" → fuentes datos (labs / wearable / cuestionario)
```

**Headline = los dos scores juntos** (ej. "64 Estético · 71 Longevidad"), siempre visibles.
**Compuesto único = opcional y secundario** (§8). No es el número principal.

---

## 2. Vigente Estético

| Subscore | Peso | Fuente | Qué mide |
|----------|------|--------|----------|
| Estructural | 40% | RGB / CV | Contornos, simetría, definición |
| Piel | 30% | ViT / CV | Textura, poros, fotoenvejecimiento |
| Termografía | 30% | IR (FLIR/Seek) | Patrones térmicos, inflamación superficial (ΔT relativo) |

`Estético = 0.40·Estructural + 0.30·Piel + 0.30·Termografía`

- **Rename obligatorio:** `subscore_biologico → subscore_termografia` (evita choque con biomarcadores de longevidad).
- **Fundamento:** salidas de modelos CV/IR. Documentar **qué mide cada modelo y sus límites** (metodología del proveedor — Haut.AI/Perfect Corp — + calibración interna). Riesgo regulatorio bajo (cosmético).
- **Límite a declarar:** la termografía es ΔT relativo adjunto de bienestar, **no** medición diagnóstica.

---

## 3. Vigente Longevidad

| Subscore | Peso | Fuente | Marcadores |
|----------|------|--------|-----------|
| Metabólico | 35% | Labs (PDF) | Glucosa, HbA1c, ApoB/LDL, triglicéridos |
| Inflamación | 25% | Labs | hs-CRP, homocisteína (si disponible) |
| Recuperación | 25% | Wearable | HRV, sueño profundo, FC reposo |
| Comportamiento | 15% | Cuestionario P04 | Sueño, ejercicio, estrés, alcohol (escala) |

`Longevidad = 0.35·Metabólico + 0.25·Inflamación + 0.25·Recuperación + 0.15·Comportamiento`

- **Pesos = heurística declarada, versionada.** Metabólico pesa más por tener la base de evidencia CV/mortalidad más fuerte. Ajustables; no se afirman como calibrados.
- Cada subscore = promedio (ponderado) de las **sub-bandas** de sus marcadores (§4–5).

---

## 4. Bandas por biomarcador (el fundamento)

Para cada marcador: **banda de optimización** (valor → 0–100, puntúa) y **umbral clínico** (cruzarlo dispara derivación, no puntúa). **PMID de cada guía ya verificado (§11);** los cutoffs numéricos son orientativos a su criterio — transcribir el valor exacto de la guía citada al implementar.

### Metabólico
| Marcador | Banda óptima (≈100) | Sub-óptima | Umbral clínico → deriva | Fuente |
|----------|--------------------|-----------|------------------------|--------|
| Glucosa ayuno | <90 mg/dL | 90–99 | ≥100 (pre) / ≥126 (DM) | ADA 2021 PMID 33298413 ✓ |
| HbA1c | <5.4% | 5.4–5.6 | ≥5.7 (pre) / ≥6.5 (DM) | ADA 2021 PMID 33298413 ✓ |
| ApoB | <0.80 g/L (<80 mg/dL) | 0.80–1.0 | >1.0 / antecedente CV | ESC/EAS 2019 PMID 31504418 ✓; causalidad: Ference PMID 28444290 ✓ |
| Triglicéridos | <90 mg/dL | 90–149 | ≥150 (síndrome metab.) | ESC/EAS 2019 PMID 31504418 ✓ |

### Inflamación
| Marcador | Banda óptima | Sub-óptima | Umbral clínico → deriva | Fuente |
|----------|-------------|-----------|------------------------|--------|
| hs-CRP | <1.0 mg/L | 1.0–3.0 | >3.0 (riesgo CV alto) / >10 (infección, repetir) | Ridker PMID 12551853 ✓ |
| Homocisteína | <9 µmol/L | 9–12 | >15 (hiperhomocisteinemia) | Wald PMID 12446535 ✓ · Clarke PMID 20937919 ✓ |

### Recuperación (wearable)
| Marcador | Banda óptima | Sub-óptima | Bandera → revisar | Fuente |
|----------|-------------|-----------|-------------------|--------|
| HRV (rMSSD) | percentil alto por edad/sexo | medio | caída sostenida + síntomas | Shaffer PMID 29034226 ✓ |
| Sueño (duración/profundo) | 7–9 h regular | 6–7 / irregular | <6 h crónico, o señales de apnea → médico | Cappuccio 20469800 ✓ · Irwin 26140821 ✓ |
| FC reposo | <60 lpm (sin meds) | 60–75 | >85 sostenida + síntomas | Zhang PMID 26598376 ✓ |

### Comportamiento (autorreporte P04 — peso bajo a propósito)
Escala 0–100 por hábito (sueño, ejercicio, estrés, alcohol). **Es la señal más débil (autorreporte)** → no debe dominar; si faltan labs, no inflar Longevidad solo con esto (§7).

> Cada banda se cita en `25_biomarcadores_panel_optimizacion.md` con su fuente, igual que las monografías. Los `[verificar]` se cierran como cerramos los `[FALTA FUENTE]` del lifestyle.

---

## 5. Normalización y agregación

1. **Valor → 0–100 por marcador:** función monótona por tramos sobre la banda (óptima=100, sub-óptima=interpolado, fuera de banda=bajo). Curva documentada por marcador, no global.
2. **Marcador → subscore:** promedio ponderado de los marcadores del subscore (pesos declarados).
3. **Subscore → vertiente:** fórmulas §2 y §3.
4. **Versionado:** cada cambio de banda/peso sube `metodologia_version` y se loggea (auditable).

---

## 6. Doble umbral y derivación (cortafuegos de compliance)

- **Banda de optimización** → puntúa el índice. Lenguaje: "oportunidad de optimización".
- **Umbral clínico** → **NO puntúa como "malo"; dispara bandera de derivación**: "Este valor amerita valoración médica" + Ruta B. El índice nunca dice "tienes X enfermedad".
- Disparadores de Ruta B (médico): valor cruza umbral clínico · solicitud de Av.2/Rx · antecedentes relevantes · combinación de banderas.
- **El modelo sugiere; el médico decide/firma** (COMPLIANCE §4). El índice no prescribe ni diagnostica.

---

## 7. Degradación por datos faltantes (anti-score-engañoso)

Al inicio casi nadie tendrá labs + wearable + cuestionario completos.

- Calcular cada vertiente **solo con los subscores disponibles**, re-normalizando pesos al subconjunto presente.
- Mostrar **completitud/confianza**: "Longevidad 71 · basado en 2 de 4 señales (faltan labs, wearable)".
- **Regla dura:** si solo hay Comportamiento (autorreporte), **no** emitir un Vigente Longevidad como si fuera medido — marcarlo "preliminar" y empujar a subir labs/wearable.
- Sin un mínimo de señales objetivas, mostrar el subscore disponible pero **no** el índice de vertiente como número "duro".

---

## 8. Compuesto (opcional, secundario)

- Default si se muestra: `Vigente = 0.5·Estético + 0.5·Longevidad`, etiquetado "vista general".
- Toggle opcional "ponderar por mi objetivo" (P04): Piel → 60/40 estético; Longevidad → 40/60. **Los dos sub-scores se quedan objetivos** (no se reponderan); solo el compuesto opcional usa el objetivo.
- **No** es el headline. El headline son los dos números.

---

## 9. Compliance (sin mover la línea)

- Optimización/bienestar, **no** diagnóstico (COFEPRIS Art. 309).
- **Biomarcadores: lectura + "por qué importa", sin tag de evidencia clínica en el valor del lab** (COMPLIANCE §3).
- Longevidad = "oportunidades de optimización", nunca "enfermedad".
- **PHI:** los labs son datos de salud sensibles (LFPDPPP). Aplica la disciplina de la auditoría de código: nada de labs reales en fixtures/git, redacción en trazas, consentimiento + Aviso de Privacidad antes de capturar.
- UI: scores etiquetados **"ilustrativo · modelo en validación"** hasta calibrar.

---

## 10. Validación — qué se puede afirmar y cuándo

- **Hoy (constructo):** cada subscore usa marcadores aceptados y dirección correcta; sanity-check contra casos conocidos (ej. labs propios) — ¿el score se mueve como se espera?
- **Futuro (predictiva):** con re-tests y outcomes acumulados, calibrar pesos/bandas contra desenlaces. Hasta entonces **no** se afirma poder predictivo.

---

## 11. Fuentes de las bandas — todas verificadas (Europe PMC, 2026-06-09)

| Marcador | Fuente | PMID |
|----------|--------|------|
| Glucosa / HbA1c | ADA, Classification and Diagnosis of Diabetes 2021 | 33298413 ✓ |
| ApoB / triglicéridos | ESC/EAS Guidelines dyslipidaemias 2019 (Mach) | 31504418 ✓ |
| ApoB (causalidad) | Ference, ApoB y ASCVD | 28444290 ✓ |
| hs-CRP | Ridker, hs-CRP en prevención CV (estratos <1/1–3/>3) | 12551853 ✓ |
| Homocisteína | Wald 12446535 ✓ · Clarke 20937919 ✓ | |
| HRV | Shaffer & Ginsberg | 29034226 ✓ |
| Sueño | Cappuccio 20469800 ✓ · Irwin 26140821 ✓ | |
| FC reposo | Zhang, FC reposo y mortalidad (meta) | 26598376 ✓ |

**0 `[verificar]` pendientes.** Nota: los cutoffs numéricos exactos por banda deben transcribirse de la guía citada al implementar (la guía es la fuente; aquí van orientativos a su criterio).

---

## 12. Implementación (orden — contrato antes que handlers)

1. **Lock de esta spec** (bandas + umbrales + fórmulas + degradación). PMIDs ya verificados (§11); transcribir los cutoffs numéricos exactos de cada guía.
2. `diagnostico_vigente.py`: `subscore_biologico → subscore_termografia`; exponer `indice_estetico`.
3. `indice_longevidad.py` (rag-bot): normalización de biomarcadores + wearable + cuestionario, con degradación y doble umbral.
4. `25_biomarcadores_panel_optimizacion.md`: documentar todas las bandas con fuente (el SSOT del índice).
5. `hv-data.jsx` P06: dos scores (ej. "64 Estético · 71 Longevidad") + señales etiquetadas por rama + completitud.
6. Sanity-check contra caso real; iterar bandas.

> Regla: el código no se escribe hasta que §4 (bandas) y §6 (umbrales/derivación) estén locked. Eso es lo difícil; el refactor es mecánico después.
