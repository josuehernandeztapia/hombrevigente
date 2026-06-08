# Fases 0 → N — Hombre Vigente

**Junio 2026**

> Mapa canónico de fases de producto, oferta comercial (Av.1/Av.2, Peldaños), stack tech y agentes IA. Alinea `Plan_Maestro`, `MVP0_Playbook`, `Blueprint_Oferta_y_Pricing`, `CapaTech_Peldano1` y `Estrategia_Digital_First`.

**Documentos relacionados:** `SPRINT_01_MVP0_Concierge.md` · `Stack_Tech_Costos_y_BuyVsBuild.md` · `Agentes_Valor_de_Desarrollo.md` · `Arquitectura_PlugAndPlay_y_Matriz.md`

---

## Dos “Fase 0” (no mezclar)

| Término | Qué es |
|---------|--------|
| **Fase 0 personal** | Tu stack de péptidos/suplementos como **Caso #1** (credibilidad, contenido, primer dato). |
| **MVP-0 producto** | Concierge manual para **validar el negocio** con 5–10 betas (donde está el proyecto hoy). |

---

## Vista rápida

| Fase | Nombre | Horizonte | Qué validas | Canal | Rx / producto |
|------|--------|-----------|-------------|-------|----------------|
| **0** | Concierge manual | Semanas 1–4 | ¿Quieren protocolo + seguimiento? | WhatsApp + Tally | Solo educativo; sin venta |
| **1** | Digital semi-auto (Peldaño 1 · **Av.1**) | Mes 2–4 | ¿Pagan diagnóstico/membresía? | Web + WA API + RAG | Suplementos; optimización sin Rx |
| **2** | IA-nativo + **Av.2** | Mes 5–12 | ¿Retienen? ¿Pro convierte? | Portal + wearables + labs auto | Médico + magistral + Prescrypto |
| **3** | Híbrido lounge (Peldaño 3) | Mes 6–18 | ¿Ticket alto + wow físico? | Lounge QRO + digital | Estética legal + térmico presencial |
| **4** | Escala / moat | 18+ meses | ¿Data moat + marca replicable? | Multi-sede / partners | Clinic-in-a-Box, franquicia |

**Secuencia recomendada (digital-first):** 0 → 1 → 2 **antes** de capex fuerte de clínica. Lounge/estética en **Fase 3**, financiada por caja digital.

---

## Fase 0 — MVP-0 “Concierge manual”

**Estado HV (jun 2026):** Tally vivo · RAG + pipeline · **P1 Caso #0 entrega lista** (`MVP0_Caso0_P1_Entrega.md`) · médico en cola · betas tras Gate A.

