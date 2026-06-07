# Arquitectura Plug-and-Play (México/LatAm) + Buy-vs-Build + Matriz de Arquetipos

**Hombre Vigente · Junio 2026**

> **Tesis (cimientos de roca, no de arena):** MEDVi prueba que puedes estar *operativo en semanas* ensamblando piezas rentadas. Pero su rascacielos está sobre infra rentada + marketing arbitraje = sin foso. La jugada correcta: **rentar las capas commodity para arrancar barato, y construir SOLO el foso** (motor de protocolo + datos + híbrido + compliance). Este documento mapea qué rentar en México y qué construir.

---

## 1. La pila plug-and-play, capa por capa (México)

| # | Capa | Mejor opción MX/LatAm | Alternativas | Madurez en MX | Veredicto HV |
|---|------|----------------------|--------------|---------------|--------------|
| 1 | **Front-end / landing** | Framer o Webflow (no-code) | Next.js si quieres control | ✅ Trivial | RENTAR |
| 2 | **Capa clínica** ("OpenLoop MX": médico + credencialización) | **No existe equivalente maduro** → ensamblar: médico responsable contratado + plataforma | mediQuo (white-label, España, precio opaco), Doc24 (AR) | 🔴 **GAP** | **ENSAMBLAR (foso)** |
| 3 | **E-receta (receta electrónica)** | **Prescrypto** (15,000+ farmacias, firma+QR, COFEPRIS, **API abierta**) | Nimbo (e-receta en su EHR), sistema oficial COFEPRIS Fracción I | ✅ Maduro | RENTAR |
| 4 | **Farmacia magistral / producto** | **O-Lab** (Monterrey), **Compounding Mexico** (1ª autorizada a formular hormonas), FADERMEX (CDMX) | Farmacias Magistrales, Farmacosmetic | 🟡 Funciona bajo receta; **research peptides = zona gris** | RENTAR (con cuidado legal) |
| 5 | **Labs** | **Salud Digna / Chopo / Olab** (toma a domicilio + convenio B2B) | Corregidora (regional QRO) | 🟡 Consumer sí; **API NO existe** | RENTAR vía convenio + parsear PDF |
| 6 | **Parseo/lectura de labs (PDF→datos+IA)** | **BloodGPT** (PDF/HL7→estructurado+interpretación) | Health Gorilla (interop FHIR + ordenar labs), build propio | 🟢 (global) | RENTAR (ahorra 2-4 meses de ing.) |
| 7 | **Wearables (Oura/Whoop/Apple→1 API)** | **Terra** (500+ devices) o **Rook** (fuerte en LatAm) | Vital/Junction (wearables + labs), Spike | 🟢 (global, vía API) | RENTAR |
| 8 | **Skin/foto AI (estética)** | **Haut.AI** (API-first, 150+ biomarcadores) o **Perfect Corp** (líder, 15 condiciones) | Revieve, Orbo.ai | 🟢 (global, vía API) | RENTAR |
| 9 | **Pagos + suscripción** | **Stripe Billing** o **Conekta** (recurrente, cards/SPEI) | Mercado Pago | ✅ Maduro | RENTAR |
| 10 | **BNPL / meses (ticket alto)** | **Kueski Pay** (~6.5%+IVA) / **Aplazo** | Mercado Crédito | ✅ Maduro | RENTAR |
| 11 | **Pago en efectivo** | **OXXO Pay** | — | ✅ pero **NO recurrente** (solo one-time) | RENTAR (solo top-ups) |
| 12 | **WhatsApp (entrega/seguimiento)** | **Yalo** (líder LatAm conversational AI) o **360dialog** (barato) / Meta Cloud API | Gupshup, Twilio, Zenvia | ✅ Maduro | RENTAR |
| 13 | **Clinic OS / EHR (backbone)** | **Healthie** (API-first, programable) o **Cerbo** (cash-pay, lab-heavy) | OptiMantra, Tellescope (CRM/automation) | 🟢 (global) | RENTAR |
| 14 | **Cerebro AI (motor de protocolo)** | **CONSTRUIR** sobre Anthropic/OpenAI + pgvector | Hippocratic AI (agentes de seguimiento, opcional) | — | **CONSTRUIR (foso #1)** |

**Lectura:** de 14 capas, **~10 se rentan hoy** (commodity). Solo 2-3 son tu trabajo real: la **capa clínica** (médico + credencialización, que no existe como servicio en MX), el **motor de protocolo/IA**, y el **híbrido físico (lounge)**. Ahí vive el foso.

---

## 2. Buy-vs-Build del "cerebro"

El "cerebro de longevidad" se descompone en piezas comprables + un núcleo que debes construir.

**CONSTRUIR (tu IP / moat):** el **motor de recomendación de protocolo + lógica de seguimiento** sobre stack LLM genérico (Anthropic/OpenAI + LangChain + pgvector). Es barato de iniciar, lo posees, y es la diferenciación. **No lo tercerices.**

**COMPRAR por componente (recomendado sobre comprar un "cerebro" entero):**
- Backbone/EHR: **Healthie** (API-first) o **Cerbo** (cash-pay).
- CRM/automatización: **Tellescope**. Comunicación: **Spruce**.
- Wearables: **Terra** (o **Rook** por LatAm).
- Skin AI: **Haut.AI** / **Perfect Corp**.
- Labs: parseo **BloodGPT** + interop/ordenar **Health Gorilla** + logística **Vital/Junction**.
- Reloj de edad biológica (opcional, feature premium): **Deep Longevity** (API).
- Agentes de seguimiento paciente (opcional): **Hippocratic AI**.

**COMPRAR el "cerebro" completo (solo si quieres saltarte construir):**
- **LongevityEHR** (longevityehr.com) — plataforma de longevidad white-label literal, lanza en 2-3 semanas. **Evaluar primero.**
- **Longevity-AI** (tu link) — grado HMO/enterprise (Maccabi, Clalit, entrenada en 1.6M registros). Potente pero venta enterprise, caro, probablemente *overkill* para arrancar. Pedir demo y precio.

> **Veredicto:** compra la plomería, construye el cerebro. Si quieres validar ultrarrápido sin construir, **LongevityEHR** es el atajo a evaluar; pero a mediano plazo el motor propio es tu activo.

---

## 3. Los 4 gaps de México = tu oportunidad de foso

Donde no hay plug-and-play, hay defensibilidad para quien lo arme bien:

1. **"OpenLoop mexicano" (red de médicos + credencialización + responsabilidad como servicio API) — NO EXISTE.** Tienes que ensamblarlo (médico responsable + Nimbo/Prescrypto + shell white-label). Es el mayor riesgo de build… y la barrera de entrada que te protege.
2. **API de labs / consumer-initiated testing — NO EXISTE.** Integración = convenio B2B + toma a domicilio (Olab/Salud Digna) + PDF parseado (BloodGPT). Quien resuelva el flujo de datos de labs en MX tiene ventaja.
3. **Canal legal para péptidos de longevidad (BPC-157/TB-500) — GAP REGULATORIO.** Solo limpio: fármacos aprobados (semaglutida) + magistral bajo receta (sermorelin, secretagogos GH). Todo lo demás es gris. **Mina legal — manéjala con el médico responsable.**
4. **Credencialización-as-a-service — NO EXISTE.** Validar cédula/título es manual. Oportunidad de proceso.

---

## 4. Matriz de arquetipos y competidores

Qué posee cada uno, su foso, su riesgo, y la lección para Hombre Vigente.

| Player | Modelo | Canal | ¿Qué posee? | Foso | Riesgo regulatorio | Lección para HV |
|--------|--------|-------|-------------|------|--------------------|-----------------|
| **MEDVi** | D2C multi-vertical (GLP-1, péptidos, men's) | 100% digital | Nada (renta clínica+farmacia) | ❌ Bajo (todo rentado) | 🔴 Alto (carta FDA, ads IA) | Copia el ensamblaje y el bundle; NO el motor de crecimiento |
| **Longevity-AI** | B2B SaaS para clínicas/HMOs | B2B | Software + datos (1.6M) | ✅ Datos/IP | 🟢 Bajo | Opción buy-vs-build de tu cerebro |
| **Function Health** | Membresía labs D2C | Digital | **Diagnóstico/labs + datos** | ✅ Alto | 🟡 | Poseer el diagnóstico = foso |
| **Hims & Hers** | D2C suscripción | Digital + retail | **Fabricación + marca** | ✅ Alto | 🟡 (compounding GLP-1) | Integrar para margen; marca fuerte |
| **Ro** | D2C cash-pay | Digital | Marca + partnerships | 🟡 Medio | 🟡 | Asociarse para suministro legítimo |
| **Hone / Marek / Defy** | TRT/hormonas | Digital / híbrido (Defy físico) | Protocolo + (Defy: clínica) | 🟡 | 🟡 | Pricing de membresía hormonal |
| **Fountain Life / Human Longevity** | Clínica longevity premium | Físico (PoS) | **Experiencia + diagnóstico profundo** | ✅ Alto | 🟢 | Ancla premium de alto ticket |
| **Next Health** | Lounge longevity (franquicia) | Físico | Experiencia + marca | 🟡 (capex) | 🟢 | Modelo de lounge replicable |
| **Prenuvo / Neko** | Imagen preventiva | Físico + tech | **Hardware + experiencia + datos** | ✅ Alto | 🟡 | Periférico como gancho premium |
| **Restore Hyper Wellness** | Lounge wellness (franquicia) | Físico | Marca | ❌ (saturado, cierres) | 🟢 | Cuidado con capex/sobreexpansión |
| **Superpower / Lifeforce** | Membresía longevity D2C | Digital | Marca + UX | 🟡 | 🟡 | Benchmark de UX/pricing ($199–$1,900/año) |
| **Cuerpoymente / Exoma / BrutalRX** | E-commerce péptidos (MX) | Digital gris | Catálogo | ❌ (gris) | 🔴 | El hueco que dejan: confianza + servicio |
| **HOMBRE VIGENTE** | **Híbrido (lounge + e-commerce IA)** | **Mixto** | **Datos + Caso #1 + experiencia + compliance** | **✅ a construir** | 🟡 (gestionable) | — |

**Patrón claro:** los de foso alto **poseen** algo difícil de copiar (diagnóstico, hardware, fabricación, datos, experiencia física). Los de foso bajo (MEDVi, e-commerce gris) **rentan todo** y compiten por precio/ads. Hombre Vigente debe pararse del lado del foso.

---

## 5. Recomendación: el stack de arranque + el foso a construir

**Fase MVP (semanas, casi sin código, plug-and-play):**
Framer + Tally (onboarding) + WhatsApp (Meta Cloud API / 360dialog) + Stripe/Conekta + médico responsable contratado + farmacia magistral (O-Lab/Compounding Mexico) + Prescrypto (e-receta). Cerebro = tú + LLM (manual). *Esto es el MVP-0 que ya tienes, ahora con proveedores nombrados.*

**Fase MVP-1 (meses):**
Suma backbone **Healthie** (API) + **Terra/Rook** (wearables) + **Haut.AI** (skin AI) + **BloodGPT** (parseo labs). Empieza a construir el **motor de protocolo** sobre LLM + pgvector.

**El foso (lo que NO se renta):**
1. **Motor de protocolo/IA propio** (tu IP).
2. **Capa clínica ensamblada** (médico responsable + credencialización + compliance) — barrera que MEDVi-MX no tiene.
3. **Lounge físico** (confianza + ticket alto + experiencia).
4. **Data moat** (cada usuario mejora el motor).
5. **Compliance como marca** (lenguaje correcto, magistral con receta, datos seguros).

> En una frase: **renta los ladrillos, construye los cimientos.** El stack plug-and-play te da velocidad; el foso (datos + clínica + híbrido + compliance) te da una empresa que no se cae.

---

*Investigación multi-fuente, junio 2026. Precios B2B mayormente no públicos (requieren demo/ventas). No es consejo legal ni médico; validar compounding de péptidos y marco COFEPRIS con asesoría especializada.*
