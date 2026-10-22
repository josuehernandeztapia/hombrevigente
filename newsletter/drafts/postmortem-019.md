# Post-mortem Pulso — 2026-10-019

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-10-22T18:25:46Z
- **Issue:** `newsletter/issues/2026-10-019.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº019 — La IA ya evalúa cientos de combinacion
- TLDR presente
- Fuente OK: Accionable — Las terapias "una sola inyección" con
- Fuente OK: Frontera — La autofagia mediada por chaperonas pod
- Fuente OK: AI × Longevity — Modelos de IA evalúan cientos de 
- Fuente OK: Contexto / Voz — El sueño fragmentado aparece liga
- Tabla bridge: 2×A, 2×C, 0 vacías
- Render OK → `newsletter/runs/2026-10-019-preview.html`
- Social pack: 4 archivos en `social/019/`
- Bridge export dry-run OK (ver salida abajo)
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- _(ninguno)_

## Salida bridge export (dry-run)
```
2026-10-019.md: 2 bridge(s) tipo A
[
  {
    "id": "bridge-2026-10-019-accionable",
    "issue_path": "newsletter/issues/2026-10-019.md",
    "numero": "019",
    "fecha": "2026-10-22",
    "bloque": "Accionable",
    "bridge_type": "A",
    "topic_ssot": "lipidos_apob",
    "monografia": "25_biomarcadores_panel_optimizacion.md",
    "pmid_doi": "s11883-026-01470-8",
    "evidence_level": "E3",
    "title": "Las terapias \"una sola inyección\" contra PCSK9 llegan a revisión formal",
    "fuente": "Curr Atheroscler Rep 2026, PMID 42878939.",
    "summary": "Estas terapias siguen en investigación y, cuando lleguen, serán para perfiles de riesgo específicos bajo supervisión médica — no un reemplazo del trabajo de base. **Lo que SÍ puedes mover hoy:** tu **ApoB** sigue siendo uno de los marcadores con mayor evidencia para riesgo cardiovascular. Pídelo en tu próximo panel de laboratorio, conoce tu número y trabájalo con alimentación, actividad física y, si tu médico lo indica, tratamiento establecido.",
    "exported_at": "2026-10-22T18:25:46.541994+00:00",
    "status": "pending"
  },
  {
    "id": "bridge-2026-10-019-ai-longevity",
    "issue_path": "newsletter/issues/2026-10-019.md",
    "numero": "019",
    "fecha": "2026-10-22",
    "bloque": "AI × Longevity",
    "bridge_type": "A",
    "topic_ssot": "descubrimiento_farmacos_ia",
    "monografia": "01_hallmarks_envejecimiento.md",
    "pmid_doi": "elife.110475",
    "evidence_level": "E3",
    "title": "Modelos de IA evalúan cientos de combinaciones fármaco-proteína para acelerar el descubrimiento",
    "fuente": "eLife 2026, PMID 42862171.",
    "summary": "Este tipo de evaluación rigurosa es exactamente lo que separa el hype de la sustancia en IA×biología. Compañías como Insilico Medicine o Isomorphic Labs dependen de que estos modelos de co-folding funcionen de verdad para acortar los tiempos de descubrimiento de fármacos, incluidos los relevantes para longevidad. Nada accionable para ti hoy directamente — pero es el tipo de infraestructura que, si madura, podría acelerar la llegada de las terapias que cubrimos en la sección Accionable.",
    "exported_at": "2026-10-22T18:25:46.542243+00:00",
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
