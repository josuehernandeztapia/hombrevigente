# User Histories — Hombre Vigente (MVP-0 → MVP-1)

**Versión:** 1.0 · Junio 2026  
**Alcance activo:** MVP-0 concierge manual (Sprint 01)  
**Relacionado:** [`SPRINT_01_MVP0_Concierge.md`](SPRINT_01_MVP0_Concierge.md) · [`MVP0_Playbook.md`](MVP0_Playbook.md) · `rag-bot`

Formato: **Como** [persona] · **Quiero** [acción] · **Para** [beneficio]  
Prioridad: **P0** (sprint) · **P1** (MVP-0 completo) · **P2** (MVP-1)

---

## Personas

| ID | Persona | Descripción |
|----|---------|-------------|
| **P0** | Juan (fundador / concierge) | Opera MVP-0, Caso #0, knowledge loop |
| **B1** | Beta | Hombre 35–55, energía/estética/longevidad, gratis a cambio de feedback |
| **M1** | Médico aliado | Revisa protocolos; clearance Av.2 / banderas |
| **M2** | Psiquiatra tratante | Solo Caso #0 y betas con psicofármacos (litio, etc.) |
| **SYS** | Sistema (RAG / tracker) | Automatización asistida, no reemplaza juicio humano |

---

## Epic E1 — Reclutamiento y onboarding

### HU-001 · Invitar beta (P0)
**Como** fundador **quiero** enviar una invitación clara por WhatsApp **para** reclutar 5–10 betas sin sonar a venta agresiva.

**Criterios de aceptación**
- Usa script #1 de `MVP0_WhatsApp_Scripts.md`
- Registro en Pipeline (nombre, estado `lead`)
- Explica: gratis, 4 semanas, feedback a cambio

---

### HU-002 · Completar onboarding (B1)
**Como** beta **quiero** llenar un formulario en &lt;10 min desde el cel **para** entregar mis datos sin fricción.

**Criterios de aceptación**
- Tally con `MVP0_Cuestionario.md`
- Sube foto y PDF labs (opcional pero incentivado)
- Consentimiento explícito (educativo, no Rx)
- Screening 🔴 obligatorio

---

### HU-003 · Confirmar recepción (P0)
**Como** fundador **quiero** confirmar al beta que recibí sus datos **para** reducir ansiedad y abandonment.

**Criterios de aceptación**
- Script #3 en &lt;24 h post-Tally
- Si bandera screening → script #3 variante médica, no protocolo aún
- Estado Pipeline → `onboarding` / `screening`

---

## Epic E2 — Screening y protocolo

### HU-004 · Screening de seguridad (P0)
**Como** fundador **quiero** revisar banderas rojas antes de armar protocolo **para** no recomendar stacks riesgosos sin médico.

**Criterios de aceptación**
- Checklist playbook §4 (onco, psiq, cardio, embarazo, menores)
- Columna Pipeline `Bandera screening` llena
- Si bandera → no entregar hasta clearance

---

### HU-005 · Armar protocolo personalizado (P0)
**Como** fundador **quiero** generar un protocolo desde plantilla + datos del beta **para** entregar valor en 24–48 h.

**Criterios de aceptación**
- Usa `MVP0_Plantilla_Protocolo.md` + LLM como copiloto
- Mapeo objetivo → stack (Glow / Wolverine / Metabolic)
- Lenguaje educativo, disclaimers, sin “cura/tratamiento”
- 20–40 min por beta (meta operativa)

---

### HU-006 · Revisión médica obligatoria (M1)
**Como** médico aliado **quiero** revisar cada protocolo antes de envío **para** asumir responsabilidad clínica de forma ordenada.

**Criterios de aceptación**
- Recibe PDF/borrador con datos baseline del beta
- Marca `Revisado x médico` en Pipeline + fecha
- Rechaza o pide ajuste con comentario trazable
- SLA objetivo: 48 h

---

### HU-007 · Entregar protocolo (P0 → B1)
**Como** beta **quiero** recibir mi protocolo por WhatsApp **para** saber qué hacer las próximas 4 semanas.

**Criterios de aceptación**
- Script #4 + PDF o mensaje estructurado
- Disclaimer visible
- Estado → `protocolo-entregado`
- Check-in semana 1 agendado (mental/calendario)

---

## Epic E3 — Concierge y RAG (asistido)

### HU-008 · Responder duda puntual (P0)
**Como** concierge **quiero** consultar el motor RAG y pegar respuesta editada **para** responder en &lt;15 min sin inventar.

**Criterios de aceptación**
- `python scripts/concierge_mvp.py "pregunta"`
- `role=concierge`, respuesta editable antes de enviar
- Fila en tracker **RAG Concierge** (decision_id, gate_path)
- Si `blocked` → derivar médico, no discutir con el modelo

---

### HU-009 · Escalar gap de conocimiento (P0)
**Como** fundador **quiero** detectar preguntas sin buena respuesta en KB **para** mejorar el producto con tráfico real.

**Criterios de aceptación**
- Revisión viernes: `/admin/knowledge/gaps`
- Clasificar: promover / ignorar / gate médico
- ≥1 promotion legítima por sprint (`promote_e2e.py`)
- Re-embed verificado en prod

---

### HU-010 · Beta pregunta off-topic (B1)
**Como** beta **quiero** una respuesta honesta cuando pregunte algo fuera de scope **para** confiar en la marca.

