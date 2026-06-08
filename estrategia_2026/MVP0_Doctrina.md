# MVP-0 — Doctrina (qué es, qué no es, cuándo simular)

**Junio 2026 · Uso interno + aliados**

---

## Una frase

> **MVP-0 valida si el valor existe con humanos y datos reales — no si el software tiene flujo E2E.**  
> Si falta un eslabón, **simulamos o manualizamos** para no parar. Eso no es deuda moral; es el diseño.

---

## Qué SÍ decir (y mantener)

| Afirmación | Verdad |
|------------|--------|
| "Es un MVP" | Concierge manual, beta gratis, alcance acotado |
| "No hay flujo automatizado" | Tally → humano → Sheets → pipeline script → WA pegado |
| "Simulamos lo que falta" | Stubs operativos: médico en cola, CRM = Sheets, bot = copy-paste RAG |
| "Validamos el negocio" | ¿Quieren protocolo + seguimiento? ¿Volverían? ¿Referirían? |
| "El RAG ya existe" | Copiloto del operador, no agente autónomo frente al cliente |

---

## Qué NO decir (aunque sea MVP)

| ❌ Evitar | Por qué |
|----------|---------|
| "Ya tenemos 9 agentes en producción" | Andamiaje / visión — no producto |
| "El bot atiende solo" | Hoy es humano + asistencia LLM |
| "Diagnóstico clínico automatizado" | Educación + screening; médico en banderas |
| "Simulamos compliance" | Screening, consentimiento y disclaimer son reales |

---

## Regla de simulación

```
¿Falta X para cerrar el caso?
  → ¿Es SEGURIDAD o CONSENTIMIENTO?     → NO simular. Parar o escalar humano.
  → ¿Es AUTOMATIZACIÓN u OPS?           → SÍ simular (manual, script, cola, placeholder).
  → ¿Es PROVEEDOR externo sin contrato? → Simular con proceso manual equivalente.
```

### Se simula (ejemplos MVP-0)

| Gap | Simulación aceptada |
|-----|---------------------|
| WhatsApp API / número HV / Twilio | **No existe aún (Fase 1).** WA **personal** a contactos, Notas, email, o calendario |
| CRM / portal | Google Sheets `MVP0_Beta_Tracker` |
| Parser labs SaaS | `labs_intake_manual.py` + PDF |
| Entrega protocolo auto | Plantilla + LLM + **revisión médica** (o cola "pendiente médico") |
| Agente multi-turno | Tú llevas la conversación; `concierge_mvp.py` asiste |
| Wearables | Campo manual en Tally |
| Pagos | Beta gratis; intención de pago verbal |
| Check-ins automáticos | Scripts WA + recordatorio en calendario |
| State machine / traces | Fila en Pipeline + notas; código después |

### No se simula (línea roja)

- Screening de exclusión (onco, psiquiátrico, interacciones) — **correr siempre**
- Disclaimer educativo en cada entrega
- Consentimiento explícito (Tally)
- Datos de salud: carpeta privada, no en git
- Protocolo a **tercero** sin revisión médica o sin "valida con tu médico" explícito

---

## Caso #0 (fundador) vs betas externas

| | Caso #0 (tú) | Beta externo |
|---|--------------|----------------|
| Objetivo | Credibilidad + primer dato + template | Validar que **otro** percibe valor |
| Médico | Puede ir en cola / consulta puntual / autovalidación con disclaimer | Revisión médica aliada **o** entrega 100% educativa + "lleva esto a tu médico" |
| Flujo | El más roto está permitido | Mínimo: Tally + screening + protocolo + 1 check-in |
| Simulación | Máxima (eres el laboratorio) | Solo en ops, nunca en safety |

**Sin médico aliado:** no reclutar betas externos; **sí** avanzar Caso #0 y stack. No es atasco — es alcance.

---

## Qué estamos validando (y qué no)

| Validamos en MVP-0 | No validamos en MVP-0 |
|--------------------|------------------------|
| Valor percibido del protocolo + seguimiento | Unit economics a escala |
| Fricción de onboarding (Tally, labs, foto) | Automatización WA |
| Señales de retención / referido | OptiVigente, MILP, 9 agentes |
| Calidad del RAG como copiloto | Agente autónomo |
| Screening y lenguaje compliance | Portal, pagos, Prescrypto |

---

## Relación con `Agentes_Valor_de_Desarrollo.md`

- Los **9 agentes** = mapa de futuro, **no** checklist del MVP.
- **AI-native en MVP-0** = 1 loop manual con datos reales: intake → protocolo → check-in → re-enganche.
- ChatVigente = **BUILD, ya** — como asistente del operador, no como producto final.
- Todo lo demás (Persona ML, Opti, Diagnóstico térmico, Asset, Safety) = **después** de ≥3 betas con señal.

---

## Relación con CMU (mismo criterio)

CMU Agent Intelligence (S1–S7) es **producto de origination**, no bloqueante de HV MVP-0.  
Si CMU avanza: bien. Si no: HV sigue con simulación manual. **Proyectos desacoplados.**

---

## Definición de "avanzar"

Avanzar en MVP-0 = **más evidencia de valor**, no más líneas de código.

| Cuenta como avance | No cuenta (solo feel busy) |
|--------------------|----------------------------|
| Caso #0 protocolo entregado | Refactor sin beta |
| 1 beta con Tally completo | Nuevo agente sintético |
| 1 gap RAG promovido desde tráfico real | Golden set sin tráfico |
| 1 check-in semana 1 respondido | UI admin traces |

**Sistema operativo (peldaños, semana, gates):** ver `MVP0_Como_Avanzar.md`.

---

## Triage y gates (verde vs marcado)

Este nivel de muro **no es para todos** — es para el **peor caso** (Caso #0/#1: litio, quetiapina, onco).

| Perfil | Experiencia cliente | Backend |
|--------|---------------------|---------|
| **Verde** | Rápido · Av.1 · stack orientativo, empieza hoy | Screening sin bandera |
| **Marcado** | Routing médico · bloques A/B/C/D con **porqué** | `bandera_activa` + mensaje tipo `MVP0_Caso0_Clearance_Psiquiatra.md` |

**La contención es el producto** frente al gris (inyectable + disclaimer). Cobras claridad fundamentada, no vial.  
**Riesgo UX:** que el promedio verde sienta fricción — el gate va pesado solo en minoría marcada; invisible para mayoría.

---

## Canal MVP-0 (realidad jun 2026)

| Existe hoy | No existe (Fase 1+) |
|------------|---------------------|
| WhatsApp **personal** (tu cel, a conocidos) | Número dedicado Hombre Vigente |
| Scripts copiar/pegar | WhatsApp Business API / 360dialog / Twilio |
| Tally link por DM | Webhooks automáticos |

**Caso #0:** entrega a ti = Notas / WA “mensaje a ti mismo” / email — no requiere número HV.  
**Betas:** mismo WA personal de Juan hasta que exista número + API (Gate B en `MVP0_Como_Avanzar.md`).

---

## Texto listo para copiar (pitch honesto)

> "Hombre Vigente está en **MVP-0**: validamos con un concierge manual si hombres quieren un protocolo de longevidad con seguimiento. No es el producto final automatizado — **no hay flujo E2E**. Donde falta integración, operamos manual o simulamos el paso. Lo que sí es real: intake, screening, RAG asistido, pipeline de labs y entrega educativa de protocolo. La automatización viene en Fase 1 cuando tengamos señal de pago y retención."

---

*Doctrina operativa. Si contradice un doc antiguo que promete "9 agentes production-ready", gana este archivo.*