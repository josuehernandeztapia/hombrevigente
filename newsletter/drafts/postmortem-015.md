# Post-mortem Pulso — 2026-09-015

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-09-17T18:02:27Z
- **Issue:** `newsletter/issues/2026-09-015.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº015 — La pastilla que quiere reemplazar la i
- TLDR presente
- Fuente OK: Accionable — La píldora que podría reemplazar la i
- Fuente OK: Frontera — Tu sangre podría estar contando la hist
- Fuente OK: AI × Longevity — La IA entra al diagnóstico de enf
- Fuente OK: Contexto — El estrés laboral se formaliza como var
- Tabla bridge: 2×A, 2×C, 0 vacías
- Render OK → `newsletter/runs/2026-09-015-preview.html`
- Social pack: 4 archivos en `social/015/`
- Bridge export dry-run OK (ver salida abajo)
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- _(ninguno)_

## Salida bridge export (dry-run)
```
2026-09-015.md: 2 bridge(s) tipo A
[
  {
    "id": "bridge-2026-09-015-accionable",
    "issue_path": "newsletter/issues/2026-09-015.md",
    "numero": "015",
    "fecha": "2026-09-17",
    "bloque": "Accionable",
    "bridge_type": "A",
    "topic_ssot": "lipidos_apob",
    "monografia": "25_biomarcadores_panel_optimizacion.md",
    "pmid_doi": "14656566.2026.2732054",
    "evidence_level": "E3",
    "title": "La píldora que podría reemplazar la inyección de PCSK9",
    "fuente": "Expert Opinion on Pharmacotherapy 2026, PMID 42709041.",
    "summary": "Que exista una versión oral en evaluación no cambia lo que puedes hacer hoy: tu **ApoB** sigue siendo, con la evidencia actual, uno de los marcadores más sólidos de riesgo cardiovascular —más informativo que el LDL-C solo en muchos perfiles. Mídelo, conoce tu número y trabájalo con alimentación, actividad física y, si tu médico lo indica, con terapia farmacológica ya disponible. La vía oral, si se confirma, sería una opción de **adherencia**, no una promesa de resultado distinto.",
    "exported_at": "2026-09-17T18:02:27.533169+00:00",
    "status": "pending"
  },
  {
    "id": "bridge-2026-09-015-ai-longevity",
    "issue_path": "newsletter/issues/2026-09-015.md",
    "numero": "015",
    "fecha": "2026-09-17",
    "bloque": "AI × Longevity",
    "bridge_type": "A",
    "topic_ssot": "descubrimiento_farmacos_ia",
    "monografia": "01_hallmarks_envejecimiento.md",
    "pmid_doi": "cells15171614",
    "evidence_level": "E3",
    "title": "La IA entra al diagnóstico de enfermedades que antes tardaban años",
    "fuente": "Cells 2026, PMID 42738907.",
    "summary": "Fabry es un caso de nicho, pero la arquitectura importa: cuando la IA logra comprimir años de diagnóstico diferencial en modelos predictivos, ese mismo pipeline eventualmente se dirige hacia diabetes tipo 2, hígado graso y otras condiciones metabólicas comunes. Vale la pena seguir esta capa de IA×biología como radar de hacia dónde va el diagnóstico de precisión, no como herramienta disponible hoy en tu chequeo anual.",
    "exported_at": "2026-09-17T18:02:27.533405+00:00",
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
