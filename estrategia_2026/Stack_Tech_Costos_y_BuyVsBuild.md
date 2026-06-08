# Stack Tech — Costos, Buy-vs-Build y Fases

**Hombre Vigente · Junio 2026**

> Análisis de proveedores del stack plug-and-play: precios públicos (o estimables), si un LLM genérico puede sustituirlos, en qué fase entran, y cómo se comparan **LongevityEHR** vs **Longevity-AI** vs el build propio (`rag-bot`).

**Documentos relacionados:** `Arquitectura_PlugAndPlay_y_Matriz.md` · `MVP0_Playbook.md` · `rag-bot/scripts/labs_intake_manual.py`

---

## 1. Respuesta corta: ¿un LLM no basta?

| Herramienta | ¿LLM genérico puede sustituirlo? | Veredicto HV |
|-------------|----------------------------------|--------------|
| **BloodGPT** | Parcialmente sí (5–10 casos beta) | Ya cubierto con `labs_intake_manual.py` |
| **Haut.AI** | No bien (métricas de piel reproducibles) | MVP-0 manual; Haut.AI en MVP-1 |
| **Healthie** | No (es EHR/ops, no IA) | MVP-1 cuando haga falta portal clínico |
| **Longevity-AI / LongevityEHR** | Compiten con el “cerebro”, no con PyMuPDF | Evaluar solo si quieres saltarte el build |

**Tesis:** renta la plomería commodity, construye el cerebro (motor de protocolo + gates + compliance MX).

---

## 2. Costos aproximados por proveedor

*Precios B2B sin cotización requieren demo/ventas. Fuentes públicas consultadas junio 2026.*

### 2.1 BloodGPT — [bloodgpt.com/labs](https://bloodgpt.com/labs)

| Plan | Fijo/mes | Variable | Bonus al signup |
|------|----------|----------|-----------------|
| **Portal** (upload manual) | **$195** | **$0.05/biomarcador** | 5,000 biomarcadores |
| **API** (automatización) | **$690** | **$0.01–$0.05/biomarcador** | 20,000 biomarcadores |
| Enterprise / white-label / on-prem | Cotización | — | — |

**Ejemplo:** panel ~50 biomarcadores vía portal ≈ **$2.50/panel** + $195/mes (o cubierto por pool de bonus al inicio).

**Qué aporta más allá de un LLM:**
- Normalización nombres/unidades entre laboratorios y locales
- Tendencias longitudinales automáticas
- PDFs paciente + clínico white-label
- HL7/FHIR, webhooks, empaquetado HIPAA
- Upsell de paneles de seguimiento

**Cuándo rentarlo:** ~50+ paneles/mes, multi-lab, o reportes paciente automatizados.

---

### 2.2 Build propio labs (MVP-0) — `rag-bot/scripts/labs_intake_manual.py`

Pipeline híbrido:
1. Texto nativo PDF (PyMuPDF) — labs digitales mexicanos
2. Si texto insuficiente → visión OpenAI (páginas renderizadas)
3. Estructuración → JSON + markdown para protocolo

| Modelo | Uso |
|--------|-----|
| `gpt-4o-mini` | Texto → JSON (default) |
| `gpt-4o-mini` | OCR fallback |
| `gpt-4o` | `--high-precision` para tablas difíciles |

**Costo real:** ~**$0.01–0.10/panel** en tokens OpenAI; PyMuPDF gratis en PDFs digitales.

---

### 2.3 Haut.AI — [haut.ai](https://haut.ai/)

| Concepto | Detalle |
|----------|---------|
| **Precio público** | No hay página de pricing; venta directa B2B |
| **Estimación startup** | ~$500–2,000/mes (típico API estética; confirmar en demo) |
| **Qué hace** | ~150 parámetros de piel por foto RGB (poros, manchas, arrugas, rojeces) |

**¿Un LLM en selfie basta?** No de forma fiable:
- No da scores comparables visita a visita
- Alucina métricas sin calibración
- No replica el gancho de conversión documentado en estética (uplift en recomendación de productos)

**HV:** MVP-0 = observación manual. MVP-1 = Haut.AI o Perfect Corp. El **Diagnóstico Vigente™ térmico** es complemento RGB, no sustituto.

---

### 2.4 Healthie — [gethealthie.com/healthie-pricing](https://gethealthie.com/healthie-pricing)

| Plan | Anual | Mensual | Clientes activos |
|------|-------|---------|------------------|
| Core | **$18/mes** | $19/mes | 10 |
| Essentials | **$45/mes** | $49/mes | 250 |
| Plus | **$115/mes** | $129/mes | Ilimitados |
| Group | **$135+/mes** | $149+/mes | +$50/clínico |

**API:** add-on (típicamente Plus/Group). **No es IA** — backbone: intake, charting, care plans, portal, telehealth, billing.

---

### 2.5 Terra (wearables) — [tryterra.co/pricing](https://tryterra.co/pricing)

