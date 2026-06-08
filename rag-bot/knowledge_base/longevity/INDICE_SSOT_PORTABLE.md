# SSOT Longevidad — Índice maestro para RAG (Hombre Vigente)

**Versión:** 1.1 · 7 de junio de 2026 (sección 7 de PMIDs corregida y verificada)  
**Autor del corpus:** sesión HV + literatura pública curada  
**Canónico en repo:** `github.com/josuehernandeztapia/hombrevigente` → `rag-bot/knowledge_base/longevity/`  
**Commit:** `2aa0f94` (rama `main`)

> Documento de referencia en `Downloads/longevity`. El contenido detallado vive en el repo (29 monografías, ~1.900 líneas). Este archivo es el **mapa, reglas y guía de uso**.

---

## 1. Qué es y qué NO es

| Es | No es |
|----|-------|
| Base de conocimiento para **Motor de Recomendación Justificada** (RAG) | Prescripción médica |
| Evidencia pública (mecanismo, preclínico, piloto, regulatorio) con tier **E1–E5** | Claim de cura, uso humano de research peptides, PMF |
| Lenguaje **optimización / wellness educativo** compliant MX | Publicidad terapéutica (Art. 309 LGS) |
| Complemento para informes con **datos del usuario + citas** | Sustituto de médico responsable (Av.2) |

**Disclaimer estándar (todo output RAG):**
> *Información educativa de optimización y bienestar. No constituye diagnóstico ni tratamiento médico. Ante patología, embarazo, psicofármacos o antecedentes oncológicos, consulta a tu médico. Compuestos de Avenida 2 requieren prescripción y farmacia autorizada.*

---

## 2. Sistema de evidencia (E1–E5)

**Principio:** evidencia es evidencia — no todo requiere RCT humano.

| Tier | Qué cuenta | Cómo habla HV |
|------|------------|---------------|
| **E1** | Mecanismo, revisiones (Hallmarks, inflammaging) | "La biología del envejecimiento describe…" |
| **E2** | Preclínico reproducido (BPC-157 roedores, fisetina senolítica) | "En modelos preclínicos se observó… (E2)" |
| **E3** | Piloto humano, cohorte pequeña, Khavinson | "Estudios piloto reportan… (E3)" |
| **E4** | RCT, FDA/EMA (tesamorelin, GLP-1, lifestyle) | Hecho acotado, sin extrapolar indicación |
| **E5** | Regulatorio (COFEPRIS, NOM-022, FDA warnings) | Solo marco legal, no consejo jurídico |
| **E0** | Anécdota, blend comercial sin estudio | Marcar explícitamente; no recomendar |

**Regla RAG:** afirmación factual → `(E#)` + PMID/DOI cuando exista.

---

## 3. Avenidas y gates

```
INTAKE (Tally: labs, wearable, cuestionario, foto, consentimiento)
    → BloodGPT / Terra / Haut.AI (rentados)
    → MOTOR JUSTIFICACIÓN (RAG + este SSOT)
    → Informe de Optimización / Perfil Vigente
         ├─ AVENIDA 1: lifestyle + suplementos (NMN, resveratrol, espermidina, fisetina…)
         └─ AVENIDA 2: screening → médico → receta → magistral
                (BPC-157, TB-500, GHK inyectable, tesamorelin, Khavinson dudoso)
```

**Gates obligatorios del motor:**
- Péptido inyectable mencionado → bloquear entrega directa; solo Av.2.
- Antecedente oncológico + inmunomodulador/senolítico → precaución + médico.
- Litio/quetiapina/bipolar + Cerluten/neuromoduladores → psiquiatra.
- Red flags neurológicos (déficit motor, vejiga) → derivar urgencia; no recomendar.

---

## 4. Catálogo completo de monografías

