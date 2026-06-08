# Bot → Agente → Plataforma agéntica (HV)

**Junio 2026**

> Marco conceptual + mapa de implementación para Hombre Vigente, usando como referencia el programa CMU de 7 sprints (`~/Downloads/SPRINT-QUIRURGICO-AGENT-INTELLIGENCE.md`).

**Relacionado:** `Agentes_Valor_de_Desarrollo.md` · `Fases_0_a_N.md` · `MVP0_User_Histories.md` · `SPRINT_01_MVP0_Concierge.md`

---

## 1. Definiciones (sin marketing)

| Nivel | Comportamiento | Memoria | Iniciativa |
|-------|----------------|---------|------------|
| **Bot** | Responde si le preguntan | Turno o ninguna | Cero |
| **Agente** | Persigue un **outcome** con herramientas | Sesión persistida + slots | Pide lo que falta, retoma, orquesta |
| **Plataforma agéntica** | Varios roles/flujos, mismo contexto, mejora con evidencia | Cross-session, cross-rol | Anticipa, escala, regresión E2E |

**HV hoy:** bot reactivo fuerte (RAG + gates) + **humano-agente** (fundador en WhatsApp) + scripts batch (`mvp0_pipeline`). El software es copiloto; tú llevas el caso.

---

## 2. Escalera CMU (7 sprints → agente)

| # | Sprint CMU | Qué agrega | Señal “ya es agente” |
|---|------------|------------|----------------------|
| 1 | Observability + reasoning trace | Diagnóstico de decisiones | MTTD &lt;2 min: “¿por qué respondió X?” |
| 2 | State machine resumible | Dónde quedó el usuario | Reentry 3 días sin perder contexto |
| 3 | Bulk vision orchestration | Actúa sobre N archivos | Clasifica + llena slots + pide faltantes |
| 4 | NLU slot-filling proactivo | Lleva la conversación | Interrupciones + re-prompt sin spam |
| 5 | RAG conversacional con contexto | FAQ sin perder slot abierto | Dialog stack: pregunta → respuesta → retoma |
| 6 | Golden trajectories E2E | Flujos largos blindados | 25 turnos en CI, no solo 1 query |
| 7 | Multi-agent shared context | Varios roles, un folio | Director/promotor/prospecto sin pisarse |

**Critical path CMU:** `1 → 2 → (3 ∥ 4) → 5 → 6 → 7`

---

## 3. Las 4 capas de una plataforma agéntica

| Capa | CMU | HV hoy | Gap |
|------|-----|--------|-----|
| **Memoria operativa** | `state_data` JSONB, fases, slots | `intake_mvp0.json` + Pipeline Sheets | State machine explícita por beta |
| **Percepción + acción** | Clasificar docs, fillSlot, notificar | `labs_intake_manual`, `mvp0_pipeline`, Tally | Bulk WA media; webhooks |
| **Razonamiento trazable** | `agent_traces` por turno | `decision_log` + `gate_path` por query | Trace por **beta + turn_number**, no solo pregunta suelta |
| **Gobierno + mejora** | Golden trajectories + multi-rol | `golden_runner`, `promote_e2e`, médico humano | Trajectory E2E: Tally → protocolo → S1 |

---

## 4. Checklist: ¿es agente?

