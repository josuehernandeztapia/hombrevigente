# Protocolo de Calidad de Suministro — Péptidos y viales (Av.2)

> **Estado**: radar / post-MVP. Aplica a **Av.2** (péptidos/inyectables/magistral con médico),
> NO al MVP (Av.1 = suplementos sin receta). Documento de procurement/calidad, no de software.
> Refuerza el moat "serio desde día 1" (ver Market_Research §7-8, COMPLIANCE.md).

## Principio rector (el que define todo lo demás)

**Un COA genérico no garantiza el lote siguiente.** Un certificado de un vendor —o un buen
ranking— prueba *un* lote en *un* momento. El único método sólido para protocolo clínico es
**testear el lote que vas a usar**. Todo lo de abajo es para *reducir el campo* antes de llegar
a ese test, nunca para reemplazarlo.

## El embudo de 3 pasos (criba → calificación → verificación)

La presencia en plataformas de ranking es **filtro inicial, no sello de confianza**. Separar:

**Paso 1 — CRIBA (barato, descarta):** ¿el vendor se somete a testeo independiente?
- ✅ Aparece en **Finnrick** con resultados aceptables → sigue.
- ⚠️ Solo en **Janoshik** → señal débil (los vendors *pagan* por mostrar resultados = sesgo de
  selección; "al menos se testean", no "son buenos").
- 🔴 No aparece en ninguno / sin testeo de terceros (ej. **Exoma**, "99% HPLC" no verificable) → descarta.

**Paso 2 — CALIFICACIÓN (por vendor):**
- COA **por lote** (no genérico).
- Para inyectables: pruebas de **endotoxinas + esterilidad** (no solo identidad/pureza).
- Idealmente lab analítico con acreditación (ISO 17025 / GLP).

**Paso 3 — VERIFICACIÓN (por lote, NO negociable):**
- Mandar una muestra del **lote específico** a un lab independiente antes de usarlo.
- Sin este paso, los pasos 1-2 no bastan para protocolo Av.2.

## Las 3 capas de laboratorios (para qué sirve cada una)

| Capa | Ejemplos | Función | Cuándo usar |
|---|---|---|---|
| **1. Plataformas de ranking** (comparan vendors) | **Finnrick** (independiente, expone fallas) · Janoshik (vendor-submitted) · Optima Labs (COA por batch) | **Criba** — a quién mirar | Antes de comprar, para filtrar |
| **2. Labs analíticos independientes** (testean TU muestra) | **MZ Biolabs** (AZ, reputado) · ACS Labs (FL) · Janoshik (barato/rápido) | **Verificación de lote** (HPLC/MS, contaminantes) | El paso 3 — testear el lote real |
| **3. Acreditados ISO 17025 / GLP** (gold standard) | Eurofins · SGS · Intertek · Charles River · NSF · cores universitarios (opción local MX: facultades de química) | **Rigor máximo** (proficiency testing) | Cuando el volumen/riesgo lo justifique |

## Gate de decisión Av.2

Ningún péptido/inyectable entra a un protocolo que se entrega a un beta sin:
1. **Proveedor calificado** (pasó criba + calificación, pasos 1-2).
2. **Lote testeado** (paso 3, lab independiente, lote específico + endotoxinas/esterilidad si inyectable).
3. **Firma del médico responsable** (cédula). La IA puede marcar brechas (ver
   `rag-bot/docs/AI_Second_Opinion_Spec.md`), pero el médico decide y firma.

Esto es continuación directa del moat de compliance: en un mercado donde todos usan "research use",
ser quien hace el procurement bien es diferenciación, no solo defensa.

## Acción concreta para verificar un proveedor MX (ej. Exoma)
- **Comparar antes de comprar** → buscar el vendor en Finnrick/Janoshik. (Exoma no aparece → su
  "99% HPLC" no es verificable.)
- **Verificar el lote** → muestra a Janoshik (barato/rápido) o MZ Biolabs (más reputado). Finnrick
  testea gratis si envías muestra.
- **Rigor máximo** → Eurofins/SGS/Intertek o core universitario (más caro/lento).

## Diferido (NO construir ahora): monitor automatizado de vendors
Un scraper/monitor de Finnrick/Janoshik es vigilancia continua de proveedores — tiene sentido
**cuando compres péptidos recurrentemente a varios vendors** (Av.2 a escala), no antes.
Nota técnica para ese momento: **API-first → fetch+Cheerio sobre HTML → headless (Playwright)
como último recurso**; revisar `robots.txt`/ToS; cron + cache para no golpear los sitios.
Finnrick (Next.js) probablemente expone JSON interno o "Researcher data access" → vía legítima
antes de scrapear.

## Pendientes de mundo real (de Josué, no de código)
- Formalizar médico responsable con cédula (gate Av.2).
- Contrato con farmacia magistral.
- Validar con asesoría legal el encuadre COFEPRIS de importación/uso de péptidos (hoy zona gris,
  inferida del comportamiento de vendors — Market_Research §7, 🔴 sin confirmar con fuente primaria).
