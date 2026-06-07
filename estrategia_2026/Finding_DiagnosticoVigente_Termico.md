# Finding — DiagnosticoVigente: diagnóstico térmico + RGB + ML (white space real)

**Corrección/ampliación a la revisión quirúrgica · Junio 2026**

> En la revisión marqué DiagnosticoVigente como "mock/simulación" — cierto a nivel de **código hoy**. Pero subvaloré la **tesis estratégica**, que es sólida: un diagnóstico estético de bajo costo (cámara RGB + térmica FLIR + ML) que evita el CapEx de un VISIA/Canfield y ataca un hueco que **no existe comercialmente**. La investigación lo confirma.

## El hueco es REAL

**1. Los incumbentes caros son TODOS ópticos — ninguno térmico:**
- **Canfield VISIA** (~$20k nuevo; $5-15k usado): luz blanca + polarizada cruzada + UV. Sin térmico.
- **Observ 520x**: daylight/polarización/UV. Sin térmico.
- **Antera 3D** (~€10k): multiespectral + 3D (melanina/hemoglobina). Sin térmico.
- **Cutometer** (elasticidad por succión), **DermaScan** (ultrasonido). Ninguno térmico.

**2. El software de IA de piel es RGB puro — ninguno térmico:**
- **Haut.AI** (150+ parámetros de 1 foto RGB), **Perfect Corp/YouCam**, **Orbo.ai**, **Skinive** (CE Class I). Todos analizan **foto RGB** (arrugas, manchas, poros, rojeces). Cero térmico.

**3. No existe producto comercial térmico+RGB+ML para diagnóstico estético.** La fusión térmico+RGB existe en investigación, pero para **otras** tareas faciales (anti-spoofing, emoción, dolor, fiebre), no para estética. → **Hueco sin competidor directo identificado.**

**Qué aporta el térmico que el RGB NO puede ver:** inflamación (calor), **vascularidad/perfusión/microcirculación**, progreso de cicatrización, y alerta temprana de **compromiso vascular** (clave en rellenos/fillers). Es una modalidad ortogonal a toda la categoría de $1B+ de imagen de piel.

## La verdad incómoda (riesgos — para no construir sobre arena otra vez)

1. **El térmico para "estética/envejecimiento" está casi sin evidencia.** Lo que SÍ está probado del térmico es **inflamación y perfusión** (dermatología médica), no arrugas/manchas/edad. No hay estudio validado que "puntúe el envejecimiento" con térmico (que es justo el caso de uso de VISIA).
2. **Baggage regulatorio (FDA):** la termografía está autorizada solo como **adjunto**, no como diagnóstico standalone; la FDA ha mandado warning letters por marketear termografía como diagnóstico. → **Nunca posicionarlo como "diagnóstico médico"; sí como consulta/optimización/monitoreo.**
3. **El hardware barato puede no alcanzar:** FLIR ONE Pro (~$400) tiene precisión **±5 °C** — demasiado grueso para el umbral de **1 °C** de inflamación. Para algo clínicamente creíble se necesita un núcleo radiométrico tipo **Lepton 3.5** (160×120, ~$200) o **Boson** + **calibración** (emisividad, drift, aclimatación, ambiente). "Ultra-barato" y "creíble" están en tensión.

## Posicionamiento que SÍ sobrevive (la jugada correcta)

- **No** "mejor que VISIA para arrugas". **Sí**: capa **complementaria** que mide lo que el RGB no ve — **vascularidad, inflamación, perfusión** — como herramienta de **consulta + monitoreo de tratamiento + seguridad post-filler**, explícitamente **adjunta**, a precio disruptivo (costo de módulo FLIR vs. $10-20k del incumbente).
- **Combo ganador:** RGB (vía Haut.AI/Perfect Corp por API, lo maduro) para piel/arrugas/manchas + **térmico propio** (tu IP/hardware) para inflamación/vascularidad. Nadie tiene los dos.