### Governance y RAG
| Archivo | Contenido |
|---------|-----------|
| `00_MARCO_SSOT_EVIDENCIA_Y_COMPLIANCE.md` | Reglas evidencia, lenguaje, matriz compuesto→avenida |
| `29_MOTOR_JUSTIFICACION_EJEMPLOS.md` | 5 respuestas canónicas listas para few-shot |

### Frameworks biológicos (01–07)
| # | Archivo | Tema | Tier |
|---|---------|------|------|
| 01 | `hallmarks_envejecimiento` | 12 hallmarks 2023, mapa intervenciones | E1 |
| 02 | `inflammaging` | Inflamación crónica, hs-CRP, térmico | E1–E3 |
| 03 | `nad_sirtuinas` | NAD+, SIRT, precursores | E1–E3 |
| 04 | `autofagia_spermidina` | Poliaminas, mTOR/AMPK | E2–E3 |
| 05 | `senescencia_senoliticos` | SASP, fisetina, D+Q | E2–E3 |
| 06 | `epigenetica_relojes_biologicos` | Horvath, TruAge, DunedinPACE | E2–E3 |
| 07 | `reprogramacion_celular` | Yamanaka, partial reprogramming — solo investigación | E1–E2 |

### Péptidos y metabolismo Rx (08–17)
| # | Archivo | Compuesto | Tier | Avenida |
|---|---------|-----------|------|---------|
| 08 | `bpc157` | BPC-157 reparación GI/tendón/nervio | E2 | 2 |
| 09 | `tb500_timpbeta4` | TB-500, Goralatide, actina | E2 | 2 |
| 10 | `ghk_cu` | Cobre péptido, colágeno, piel | E2–E3 | 1 tópico / 2 inyectable |
| 11 | `tesamorelin` | GHRH, grasa visceral (FDA HIV) | E4 | 2 |
| 12 | `glow_limitless_blend` | Blends comerciales — evidencia por componente | E0–E2 | 2 |
| 13 | `nmn` | Precursor NAD+ | E2–E3 | 1 |
| 14 | `resveratrol` | Sirtuinas, polifenol | E2–E3 | 1 |
| 15 | `fisetin_quercetina` | Senolíticos orales pulsados | E2 | 1 |
| 16 | `epitalon` | Pineal Khavinson, telómeras claims | E2–E3 | 1–2 |
| 17 | `glp1_metabolismo_longevidad` | Semaglutida/tirzepatida contexto | E4 | 2 |

### Khavinson (20–24)
| # | Archivo | Producto | Órgano / eje |
|---|---------|----------|--------------|
| 20 | `khavinson_marco_biorreguladores` | Marco general, crítica occidental | — |
| 21 | `endoluten` | Pineal, sueño, circadiano | |
| 22 | `cerluten` | SNC — **gate psiquiatría** | |
| 23 | `vladonix` | Timo — **gate oncología** | |
| 24 | `ventfort` | Vascular, perfusión | |

### Aplicación HV (25–28)
| # | Archivo | Uso |
|---|---------|-----|
| 25 | `biomarcadores_panel_optimizacion` | Interpretación labs (hs-CRP, IGF-1, HbA1c, litio…) |
| 26 | `lifestyle_pilares` | Sueño, ejercicio, nutrición — E4 primero |
| 27 | `regeneracion_neuro_musculo_esqueletico` | Discopatía, ciática, RM — sin prometer cura |
| 28 | `termografia_inflammaging` | ΔT, Seek/FLIR, lenguaje adjunto |

### Tarjetas atómicas (`tarjetas/` — 15 chunks YAML)

Formato alineado a `Prompt_Construir_SSOT_RAG.md`. Una tarjeta = un embedding óptimo para el motor Peldaño 1.