| # | Pregunta | HV (jun 2026) |
|---|----------|---------------|
| 1 | ¿Estado persiste entre sesiones? | Parcial (`intake.json`, Sheets manual) |
| 2 | ¿Sabe qué falta y lo pide solo? | No (scripts #2 humanos) |
| 3 | ¿Orquesta herramientas (parse, CRM, WA)? | Parcial (`mvp0_pipeline` manual) |
| 4 | ¿Explicas por qué decidió en &lt;2 min? | Parcial (RAG sí; flujo beta no) |
| 5 | ¿Tests E2E de trayectoria? | Parcial (golden Q&A; falta TRAJ beta) |
| 6 | ¿Multi-rol mismo caso? | Manual (tú + médico + beta) |

**Score:** ~2/6 → **bot avanzado + concierge humano**, no agente software end-to-end.

---

## 5. Mapa CMU → Hombre Vigente

| Concepto CMU | Equivalente HV |
|--------------|----------------|
| `origination_id` | `tally_response_id` / `pipeline_row` |
| `current_phase` | `pipeline.estado` (lead → onboarding → screening → protocolo → semana-N) |
| `slots_filled` | `data_moat` (foto, labs, wearable) |
| `resumeConversation(3d)` | Script #2 + “vas en 5/8 pasos” |
| `handleBulkDocs` | WA: varios PDFs/fotos → pipeline |
| `escalateToHuman` | `screening.bandera_activa` → médico (gate `blocked`) |
| `parseGeneralQuestionIntent` | `concierge_mvp.py` + contexto intake |
| `frozen_context` | `identity` + `objetivos` + `screening` en intake JSON |
| Director / promotor / prospecto | Fundador / médico / beta |

---

## 6. Sprint CMU → User Histories HV

| Sprint | Prioridad HV | Historias | Fase | Entregable técnico |
|--------|--------------|-----------|------|-------------------|
| **S1 Traces** | **P0** | HU-008, HU-009 | F0→1 | Extender `decision_log`: `beta_id`, `turn_number`, `channel=whatsapp` |
| **S2 State** | **P0** | HU-002, HU-003, HU-004, HU-007 | F0→1 | `schemas/beta_state.json` + enum fases + `next_action` |
| **S3 Bulk** | **P1** | HU-002, HU-005 | F1 | Media batcher WA → `labs_intake` + foto slot |
| **S4 Proactivo** | **P1** | HU-003, HU-011 | F1 | Nudges: slots faltantes post-Tally; reentry 24h/3d |
| **S5 RAG+contexto** | **P0** | HU-008 | F1 | `/rag/query` con `intake_id` en body; reprompt slot |
| **S6 Trajectories** | **P1** | HU-014 (Caso #0), DoD MVP-0 | F1 | `TRAJ-HV-001` … `006` en `golden_runner` o script aparte |
| **S7 Multi-rol** | **P2** | HU-006 (M1), HU-018 | F2 | Vistas médico vs beta; notas con visibility |

---

## 7. Golden trajectories HV (borrador)

| ID | Nombre | Turnos clave | Estado final esperado |
|----|--------|--------------|------------------------|
| **TRAJ-HV-001** | Beta happy path | Invitación → Tally completo → protocolo → S1 check-in | `protocolo-entregado` |
| **TRAJ-HV-002** | Preguntas mid-onboarding | Tally parcial → FAQ RAG → retoma form | slots incompletos OK |
| **TRAJ-HV-003** | Bulk labs | WA 3 PDFs → parse → intake actualizado | `labs_parse_json` lleno |
| **TRAJ-HV-004** | Screening bandera | Tally onco/psiq → no protocolo → clearance médico | `screening` hasta M1 OK |
| **TRAJ-HV-005** | Reentry 3 días | Abandona Tally → script #2 → completa | resume sin perder datos |
| **TRAJ-HV-006** | Caso #0 regression | Intake gbAO6Yl + litio labs + gates G-006 | golden gates pass |

---

## 8. Roadmap HV (critical path agente)

Fase 0 (ahora): **humano = agente**, software = copiloto.

```
Fase 1 — importar tesis CMU (sin overbuild):

  S1 Traces por beta          ← extender decision_log
       ↓
  S2 State machine Pipeline   ← JSON/DB + next_action
       ↓
  S3 Bulk intake  ∥  S4 Nudges
       ↓
  S5 RAG + frozen_context (intake_id)
       ↓
  S6 TRAJ-HV-001..006 en CI
       ↓
  S7 Multi-rol (portal / Healthie) — Fase 2
```

**No construir S7 en Fase 0.** Médico sigue como `escalate`/`blocked` humano — correcto para compliance HV.

---

## 9. Qué NO copiar de CMU

| CMU | Por qué no tal cual en HV |
|-----|---------------------------|
| Onboarding 25 turnos auto | MVP-0 valida con 5–10 betas manuales primero |
| Vision classifier 9 tipos doc | HV: labs PDF + selfie (menos tipos) |
| Multi-rol director/promotor | HV: fundador + médico + beta (3 roles, no 3 canales B2B) |
| Bot “humano” sin gates clínicos | HV: `blocked` obligatorio en psiq/onco/litio |

---

## 10. Agentes HV vs sprints CMU (visión `Agentes_Valor_de_Desarrollo`)

| Agente HV | Bot hoy | Agente cuando… |
|-----------|---------|----------------|
| **ChatVigente** | `concierge_mvp.py` paste | S5 + webhook WA + intake context |
| **PersonaVigente** | `mvp0_lib` reglas | S2 + S5 + auto `protocol_draft` |
| **DiagnosticoVigente** | Foto manual | S3 bulk + Haut.AI (Fase 1) |
| **OptiVigente** | — | Fase 3 lounge |
| **RiskGuard** | `gate_path` RAG | Ya parcial; reforzar en S6 trajectories |

---

## 11. Estado y siguiente paso

```
[██░░░░] Agente software HV ~30%
  ✅ RAG + gates + intake schema + pipeline batch
  ⏳ S1+S2 (traces + state) — máximo ROI Fase 1
  ⏳ TRAJ-HV-001 (Caso #0 E2E)
```

**Próximo hito técnico P0:** `beta_state.json` + log de turnos WA ligado a `pipeline_row` (Sprint CMU 1+2 en miniatura).

**Próximo hito operativo:** cerrar Caso #0 manual — el primer `TRAJ-HV-006` humano validado.

---

*Referencia CMU: `~/Downloads/SPRINT-QUIRURGICO-AGENT-INTELLIGENCE.md`. No es consejo legal ni médico.*