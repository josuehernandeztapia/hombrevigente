# Post-mortem Pulso — 2026-07-006

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-07-09T16:30:45Z
- **Issue:** `newsletter/issues/2026-07-006.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº006 — El fármaco que baja el colesterol sin 
- TLDR presente
- Fuente OK: Accionable — Sin estatinas no significa sin opcion
- Fuente OK: Frontera — Tu oído interno como espejo del envejec
- Fuente OK: AI × Longevity — Vesículas extracelulares diseñada
- Fuente OK: Contexto / Voz — Angiopatía amiloide cerebral: el 
- Render OK → `newsletter/runs/2026-07-006-preview.html`
- Social pack: 4 archivos en `social/006/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Sin tabla Editorial bridge
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-07-006.md: 0 bridge(s) tipo A
[]
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
