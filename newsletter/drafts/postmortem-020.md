# Post-mortem Pulso — 2026-11-020

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-11-05T20:59:18Z
- **Issue:** `newsletter/issues/2026-11-020.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº020 — Reprogramar neuronas con 4 factores re
- TLDR presente
- Fuente OK: Accionable — La píldora oral que le pisa los talon
- Fuente OK: Frontera — Reprogramar neuronas con 4 factores pro
- Fuente OK: AI × Longevity — Los organoides (y la IA que los l
- Fuente OK: Contexto / Voz — El diálogo molecular que conecta 
- Tabla bridge: 3×A, 1×C, 0 vacías
- Render OK → `newsletter/runs/2026-11-020-preview.html`
- Social pack: 4 archivos en `social/020/`
- Bridge export dry-run OK (ver salida abajo)
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- _(ninguno)_

## Salida bridge export (dry-run)
```
2026-11-020.md: 3 bridge(s) tipo A
[
  {
    "id": "bridge-2026-11-020-accionable",
    "issue_path": "newsletter/issues/2026-11-020.md",
    "numero": "020",
    "fecha": "2026-11-05",
    "bloque": "Accionable",
    "bridge_type": "A",
    "topic_ssot": "lipidos_apob",
    "monografia": "25_biomarcadores_panel_optimizacion.md",
    "pmid_doi": "edm2.70358",
    "evidence_level": "E3",
    "title": "La píldora oral que le pisa los talones al PCSK9 inyectable",
    "fuente": "Endocrinol Diabetes Metab 2026, PMID 42867105.",
    "summary": "Es evidencia humana consolidada (meta-análisis), pero el fármaco sigue en desarrollo y no está disponible para uso general. **Lo que SÍ puedes mover hoy:** conoce tu **LDL-C y, si es posible, tu ApoB** — siguen siendo de los marcadores con mayor respaldo para riesgo cardiovascular. Trabájalos con alimentación, actividad física y, si tu médico lo indica, terapia farmacológica ya aprobada.",
    "exported_at": "2026-11-05T20:59:18.675494+00:00",
    "status": "pending"
  },
  {
    "id": "bridge-2026-11-020-frontera",
    "issue_path": "newsletter/issues/2026-11-020.md",
    "numero": "020",
    "fecha": "2026-11-05",
    "bloque": "Frontera",
    "bridge_type": "A",
    "topic_ssot": "epigenetica_relojes_reprogramacion",
    "monografia": "07_reprogramacion_celular.md",
    "pmid_doi": "acel.70776",
    "evidence_level": "E2",
    "title": "Reprogramar neuronas con 4 factores protegió al cerebro envejecido de la falta de oxígeno",
    "fuente": "Aging Cell 2026, PMID 42924487.",
    "summary": "Esto es **preclínico, en modelo murino** — frontera pura, no una intervención disponible ni cercana para humanos. Lo relevante es la dirección: la reprogramación epigenética se está probando como posible estrategia de protección tisular ante eventos vasculares agudos, un territorio que vale la pena seguir, no replicar.",
    "exported_at": "2026-11-05T20:59:18.675617+00:00",
    "status": "pending"
  },
  {
    "id": "bridge-2026-11-020-ai-longevity",
    "issue_path": "newsletter/issues/2026-11-020.md",
    "numero": "020",
    "fecha": "2026-11-05",
    "bloque": "AI × Longevity",
    "bridge_type": "A",
    "topic_ssot": "descubrimiento_farmacos_ia",
    "monografia": "01_hallmarks_envejecimiento.md",
    "pmid_doi": "j.stem.2026.10.003",
    "evidence_level": "E3",
    "title": "Los organoides (y la IA que los lee) empiezan a reemplazar al ratón de laboratorio",
    "fuente": "Cell Stem Cell 2026, PMID 42950820.",
    "summary": "Es infraestructura de descubrimiento, no un tratamiento. Pero es la razón por la que el \"descubrimiento de fármacos con IA\" deja de ser solo cómputo y empieza a tener sustrato biológico real detrás. Vale la pena seguir qué compañías logran validar estos modelos con datos humanos posteriores.",
    "exported_at": "2026-11-05T20:59:18.675726+00:00",
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