| Plan | Precio | Incluye |
|------|--------|---------|
| Quick Start | **$499/mes** ($399 anual) | 100k créditos/mes |
| Overages | desde **$0.005/crédito** | — |
| Add-ons (Health Scores, Blood Report API, etc.) | **+$499/mes** c/u | — |

**Rook** ([tryrook.io](https://www.tryrook.io/)): pricing no público; modelo usage-based similar; fuerte en LatAm según matriz interna.

---

### 2.6 WhatsApp — 360dialog — [docs.360dialog.com/pricing](https://docs.360dialog.com/docs/get-started/pricing)

| Concepto | Costo |
|----------|-------|
| Licencia canal (Regular) | **$59 USD/mes** (~49 EUR) |
| Premium | $119/mes |
| Mensajes Meta | Variable por categoría (utility/marketing) + país |

MVP-0: WhatsApp personal ($0). API cuando automatizas webhooks, plantillas y escala.

---

### 2.7 Longevity-AI — [longevity-ai.com/plans](https://www.longevity-ai.com/plans)

| Plan | Precio |
|------|--------|
| Starter | **$349/mes/asiento** (trial 14 días) |
| Growth | **$1,899/mes** (6 asientos, +$299/asiento extra) |
| Enterprise | Custom |

**Incluye:** Florence AI (labs PDF, SOAP, planes), app miembro, wearables, “Book About You” PDF, dashboard clínico. Entrenado con narrativa de **1.6M EHR** (sesgo HMO/enterprise).

---

### 2.8 LongevityEHR — [longevityehr.com](https://www.longevityehr.com/)

| Concepto | Detalle |
|----------|---------|
| Precio público | Sin cifra — “monthly license” vs **$200k+ build** |
| Time-to-market | **2–3 semanas** white-label |
| Incluye | Portal branded, intake, scheduling labs, planes, tracking, digest biomarcadores IA, templates, HIPAA |

---

## 3. Stack completo por fase

### 3.1 MVP-0 (semanas — estado actual)

| Capa | Herramienta | Costo aprox. | Estado HV |
|------|-------------|--------------|-----------|
| Landing | Framer / HTML | $0–20/mes | Existe |
| Onboarding | Tally | Free–$29/mes | Pendiente operativo |
| Cerebro | RAG + LLM (`rag-bot`) | ~$5–50/mes tokens | ✅ Hecho |
| Labs | PyMuPDF + gpt-4o-mini | ~$0.01–0.10/panel | ✅ Hecho |
| WhatsApp | Manual / personal | $0 | Manual |
| Pagos | Stripe/Conekta | % transacción | Pendiente |
| Médico + Rx | Médico + Prescrypto | Variable MX | Ensamblar |
| Farmacia | O-Lab / Compounding MX | Por receta | Convenio |
| Foto piel | Manual | $0 | MVP-0 |
| Wearables | Manual (screenshots) | $0 | MVP-0 |

**Burn fijo software MVP-0:** ~**$0–100/mes** (Tally + OpenAI).

---

### 3.2 MVP-1 (meses — 20–100 usuarios)

| Capa | Herramienta | Costo aprox. |
|------|-------------|--------------|
| EHR backbone | Healthie Plus | ~$115/mes + API add-on |
| Labs parseo | BloodGPT portal **o** build propio | $195/mes + variable |
| Wearables | Terra Quick Start | $499/mes |
| Skin AI | Haut.AI / Perfect Corp | Sales (~$500–2k/mes) |
| WhatsApp API | 360dialog | $59/mes + Meta msgs |
| Motor protocolo | **Build** pgvector + gates | IP propia |

**Burn fijo estimado MVP-1:** ~**$900–1,500/mes** (sin Longevity-AI).

---

### 3.3 MVP-2 / Av.2 (médico + Rx + lounge)

| Capa | Herramienta | Notas |
|------|-------------|-------|
| E-receta MX | Prescrypto | API abierta, COFEPRIS |
| Deep Longevity | API reloj biológico | Feature premium opcional |
| Health Gorilla | Ordenar labs estilo US | Si expandes US |
| Hippocratic AI | Agentes seguimiento | Opcional |
| Lounge físico | Capex | Experiencia + ticket alto |

---

## 4. Las 14 capas del stack (referencia)

De `Arquitectura_PlugAndPlay_y_Matriz.md`:

| # | Capa | Fase típica | Rentar / Build |
|---|------|-------------|----------------|
| 1 | Framer/Webflow | MVP-0 | Rentar |
| 2 | Capa clínica MX | MVP-0+ | **ENSAMBLAR** (gap MX) |
| 3 | Prescrypto | Av.2 Rx | Rentar |
| 4 | Farmacia magistral | Av.2 | Rentar |
| 5 | Labs (Chopo/Olab) | MVP-0 | Convenio + PDF |
| 6 | BloodGPT | MVP-1 | Rentar o build ✅ |
| 7 | Terra/Rook | MVP-1 | Rentar |
| 8 | Haut.AI / Perfect Corp | MVP-1 | Rentar |
| 9–11 | Stripe/Conekta/Kueski/OXXO | MVP-0/1 | Rentar |
| 12 | WhatsApp 360dialog | MVP-1 | Rentar |
| 13 | Healthie/Cerbo | MVP-1 | Rentar |
| 14 | **Motor protocolo** | MVP-0→ | **CONSTRUIR** ✅ |

**Opcionales MVP-2+:** Deep Longevity · Health Gorilla · Hippocratic AI · Tellescope (CRM) · Spruce (comms clínica).

---

## 5. LongevityEHR vs Longevity-AI vs build HV

Superficie similar (longevity + labs + planes + portal); propósito distinto:

| Dimensión | LongevityEHR | Longevity-AI | Hombre Vigente (build) |
|-----------|--------------|--------------|------------------------|
| **Qué venden** | Portal white-label rápido | Plataforma clínica AI completa | Motor protocolo + compliance MX |
| **Time-to-market** | 2–3 semanas | Días (self-serve trial) | Operativo en labs/RAG |
| **Precio entrada** | Licencia mensual (demo) | **$349/mes/asiento** | Infra mínima |
| **IA** | Digest biomarcadores + insights | **Florence** (1.6M EHR, studies) | RAG corpus HV + gates |
| **Wearables** | Integraciones genéricas | Integrado | Terra/Rook en MVP-1 |
| **Skin RGB** | No es foco | No es foco | Haut.AI + térmico propio (IP) |
| **MX / COFEPRIS** | Genérico US | Genérico US/IL | Copy educativo + médico responsable |
| **Foso** | Bajo (marca tuya, motor de ellos) | Medio (datos HMO) | **Alto** (motor + data moat) |
| **Mejor si…** | App branded sin dev | Clínica OS + AI out-of-box | IP, Av.1 educativo, control total |

**Overlap con repo actual:**

| Función | LongevityEHR / L-AI | HV hoy |
|---------|---------------------|--------|
| Labs PDF | Sí | `labs_intake_manual.py` |
| Intake | Sí | Tally + `schemas/intake_mvp0.json` |
| Planes | Book About You / templates | `protocol_draft.py` + RAG |
| Diferenciador | — | Gates MX (litio+ayuno), servicios+longevity KB, lounge |

**Veredicto:** LongevityEHR = atajo si validas sin código. Longevity-AI = overkill caro para 5–10 betas; buen benchmark UX clínica (trial 14 días).

---

## 6. BloodGPT vs LLM propio — matriz de decisión

| Criterio | LLM + PyMuPDF (MVP-0) | BloodGPT |
|----------|----------------------|----------|
| Costo 10 paneles/mes | ~$1–5 tokens | $195/mes mínimo |
| PDF digital MX (Chopo) | ✅ Muy bueno | ✅ Muy bueno |
| PDF escaneado | ✅ con visión | ✅ nativo |
| Normalización multi-lab | Manual / reglas | ✅ Automático |
| Tendencias longitudinales | Build propio | ✅ Incluido |
| PDF paciente branded | Build propio | ✅ Incluido |
| HL7/FHIR | No | ✅ |
| HIPAA empaquetado | Depende de tu infra | ✅ |

**Recomendación HV:** no comprar BloodGPT para las primeras 5–10 betas. Reevaluar al pasar ~50 paneles/mes o al necesitar portal paciente de labs automatizado.

---

## 7. Recomendaciones prácticas (junio 2026)

1. **No contratar** BloodGPT, Haut.AI ni Healthie para las primeras 5–10 betas.
2. **Seguir con** `labs_intake_manual.py` + RAG + Tally + WA manual — costo marginal casi cero.
3. **Evaluar LongevityEHR** solo si necesitas portal paciente branded en ~3 semanas sin dev (pedir demo + cifra de licencia).
4. **No contratar Longevity-AI Starter ($349/mes)** hasta que el volumen justifique reemplazar el motor; usar trial como benchmark UX.
5. **Primer rent con ROI claro:** 360dialog ($59/mes) al automatizar seguimiento; luego Terra ($499/mes) si wearables son core del protocolo.

---

## 8. Escenarios de burn mensual (estimado)

| Escenario | Usuarios activos | Stack | Burn software fijo |
|-----------|------------------|-------|-------------------|
| **Beta MVP-0** | 5–10 | Tally + OpenAI + WA manual | **$0–100/mes** |
| **MVP-1 lite** | 20–50 | + 360dialog + Healthie Essentials | **~$200–300/mes** |
| **MVP-1 full** | 50–100 | + Terra + BloodGPT portal + Haut.AI | **~$900–1,500/mes** |
| **Buy cerebro** | cualquiera | Longevity-AI Starter (1 seat) | **+$349/mes** |
| **Buy portal** | cualquiera | LongevityEHR (licencia) | **TBD (demo)** |

*No incluye: honorarios médico, magistral, labs del paciente, marketing, capex lounge.*

---

*Investigación multi-fuente, junio 2026. Precios sujetos a cambio; validar en demo antes de comprometer presupuesto. No es consejo legal ni médico.*