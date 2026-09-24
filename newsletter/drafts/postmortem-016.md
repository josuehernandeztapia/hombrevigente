# Post-mortem Pulso — 2026-09-016

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-09-24T18:20:56Z
- **Issue:** `newsletter/issues/2026-09-016.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Cero resultados (todavía): así se diseñó el ensayo que pondr
- TLDR presente
- Fuente OK: Accionable — El ensayo que aún no tiene resultados
- Fuente OK: Frontera — Neuronas que envejecen antes de tiempo:
- Fuente OK: AI × Longevity — Organoides cerebrales: la platafo
- Fuente OK: Contexto / Voz — El estrés laboral entra al mapa d
- Tabla bridge: 3×A, 1×C, 0 vacías
- Render OK → `newsletter/runs/2026-09-016-preview.html`
- Social pack: 4 archivos en `social/016/`
- Bridge export dry-run OK (ver salida abajo)
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- _(ninguno)_

## Salida bridge export (dry-run)
```
2026-09-016.md: 3 bridge(s) tipo A
[
  {
    "id": "bridge-2026-09-016-accionable",
    "issue_path": "newsletter/issues/2026-09-016.md",
    "numero": "016",
    "fecha": "2026-09-24",
    "bloque": "Accionable",
    "bridge_type": "A",
    "topic_ssot": "lipidos_apob",
    "monografia": "25_biomarcadores_panel_optimizacion.md",
    "pmid_doi": "bmjopen-2026-124025",
    "evidence_level": "E3",
    "title": "El ensayo que aún no tiene resultados (pero sí un diseño riguroso)",
    "fuente": "BMJ Open 2026, PMID 42760081.",
    "summary": "Vale la pena mencionarlo justo porque *no* promete nada todavía. El ángulo real para ti hoy: si tienes un perfil metabólico con resistencia a la insulina, tu **ApoB** y tu perfil lipídico siguen siendo los marcadores con más evidencia acumulada para gestionar riesgo cardiovascular — con o sin este ensayo. El omega-3 como adyuvante metabólico está **en investigación**; no sustituye el trabajo de base (composición corporal, sensibilidad a la insulina, lo que tu médico indique).",
    "exported_at": "2026-09-24T18:20:56.603988+00:00",
    "status": "pending"
  },
  {
    "id": "bridge-2026-09-016-frontera",
    "issue_path": "newsletter/issues/2026-09-016.md",
    "numero": "016",
    "fecha": "2026-09-24",
    "bloque": "Frontera",
    "bridge_type": "A",
    "topic_ssot": "senescencia_senoliticos",
    "monografia": "05_senescencia_senoliticos.md",
    "pmid_doi": "j.nbd.2026.107610",
    "evidence_level": "E2",
    "title": "Neuronas que envejecen antes de tiempo: senescencia como blanco temprano en ELA",
    "fuente": "Neurobiol Dis 2026, PMID 42759848.",
    "summary": "El campo senolítico sigue expandiéndose más allá de lo \"clásico\" (piel, articulaciones, metabolismo) hacia neurodegeneración. Es frontera pura: modelo animal, mutación específica, sin traducción clínica todavía. Lo que sí conecta con lo que ya sabemos: la senescencia celular es un mecanismo transversal del envejecimiento — motivo por el cual monitoreamos este espacio, no para actuar hoy sobre ELA, sino para entender hacia dónde va la ciencia senolítica.",
    "exported_at": "2026-09-24T18:20:56.604145+00:00",
    "status": "pending"
  },
  {
    "id": "bridge-2026-09-016-ai-longevity",
    "issue_path": "newsletter/issues/2026-09-016.md",
    "numero": "016",
    "fecha": "2026-09-24",
    "bloque": "AI × Longevity",
    "bridge_type": "A",
    "topic_ssot": "descubrimiento_farmacos_ia",
    "monografia": "01_hallmarks_envejecimiento.md",
    "pmid_doi": "s10571-026-01808-5",
    "evidence_level": "E3",
    "title": "Organoides cerebrales: la plataforma que está redefiniendo cómo se estudia el cerebro humano",
    "fuente": "Cell Mol Neurobiol 2026, PMID 42758369.",
    "summary": "El valor no está en el organoide aislado, sino en lo que habilita: menos dependencia de modelos animales, más traducción a biología humana real, y datos de mayor resolución para alimentar pipelines de IA en descubrimiento de fármacos. Es infraestructura, no un tratamiento — pero infraestructura es exactamente lo que acelera (o frena) todo lo demás en este espacio.",
    "exported_at": "2026-09-24T18:20:56.604288+00:00",
    "status": "pending"
  }
]
```

## Próximo finetune

1. Corrige warnings arriba en el issue.
2. Vuelve a correr: `python newsletter/rehearsal.py <issue>`
3. Cuando post-mortem limpio → merge a `main` (envío real) o dispatch con `PULSO_MODE=production`.

## Modos

| Modo | Envío email | Redes auto | Uso |
|------|-------------|------------|-----|
| `shadow` (default rehearsal) | No | No | Validar flujo + post-mortem |
| `production` | Sí (merge main + secrets) | Sí (carril auto) | Operación real |
