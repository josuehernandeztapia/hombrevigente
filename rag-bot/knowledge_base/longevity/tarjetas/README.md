# Tarjetas atómicas SSOT — Formato RAG (Peldaño 1)

**15 tarjetas** alineadas a `Prompt_Construir_SSOT_RAG.md`. Una tarjeta = un chunk óptimo para embeddings.

| id | Archivo |
|----|---------|
| supl-vitamina-d | Vitamina D3 |
| supl-omega3 | EPA/DHA |
| supl-magnesio | Magnesio |
| supl-coq10 | CoQ10 |
| supl-tmg | TMG / betaína |
| bio-homocisteina | Homocisteína |
| bio-lipidos-apob | LDL, ApoB, TG |
| bio-vitamina-d | 25(OH)D |
| wearable-hrv | HRV |
| wearable-sueno | Sueño wearable |
| wearable-readiness | Readiness score |
| wearable-fc-reposo | FC reposo |
| habito-ayuno | Ayuno intermitente |
| habito-frio-calor | Sauna / frío |
| interaccion-litio-psicofarmacos | Gate litio/quetiapina |

**Copia espejo:** `~/Downloads/longevity/tarjetas/`

**Monografías profundas:** `../` (archivos `00_`–`29_`)

Todas con `revisado_por: PENDIENTE-MEDICO` hasta validación del médico aliado.

---

## Corrección de citas — v0.2 (2026-06-07)

Auditoría: el 100% de los PMIDs se verificó contra PubMed (NCBI E-utilities). En la v0.1, 18 citas apuntaban a papers de temas ajenos (PMIDs mal asignados). En **v0.2** se reemplazaron por el PMID **real verificado** del paper intencionado, o por `[FALTA FUENTE]` cuando no se pudo confirmar.

PMIDs corregidos (intención → PMID real verificado):
- Calder omega-3 → **28900017** · Fiorentini Mg → **33808247** · Dludla CoQ10 → **32318636**
- Schwab betaína → **12399266** · Olthof betaína → **16871332**
- Wald homocisteína → **12446535** · Clarke B-vitaminas → **20937919**
- Ference LDL/EAS → **28444290** · Bouillon vit D → **23922354**
- Shaffer HRV → **29034226** · Kinnunen ring PPG → **32217820** (en hrv y readiness)
- Irwin sueño/inflamación → **26140821** · Zhang RHR → **26598376** · Düking wearables → **29712629**
- Liu ayuno (NEJM RCT) → **35443107** · Gitlin litio → **27900734** · Malhi bipolar → **33296123**

Pendiente (`[FALTA FUENTE]`): Espeland cold-water review (Int J Circumpolar Health 2022) — el artículo existe pero su PMID exacto queda por confirmar antes de producción.

Sin cambios (ya correctos en v0.1): supl-vitamina-d (17634462, 28202713), REDUCE-IT (30415628), Abbasi Mg (23853635), Q-SYMBIO (25282031), Sutton eTRF (29754952), Grundy (30586774), Holick guideline (21646368), Laukkanen sauna (25705824).

> Gate de producción intacto: toda tarjeta con `[FALTA FUENTE]`, `confianza: baja` o `flag_seguridad: alto-riesgo` requiere revisión del médico aliado antes de embeber.