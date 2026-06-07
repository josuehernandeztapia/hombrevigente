# Auditoría — SSOT + tarjetas vs. `Prompt_Construir_SSOT_RAG.md`

**Revisión de cumplimiento · 7 de junio de 2026**

> Veredicto corto: la **forma** cumple casi perfecto, pero la **regla #1 del prompt** (la razón de ser del SSOT) está **rota en masa**. ~17 de ~26 PMIDs apuntan a papers de temas totalmente ajenos. Esto es exactamente la alucinación que el prompt existía para impedir. **No embeber ni usar en producción hasta corregir.**

---

## 1. Lo que SÍ cumple (forma) ✅

| Requisito del prompt | Estado |
|----------------------|--------|
| Esquema de 16 campos (id, tipo, nombre, resumen, mecanismo, señales_que_lo_activan, dosis_referencia, evidencia{nivel/resumen/fuentes}, requiere_receta, contraindicaciones, flag_seguridad, confianza, disclaimer, version, revisado_por, fecha) | ✅ Las 15 tarjetas lo tienen completo |
| `tipo` dentro del enum (Suplemento, Biomarcador, Señal-Wearable, Habito, Interaccion) | ✅ |
| Lenguaje **educativo, no terapéutico** ("se asocia / se ha estudiado", sin "cura/revierte") | ✅ Consistente |
| `contraindicaciones` + `flag_seguridad` en cada tarjeta | ✅ |
| Gate `requiere_receta` y derivación médica | ✅ (litio = `alto-riesgo`, bien resuelto) |
| `confianza` (alta/media/baja) | ✅ |
| `disclaimer` estándar | ✅ |
| `revisado_por: PENDIENTE-MEDICO` | ✅ En todas |
| 1 concepto = 1 chunk + temas relacionados | ✅ |
| Uso correcto de `[FALTA FUENTE]` | ✅ Aparece donde no hay RCT (ej. `wearable-readiness`) |

La estructura es lista-para-embeddings. El problema **no** es el formato.

---

## 2. Lo que NO cumple — Regla #1 rota ❌ (crítico)

El prompt dice, textual: *"SOLO fuentes REALES y verificables… Está PROHIBIDO fabricar citas, PMIDs o resultados."*

Verifiqué **todos** los PMIDs contra PubMed (NCBI E-utilities). Resultado:

### PMIDs CORRECTOS (9) ✅
| PMID | Tarjeta | Es realmente |
|------|---------|--------------|
| 17634462 | supl-vitamina-d | Holick, *Vitamin D deficiency*, NEJM 2007 ✓ |
| 28202713 | supl-vitamina-d | Martineau, *Vit D & resp. infection*, BMJ 2017 ✓ |
| 30415628 | supl-omega3 | Bhatt, REDUCE-IT, NEJM 2019 ✓ |
| 23853635 | supl-magnesio | Abbasi, *Mg & insomnia in elderly*, 2012 ✓ |
| 25282031 | supl-coq10 | Mortensen, Q-SYMBIO CoQ10, 2014 ✓ |
| 29754952 | habito-ayuno | Sutton, eTRF prediabetes, Cell Metab 2018 ✓ |
| 30586774 | bio-lipidos-apob | Grundy, AHA/ACC cholesterol guideline ✓ |
| 21646368 | bio-vitamina-d | Holick, Endocrine Society vit D guideline 2011 ✓ |
| 25705824 | habito-frio-calor | Laukkanen, *Sauna & mortality*, JAMA IM 2015 ✓ |

→ Patrón: el **estudio landmark/famoso** de cada tarjeta casi siempre tiene el PMID correcto.

### PMIDs INVENTADOS / MAL ASIGNADOS (18) ❌
El número existe pero apunta a un paper **de otro tema** (o no resuelve):