| id | Archivo | Tema |
|----|---------|------|
| supl-vitamina-d | `supl-vitamina-d.md` | Vitamina D3 |
| supl-omega3 | `supl-omega3.md` | EPA/DHA |
| supl-magnesio | `supl-magnesio.md` | Magnesio |
| supl-coq10 | `supl-coq10.md` | CoQ10 |
| supl-tmg | `supl-tmg.md` | TMG / betaína |
| bio-homocisteina | `bio-homocisteina.md` | Homocisteína |
| bio-lipidos-apob | `bio-lipidos-apob.md` | LDL, ApoB, TG |
| bio-vitamina-d | `bio-vitamina-d.md` | 25(OH)D |
| wearable-hrv | `wearable-hrv.md` | HRV |
| wearable-sueno | `wearable-sueno.md` | Sueño wearable |
| wearable-readiness | `wearable-readiness.md` | Readiness score |
| wearable-fc-reposo | `wearable-fc-reposo.md` | FC reposo |
| habito-ayuno | `habito-ayuno.md` | Ayuno intermitente |
| habito-frio-calor | `habito-frio-calor.md` | Sauna / frío |
| interaccion-litio-psicofarmacos | `interaccion-litio-psicofarmacos.md` | Gate litio/quetiapina |

**Rutas:** repo `rag-bot/knowledge_base/longevity/tarjetas/` · espejo `~/Downloads/longevity/tarjetas/`

---

## 5. Matriz rápida — stack protocolo personal → SSOT

| Elemento protocolo Juan Josué | Monografía SSOT | Nota RAG |
|-------------------------------|-----------------|----------|
| GLOW Limitless + BPC + GHK | 08, 09, 10, 12 | Av.2; blend E0 |
| Tesamorelin | 11 | Av.2; monitoreo IGF-1 |
| NMN + resveratrol | 03, 13, 14 | Av.1 |
| Spermidina | 04 | Av.1 |
| Fisetina + quercetina | 05, 15 | Av.1 pulsos |
| Khavinson ciclo 20/10 | 20–24 | Gate psiquiatra/oncólogo |
| Ciática / RM lumbar | 27 | Educación + rehab E4 |
| Térmico Seek/FLIR | 28 | ΔT seguimiento |
| Litio + quetiapina | 00, 22, 25 | Nunca ajustar; derivar |

---

## 6. Lenguaje permitido vs prohibido (resumen)

### Permitido
- "Se asocia con vías de… en literatura (E#)"
- "Tus labs muestran… que en estudios se correlaciona con…"
- "Informe de Optimización / Perfil Vigente"
- "Suplemento de optimización" (Av.1)
- "Bajo valoración médica" (Av.2)
- "Monitoreo ΔT adjunto, no diagnóstico"

### Prohibido
- Curar, tratar, sanar, anticancerogénico
- "Research peptide for human use"
- Dosificación personalizada por bot
- Diagnóstico médico por foto/térmico solo
- "Aprobado para longevidad" (salvo hecho regulatorio exacto)

---

## 7. Referencias maestras (PMIDs ancla)

> **Corregido v1.1 (2026-06-07):** todos verificados contra PubMed/Europe PMC. En v1.0, 10 de 13 PMIDs apuntaban a papers ajenos (mismo defecto que las tarjetas v0.1). Reemplazados por el PMID real verificado.