## Conexión con el pivote longevidad (esto sube de valor)

El térmico mide **inflamación y perfusión** — y la **inflamación crónica ("inflammaging")** es un eje central del envejecimiento. Es decir: **tu cámara térmica vale MÁS en el marco de longevidad/optimización que en pura estética.** Ej.: trackear inflamación sistémica/local, recuperación, respuesta a protocolos. Ahí el claim "optimización/wellness" es natural y esquiva el problema regulatorio del "diagnóstico".

## Veredicto

DiagnosticoVigente **no es vaporware estratégico — es un white space real y defendible.** Lo que faltaba (y sigue faltando) es: (1) construir el modelo de verdad (no el mock), (2) un **núcleo térmico suficientemente bueno** (no el FLIR ONE más barato), (3) **validación** con datos reales, y (4) **lenguaje adjunto/wellness** (no diagnóstico). El hardware que ya compraste es el primer paso correcto — la pregunta clave es **cuál exactamente** (resolución/NETD), porque define si el claim de inflamación es viable.

---
*Fuentes: Canfield VISIA, Sylton Observ, Miravex Antera 3D, Haut.AI, Perfect Corp, J Eur Acad Dermatol Venereol 2024 (scoping review IRT), MDPI Diagnostics 2025 (botox térmico), FDA thermography warning, FLIR Lepton/Boson specs. No es consejo médico ni regulatorio.*

---

## ADDENDUM · Hardware comprado (MVP) y protocolo de captura

**Hardware actual del fundador:**
| Equipo | Specs | Rol en MVP |
|--------|-------|-----------|
| **Seek Thermal CompactPRO** | 320×240 IR, NETD ~70 mK (~0.07 °C) | **Térmico principal** — la mejor de las dos (más resolución; sensibilidad alcanza para ΔT ~1 °C) |
| **FLIR One Edge** | 160×120 IR, abs. ±3-5 °C | Respaldo / segundo ángulo |
| **Logitech Brio 4K (90 fps)** | RGB 4K | **Capa RGB** (arrugas/manchas/poros) — perfecta |

**Veredicto:** suficiente para MVP. **No cambiar nada todavía.** CapEx de diagnóstico ≈ cientos de USD vs ~$20k de un VISIA → el foso de costo es real.

**Regla de oro — medir DIFERENCIAS, no absolutos:**
- Reportar **ΔT relativo**: izquierda vs derecha (asimetría), zona vs zona, y **antes/después** de tratamiento. NO "tu piel está a 34.2 °C".
- Es donde estos sensores son confiables, es lo clínicamente significativo (inflamación/vascularidad), y es lenguaje "optimización/seguimiento" — no "diagnóstico" (esquiva FDA/COFEPRIS).

**Protocolo de captura (sin esto, el térmico da basura):**
1. **Aclimatación**: paciente 5-10 min en el cuarto, sin sol/ejercicio/maquillaje/cremas/sudor previos.
2. **Ambiente controlado**: temperatura estable (~21-23 °C), sin corrientes de aire ni fuentes de calor cerca; cámara encendida ≥5 min (evitar drift de auto-calentamiento).
3. **Geometría fija**: misma distancia y ángulo (marca/tripié); rostro frontal + perfiles.
4. **Captura pareada RGB + térmico** del mismo encuadre, mismo instante.
5. **Registro/alineación** RGB↔térmico sobre landmarks faciales (ojos/nariz) para superponer mapas.
6. **Salida**: mapa de ΔT + índice simple de asimetría/inflamación ("Índice de Vigencia"), comparable entre visitas.

**Dónde está el trabajo real (no la cámara):** (1) protocolo arriba, (2) alineación RGB↔térmico, (3) el modelo/heurística ΔT→señal. La cámara es lo barato.

**Upgrade futuro (solo si se necesita temperatura absoluta calibrada):** núcleo radiométrico Lepton 3.5 / Boson + calibración. Para el MVP adjunto/wellness **no es necesario**.
