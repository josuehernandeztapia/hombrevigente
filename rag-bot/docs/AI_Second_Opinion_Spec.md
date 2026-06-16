# AI Second Opinion — Revisor Clínico HV (spec / contrato)

> **Estado**: spec post-MVP, Av.2. NO implementado. Este documento es el **contrato**
> que el médico aliado revisa antes de que exista código (misma disciplina que
> `Metodologia_Indice_Vigente.md`: contrato primero, handler después).
> **Versión** 0.1 · jun-2026.

## 0. Qué es y qué NO es

Un asistente que, **antes de que un protocolo/reporte de consulta llegue al beta**,
revisa las recomendaciones del **médico aliado** contra el SSOT de evidencia (monografías
+ guías) y **marca** posibles adiciones, aclaraciones, interacciones o consideraciones
faltantes. El médico ve las marcas y **decide**.

Inspirado en el "AI Longevity Brain" de Longevium (ver [[longevium-competitor]]), adaptado
al encuadre regulatorio de México.

**NO es:**
- ❌ No es de cara al usuario. **Nunca** se le muestra al beta. Es una herramienta PARA el médico.
- ❌ No decide ni prescribe. **Marca; el médico aprueba/firma.** (Doctrina HV: "el modelo sugiere, el médico firma".)
- ❌ No reemplaza al médico. Reduce puntos ciegos — es "segunda opinión", no opinión única.
- ❌ No inventa: cada marca cita su fuente (PMID / monografía + nivel de evidencia) o no se emite.

## 1. Por qué encaja (y por qué es defendible en COFEPRIS)

Es **clinical decision support** (categoría más regulada que el Índice). La defensa es de
diseño: **el médico responsable sigue siendo el responsable de cada decisión** — la IA solo
le da contexto basado en evidencia. Un asistente que mantiene al médico en el loop por
construcción es defendible; uno que decide autónomamente, no. Slide 7 de Longevium lo dice
igual: *"the physician remains responsible for every medical decision"*.

Además **profundiza el moat**: no es "IA que diagnostica" (riesgo), es "IA que audita a favor
del médico" (confianza). Es exactamente el atributo "serio" que el market research dice que
ningún competidor mexicano tiene.

## 2. Contrato (inputs → output)

### Input
```
ReviewRequest {
  beta_id: str
  draft: {                        # borrador del médico aliado
    recomendaciones: [str]        # o estructura de protocolo (stack, dosis, lifestyle)
    notas_consulta: str
    avenida: "1" | "2"            # Av.1 suplementos / Av.2 Rx-péptidos
  }
  contexto: {                     # ya existe en HV
    intake, labs, indice_vigente, fase, gates_activos
  }
}
```

### Proceso (reusa primitivos existentes)
1. `rag_retrieval_local` sobre SSOT (longevity + servicios, evidence-tiered) con la query
   construida desde `draft.recomendaciones` + `contexto`.
2. `confidence_gate` — los **mismos gates** (psiquiatría/onco/péptidos): si el draft sugiere
   algo que cae en gate, se marca como flag de severidad alta, no se "aprueba" en silencio.
3. Comparación recomendación ↔ evidencia recuperada → genera flags. (LLM con prompt acotado:
   "compara este borrador contra esta evidencia; marca brechas; NO inventes; cita fuente".)

### Output (objeto de revisión — NO una decisión)
```
ReviewResult {
  flags: [ {
      tipo: "adicion" | "aclaracion" | "faltante" | "interaccion" | "contraindicacion",
      severidad: "alta" | "media" | "baja",
      texto: str,                 # qué considerar
      evidencia: { fuente: "PMID:xxxx" | "monografia:NN", nivel: "E1..E5" },  # obligatorio
      gate: str | null            # si disparó un gate de seguridad
  } ],
  sin_observaciones: bool,        # true = el draft luce alineado con la evidencia
  confianza: float,
  reviewed_at: iso8601
}
```

## 3. Gate humano (no negociable)

```
draft del médico → ReviewResult (IA marca) → médico acepta/rechaza cada flag y FIRMA
                 → solo entonces el protocolo va al beta
```
La IA **nunca** entrega al beta. El paso de firma del médico es obligatorio y se audita.

## 4. Reúsa vs nuevo

| Pieza | Estado |
|---|---|
| Retrieval sobre SSOT (`rag_retrieval_local`) | ✅ existe |
| Gates de seguridad (`confidence_gate`) | ✅ existe |
| Monografías con nivel de evidencia + PMIDs | ✅ existe (longevity 30-35 + servicios 26) |
| Traza/auditoría (`hv_agent_traces`, `log_trace`) | ✅ existe |
| Prompt "revisa borrador vs evidencia, marca brechas, cita fuente" | ❌ nuevo |
| Schema `ReviewResult` + persistencia de revisión + firma del médico | ❌ nuevo (migración) |
| Flujo/UI del médico para aceptar/rechazar flags | ❌ nuevo |

## 5. Riesgos / framing-as-code (igual que el Índice)

- **Cada flag sin fuente no se emite** (forzado en código, no en copy).
- **Vocabulario**: el claim-guard aplica — la IA marca "considerar X (evidencia Y)", nunca
  "el paciente tiene/cura/trata".
- **Av.1/Av.2**: un flag no puede recomendar Av.2 (péptido/Rx) como Av.1 — los gates lo bloquean.
- **Auditoría completa**: cada revisión + decisión del médico → `hv_agent_traces` (quién, qué, cuándo).
- **Médico responsable**: cédula del médico aliado firma cada protocolo. La IA es asistencia, no autoría.

## 6. Posicionamiento

- **Cuándo**: post-MVP. Requiere primero (a) primer beta corriendo el flujo end-to-end,
  (b) médico aliado con cédula formalizado (Av.2), (c) volumen de consultas que justifique automatizar la revisión.
- **Valor**: hace al médico aliado más rápido y seguro ("segunda opinión en cada consulta"),
  y es un diferenciador que profundiza el moat de compliance.
- **Antes de construir**: validar con el médico aliado que este contrato refleja su flujo real
  de revisión, y con asesoría legal que el encuadre de "decision support con médico responsable"
  está cubierto bajo COFEPRIS / NOM aplicable.
