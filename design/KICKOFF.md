# Brief de desarrollo — Hombre Vigente (MVP)

> Prompt de arranque para el equipo dev. Sirve para Claude Code o como brief humano.

## Contexto
Construimos **Hombre Vigente**, un producto de *longevidad gestionada* digital-first para hombres en México: diagnóstico con datos → protocolo personalizado → conversión (Av.1 sin receta / Av.2 vía médica) → seguimiento recurrente. Paquete de diseño en [`handoff/`](handoff/):

- [`handoff/README.md`](handoff/README.md) — tokens, pantallas, interacciones, estados
- [`handoff/Inventario Hombre Vigente.md`](handoff/Inventario%20Hombre%20Vigente.md) — copy exacto por pantalla
- [`handoff/COMPLIANCE.md`](handoff/COMPLIANCE.md) — reglas no negociables (marca, Av.1/Av.2, lenguaje, LFPDPPP)
- Prototipos HTML/React en `handoff/*.html` + `handoff/*.jsx`
- Evidencia RAG (SSOT técnico): [`rag-bot/knowledge_base/longevity/00_MARCO_SSOT_EVIDENCIA_Y_COMPLIANCE.md`](../rag-bot/knowledge_base/longevity/00_MARCO_SSOT_EVIDENCIA_Y_COMPLIANCE.md)

**Los HTML son referencia de diseño, no producción.** Recréenlos en el stack real respetando pixel, copy y comportamiento.

**Operación actual (pre-producto):** [`estrategia_2026/MVP0_Doctrina.md`](../estrategia_2026/MVP0_Doctrina.md) — concierge manual mientras M0–M2 no existen.

## Stack objetivo
- **App móvil:** React Native (Expo) — el prototipo ya es React, migración directa.
- **Landing/web:** Next.js (la landing usa Tailwind, port sencillo).
- **Backend:** API (Node/Nest o el de su preferencia) + Postgres. Auth + almacenamiento de datos de salud **cifrado en reposo**.
- **Design system:** extraer tokens de `handoff/README.md` a theme (Montserrat + IBM Plex Mono, bronce **#C6A06A** sobre base noir).

## Orden de construcción (milestones)

### M0 · Fundaciones (semana 1–2)
- Theme/design system + componentes base (GlassCard, PrimaryButton, Chip, Eyebrow, stepper, estados error/vacío/loading).
- Navegación por flujos + shell onboarding (7 pasos) con persistencia de progreso.

### M1 · Diagnóstico (el corazón)
- Onboarding 7 pantallas: **foto**, **PDF labs**, **wearable** (OAuth Oura/Whoop), cuestionario.
- **Índice Vigente** (placeholder ilustrativo; modelo real en M4 — ver `COMPLIANCE.md` §0).
- Routing Av.1 / Av.2 por elegibilidad.

### M2 · Conversión + pagos
- Checkout Av.1: pasarela MX (Conekta/Stripe: Tarjeta, SPEI, OXXO, MSI/Kueski).
- Av.2: teleconsulta + intake clínico (sin Rx hasta M5).

### M3 · Recurrencia + canal
- Check-in semanal, sync wearable, dashboard.
- **WhatsApp Business API**: plantillas con merge field `{nombre}` (copy en inventario).

### M4 · Inteligencia (datos reales)
- CV foto (Haut.AI/Perfect Corp).
- Parsing labs (hs-CRP, glucosa, IGF-1, panel).
- Conectar el `rag-bot/` EXISTENTE (Postgres+pgvector, 31 monografías de longevity
  verificadas + tarjetas en knowledge_base/longevity/) como motor de evidencia citada.
  NO reconstruir el RAG — ya está QA'd.

### M5 · Compliance médico (gate Av.2)
- Responsable sanitario real, receta firmada, magistral con contrato, consentimiento informado.

## Reglas no negociables
Ver [`handoff/COMPLIANCE.md`](handoff/COMPLIANCE.md) (fuente de verdad). Resumen:
1. **Marca = Hombre Vigente™**; Índice Vigente sin ™ y scores ilustrativos hasta M4.
2. **Av.1 = solo suplementos sin receta** (`STACK_VIGENTE`). Rx/péptidos solo **Av.2** con médico.
3. Lenguaje **optimización/bienestar**; nunca diagnóstico/cura/tratar enfermedad.
4. Evidencia con **nivel + PMID**; biomarcadores sin "nivel de evidencia".
5. **El modelo sugiere; el médico aprueba/firma** prescripciones.
6. **Aviso de Privacidad (LFPDPPP)** antes de capturar datos de salud.

## Pendientes mundo real (paralelo, no código)
Aviso de Privacidad · médico + magistral con contrato · PMIDs vs SSOT · APIs (CV, wearables, pagos, WhatsApp).

## Definición de "listo" del MVP
Usuario: landing → diagnóstico → Índice → Av.1 → paga → loop WhatsApp, con compliance activo. Av.2 con médico real.

**Primer paso dev:** `handoff/README.md` + `handoff/COMPLIANCE.md` → design system (M0) → onboarding pixel-perfect (M1).