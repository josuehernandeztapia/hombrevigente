# Revisión del Inventario de Producto (flujos/copy) — errata accionable

**Junio 2026 · para el dueño + peer.** Revisión del `Inventario Hombre Vigente.md` (landing, onboarding, conversión Av.1/Av.2, seguimiento, confianza, canal). El producto está completo y coherente; esto es lo que hay que corregir antes de live, por prioridad.

---

## 🔴 1. Escala de evidencia — inversión + contradicción interna (CRÍTICO)
**Problema:**
- `Confianza Vigente` define **E1 = meta-análisis (fuerte) … E4 = emergente (débil)**.
- El SSOT del repo (`rag-bot/knowledge_base/longevity/00_MARCO`) define lo **opuesto**: **E1 = mecanismo … E4 = humano robusto/RCT (fuerte) … E5 = regulatorio**.
- Peor: la app se contradice sola — en *Tu Índice* (P06), "Glucosa · en rango · **E4**" se usa como señal *estable/fuerte* (escala SSOT), mientras la leyenda de Confianza dice E4 = débil.

**Fix (recomendado):** **No exponer códigos E1–E5 al usuario.** Son taxonomía interna del RAG. En la UI traducir a lenguaje plano:
- **Fuerte** = RCT / meta-análisis humano
- **Moderada** = humano temprano (piloto/cohorte)
- **Emergente** = preclínico / animal / mecanístico

Los E1–E5 se quedan internos en el SSOT (sin re-etiquetar las 28 monografías ya verificadas). Mapear los tags actuales de la app a las 3 etiquetas planas.

## 🔴 2. "Evidencia citada" sin citas
**Problema:** la pantalla cuyo propósito es citar lista "Meta-análisis 2022" sin PMID/DOI.
**Fix:** amarrar cada ingrediente a los PMIDs verificados del SSOT:
- Omega-3 → Calder 28900017 / REDUCE-IT 30415628 · NMN → Yoshino 33888596 / 36482258 · Espermidina → Eisenberg 19801973 · BPC-157 → Sikiric 21548867 · GHK-Cu → Pickart 29986520.

## 🟠 3. Pantalla Receta + Magistral (Teleconsulta P3) — la de mayor riesgo
- **Cédula del médico** ("Dr. Andrés Lemus · Céd. Prof. 7 482 119"): si es placeholder, **etiquetar como ejemplo**. Mostrar una cédula profesional inventada en una receta firmada es terreno de suplantación. Antes de live: médico real, cédula real, contrato de responsable sanitario.
- **"Wolverine Stack"** como nombre de **receta médica firmada** choca con el posicionamiento clínico. Renombrar a algo clínico (ej. "Protocolo magistral de reparación · péptidos").
- BPC-157/TB-500 = péptidos bajo revisión FDA (503A). Vía médico+magistral en MX es la ruta legítima, pero esta superficie no pasa de prototipo sin médico responsable + farmacia magistral con contrato + consentimiento informado real.

## 🟠 4. Seguimiento P3 contradice "el médico firma"
**Problema:** copy *"el modelo recalibra tu stack"* + *"Subimos Tesamorelin 0.5 → 1 mg"* pinta al software ajustando una **dosis de prescripción (Av.2)** solo.
**Fix:** para cualquier Rx, el copy debe ser *"tu médico ajustó/aprobó"*; el modelo **sugiere**, el médico **decide**. Además, tesamorelin/fisetin/ciática es el protocolo personal del Caso #1 filtrándose al flujo genérico — usar ejemplos neutros en el producto.

## 🟡 5. Menores
- **Stack Vigente** inconsistente: conversión lista "NMN·Omega-3·Creatina·Vit D3+K2·Magnesio"; WhatsApp Hilo 1 solo "NMN·Omega-3·Creatina". Alinear la composición canónica.
- **Aviso de Privacidad:** el consentimiento (Onboarding P02) enlaza a un documento que aún no existe. Redactar la política real (LFPDPPP) antes de live — sin ella, el consentimiento es cosmético.
- **Scores 68 (onboarding) vs 64 (escaneo):** ok que difieran (diagnóstico completo vs 3 datos); asegurar que el copy lo explique.
- **Caso #1 métricas** (hs-CRP −34%, etc.): ya tienen footer "ilustrativo, no garantiza" ✓ — mantener.

---

## Lo que está bien (no tocar)
Routing Av.1/Av.2 · consentimiento como pantalla temprana · lenguaje optimización/no-diagnóstico · disclaimers · térmico como ΔT adjunto · rieles de pago MX · estados de error/vacío · guiones de WhatsApp · Confianza como producto · marca noir+bronce consistente.

---

## Snippets corregidos (fix #1 + #2) — listos para pegar
Reemplazar en `Inventario Hombre Vigente.html` **y** en la pantalla real `Confianza Vigente`.

**Leyenda — los 4 `<li>` de E1–E4 → estos 3 (lenguaje plano; E1–E5 quedan internos del SSOT):**
```html
<li class="lv1"><strong>Fuerte</strong> — RCT o meta-análisis humano</li>
<li class="lv1"><strong>Moderada</strong> — humano temprano (piloto / cohorte)</li>
<li class="lv1"><strong>Emergente</strong> — preclínico / mecanístico / animal</li>
```

**Ingredientes — los 6 `<li>` → estos (tier honesto + fuente verificada):**
```html
<li class="lv1"><strong>Omega-3</strong> · Baja inflamación (hs-CRP) · <strong>Fuerte</strong> — Calder 2017, PMID 28900017</li>
<li class="lv1"><strong>Creatina</strong> · Fuerza y cognición · <strong>Fuerte</strong> — meta-análisis (PMID por verificar)</li>
<li class="lv1"><strong>NMN</strong> · Sube NAD+ · <strong>Moderada</strong> — Yoshino 2021, PMID 33888596</li>
<li class="lv1"><strong>Espermidina</strong> · Autofagia · <strong>Moderada</strong> — Eisenberg 2009, PMID 19801973</li>
<li class="lv1"><strong>GHK-Cu</strong> · Remodelación de colágeno · <strong>Emergente</strong> — Pickart 2018, PMID 29986520</li>
<li class="lv1"><strong>BPC-157</strong> · Reparación de tejido · <strong>Emergente</strong> — Sikiric 2011, PMID 21548867</li>
```

Cambios deliberados (honestidad de evidencia):
- **NMN y Espermidina bajaron a "Moderada"** (NMN = RCTs pequeños; espermidina = cohorte/preclínico). Ponerlas a la par de Omega-3 inflaba la evidencia.
- **Creatina** queda "Fuerte" pero **sin PMID inventado** — "por verificar".

**Fix extra — `Tu Índice` (P06):** quitar los E-tags de los **biomarcadores** (hs-CRP, HRV, glucosa). Un valor de lab no tiene "nivel de evidencia"; el tier es para **claims de intervención**, no para mostrar una lectura. Esto elimina de raíz la confusión E4=fuerte/débil.

---
*Prioridad de ejecución: 1 y 2 antes de cualquier demo pública; 3 y 4 antes de operar Av.2; 5 antes de live. No es consejo legal — validar 3 y el Aviso de Privacidad con asesoría.*