**Criterios de aceptación**
- RAG devuelve `escalate` o mensaje claro “fuera de alcance”
- Concierge no improvisa clínica
- Opcional: anotar en gaps si es recurrente

---

## Epic E4 — Seguimiento y feedback

### HU-011 · Check-in semanal (P0 → B1)
**Como** fundador **quiero** hacer check-in semanas 1–3 **para** medir adherencia y ajustar.

**Criterios de aceptación**
- Script #5
- Registro en **Check-ins semanales** (energía, sueño, ánimo, dolor, adherencia %)
- Foto semanal opcional solicitada

---

### HU-012 · Feedback final e intención de pago (B1)
**Como** beta **quiero** dar feedback estructurado en semana 4 **para** cerrar el ciclo gratis con honestidad.

**Criterios de aceptación**
- Script #6 / encuesta
- Hoja **Feedback**: NPS, ¿pagaría?, ¿cuánto?, ¿refirió?
- Métrica reina: referido espontáneo

---

### HU-013 · Decidir go/no-go MVP-1 (P0)
**Como** fundador **quiero** evaluar métricas del sprint **para** decidir si construir semi-automático.

**Criterios de aceptación**
- Dashboard Sprint: ≥3 criterios GO de `SPRINT_01`
- Documentar retro en §10 del sprint
- Si NO-GO → iterar oferta, no código

---

## Epic E5 — Caso #0 (fundador)

### HU-014 · Baseline Caso #0 (P0)
**Como** fundador **quiero** completar mi propio baseline **para** probar el flujo antes de betas.

**Criterios de aceptación**
- Labs + RM/RX indexados (`MVP0_Caso0_Baseline.md`)
- Foto baseline checklist 3 min
- Subjetivo 1–5 documentado
- Pipeline fila #0 actualizada

---

### HU-015 · Protocolo Caso #0 con banderas (P0, M1, M2)
**Como** fundador con litio + antec. oncológico **quiero** un protocolo conservador revisado **para** no auto-experimentar sin red de seguridad.

**Criterios de aceptación**
- `MVP0_Caso0_Protocolo.md` enviado a médico + psiquiatra
- Litio 0.42 documentado → psiquiatra antes de cambios
- Gates RAG (`gate_psiquiatria`, `gate_oncologia`) validados en preguntas de prueba
- No iniciar stack hasta firmas

---

### HU-016 · Documentar transformación (P0)
**Como** fundador **quiero** registrar mi evolución 4 semanas **para** contenido de marca y primer dato del motor.

**Criterios de aceptación**
- Fotos semanales misma luz
- Diario ánimo/energía/ciática
- Anónimo disponible para SSOT narrativa E0 (sin PHI en repo público)

---

## Epic E6 — Compliance (transversal)

### HU-017 · Lenguaje COFEPRIS-safe (P0)
**Como** operador **quiero** que todo mensaje al cliente use lenguaje educativo **para** reducir riesgo regulatorio.

**Criterios de aceptación**
- Sin “cura/tratamiento/medicamento” en entregas
- Disclaimer en protocolo y WhatsApp
- Av.2 solo con médico + magistral

---

### HU-018 · Datos de salud privados (P0)
**Como** beta **quiero** que mis labs/fotos no se publiquen **para** confiar en el programa.

**Criterios de aceptación**
- PDFs/fotos en carpeta privada o Drive, no en git
- Consentimiento Tally
- Repo solo markdown agregado sin archivos clínicos

---

## Backlog MVP-1 (P2 — no sprint actual)

| ID | Historia (resumen) | Persona |
|----|-------------------|---------|
| HU-101 | Conectar wearable vía Terra/Rook | B1 |
| HU-102 | Subir labs → BloodGPT → datos estructurados | B1 |
| HU-103 | Selfie → Haut.AI scoring piel | B1 |
| HU-104 | Motor protocolo auto-borrador desde intake | P0 |
| HU-105 | Portal perfil (Healthie o similar) | B1 |
| HU-106 | WhatsApp API webhook (360dialog) | SYS |
| HU-107 | Checkout membresía Conekta/Stripe | B1 |
| HU-108 | Informe de Optimización PDF automático | B1 |

---

## Mapa historia → artefacto

| HU | Artefacto / herramienta |
|----|-------------------------|
| 001–003 | `MVP0_WhatsApp_Scripts.md`, Tally, Pipeline |
| 004–007 | `MVP0_Plantilla_Protocolo.md`, médico aliado |
| 008–010 | `concierge_mvp.py`, `hv-rag-api`, RAG Concierge sheet |
| 009 | `promote_e2e.py`, gaps API |
| 011–012 | Check-ins, Feedback sheets |
| 014–016 | `MVP0_Caso0_Baseline.md`, foto checklist |
| 017–018 | Playbook §4, consentimiento Tally |

---

## Definition of Done (MVP-0)

Una historia está **Done** cuando:
1. El flujo se probó con al menos 1 persona real (o Caso #0).
2. Quedó registro en tracker (Pipeline, RAG o Check-in).
3. No viola guardarraíles §4 playbook.
4. Si toca KB → decisión logged o gap tratado.

---

*Historias vivas: al cerrar Sprint 01, marcar Done en esta tabla o en el Dashboard del tracker.*