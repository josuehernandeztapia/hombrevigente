# MVP-0 — Cómo avanzar (sistema operativo)

**Junio 2026**

> Complementa `MVP0_Doctrina.md` (qué es el MVP) con **cómo moverse cada semana** sin atascarse en flujo o código.

**Relacionado:** `SPRINT_01_MVP0_Concierge.md` · `MVP0_Playbook.md` · `Fases_0_a_N.md`

---

## 1. Regla madre

**Avanzar = subir un peldaño de evidencia.**  
No avanzar = escribir código, docs o arquitectura sin que cambie una fila del Pipeline o un dato de un humano real.

```
EVIDENCIA > AUTOMATIZACIÓN > ARQUITECTURA > VISIÓN DE AGENTES
```

Si dudas qué hacer: **¿esto genera evidencia esta semana?** Si no → difiere.

---

## 2. Escalera de peldaños (orden fijo)

No saltas peldaños hacia arriba. Sí puedes hacer varios en paralelo si son el mismo esfuerzo humano.

| # | Peldaño | Evidencia (DoD) | Simulación permitida |
|---|---------|-----------------|----------------------|
| **P0** | Stack mínimo vivo | Tally + RAG + pipeline corre 1 vez | — |
| **P1** | Caso #0 cerrado | Protocolo PDF/WA entregado a ti + check-in S1 | Médico = consulta puntual / cola |
| **P2** | Template replicable | Misma plantilla usada sin reescribir desde cero | LLM redacta; tú editas |
| **P3** | Tracker operativo | Sheets Pipeline con ≥1 fila real actualizada | CRM = Sheets |
| **P4** | Primer beta externo | 1 persona: Tally completo + screening OK | WA manual; sin API |
| **P5** | Segundo protocolo entregado | ≥2 filas `protocolo-entregado` | Igual que P1 |
| **P6** | Señal de valor | ≥1 “aha” o intención de pago documentada | Encuesta verbal |
| **P7** | Loop RAG | ≥1 gap promovido desde pregunta real | promote manual |
| **P8** | Go Fase 1 | ≥3 betas + médico SLA + retro sprint | — |

**Hoy (jun 2026):** P0–P3 ✅ · clearance psiq ✅ · día 0 subjetivo ✅ · **C1 NMN lun 9 jun** · foto + Sheets + Gate A pendientes

---

## 3. Prioridades esta semana (HV only)

