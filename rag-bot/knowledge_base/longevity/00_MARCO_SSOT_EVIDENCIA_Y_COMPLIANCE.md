# Marco SSOT — Evidencia, Lenguaje y Compliance (Hombre Vigente)

**Categoría**: Governance / RAG  
**Avenida HV**: Transversal  
**Versión**: 1.0 · Junio 2026

---

## 📋 Definición

Este documento define **cómo el Motor de Recomendación Justificada** puede hablar de longevidad, bio-optimización y compuestos en el SSOT, sin cruzar a medicina ilícita ni publicidad sanitaria prohibida en México.

**Principio:** *Evidencia es evidencia* — preclínica, mecanística y observacional cuentan para **educar y contextualizar**, no para **prometer curación**.

---

## 🔬 Sistema de evidencia E1–E5

### E1 — Mecanismo establecido
- Descripción de vías (p. ej. mTOR, NAD+, SASP, inflamación NF-κB).
- Fuentes: revisiones en *Cell*, *Nature Reviews*, *Ageing Research Reviews*.
- **Uso HV:** "La biología del envejecimiento describe que…"

### E2 — Preclínico
- In vitro, roedores, ex vivo humano.
- Reproducibilidad importa más que un solo paper llamativo.
- **Uso HV:** "En modelos preclínicos se ha observado… (E2). Esto no establece el mismo efecto en personas."

### E3 — Humano temprano
- Pilotos, n=1 publicados, cohortes pequeñas, registros.
- **Uso HV:** "Un estudio piloto en humanos reportó… (E3). Requiere confirmación."

### E4 — Humano robusto
- RCT, meta-análisis, indicación aprobada en alguna jurisdicción.
- **Uso HV:** citar hecho sin extrapolar a otras indicaciones.

### E5 — Regulatorio / legal
- FDA, EMA, COFEPRIS, NOM, Art. 309 LGS.
- **Uso HV:** hechos de marco legal, no consejo jurídico.

---

## ✅ Lenguaje PERMITIDO (optimización / wellness educativo)

| Contexto | Ejemplos permitidos |
|----------|---------------------|
| Mecanismo | "Se asocia con vías de reparación tisular en literatura preclínica" |
| Biomarcador | "Tu hs-CRP elevada se correlaciona con estado inflamatorio en estudios poblacionales" |
| Estilo de vida | "El sueño profundo se vincula con recuperación y regulación metabólica" |
| Producto Av.1 | "Suplemento alimenticio / optimización nutricional" |
| Producto Av.2 | "Solo bajo valoración y prescripción de profesional de la salud" |
| Térmico | "Herramienta de monitoreo de variación térmica relativa (ΔT), adjunta, no diagnóstica" |
| Educación | "Algunos investigadores exploran…", "La evidencia preclínica sugiere…" |

---

## 🚫 Lenguaje PROHIBIDO (copy, RAG, redes, WhatsApp)

- Curar, tratar, sanar, revertir enfermedad, anticancerogénico garantizado.
- "Aprobado para longevidad" (salvo hecho regulatorio exacto y acotado).
- "Seguro para todos", "sin efectos secundarios".
- Sustituir médico/psiquiatra (especialmente psicofármacos, litio, antecedente oncológico).
- "Research peptide for human use" / incitar uso humano de research-only.
- Diagnóstico médico basado solo en selfie, térmico o wearable.
- Dosificación personalizada sin médico (Av.2).

**Art. 309 Ley General de Salud (MX):** publicidad de productos con alegaciones de salud requiere autorización COFEPRIS. HV prioriza **educación** y **consulta**, no ads terapéuticos.

---

## 🛤️ Routing Avenida 1 vs Avenida 2

