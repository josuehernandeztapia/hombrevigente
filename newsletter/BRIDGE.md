# Bridge editorial — Pulso Vigente ↔ SSOT RAG

> **Fase 0 (manual).** Ritual al cerrar cada número. Sin automatización todavía.

Pulso y el bot comparten tema pero **no comparten el mismo artefacto**. Este doc define cómo pasar claims **ya verificados** del newsletter al corpus RAG — sin mezclar dos procesos distintos.

---

## Dos procesos — no los confundas

| Proceso | Origen | Destino | Cuándo |
|---------|--------|---------|--------|
| **Bridge editorial (este doc)** | Pulso `issues/*.md` — papers y lentes verificados | Monografías `rag-bot/knowledge_base/longevity/*.md` | Al **cerrar** un número publicable |
| **Autoaprendizaje Q&A** | Gaps en tráfico (`knowledge-gaps-*.md`, WhatsApp, API) | `knowledge-promotions-pending.json` → `FAQ_PROMOTED.md` + golden | Loop RAG aparte — ver `rag-bot/README.md` |

**Regla:** Pulso **enriquece el SSOT** (monografías). Las preguntas de usuarios **no** se promueven desde el newsletter; van por `POST /admin/knowledge/promote` o el workflow `rag-bot-process-promotions.yml`.

---

## Tipos de bridge (por bloque del número)

| Tipo | Cuándo | Acción |
|------|--------|--------|
| **A · SSOT** | Bloque con PMID/DOI + “Lente Vigente” accionable o claim factual para el motor | PR a monografía: sección *Evidencia reciente* o *Referencias* + nivel E |
| **C · Solo Pulso** | Contexto, voz, PR como lead, AI hype sin paper, geopolítica | **No tocar RAG** — queda solo en Pulso/redes |

Un número puede tener **hasta 4 bloques**; en la práctica **1–2 bridges A** (suelen ser Accionable y a veces Frontera con paper fuerte).

---

## Mapa `topic_ssot` → monografía

Alineado a `watchlist.yml` y `harvest.py`. Si dudas, usa `INDICE_SSOT_PORTABLE.md`.

| `topic_ssot` (watchlist) | Monografía principal |
|--------------------------|----------------------|
| `hallmarks_envejecimiento` | `01_hallmarks_envejecimiento.md` |
| `inflammaging` | `02_inflammaging.md` |
| `nad_nmn_sirtuinas` | `03_nad_sirtuinas.md`, `13_nmn.md` |
| `autofagia_espermidina` | `04_autofagia_spermidina.md` |
| `senescencia_senoliticos` | `05_senescencia_senoliticos.md`, `15_fisetin_quercetina.md` |
| `epigenetica_relojes_reprogramacion` | `06_epigenetica_relojes_biologicos.md`, `07_reprogramacion_celular.md` |
| `peptidos_bpc_tb500_ghk_tesamorelin` | `08_bpc157.md`, `09_tb500_timpbeta4.md`, `10_ghk_cu.md`, `11_tesamorelin.md` |
| `glp1_metabolismo` | `17_glp1_metabolismo_longevidad.md` |
| `lipidos_apob` | `25_biomarcadores_panel_optimizacion.md` (ApoB/LDL) |
| `sueno` | `26_lifestyle_pilares.md` |
| `termico_inflamacion` | `28_termografia_inflammaging.md`, `02_inflammaging.md` |
| `piel_optimizacion` | `12_glow_limitless_blend.md`, `10_ghk_cu.md` (tópico) |

---

## Checklist — cierre editorial (15–30 min)

Ejecutar **antes o justo después** del merge del issue a `main` (antes del envío si quieres coherencia bot ↔ email).

1. [ ] Cada bloque publicado tiene **PMID/DOI/registro** verificado (regla de hierro — `EDITORIAL.md`).
2. [ ] Rellenar tabla **Editorial bridge** al pie del `issues/NNN.md` (plantilla en stub del draft).
3. [ ] Por cada fila **A**: asignar nivel **E1–E5** (`00_MARCO_SSOT_EVIDENCIA_Y_COMPLIANCE.md`).
4. [ ] Lenguaje RAG: optimización/bienestar; sin diagnóstico/cura; sin condiciones nombradas; Av.2 solo con gate médico.
5. [ ] Abrir **PR enfocado** a `rag-bot/knowledge_base/longevity/`:
   - Patch corto (bullet + PMID + tier), no pegar el tono marketing de Pulso.
   - Si el claim es **investigación / preclínico** → etiqueta E2 y texto “no establece efecto en personas”.
6. [ ] Merge monografía → `rag-bot-nightly.yml` re-embede solo (CI existente).
7. [ ] Filas **C** → marcar `bridge: C` y no abrir PR RAG.

**No hacer en el mismo PR:** mezclar bridge Pulso con promotions Q&A del knowledge loop.

---

## Plantilla de patch en monografía

```markdown
### Evidencia reciente (Pulso NºNNN · YYYY-MM-DD)
- **[Título corto]** — *[Journal]* (YYYY). PMID XXXXX · E3.
  - Resumen factual (1–2 líneas, tono SSOT).
  - Límite: [piloto / n pequeño / preclínico / en investigación].
```

---

## Dirección inversa (RAG → Pulso) — opcional, mismo ritual

| Señal | Idea para Pulso |
|-------|-----------------|
| Top preguntas en `knowledge-gaps-*.md` | Beat “lo que más preguntan” (sin prometer lo que el bot aún escala) |
| `Gap:` explícito en monografía | Bloque Frontera honesta |
| Tema frío en harvest (0 papers 14d) | Deep-dive manual o bajar prioridad en `watchlist.yml` |

---

## Referencias

- Política Pulso: `EDITORIAL.md`
- Compliance producto: `design/handoff/COMPLIANCE.md`
- Marco evidencia RAG: `rag-bot/knowledge_base/longevity/00_MARCO_SSOT_EVIDENCIA_Y_COMPLIANCE.md`
- Knowledge loop Q&A: `rag-bot/README.md` (sección Knowledge Loop)