| Dimensión | Contenido |
|-----------|-----------|
| **Objetivo** | Comportamiento real; reemplazar datos sintéticos |
| **Producto** | Protocolo educativo 8 semanas + screening + check-ins |
| **Stack** | [Tally](https://tally.so/r/5BVeRd) · WA personal · Google Sheets · `concierge_mvp.py` · `mvp0_pipeline.py` · `hv-rag-api` |
| **IA** | Tú + LLM; ChatVigente (paste manual); PersonaVigente = reglas (`mvp0_lib`) |
| **Datos** | Foto manual · labs PDF (`labs_intake_manual.py`) · wearable manual |
| **Compliance** | Disclaimer educativo · médico en banderas · **no vendes insumo** |
| **Cobro** | Beta gratis → medir intención de pago |
| **Meta go → Fase 1** | ≥3 betas con valor percibido · ≥2 protocolos entregados · médico aliado con SLA 48h |

**Kit operativo:** `MVP0_Playbook.md` · `MVP0_Cuestionario.md` · `MVP0_Plantilla_Protocolo.md` · `MVP0_WhatsApp_Scripts.md` · `MVP0_Beta_Tracker.xlsx`

---

## Fase 1 — MVP-1 “Semi-automático” (Peldaño 1 · Avenida 1)

| Dimensión | Contenido |
|-----------|-----------|
| **Objetivo** | Producto digital que cobra sin cuello de botella del fundador |
| **Oferta** | Escaneo gratis → **Diagnóstico Vigente** ($1,490–2,490 MXN) → Membresía Esencial/Plus + Stack oral |
| **Producto** | Informe de Optimización + recomendación justificada (RAG + SSOT) |
| **Stack** | Framer/Next · Healthie o portal · 360dialog · Stripe/Conekta · Terra · Haut.AI · BloodGPT o build labs |
| **IA** | ChatVigente + PersonaVigente v1 · `protocol_draft` auto · RGB (Haut.AI) · térmico captura MVP |
| **Av.1** | Suplementos curados — **sin péptidos Rx** |
| **Compliance** | Política de privacidad · datos cifrados · lenguaje COFEPRIS-safe |
| **Meta go → Fase 2** | Retención 3 meses · ARPU creíble · LTV:CAC 3–5:1 (orgánico) |
| **Burn software** | ~$900–1,500/mes (ver `Stack_Tech_Costos_y_BuyVsBuild.md`) |

---

## Fase 2 — MVP-2 “IA-nativo” + Avenida 2

| Dimensión | Contenido |
|-----------|-----------|
| **Objetivo** | Loop cerrado con datos + capa premium médico-magistral |
| **Oferta** | **Protocolo Vigente Pro** ($3,500–8,000+/mes MXN): teleconsulta + receta + magistral + seguimiento |
| **Producto** | Cruce multimodal · tendencias labs · ajuste trimestral · predicciones de progreso |
| **Stack** | Wearables live · BloodGPT escala · Prescrypto · O-Lab/Compounding · pgvector data moat |
| **IA** | Detección inconsistencias · OptiVigente v1 (agenda) · knowledge loop semi-automático |
| **Av.2** | Péptidos/hormonas **solo** con médico + magistral |
| **Meta go → Fase 3** | Conversión Av.1→Av.2 · adherencia · menos escalate humano en RAG |

---

## Fase 3 — Híbrido lounge (Peldaño 3 · estética)

| Dimensión | Contenido |
|-----------|-----------|
| **Objetivo** | Estética regenerativa paga cuentas; longevidad = foso |
| **Oferta** | HIFU, Botox, RF, etc. + **Add-on térmico** ($490–990/sesión) + upgrade a Pro |
| **Físico** | Lounge ligero Querétaro (por cita → espacio fijo) |
| **IA** | DiagnosticoVigente RGB+térmico · OptiVigente llena slots del equipo |
| **Economía** | Margen 70–86% en procedimientos · digital alimenta lounge |
| **Meta go → Fase 4** | Utilización equipo · NPS presencial · upsell digital→físico |

---

## Fase 4 — Escala (horizonte 2026–2030)

| Dimensión | Contenido |
|-----------|-----------|
| **Negocio** | Multi-sede · partnerships médicos · educación (ej. Péptidos 360) |
| **Tech** | Modelo propio con data moat · Clinic-in-a-Box / franquicia SaaS |
| **Radar** | Relojes epigenéticos · senolíticos (evidencia) · MSCs 2027+ |

---

## Los 7 pasos del producto × fase

| # | Etapa | F0 | F1 | F2 | F3 |
|---|-------|----|----|----|-----|
| 1 | Onboarding & upload | Tally | Web + APIs | Automático | Lounge |
| 2 | Análisis multimodal | Manual + LLM | Haut.AI + labs | + wearables | + térmico |
| 3 | Inconsistencias | Humano | Reglas | Automático | Integrado |
| 4 | Recomendación | Plantilla + RAG | Motor justificación | Auto + gates | + estética |
| 5 | Compra inteligente | No | Checkout | Bundles dinámicos | POS lounge |
| 6 | Seguimiento | WA manual | Bot check-ins | Predicciones | Híbrido |
| 7 | Loop mejora | `promote_e2e` manual | Semi-auto | Data moat | Escala |

---

## Embudo comercial (Av.1 / Av.2)

```
Lead → Onboard (Tally/Web)
         ↓
   Informe de Optimización (Peldaño 1)
         ↓
    ┌────┴────┐
    ▼         ▼
 Av.1        Av.2 (screening OK)
 Stack       Médico → magistral → Pro
 Membresía   (Fase 2)
 (Fase 1)
         ↓ (Fase 3)
   Lounge + térmico + estética
```

| Avenida | Qué vendes | Fase | Diferenciador vs gray market |
|---------|------------|------|------------------------------|
| **Av.1** | Claridad + suplementos + seguimiento | 1 | Informe con *tus* datos + evidencia |
| **Av.2** | Protocolo gestionado con Rx | 2 | Médico + magistral + datos continuos |

---

## Agentes IA por fase

| Agente | F0 | F1 | F2 | F3 |
|--------|----|----|----|-----|
| **ChatVigente** (RAG) | Paste manual WA | Webhook | Portal | + reservas |
| **PersonaVigente** | `mvp0_lib` reglas | Intake+labs+RAG | Personalización | + estética |
| **DiagnosticoVigente** | Foto manual | Haut.AI + térmico MVP | Loop completo | Presencial |
| **OptiVigente** | — | — | Reglas agenda | Utilización equipo |
| **RiskGuard** | Gates RAG | Pisos margen | Checkout | Pricing lounge |

Los “9 agentes” del demo investor eran mocks — ver `wiki/02_AGENTES_AI_CORE.md` y `Agentes_Valor_de_Desarrollo.md`.

---

## Stacks de producto (catálogo longitudinal)

| Stack | Foco | Fase típica de recomendación |
|-------|------|------------------------------|
| **Glow** | Piel, colágeno, antiinflamatorio | Av.1 |
| **Wolverine** | Reparación estructural/nerviosa | Av.1 screening / Av.2 |
| **Metabolic Longevity** | Grasa visceral, NAD+, epigenética | Av.1–2 |

---

## Estado actual y siguiente paso

```
[████████░░] Fase 0 ~80%
  ✅ Tally · RAG · pipeline · Caso #0 intake
  ⏳ Ejecutar P1 (WA #4 + Sheets) · foto baseline · check-in S1

[░░░░░░░░░░] Fase 1 — tras go/no-go sprint
```

**Criterio go Fase 1:** ≥3 betas reportan valor + intención de pago + médico operativo.

**Próximo hito operativo:** ejecutar `MVP0_Caso0_P1_Entrega.md` (15 min) → P1 ✅ → P3 tracker + foto baseline.

**Cómo avanzar sin flujo E2E:** `MVP0_Doctrina.md` + `MVP0_Como_Avanzar.md` (peldaños P0–P8).

---

*No es consejo médico, legal ni financiero. Precios ilustrativos en `Blueprint_Oferta_y_Pricing.md`.*