| PMID citado | Tarjeta | Dice ser… | **Realmente es…** |
|-------------|---------|-----------|-------------------|
| 33540229 | supl-magnesio | Fiorentini, Mg review 2021 | Química de inhibidores de neuraminidasa (influenza) |
| 32316700 | supl-coq10 | Dludla, CoQ10 meta HF 2020 | Nanopartículas de granate de hierro-itrio (láser) |
| 32803460 | wearable-hrv **y** wearable-readiness | Kinnunen, validación Oura 2020 | Colonoscopías durante COVID |
| 15735095 | supl-tmg | Olthof, betaína baja homocisteína 2005 | Licopeno sérico (NHANES) |
| 21270374 | supl-tmg | Schwab, betaína y homocisteína 2011 | Folato y cáncer colorrectal |
| 11834528 | bio-homocisteina | Wald, homocisteína y ECV 2002 | Hiperlipidemia familiar combinada |
| 20571086 | bio-homocisteina | Clarke, vitaminas B 2010 | Secuenciación genómica (consensus circular) |
| 28158798 | bio-vitamina-d | Bouillon, vit D óptima 2017 | Metilación de ADN en fibroblastos de pollo |
| 28859947 | bio-lipidos-apob | Ference, LDL causal 2017 | FOURIER/evolocumab (CV real, pero **no** es Ference) |
| 28072787 | wearable-hrv | Shaffer, HRV review 2017 | *"Obama signs 21st Century Cures Act"* |
| 27059824 | wearable-sueno | Irwin, sueño e inflamación 2016 | Ingeniería de cianobacterias (eritritol) |
| 27188887 | wearable-fc-reposo | Zhang, RHR y mortalidad 2016 | Ecología de *Cryptococcus* (Mediterráneo) |
| 30132057 | wearable-fc-reposo | Düking, wearables deporte 2018 | Espectrometría LA-ICP-MS |
| 35487895 | habito-ayuno | Liu, meta-análisis ayuno 2022 | mRNA de CFTR (biología molecular) |
| 35768581 | habito-frio-calor | Espeland, winter swimming 2022 | Itaconato y osteoartritis (condrocitos) |
| 26999127 | interaccion-litio | Gitlin, toxicidad de litio 2016 | Diversidad de virus de Hepatitis C (Yunnan) |
| 28440185 | interaccion-litio | Malhi, guías de bipolar 2017 | Péptidos antimicrobianos β-hairpin |
| 28637797 | supl-omega3 | Calder, omega-3 inflamación 2017 | **No resuelve en PubMed** (inválido) |

**18 citas defectuosas** (32803460 se usa en 2 tarjetas). Es decir: ~2 de cada 3 PMIDs están mal.

> Lo grave no es solo que estén mal — es que **se ven plausibles**: autor real, año real, título creíble. Un médico revisor que no abra cada PMID los aprobaría. Eso es justo el riesgo que el prompt quería matar.

---

## 3. Hallazgo secundario — el índice maestro afirma cosas no verificables

`SSOT_Longevidad_RAG_HombreVigente.md` dice tener *"29 monografías, ~1.900 líneas"* en el repo (`rag-bot/knowledge_base/longevity/`, commit `2aa0f94`) y referencia archivos `00_`–`29_`. **Localmente esos archivos no existen** — solo están las 15 tarjetas. Además el índice trae su **propia** tabla de "PMIDs ancla" (sección 7: 37014410, 24833586, etc.) que **no he verificado** y que, dado lo anterior, hay que auditar igual antes de confiar.

Acción: confirmar que las 29 monografías existan de verdad en el repo y con ese commit, o marcar la afirmación como pendiente.

---

## 4. Veredicto

- **Andamiaje (formato, lenguaje, gates, seguridad): aprobado.** El diseño de la tarjeta es exactamente lo que pide el prompt y es buen insumo para RAG.
- **Contenido citacional: reprobado.** Viola la regla #1, la única que de verdad importa para la defensa legal y la confianza clínica. Embeber esto = construir el RAG sobre citas falsas = el mismo pecado del repo original (dato inventado con apariencia de válido), pero ahora en territorio médico.
- **Decisión:** **NO embeber, NO mostrar a médico-aliado como está.** Primero corregir las 18 citas.

---

## 5. Cómo arreglarlo (orden correcto)

1. **Por cada PMID de la tabla ❌:** buscar el paper que la cita *dice* ser y poner su PMID **real verificado**, o — si no se encuentra rápido — sustituir por `[FALTA FUENTE]`. Nunca dejar un número "que suena bien".
2. **Verificar siempre contra PubMed** (E-utilities `efetch?db=pubmed&id=…&rettype=docsum`) antes de aceptar cualquier PMID. Regla operativa: *ningún PMID entra sin que alguien (o un script) haya abierto el docsum y confirmado título+tema.*
3. **Bajar `confianza`** de toda tarjeta que quede con `[FALTA FUENTE]` y mandarla a revisión médica.
4. **Auditar la sección 7** del índice maestro (PMIDs ancla) con el mismo método.
5. Recién entonces: embeddings.

> Sugerencia: puedo regenerar las 15 tarjetas dejando los 9 PMIDs verificados, y reemplazando los 18 malos por el PMID real (verificándolo en PubMed en el momento) o por `[FALTA FUENTE]`. Así quedan limpias y listas para el médico.

---
*Método: 100% de los PMIDs citados en `tarjetas/*.md` verificados contra NCBI PubMed E-utilities el 2026-06-07. No es consejo médico ni legal.*
