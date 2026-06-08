# Handoff: Hombre Vigente™ — App de longevidad gestionada (web + móvil)

## Overview
Hombre Vigente es un producto de "longevidad gestionada" digital-first para hombres en México: diagnóstico con datos → protocolo personalizado → conversión (Av.1 sin receta / Av.2 vía médica) → seguimiento recurrente. Este paquete contiene el **journey completo** como prototipos de diseño de alta fidelidad: landing de captación + 6 flujos de app móvil + un índice navegable (Mapa).

## About the Design Files
Los archivos `.html` de este bundle son **referencias de diseño creadas en HTML** (prototipos que muestran el look & feel y el comportamiento esperado), **no código de producción para copiar tal cual**. La tarea es **recrear estos diseños en el entorno del codebase destino** usando sus patrones y librerías establecidos:
- **Landing** (`Landing Vigente.html`) → web (Next.js/Astro/etc.) — usa Tailwind, fácil de portar.
- **Flujos de app** (onboarding, conversión, teleconsulta, seguimiento, confianza, canal) → app móvil (React Native / Flutter / Swift) o web responsive. Hoy están en **React** (con Babel en navegador, solo para prototipar) y un sistema de tema propio.

Si no existe codebase aún, elegir el framework más apropiado (sugerencia: **Next.js** para la web + **React Native/Expo** para la app, dado que el prototipo ya es React) e implementar ahí.

## Fidelity
**Alta fidelidad (hifi).** Colores, tipografía, espaciado, copy e interacciones son finales. Recrear pixel-perfect con las librerías del codebase. El copy en español es **definitivo y compliant** (revisado) — no parafrasear sin revisión legal.

**Errata jun-2026 aplicada** en este bundle (evidencia plana, PMIDs, Av.2 ejemplo, ajustes Rx). Historial de la revisión: [`estrategia_2026/Revision_Inventario_Producto.md`](../../estrategia_2026/Revision_Inventario_Producto.md).

**Demo local:** abrir `Mapa Vigente.html` en el navegador (punto de entrada a todos los flujos).

---

## Sistema de diseño (Design Tokens)

### Colores
| Token | Hex | Uso |
|---|---|---|
| `bg` | `#08080A` | Fondo principal (negro) |
| `bg2` | `#0D0D10` | Fondo de hojas/sheets |
| `surface` | `rgba(255,255,255,0.035)` | Tarjetas (glass) |
| `surface2` | `rgba(255,255,255,0.06)` | Tarjetas elevadas / iconos |
| `solid` | `#141417` | Panel sólido |
| `line` | `rgba(255,255,255,0.09)` | Bordes sutiles |
| `lineStrong` | `rgba(255,255,255,0.18)` | Bordes marcados |
| `hi` (ink) | `#F3F1EC` | Texto principal |
| `mid` | `#9A9AA0` | Texto secundario |
| `low` | `#5C5C62` | Texto terciario / mono labels |
| `danger` | `#E0795F` | Errores |
| **`accent` (bronze)** | **`#C6A06A`** | **Acento de marca** — CTA, estados activos, score, ✦, candado |
| `soft` | `rgba(198,160,106,0.13)` | Fondo de acento (chips activos, glow) |
| `ring` | `rgba(198,160,106,0.32)` | Borde de acento |
| `on` | `#08080A` | Texto sobre botón bronce (oscuro) |

**Regla de marca:** UI mayormente **monocromática (noir)**; el bronce vive **solo** en CTA primario, estado activo/seleccionado, el score del Índice, el punto del eyebrow y el ✦/candado de ruta. No usar bronce en chips secundarios, valores de dato ni textos.

### Acentos alternativos (variantes de Tweaks — el oficial es Bronce)
- `noir`: accent `#EDEBE6` · `vital`: accent `#5FE0A2`. (Solo exploración; **producción = bronce**.)

### Tipografía
- **Display/UI:** `Montserrat` — pesos 900 (títulos), 800 (botones/headers), 700 (labels), 600/400 (texto).
- **Mono/labels/datos:** `IBM Plex Mono` — pesos 400/500/600.
- Títulos de pantalla: 28–30px / weight 900 / line-height 1.05 / letter-spacing −0.02em / `text-wrap: balance`.
- Eyebrow (kicker): IBM Plex Mono 10.5px / letter-spacing 0.22em / uppercase / color `mid`, con punto bronce 5px.
- Body: 13.5–14.5px / line-height 1.5–1.6.
- Mínimo legible: ~10px solo en mono-labels.