```
Intake (labs, wearable, cuestionario, foto)
    → Motor Justificación (RAG + este SSOT)
    → Informe de Optimización / Perfil Vigente
         ├─ AVENIDA 1: lifestyle + suplementos (NMN, resveratrol, spermidina, etc.)
         │             + educación sobre biomarcadores
         └─ AVENIDA 2: screening → teleconsulta médico → Rx → magistral
                        (péptidos inyectables, secretagogos, etc.)
```

**Gate crítico:** si el output menciona BPC-157, TB-500, tesamorelin inyectable, Khavinson inyectable, o stack combinado inyectable → **bloquear entrega directa**; solo educación general + derivación médica.

---

## 📊 Matriz compuesto → evidencia → avenida

| Compuesto / tema | E predominante | Avenida | Nota regulatoria MX |
|------------------|----------------|---------|-------------------|
| Hallmarks / inflammaging | E1 | 1 | Educación |
| NMN / NR | E2–E3 | 1 | Suplemento |
| Resveratrol | E2–E3 | 1 | Suplemento |
| Spermidina | E2–E3 | 1 | Suplemento |
| Fisetina / quercetina | E2 | 1 | Senolítico experimental oral |
| BPC-157 | E2 | 2 | Research / magistral Rx |
| TB-500 / Tβ4 | E2 | 2 | Research / magistral Rx |
| GHK-Cu inyectable | E2 | 2 | Research / cosmético según vía |
| Tesamorelin | E4 (indicación HIV lipodistrofia FDA) | 2 | Rx |
| Khavinson oral | E2–E3 (literatura nicho) | 1–2 | Zona gris; suplemento/importación |
| Termografía ΔT | E2–E3 (inflamación) | 1 | Adjunto wellness |
| Reprogramación celular | E1–E2 | 1 | Solo investigación futura |

---

## 📝 Plantilla de chunk RAG (obligatoria)

Cada recomendación generada debe incluir:

1. **Dato del usuario** ("Tus labs muestran…")
2. **Mecanismo o correlación** con tier `(E#)`
3. **Referencia** (PMID, DOI o sección SSOT)
4. **Disclaimer** estándar (abajo)
5. **Routing** si aplica Av.2

**Disclaimer estándar:**
> *Información educativa de optimización y bienestar. No constituye diagnóstico ni tratamiento médico. Ante patología, embarazo, psicofármacos o antecedentes oncológicos, consulta a tu médico. Compuestos de Avenida 2 requieren prescripción y farmacia autorizada.*

---

## 🔗 Fuentes maestras del SSOT

- PubMed / PMC (revisiones y mecanismos)
- Hallmarks of Aging (López-Otín et al., Cell 2013 PMID: 23746838; Cell 2023 update PMID: 36599349)
- Inflammaging (Franceschi et al.)
- COFEPRIS marco general; NOM-022-SSA3-2012 (actos médicos)
- Papers específicos por monografía en archivos `01–29`

---

## 📖 FAQ para el motor

**¿Puede el RAG recomendar BPC-157 directamente?**  
No. Puede explicar evidencia preclínica (E2) y derivar a Av.2.

**¿Puede decir "antiinflamatorio"?:**  
Sí en contexto educativo: "vías asociadas con modulación inflamatoria en modelos preclínicos", no "curará tu inflamación".

**¿Puede usar datos del Caso #1 del fundador?:**  
Solo como narrativa de marketing con consentimiento; no como evidencia clínica (E0 anecdótico).

**¿Khavinson es evidencia occidental fuerte?:**  
Predominantemente E2–E3 en literatura rusa/europea; presentar con matiz.

---

## 🏷️ Metadata para embeddings

```yaml
categoria: governance
avenida: transversal
evidencia: E5
tags: [compliance, evidencia, lenguaje, COFEPRIS, RAG]
```

---

## Auditoría citas (2026-06-07)
- PMID 37014410 → reemplazado por **36599349** (Hallmarks of aging: an expanding universe, López-Otín, Cell 2023). El 37014410 apuntaba a un paper de radiómica de cáncer de mama.