| Tema | PMID verificado | Referencia |
|------|-----------------|------------|
| Hallmarks of aging 2013 | **23746838** | López-Otín et al., Cell 2013 |
| Hallmarks of aging 2023 | **36599349** | López-Otín et al., Cell 2023 |
| Geroscience framework | **25417146** | Kennedy et al., Cell 2014 |
| Senescent cells in ageing (framework) | **24848057** | van Deursen, Nature 2014 |
| Senolytic drugs review | **32686219** | Kirkland & Tchkonia, J Intern Med 2020 |
| Inflammaging | 24833586 | Franceschi & Campisi, J Gerontol 2014 |
| NAD+ boosting (review) | **26785480**, 29514064 | Verdin, Science 2015; Rajman/Sinclair, Cell Metab 2018 |
| NR bioavailability (human) | **27721479** | Trammell et al., Nat Commun 2016 |
| NMN humano (RCT) | **33888596** | Yoshino et al., Science 2021 |
| NMN aerobic capacity (RCT) | **34238308** | Liao et al., JISSN 2021 |
| NMN older men (pilot) | **35927255** | Igarashi et al., NPJ Aging 2022 |
| Resveratrol CR-mimetic (human RCT) | **22055504** | Timmers et al., Cell Metab 2011 |
| Resveratrol insulin sensitivity (T2DM) | **21385509** | Brasnyó et al., Br J Nutr 2011 |
| Resveratrol oral bioavailability | **15084383** | Walle et al., Drug Metab Dispos 2004 |
| Resveratrol SIRT1 yeast (foundational) | **12939617** | Howitz et al., Nature 2003 |
| Resveratrol mice high-calorie diet | **17086191** | Baur et al., Nature 2006 |
| Espermidina longevity mice | **19801973** | Eisenberg et al., Nat Cell Biol 2009 |
| Espermidina review (health/disease) | **29371440** | Madeo et al., Science 2018 |
| Espermidina cardioprotection + diet cohort | **27841876** | Eisenberg et al., Nat Med 2016 |
| Espermidina memory RCT (older adults) | **30388439** | Wirth et al., Cortex 2018 |
| Dietary spermidine mortality cohort | **29955838** | Kouli et al., Am J Clin Nutr 2018 |
| Fisetina senolytic | **30279143** | Yousefzadeh et al., EBioMedicine 2018 |
| Quercetin senolytic discovery (transcriptome) | **25754370** | Zhu et al., Aging Cell 2015 |
| D+Q senolytics IPF (first-in-human) | **30616998** | Justice et al., EBioMedicine 2019 |
| D+Q senolytics diabetic kidney (human pilot) | **31542391** | Hickson et al., EBioMedicine 2019 |
| BPC-157 review (GI) | **21548867** | Sikiric et al., Curr Pharm Des 2011 |
| BPC-157 and blood vessels (review) | **23782145** | Seiwerth et al., Curr Pharm Des 2014 |
| BPC-157 vascular / ICV model | **29510201** | Vukojević et al., Vascul Pharmacol 2018 |
| BPC-157 tendon healing (rats) | **21030672** | Chang et al., J Appl Physiol 2011 |
| BPC-157 musculoskeletal review | **30915550** | Gwyer et al., Cell Tissue Res 2019 |
| Tβ4 dermal wound repair (mice) | **12581423** | Philp et al., Wound Repair Regen 2003 |
| Tβ4 actin / repair review | **16099219** | Goldstein et al., Trends Mol Med 2005 |
| Tβ4 epicardial progenitors | **17108969** | Smart et al., Nature 2007 |
| Tβ4 de novo cardiomyocytes | **21654746** | Smart et al., Nature 2011 |
| Tβ4 venous ulcers (human) | **20536470** | Kleinman et al., Ann NY Acad Sci 2010 |
| Tβ4 clinical applications review | **26096726** | Goldstein et al., Expert Opin Biol Ther 2015 |
| GHK-Cu review (gene data) | **29986520** | Pickart & Margolina, Int J Mol Sci 2018 |
| GHK-Cu skin pathways | **26236730** | Pickart et al., Biomed Res Int 2015 |
| Cold water exposure review | **36137565** | Esperland et al., Int J Circumpolar Health 2022 |
| Sauna mortality cohort | **25705824** | Laukkanen et al., JAMA Intern Med 2015 |
| Oura ring HRV validation | **32217820** | Kinnunen et al., Physiol Meas 2020 |
| HRV-guided training (RCT) | **28570494** | Kiviniemi et al., J Strength Cond Res 2017 |
| Tesamorelin GHRH HIV lipodystrophy (RCT) | **15249570** | Koutkia et al., JAMA 2004 |
| Tesamorelin NEJM metabolic (RCT) | **18057338** | Falutz et al., NEJM 2007 |
| Tesamorelin visceral + liver fat (RCT) | **25038357** | Stanley et al., JAMA 2014 |
| Tesamorelin liver enzymes (HIV) | **28832410** | Fourman et al., AIDS 2017 |
| Senolytics IPF (pilot) | **30616998** | Justice et al., EBioMedicine 2019 |
| Epitalon mice | **14501183** | Anisimov et al., Biogerontology 2003 |
| Horvath clock | 24138928 | Horvath, Genome Biol 2013 |
| Partial reprogramming (Ocampo) | **27984723** | Ocampo et al., Cell 2016 |
| Reprogramming & vision (Lu) | **33268865** | Lu et al., Nature 2020 |
| Partial reprogramming human cells | **35390271** | Gill et al., eLife 2022 |
| ICE / epigenetic aging (Sinclair) | **36638792** | Yang et al., Cell 2023 |

