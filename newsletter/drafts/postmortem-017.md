# Post-mortem Pulso — 2026-10-017

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-10-01T19:21:23Z
- **Issue:** `newsletter/issues/2026-10-017.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº017 — Una imagen en 3D predice la edad de tu
- TLDR presente
- Fuente OK: Accionable — Tu LDL puede estar "bien" mientras tu
- Fuente OK: Frontera — La autofagia no envejece igual en hombr
- Fuente OK: AI × Longevity — Una red neuronal "lee" la edad bi
- Fuente OK: Contexto / Voz — Lo que la medicina tradicional ch
- Tabla bridge: 0×A, 0×C, 0 vacías
- Render OK → `newsletter/runs/2026-10-017-preview.html`
- Social pack: 4 archivos en `social/017/`
- Bridge export dry-run OK (ver salida abajo)
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Ningún bridge tipo A — RAG no se enriquecerá

## Salida bridge export (dry-run)
```
2026-10-017.md: 1 bridge(s) tipo A
[
  {
    "id": "bridge-2026-10-017-",
    "issue_path": "newsletter/issues/2026-10-017.md",
    "numero": "017",
    "fecha": "2026-10-01",
    "bloque": "",
    "bridge_type": "A",
    "topic_ssot": "lipidos_apob",
    "monografia": "25_biomarcadores_panel_optimizacion.md",
    "pmid_doi": "42801018 / 10.1007/s40200-026-02091-3",
    "evidence_level": "E3",
    "title": "Tu LDL puede estar \"bien\" mientras tu riesgo real se esconde en otro número",
    "fuente": "J Diabetes Metab Disord 2026, PMID 42801018.",
    "summary": "Esto no cambia la jerarquía de evidencia sobre lípidos y riesgo cardiovascular — la refuerza. Lo que sí cambia es tu checklist de laboratorio: si tu LDL sale \"normal\" pero tienes marcadores de resistencia a la insulina, triglicéridos altos o historia familiar, **pide que incluyan ApoB** en tu panel. Es un dato de bajo costo, alta disponibilidad, y de los de mayor evidencia acumulada para afinar decisiones junto con tu médico — no para autodiagnosticarte.",
    "exported_at": "2026-10-01T19:21:23.780182+00:00",
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
