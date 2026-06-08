# Sprint 01 — MVP-0 Concierge Manual + RAG Loop

**Hombre Vigente · Junio 2026**
**Duración:** 14 días · **Canal:** WhatsApp personal/Business (sin API)
**Motor:** `hv-rag-api` + `concierge_mvp.py` (asistencia, no reemplazo del juicio humano)

---

## North Star (una frase)

> **5 conversaciones reales con intención de protocolo, 3 onboardings completos, y ≥1 gap promovido desde tráfico real** — demostrando que el loop humano + RAG aprende.

---

## Qué NO es este sprint

- No Twilio / Meta Cloud API (falta número dedicado).
- No cobro (beta gratis a cambio de feedback).
- No MVP-1 (web, bot, parser de labs).
- No escalar péptidos Rx sin médico aliado.

---

## Entregables del sprint

| # | Entregable | Dueño | DoD |
|---|------------|-------|-----|
| E1 | Médico aliado confirma revisión de protocolos | Juan | Nombre + SLA 48h por protocolo |
| E2 | Tally publicado (`MVP0_Cuestionario.md`) | Juan | Link funcional + prueba tú mismo |
| E3 | Tracker en Google Sheets (`MVP0_Beta_Tracker.xlsx`) | Juan | Hoja Pipeline + RAG Concierge activas |
| E4 | 5–10 invitaciones enviadas (script #1) | Juan | Registradas en Pipeline |
| E5 | Caso #0 (tú) con baseline documentado | Juan | Fila #0 en Pipeline + foto/labs si aplica |
| E6 | ≥20 consultas RAG logueadas en prod | RAG | `decision_log` con source whatsapp/concierge |
| E7 | ≥1 knowledge promotion desde gap real | RAG | FAQ + golden P-xxx + re-embed verificado |
| E8 | Retro sprint + go/no-go MVP-1 | Juan | Doc §10 completado |

---

## Calendario (14 días)

### Día 0–2 · Setup (bloqueantes)

- [ ] Confirmar médico aliado (si no hay → **no reclutar betas**, solo Caso #0).
- [ ] Tally + link guardado en respuestas rápidas WhatsApp.
- [ ] Subir tracker a Google Sheets; compartir solo con médico (view/edit según necesidad).
- [ ] Probar una vez: `python scripts/concierge_mvp.py "¿cuánto cuesta HIFU?"`.
- [ ] Etiquetas WhatsApp Business: `lead`, `onboarding`, `protocolo-entregado`, `semana-1`…`semana-4`, `escalate-humano`.
- [ ] Carpeta privada para fotos/labs (Drive cifrado o local; nunca en repo git).
- [x] **Caso #0** fila #0 en Pipeline + [`MVP0_Caso0_Baseline.md`](MVP0_Caso0_Baseline.md).

### Día 3–7 · Reclutamiento + primeras entregas

- [ ] Enviar script #1 a red (meta: 5–10 “sí”).
- [ ] Cada “sí” → fila en **Pipeline** + etiqueta `lead`.
- [ ] Onboarding enviado → `onboarding`; recordatorio día 2 (script #2).
- [ ] Screening en cada Tally completado (§4 playbook).
- [ ] Protocolo armado (`MVP0_Plantilla_Protocolo.md`) + revisión médico → entrega script #4.
- [ ] Preguntas puntuales del beta → `concierge_mvp.py` → pegar respuesta (editar si hace falta).

### Día 8–14 · Seguimiento + knowledge loop

- [ ] Check-in semana 1 (script #5) para quien ya recibió protocolo.
- [ ] Viernes: revisar `/admin/knowledge/gaps` (últimos 7 días).
- [ ] Promover 1–2 gaps legítimos con `promote_e2e.py` (solo en scope HV).
- [ ] `expand_golden_from_log.py` si hay tráfico repetido nuevo.
- [ ] Día 14: retro + llenar **Feedback** para quien llegue a semana 4 (o marcar pendiente).

---

## Métricas — negocio (hoja Pipeline / Feedback)

Copiado del playbook; umbrales para **fin de sprint**:

| Métrica | Cómo medir | Meta sprint | Señal fuerte |
|---------|------------|-------------|--------------|
| Invitaciones enviadas | Conteo manual | ≥10 | — |
| Confirmados (“sí”) | Pipeline | ≥5 | — |
| Onboarding completado | Tally + Pipeline | ≥3 | >60% de confirmados |
| Subió foto o labs | Pipeline cols | ≥2 | Data moat real |
| Protocolos entregados | Pipeline + médico OK | ≥2 | — |
| Adherencia semana 1 | Check-ins | ≥50% de entregados | — |
| “Aha moment” subjetivo | Check-in comentario | ≥1 | Energía/sueño/piel |
| Intención de pago | Feedback col | ≥1 “Sí” | Aunque beta sea gratis |
| Referido espontáneo | Feedback col | ≥1 | **Métrica reina** |

---

## Métricas — RAG / concierge (hoja **RAG Concierge**)

Registrar **cada** consulta que pases por el motor (betas, leads, curiosos, tú mismo).

| Métrica | Cómo medir | Meta sprint | Acción si falla |
|---------|------------|-------------|-----------------|
| Consultas totales | Filas hoja RAG Concierge | ≥20 | Más touchpoints en check-ins |
| % `auto` + `caveat` | gate_path en log | ≥70% | Promover gaps frecuentes |
| % `escalate` | gate_path | <25% | KB gap → promote_e2e |
| % `blocked` (gates) | gate_path | Esperado en Rx/onco/psiq | No promover; mensaje médico |
| Tiempo respuesta (TTR) | Hora pregunta → envío WA | <15 min horario activo | Respuestas rápidas pre-armadas |
| Gaps únicos detectados | `/admin/knowledge/gaps` | Registrar top 5 | Priorizar por frecuencia |
| Promotions aplicadas | FAQ_PROMOTED | ≥1 | Cerrar loop |
| Golden T nuevos | `expand_golden_from_log` | ≥0 (opcional) | Tráfico repetido exitoso |

**Campos por fila (tracker):** Fecha · Contacto · Pregunta · gate_path · confidence · top_service · decision_id · TTR (min) · ¿Editaste respuesta? · Notas

---

## Ritual diario (10 min)

1. Revisar WhatsApp pendientes.
2. Consultas nuevas → `concierge_mvp.py "…"` → copiar → **editar tono** → enviar.
3. Anotar fila en **RAG Concierge** (decision_id del script).
4. Si `escalate` o duda clínica → etiqueta `escalate-humano` + no improvisar Rx.

```bash
cd rag-bot
python scripts/concierge_mvp.py "pregunta del cliente"
# escalate / gaps (semanal):
curl -H "x-admin-pin: $HV_ADMIN_PIN" \
  'https://hv-rag-api.fly.dev/admin/knowledge/gaps?days=7'
```

---

## Ritual viernes (30 min) — “Knowledge Loop”

1. Exportar o revisar gaps semana (`knowledge-gaps` report o API).
2. Clasificar: **promover** (HV scope) · **ignorar** (off-topic) · **gate** (médico, no KB).
3. Si promover: `python scripts/promote_e2e.py --from-gap --gap-match "…" --answer "…" --kb-route servicios|longevity --skip-verify` luego re-embed si hace falta.
4. Contar métricas negocio + RAG; actualizar tabla §9 abajo.

---

## Guardarraíles (recordatorio)

- Médico revisa **cada protocolo** antes de enviar.
- RAG = educación + servicios; **no** sustituye screening ni consejo médico.
- Gates `blocked` → script #3 variante screening, no pelear con el modelo.
- Disclaimer en cada entrega de protocolo (script #4).

---

## Tabla de seguimiento sprint (llenar día 14)

| Métrica | Objetivo | Real | ✓/✗ |
|---------|----------|------|-----|
| Invitaciones | ≥10 | | |
| Confirmados | ≥5 | | |
| Onboarding OK | ≥3 | | |
| Protocolos entregados | ≥2 | | |
| Consultas RAG | ≥20 | | |
| % auto+caveat | ≥70% | | |
| Promotions | ≥1 | | |
| Intención pago | ≥1 | | |
| Referido espontáneo | ≥1 | | |

---

## Go / No-Go → Sprint 02

**GO** (siguiente sprint) si se cumplen **≥3** de:

- ≥3 onboardings completos
- ≥2 protocolos entregados con check-in semana 1
- ≥1 intención de pago o referido espontáneo
- RAG loop cerrado (≥1 promotion desde tráfico real)
- Médico aliado operativo sin fricción

**Sprint 02 candidato:** semanas 3–4 del ciclo beta (check-ins 2–4) + evaluar número WhatsApp Business dedicado + primer borrador webhook solo si GO fuerte.

**NO-GO:** iterar oferta/segmento/mensaje antes de código o número nuevo.

---

## Archivos relacionados

| Archivo | Uso |
|---------|-----|
| `MVP0_Playbook.md` | Flujo end-to-end betas |
| `MVP0_WhatsApp_Scripts.md` | Respuestas rápidas |
| `MVP0_Beta_Tracker.xlsx` | Pipeline + RAG Concierge + Check-ins |
| `MVP0_Cuestionario.md` | Tally |
| `rag-bot/scripts/concierge_mvp.py` | Asistente respuestas |
| `rag-bot/scripts/promote_e2e.py` | Cerrar gaps en KB |

---

*Sprint 01 · Validación manual. El RAG acelera respuestas; el juicio clínico y comercial sigue siendo humano.*