| Prioridad | Acción | Doc |
|-----------|--------|-----|
| **1** | **NMN 500 mg** lun 9 + diario 3 días | `MVP0_Caso0_Diario.md` · `MVP0_Caso0_Plan_C1_Gradual.md` |
| **2** | Foto baseline (3 min) | `MVP0_Caso0_Baseline.md` §5 |
| **3** | Subir tracker a Sheets | `MVP0_Tracker_Setup.md` |
| **4** | Check-in S1 dom 15 jun | `MVP0_Caso0_P1_Entrega.md` (#5) |
| **5** | Gate A → 1 beta (WA personal) | `MVP0_GateA_Invitacion.md` |
| **6** | Follow-up psiq: ayuno 16:8 + litio 0.42 | 1 línea WA |
| **—** | Médico aliado HV (cola) | `MVP0_Cola_Medica.md` |

**Anti-prioridades (prohibido esta fase):**
- Nuevos agentes / módulos HV
- Automatizar WA / webhooks Tally
- Golden trajectories E2E
- CMU S2+ (salvo que CMU sea tu único foco esa semana — entonces HV pausa, no paralelo)

---

## 4. Flujo manual canónico (el “producto” del MVP)

Un caso de punta a punta **sin integraciones**:

```
┌─────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────────┐
│  Tally  │───►│ Screening │───►│  Pipeline   │───►│  Protocolo   │
│  (link) │    │  (script) │    │  (1 comando)│    │  (plantilla) │
└─────────┘    └──────────┘    └─────────────┘    └──────┬───────┘
                                                          │
┌─────────┐    ┌──────────┐    ┌─────────────┐           ▼
│ Check-in│◄───│ WA pegado│◄───│ Revisión    │◄─── PDF / mensaje
│ semanal │    │ + RAG    │    │ médico/cola │
└─────────┘    └──────────┘    └─────────────┘
```

### Comandos (Caso #0 o beta)

```bash
cd ~/Desktop/hombrevigente/rag-bot

# 1. Intake → pipeline (ajusta paths a tu CSV/PDF)
python scripts/mvp0_pipeline.py --intake fixtures/caso0_intake.json  # o tally export

# 2. Pregunta del beta / tú
python scripts/concierge_mvp.py "tu pregunta aquí"

# 3. Screening ya en pipeline output — revisar flags antes de enviar protocolo
```

### Registro (cada paso = 1 fila o celda)

| Paso | Dónde registrar |
|------|-----------------|
| Tally recibido | Pipeline: `onboarding_completo`, fecha |
| Screening | Pipeline: notas + flags |
| Protocolo borrador | Pipeline: `borrador_listo` |
| Revisión médica | Pipeline: `medico_ok` o `pendiente_medico` |
| Entrega | Pipeline: `protocolo_entregado`, script #4 |
| Pregunta RAG | Hoja **RAG Concierge** |
| Check-in S1 | Pipeline + script #5 |

---

## 5. Árbol de decisión (cuando te atasques)

```
¿Qué quiero hacer?
│
├─ ¿Es para Caso #0 o beta esta semana?
│   ├─ NO → COLA (escribe en backlog, no ejecutes)
│   └─ SÍ ↓
│
├─ ¿Falta integración técnica?
│   ├─ SÍ → ¿Seguridad/consentimiento?
│   │        ├─ SÍ → NO simular. Parar.
│   │        └─ NO → Manual / script existente / pegar WA
│   └─ NO ↓
│
├─ ¿Falta médico?
│   ├─ Caso #0 → consulta puntual O entrega educativa con disclaimer fuerte
│   └─ Beta externo → no reclutar hasta SLA médico O modelo "lleva a tu médico"
│
└─ ¿Tengo >2h para code?
    → Solo si desbloquea P1–P3 (ej. fix tally_field_map, no nuevo agente)
```

---

## 6. Ritmo semanal (mínimo viable)

| Día | 15–30 min | Evidencia |
|-----|-----------|-----------|
| **Lun** | Revisar Pipeline + WA pendientes | 0 mensajes colgados |
| **Mar** | Avanzar **1 peldaño** (tabla §2) | 1 celda/fila actualizada |
| **Mié** | RAG: 1 consulta real logueada | Fila RAG Concierge |
| **Jue** | Check-in a quien tenga protocolo | 1 mensaje enviado |
| **Vie** | Gaps RAG (si hay tráfico) + retro 5 min | Nota: qué peldaño subió |

**Regla:** si la semana termina sin subir peldaño → la semana falló, aunque hayas codeado.

---

## 7. Cuándo sí escribir código (whitelist)

| OK | Ejemplo |
|----|---------|
| Fix que desbloquea pipeline real | `tally_field_map`, intake schema |
| Script que ahorra >30 min/caso | `tracker_pipeline_row.py` |
| RAG gap → promote | `promote_e2e.py` tras pregunta repetida |
| Test de regresión de lo que usas | `test_mvp0_lib.py` |

| NO | Ejemplo |
|----|---------|
| Nuevo agente | PersonaVigente ML |
| Infra “por si acaso” | State machine, traces CMU-port |
| Integración sin caso | Tally webhook, 360dialog |
| Refactor estético | Renombrar módulos |

**Presupuesto dev:** ≤**4 h/semana** en MVP-0. El resto = operación.

---

## 8. Puertas (gates)

### Gate A — Reclutar betas externos

- [ ] P1 Caso #0 protocolo entregado (aunque médico fuera “cola”)
- [ ] P3 Tracker con columnas del sprint
- [ ] Script #1 probado una vez
- [ ] Médico con SLA **o** modelo explícito “educativo + tu médico valida”

### Gate B — Automatizar algo (Fase 1 prep)

- [ ] P5 ≥2 protocolos entregados
- [ ] P6 ≥1 intención de pago
- [ ] Dolor repetido documentado (ej. “pegué WA 40 veces” → entonces API)

### Gate C — Go Fase 1

- [ ] P8 completo (ver `SPRINT_01` § métricas)
- [ ] Retro sprint escrita
- [ ] Burn stack estimado aceptado (`Stack_Tech_Costos_y_BuyVsBuild.md`)

---

## 9. Plan concreto — próximos 7 días

### Día 1–2: P1 Caso #0

- [ ] Correr pipeline si hace falta refresh
- [ ] Redactar protocolo desde `MVP0_Plantilla_Protocolo.md` + output pipeline
- [ ] Revisión: médico aliado **o** autorevisión con checklist screening + disclaimer
- [ ] Entregar a ti por WA (script #4) = **P1 done**
- [ ] Fila #0 Pipeline: todas las celdas hasta `protocolo_entregado`

### Día 3: P3

- [ ] Subir `MVP0_Beta_Tracker.xlsx` a Sheets
- [ ] Copiar fila #0; probar `tracker_pipeline_row.py` si aplica

### Día 4–5: P2 + check-in

- [ ] Guardar protocolo #0 como **template** (qué se reutiliza vs qué se edita)
- [ ] Check-in semana 1 a ti mismo (script #5)

### Día 6–7: P4 o P7 (el que toque)

- **Si Gate A:** 1 invitación beta (script #1)
- **Si no Gate A:** 5 consultas RAG tuyas reales → loguear → intentar 1 promote

---

## 10. Métrica única de dashboard

Un solo número por semana:

**`peldaño_máximo_alcanzado`** (0–8 de la tabla §2)

| Semana | Meta mínima |
|--------|-------------|
| Esta | P1 |
| Siguiente | P3 + P4 o P6 |
| Sprint end | P5–P8 según betas |

---

## 11. CMU vs HV (regla de foco)

| Semana tipo | HV | CMU |
|-------------|-----|-----|
| **HV** (default) | Peldaños P1–P8 | Solo mantenimiento |
| **CMU** (explícita) | Ritual diario 10 min | S1 cierre / S2 |
| **Nunca** | Ambos con features nuevas en paralelo | — |

---

## 12. Una línea para el equipo

> *"Estamos en MVP-0: avanzamos subiendo peldaños de evidencia con humanos en el loop. Si no hay flujo, simulamos ops — no safety. El código sirve al caso, no al revés."*

---

*Si este doc y `MVP0_Doctrina.md` divergen de un sprint antiguo, gana este par.*