### Espaciado / radios / sombras
- Padding de pantalla: `14px 20px 26px`.
- Radio tarjetas: 18px · botones: 999px (pill) · chips: 7px · iconos-cuadro: 10–12px.
- Gap entre tarjetas: 10–12px.
- Glow ambiental: `radial-gradient(circle, soft 0%, transparent 68%)` arriba-centro.
- Grano de película: SVG fractalNoise, opacity 0.5, mix-blend overlay (decorativo, togglable).
- Sombra de botón primario: `0 8px 30px -10px accent`.

### Iconografía
Line icons SVG simples (stroke 1.6, 24×24 viewBox), definidos en `hv-data.jsx` función `Icon`: camera, lab, watch, doc, eye, chart, spark, check, alert, arrow, chat, lock, refresh, up, down, plus, dot. Reusar como set de iconos o mapear a la librería del codebase (Lucide/Phosphor equivalentes).

### Animaciones
- Entrada de elementos `hvRise`: opacity 0→1 + translateY 12px→0, .55s cubic-bezier(.16,.84,.44,1), stagger 0.05s. **Importante:** el estado final visible debe ser la base (no depender de la animación para mostrar contenido) — gatear en `prefers-reduced-motion`.
- Cambio de pantalla `hvScreen`: .4s fade+rise.
- Scan (análisis): barra que recorre verticalmente. Spinner: rotación .7s.
- Hoja/sheet: slide-up .32s.

---

## Pantallas / Vistas

> El **copy exacto** de cada pantalla está en `Inventario Hombre Vigente.md` (incluido). Aquí va la estructura; ahí el texto literal.

### Patrón base de pantalla (app móvil, 390×844)
- Marco de teléfono (status bar 9:41, dynamic island, home indicator) — en producción es la pantalla nativa real, sin marco.
- Top: barra de progreso (stepper) con N segmentos; segmento activo bronce con glow. Botón back izquierda. Contador `0X/0N` derecha (abre overview de pasos en el onboarding).
- Cuerpo scrolleable: Eyebrow → Título → Sub → contenido (tarjetas) → CTA primario (pill bronce) → footer mono (disclaimer).
- Footer legal recurrente: *"Optimización y bienestar. No sustituye atención médica."*

### 1. Landing (`Landing Vigente.html`) — web
Hero "No te vendemos un vial. Te damos un plan con médico.", tabla comparativa (mercado gris vs. clínica US vs. Vigente), loop de 6 pasos, programas con routing Av.1/Av.2, CTA "Hacer mi Escaneo gratis" → onboarding. Usa Tailwind; acento bronce vía CSS vars `--bronze:#C6A06A`.

### 2. Onboarding (`Onboarding Vigente.html`) — 7 pantallas
Bienvenida → Consentimiento (3 checkboxes, CTA gated) → Tu historial (3 fuentes: foto/labs/wearable, mín. 2) → Cuestionario (objetivos multi + hábitos en escala) → Análisis (líneas rotativas, auto-avanza) → **Índice Vigente** (score 68/100 **ilustrativo**, 4 señales expandibles "ver por qué" — **sin tag de evidencia en biomarcadores**) → Tu siguiente paso (routing Ruta A sólido / Ruta B con candado). Variantes de Historial: Guiado/Tablero/Chat.

### 3. Conversión Av.1 (`Conversion Vigente.html`) — 4 pantallas
Resultado del Escaneo (score 64 **ilustrativo**) → Elegir programa (4 tiers) → Checkout (Diagnóstico $1,490 + Stack $899/mes; pagos Tarjeta/SPEI/OXXO/Kueski-MSI) → Confirmación. Deep-link: entra a "programa" vía `#programa`.

### 4. Teleconsulta Av.2 (`Teleconsulta Vigente.html`) — 4 pantallas
Elegibilidad (3 razones + ficha médico **etiquetado "ejemplo"**) → Agendar (slots, $890) → Receta + Magistral ("Protocolo magistral de reparación", péptidos, COA por lote, gate de consentimiento) → Confirmación. **Compliance:** médico/cédula son placeholder; antes de producción, responsable sanitario real.

### 5. Seguimiento (`Seguimiento Vigente.html`) — 4 pantallas
Dashboard (Semana 4, resultados −28% inflamación, térmico ΔT adjunto) → Check-in semanal (foto/wearable/síntomas) → Ajuste & Membresía ("el modelo sugiere; tu médico aprueba", tiers Esencial $899 / Plus $2,499) → Al día.

