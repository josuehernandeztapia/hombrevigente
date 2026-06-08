# Triage MVP-0 — Verde vs marcado

**HV only · La contención segmentada es el producto**

---

## Regla en una línea

| Perfil | Cliente ve | Tú haces |
|--------|------------|----------|
| **Verde** | Velocidad · stack · empieza hoy | Pipeline → plantilla → WA #4 verde |
| **Marcado** | Empatía · “lo alineamos con tu médico” | Clearance A/B/C1/C2/D · no plantilla verde |

El gate pesado es **invisible para la mayoría** — vive en Tally + `mvp0_lib` + routing.

---

## Cómo se decide (automático)

`bandera_activa` en intake si cualquiera:

- Antecedente oncológico  
- Psiquiatría / medicación (litio, quetiapina, bipolar…)  
- Cardio / renal / hepática significativa  
- Embarazo / lactancia / menor  

```bash
cd rag-bot
python scripts/mvp0_route.py fixtures/caso0_intake_p1_entrega.json
# → MARCADO

python scripts/mvp0_route.py fixtures/caso0_intake.json  # sin banderas → VERDE
```

---

## Rutas operativas

| Paso | Verde | Marcado |
|------|-------|---------|
| Post-Tally | Script #3 corto | Script #3 + bandera |
| Protocolo | `MVP0_Template_Beta.md` | Template + bloques + clearance |
| Entrega WA | `MVP0_Entrega_Verde.md` #4 | Lifestyle primero + clearance (`MVP0_Entrega_Marcado.md`) |
| Médico | Revisión aliado HV (ideal) | **Específico por bandera** (psiq, onco…) |
| Caso #0 / #1 | — | `MVP0_Caso0_Clearance_Psiquiatra.md` (peor caso) |

---

## UX — qué NO hacer

- ❌ Mostrar bloques A/B/C/D al cliente verde  
- ❌ Mismo mensaje #4 para todos  
- ❌ “Necesitas tesis médica” en onboarding de quien no tiene bandera  

## UX — qué SÍ hacer

- ✅ Verde: “Tu Stack Vigente está listo” en 24–48h  
- ✅ Marcado: “Por tu perfil de salud, lo revisamos contigo y tu médico — eso es lo que nos diferencia”  
- ✅ Caso #1 (tú): máximo cuidado = credibilidad del sistema  

---

## Foso vs gris

| Gris | Hombre Vigente |
|------|----------------|
| Inyectable + disclaimer | No inyectable a bipolar sin psiquiatra |
| Mismo funnel para todos | Triage silencioso |
| Carrera al fondo legal | Claridad fundamentada = premium |

---

*Ver `MVP0_Doctrina.md` · routing: `rag-bot/scripts/mvp0_route.py`*