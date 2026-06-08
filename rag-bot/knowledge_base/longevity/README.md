# SSOT Longevidad — Knowledge Base para RAG (Hombre Vigente)

**Versión:** 1.0 · Junio 2026  
**Propósito:** Base de conocimiento curada para el **Motor de Recomendación Justificada**. Cada chunk debe poder citar mecanismo + evidencia pública + lenguaje permitido.

> **No es prescripción.** No afirma uso humano, cura ni tratamiento de enfermedad. Lenguaje: *optimización, rendimiento, recuperación, wellness educativo.*

---

## Estructura

| Prefijo | Archivo | Contenido |
|---------|---------|-----------|
| `00` | `00_MARCO_SSOT_EVIDENCIA_Y_COMPLIANCE.md` | Reglas de evidencia, tiers E1–E5, lenguaje legal MX, routing Avenida 1/2 |
| `01–07` | Frameworks biológicos | Hallmarks, inflammaging, NAD+, autofagia, senescencia, epigenética, reprogramación |
| `08–14` | Péptidos y secretagogos | BPC-157, TB-500, GHK-Cu, tesamorelin, blends |
| `15–19` | Oral longevidad | NMN, resveratrol, spermidina, fisetina/quercetina |
| `20–24` | Khavinson | Marco + Endoluten, Cerluten, Vladonix, Ventfort |
| `25–28` | Aplicación HV | Biomarcadores, lifestyle, nervio periférico, termografía |
| `29` | `29_MOTOR_JUSTIFICACION_EJEMPLOS.md` | Plantillas de respuesta RAG con citas |
| `tarjetas/` | 15 tarjetas atómicas YAML | Chunks Peldaño 1 (suplementos, biomarcadores, wearables, hábitos, gates) |

**Copia espejo:** `~/Downloads/longevity/tarjetas/` · monografías en `~/Downloads/longevity/repo_monografias/`

**Auditoría PMIDs (2026-06-08):** SSOT longevity completo — monografías y tarjetas sin `[FALTA FUENTE]` en contenido embebible. Ver `## Auditoría citas` por archivo e `INDICE_SSOT_PORTABLE.md` §7.

**Changelog monografías:**
- `07_reprogramacion_celular.md` — 2026-06-07: +Ocampo/Lu/Gill/Yang; 0 huecos
- `13_nmn.md` — 2026-06-08: +Liao 34238308, +Igarashi 35927255; 0 huecos
- `03_nad_sirtuinas.md` — 2026-06-08: +Trammell 27721479; eje NAD+ sin huecos

---

## Niveles de evidencia (E1–E5)

| Tier | Significado | Uso en recomendación HV |
|------|-------------|-------------------------|
| **E1** | Mecanismo molecular bien descrito (revisiones, libros de texto) | Educación + correlación con biomarcador |
| **E2** | Preclínico reproducido (in vitro, roedores, modelos tejido) | "La literatura preclínica sugiere…" + disclaimer |
| **E3** | Piloto humano, cohorte pequeña, observacional | "Estudios piloto reportan…" + no prometer resultado |
| **E4** | RCT, meta-análisis, aprobación regulatoria en alguna indicación | Evidencia fuerte; aún sin claims terapéuticos en copy |
| **E5** | Guía de práctica / regulatorio (FDA, EMA, COFEPRIS en su ámbito) | Solo hechos regulatorios, no extrapolar indicación |

**Regla RAG:** toda afirmación factual lleva `(E#)` y preferiblemente PMID/DOI.

---

## Avenidas HV

- **Avenida 1:** optimización sin Rx — suplementos, lifestyle, interpretación de labs, wearables.
- **Avenida 2:** requiere **médico responsable** — péptidos inyectables, secretagogos, magistral, cualquier intervención con perfil Rx.

---

## Ingesta a Pinecone

```bash
cd rag-bot
python generate_embeddings.py --source longevity   # tras actualizar script
```

---

## Revisión médica

Contenido basado en literatura pública. **Requiere revisión del médico aliado** antes de producción con clientes.