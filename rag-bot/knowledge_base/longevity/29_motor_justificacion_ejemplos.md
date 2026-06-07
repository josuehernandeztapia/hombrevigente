# Motor de Justificación — Ejemplos canónicos RAG

**Categoría**: RAG templates  
**Avenida HV**: Transversal  
**Tags**: ejemplos, prompts, justificación, routing

---

## Ejemplo 1 — Avenida 1 (labs + stack oral)

**Input usuario:** Hombre 44, HbA1c 5.4%, hs-CRP 2.6, sueño Oura 6.2h, objetivo energía + piel.

**Output RAG:**
> **Perfil Vigente — Informe de Optimización (educativo)**
>
> **Tus datos:** Glucosa y HbA1c en rango favorable (E4). hs-CRP 2.6 mg/L sugiere **carga inflamatoria moderada** respecto a objetivos de optimización (<1 mg/L en prevención agresiva, E3). Sueño 6.2h — por debajo de 7–9h recomendadas (E4).
>
> **Por qué importa:** La inflamación crónica de bajo grado (inflammaging) se vincula con menor recuperación y envejecimiento acelerado en estudios poblacionales (E1, PMID 24833586).
>
> **Recomendación Av.1:**
> 1. Priorizar **higiene del sueño** 14 días (E4) — ver `26_lifestyle_pilares.md`
> 2. **Stack Vigente:** NMN + resveratrol + espermidina — soporte eje NAD+/autofagia (E2–E3, `03_nad`, `04_autofagia`, `13_nmn`, `14_resveratrol`)
> 3. **Pulsos fisetina/quercetina** 2 días/sem — senolíticos experimentales (E2, `15_fisetin`)
> 4. Re-test hs-CRP en 8–12 semanas
>
> **No incluye:** péptidos inyectables.
>
> *Disclaimer estándar — ver `00_MARCO`.*

---

## Ejemplo 2 — Gate Av.2 (péptidos)

**Input:** Mismo usuario + ciática recurrente + RM discopatía L4-S1 documentada + pide "Wolverine stack".

**Output RAG:**
> **Educación:** BPC-157 y TB-500 muestran efectos en **reparación tisular y modelos de lesión nerviosa periférica** en roedores (E2, PMID 21548867 BPC-157, 12581423 Tβ4). **No hay RCT en humanos para ciática.**
>
> **Routing:** Esta solicitud activa **Avenida 2**. Próximo paso: **teleconsulta médica** para evaluar indicación, interacciones (**litio/quetiapina si aplica**), y vía **magistral con receta** — no venta de research peptide.
>
> Mientras tanto: **rehab conservador** (E4, `27_regeneracion_neuro`).

---

## Ejemplo 3 — Khavinson + oncología familiar

**Input:** Antecedente padre cáncer activo, usuario pregunta Vladonix.

**Output RAG:**
> **Precaución:** Vladonix se discute en literatura Khavinson para **inmunosenescencia** (E2–E3). Con **antecedente oncológico familiar/activo**, los inmunomoduladores requieren **médico/oncólogo** — HV **no recomienda** ciclos Khavinson sin valoración (E5 prudencia clínica).
>
> **Permitido Av.1:** lifestyle, labs, sueño, stack oral básico con aprobación médica.

---

## Ejemplo 4 — Termografía

**Input:** ΔT 0.5°C glúteo post-protocolo 4 semanas, dolor 6→4.

**Output RAG:**
> **Seguimiento:** Disminución de dolor autorreportado + tendencia a menor asimetría térmica. IRT documenta **cambios de perfusión local** en estudios de recuperación (E2–E3). **Correlación no es causalidad.** Continuar seguimiento con escala dolor + labs inflamación.

---

## Ejemplo 5 — Tesamorelin

**Input:** Perímetro cintura ↑, IGF-1 límite bajo, pide tesamorelin.

**Output RAG:**
> Tesamorelin tiene evidencia **E4** para grasa visceral en **indicación FDA específica** (lipodistrofia HIV). Uso en composición corporal general = **off-label**, requiere **endocrinólogo**, monitoreo IGF-1/glucosa. **Av.2 únicamente.**

---

## Reglas post-proceso (guardrails código)

1. Si menciona BPC/TB/tesamorelin inyectable sin flag médico → insertar bloque Av.2.
2. Si antecedente oncológico + inmunomodulador/senolítico → bloque precaución.
3. Si litio/psiquiátricos en intake + Cerluten/estimulantes → derivar psiquiatra.
4. Siempre append disclaimer `00_MARCO`.
5. Citar `(E#)` y PMID cuando exista en chunk.

---

## Auditoría citas (2026-06-07)
- PMID 24833586 → OK (Franceschi, inflammaging, J Gerontol 2014)
- PMID 29738410 → reemplazado por **21548867** (Sikiric, BPC-157 review; el viejo era alineación espinal)
- PMID 30993593 → reemplazado por **12581423** (Philp, Tβ4 reparación dérmica; el viejo era errata de Vestronidase)