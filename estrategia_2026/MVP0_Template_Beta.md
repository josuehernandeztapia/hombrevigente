# Template protocolo beta — Hombre Vigente (P2)

**Uso:** duplicar por cada beta. Solo editar bloques `[VAR]`. El resto es fijo MVP-0.

**Flujo:** Tally → `mvp0_route.py` → plantilla entrega → protocolo → WA

```bash
python scripts/mvp0_route.py data/intake/NOMBRE_intake.json
# verde  → MVP0_Entrega_Verde.md
# marcado → MVP0_Entrega_Marcado.md + clearance si aplica
```

---

## Bloques fijos (no reescribir)

Copiar tal cual de `MVP0_Plantilla_Protocolo.md` §7 disclaimers + regla farmacia magistral.

**Si `bandera_activa`:** insertar al inicio:

> ⚠️ Caso con bandera de screening. No iniciar stack sin clearance médico. Información educativa, no prescripción.

---

## Bloques variables por beta

| Bloque | Fuente | Campo |
|--------|--------|-------|
| Nombre | Tally | `identity.nombre` |
| Objetivo principal | Tally | `objetivos.principal` |
| Meta 8 semanas | Tally | `objetivos.meta_8_semanas` |
| Subjetivo | Tally | energía/sueño/entreno/dolor |
| Screening | Pipeline | `screening.bandera_detalle` |
| Labs | `labs_intake_manual` | snippet JSON |
| Stack | `mvp0_lib` | `pipeline.stack_sugerido` |
| Lifestyle inmediato | Reglas | ver tabla abajo |
| Stack avanzado | Solo si sin bandera o post-clearance | tabla plantilla |

---

## Mapeo stack → enfoque (v1 reglas)

| `stack_sugerido` | Enfoque 1 línea | Lifestyle inmediato |
|------------------|-----------------|---------------------|
| `wolverine` | Reparación / dolor / estructural | Movilidad + fuerza bajo impacto + sueño |
| `glow` | Piel / colágeno / glow | SPF + proteína + sueño |
| `metabolic` | Grasa visceral / metabólico | Zona 2 + proteína + monitoreo glucosa si aplica |
| `base` | Energía / longevidad general | Sueño + movimiento + estrés |

**Con bandera activa:** solo fila lifestyle + "stack avanzado bloqueado hasta médico".

---

## Esqueleto (copiar por beta)

```markdown
# PROTOCOLO — [NOMBRE]

Fecha: [FECHA] · Revisado: [Pendiente médico / nombre] · Vigencia: 4 semanas

## 1. Punto de partida
- [EDAD] · objetivo: [OBJETIVO]
- Meta 8 sem: "[META]"
- Energía [X]/5 · Sueño [X]/5 · Entreno [N]d/sem · Dolor: [TEXTO]
- Datos: foto [S/N] · labs [S/N] · wearable [S/N]
- Banderas: [NINGUNA / detalle]

## 2. Lectura datos
[Pegar snippet labs o "pendiente"]

## 3. Enfoque
Stack: [STACK] — [razón 1 línea]

### Empieza ya (todos)
- Sueño 7-9h · hidratación · movimiento según tabla stack
- Diario 1-5: energía, sueño, ánimo, dolor
- Foto semanal misma luz

### Stack avanzado
[Si bandera: "Bloqueado hasta clearance" + lista orientativa para médico]
[Si no bandera: oral + avanzado de plantilla con dosis conservadoras]

## 4. Seguimiento
Check-in semanal · re-eval 4 sem

## 5. Disclaimer
[FIJO — plantilla §7]
```

---

## Comandos por beta nuevo

```bash
cd ~/Desktop/hombrevigente/rag-bot

# 1. Intake desde Tally export
python scripts/intake_from_tally.py path/to/export.csv -o data/intake/NOMBRE_intake.json

# 2. Pipeline
python scripts/mvp0_pipeline.py --intake data/intake/NOMBRE_intake.json

# 3. Fila tracker
python scripts/tracker_pipeline_row.py data/intake/NOMBRE_intake.json --tsv

# 4. Borrador protocolo (si existe)
python scripts/protocol_draft.py data/mvp0_runs/.../intake/....json
```

---

## Caso #0 = referencia P2

| Elemento | Archivo modelo |
|----------|----------------|
| Protocolo completo | `MVP0_Caso0_Protocolo.md` |
| Resumen WA | `MVP0_Caso0_Resumen_Entrega.md` |
| Entrega ops | `MVP0_Caso0_P1_Entrega.md` |
| Baseline | `MVP0_Caso0_Baseline.md` |

**P2 done cuando:** el segundo beta use este esqueleto sin reescribir estructura — solo `[VAR]`.

---

*HV MVP-0 · P2*