### 6. Confianza (`Confianza Vigente.html`) — 3 pantallas
Hub "Por qué creerte" (4 pilares) → Caso #1 (métricas del fundador, ilustrativas) → **Evidencia citada** (niveles en lenguaje plano **Fuerte/Moderada/Emergente** + **PMIDs**: Omega-3 28900017·30415628, Creatina 28615996, NMN 33888596, Espermidina 19801973, GHK-Cu 29986520, BPC-157 21548867).

### 7. Canal (`Canal Vigente.html`) — WhatsApp + Estados
**E ·** 4 guiones de WhatsApp (entrega de lectura · check-in · re-test · re-enganche) con burbujas in/out, tarjetas, quick-replies, typing. El verde es chrome de WhatsApp; marca = bronce.
**F ·** 6 estados de borde (error PDF, wearable, pago fallido, vacío, en proceso, re-test). Errores en `danger` rojo, nudges en bronce.

---

## Interactions & Behavior
- **Navegación:** stepper lineal con back; overview-sheet para saltar (onboarding). Deep-links entre flujos por nombre de archivo (`Conversion Vigente.html#programa`, etc.).
- **Selección:** tarjetas toggle (borde→ring bronce, fondo→soft). Radios/checkbox con check bronce.
- **CTA gating:** consentimiento (3/3), historial (≥2 fuentes), receta (consentimiento) — botón disabled con copy dinámico hasta cumplir.
- **Análisis:** auto-avanza tras ~4s con barra de progreso + líneas rotativas.
- **Expandibles:** señales del Índice ("ver por qué ↓ / ocultar ↑").
- **Persistencia:** paso actual del onboarding en `localStorage` (`hv2_step`); reel en `hv_reel`.
- **Estados:** loading (spinner/scan), error (rojo + 2 CTAs), vacío (nudge), éxito (check bronce + próximos pasos).

## State Management
- `step/idx` (entero) por flujo · `uploads{}` (fuentes marcadas) · `consent[]` · `goals[] / habits{}` · `program/tier` · `rail/msi` (pago) · `slot/consent` (Av.2) · `route` (A/B) · `checks{}` (seguimiento) · `mem` (membresía).
- Datos hoy **ilustrativos** (score 68/64, señales, stacks). En producción conectar: Computer Vision (foto), parsing de labs, API wearables (Oura/Whoop), RAG/SSOT para evidencia+PMIDs, pagos (Conekta/Stripe MX), WhatsApp Business API, agenda de teleconsulta + farmacia magistral.

## Assets
- **Fuentes:** Google Fonts — Montserrat + IBM Plex Mono.
- **Iconos:** SVG inline propios (ver `hv-data.jsx`).
- **Imágenes:** placeholders rayados con label (fotos de rostro/cuerpo, mapas térmicos) — reemplazar por capturas/uploads reales del usuario.
- **Sin assets de marca de terceros.** Acento bronce + Montserrat es la identidad.

## Files (en este bundle)
- `Mapa Vigente.html` — índice navegable de todos los flujos (punto de partida del demo).
- `Landing Vigente.html` — captación (web, Tailwind).
- `Onboarding Vigente.html` · `Conversion Vigente.html` · `Teleconsulta Vigente.html` · `Seguimiento Vigente.html` · `Confianza Vigente.html` · `Canal Vigente.html` — flujos de app (React).
- **Soporte (lógica/diseño reutilizable):** `hv-data.jsx` (tokens, contenido/copy, iconos, UI compartida: GlassCard, PrimaryButton, GhostButton, Chip, Eyebrow, Placeholder, Icon), `hv2-screens.jsx`…`hv7-canal.jsx` (pantallas), `frames/ios-frame.jsx` (marco), `tweaks-panel.jsx` (variantes).
- `Inventario Hombre Vigente.md` — **copy exacto** de cada pantalla + sistema de marca + pendientes.
- `COMPLIANCE.md` — **reglas no negociables** (marca, Av.1/Av.2, lenguaje, evidencia, LFPDPPP).

## Pendientes antes de producción (no de diseño)
1. **Aviso de Privacidad (LFPDPPP)** real — el consentimiento lo enlaza.
2. **Responsable sanitario real** (médico, cédula, contrato) — hoy "ejemplo".
3. **Validar PMIDs** contra el SSOT/RAG; conectar el motor de evidencia.
4. Integraciones reales: CV, labs, wearables, pagos MX, WhatsApp API, teleconsulta + magistral.