*PMIDs en negrita = corregidos en v1.1 (el v1.0 apuntaba a un paper ajeno). Los no-negrita ya eran correctos.*

> ✅ **Auditoría SSOT completa (2026-06-08):** monografías `00–29` y tarjetas `tarjetas/*.md` — **0 huecos `[FALTA FUENTE]`** en cuerpo embebible. Changelog `## Auditoría citas` puede mencionar PMIDs retirados; no se embebe (split en `kb_pipeline`).

---

## 8. Cómo activar en producción

### Paso 1 — Revisión médico aliado
Revisar monografías **08–11, 20–24, 27** antes de clientes reales.

### Paso 2 — Embeddings Pinecone
```bash
cd ~/Desktop/hombrevigente/rag-bot
# Requiere .env con OPENAI_API_KEY y PINECONE_API_KEY
python generate_embeddings.py --source longevity
# O estética + longevidad:
python generate_embeddings.py --source all
```

### Paso 3 — Prompt sistema Motor de Justificación
Instrucciones mínimas para el LLM:
1. Solo usar chunks recuperados + tiers E#.
2. Siempre: dato usuario → mecanismo → recomendación → disclaimer.
3. Nunca Av.2 sin mencionar médico + magistral.
4. Output = "Informe de Optimización", no "diagnóstico".

### Paso 4 — MVP-0
Usar con Tally intake + WhatsApp; médico revisa Av.2 manualmente.

---

## 9. Relación con otros docs en `Downloads/longevity`

| Documento local | Relación con SSOT |
|-----------------|-------------------|
| `CapaTech_Peldano1_Motor_Recomendacion.md` | Arquitectura tech — este SSOT es el KB |
| `Blueprint_Oferta_y_Pricing.md` | Tiers comerciales — Av.1/2 del SSOT |
| `Estrategia_Digital_First_Ola_Longevidad.md` | Go-to-market — longevidad gestionada |
| `Protocolo_Personal_*` | Caso #1 — **E0** narrativa, no evidencia clínica |
| `Marco_Regulatorio_Legal_Mexico.md` | Legal — alineado con `00_MARCO` |
| `MEMORIA_Proyecto_HombreVigente.md` | Contexto fundador — gates litio/oncología |

---

## 10. Mantenimiento del SSOT

| Acción | Cuándo |
|--------|--------|
| Añadir monografía nuevo compuesto | Al introducir producto en catálogo |
| Actualizar PMID | Si sale paper relevante |
| Re-embed Pinecone | Tras cada cambio en `longevity/*.md` o `longevity/tarjetas/*.md` |
| Sync Downloads ↔ repo | Copiar este índice o monografías puntuales |
| Versión | Incrementar en README longevity + este archivo |

---

## 11. Una línea

**El SSOT convierte "lo que el LLM sabe de internet" en citas tiered + lenguaje legal — para que HV cobre por claridad fundamentada, no por vender un vial.**

---

*No es consejo médico, legal ni financiero. Corpus basado en literatura pública; validación clínica y legal pendiente del médico aliado.*