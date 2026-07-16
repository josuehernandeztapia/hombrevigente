# Post-mortem Pulso — 2026-07-007

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-07-16T15:42:16Z
- **Issue:** `newsletter/issues/2026-07-007.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº007 — Tu músculo envejece antes que tu calen
- TLDR presente
- Fuente OK: Accionable — El colesterol "malo" tiene un nuevo m
- Fuente OK: Frontera — Senescencia celular: el mapa molecular 
- Fuente OK: AI × Longevity — Una IA hace ciencia biomédica aut
- Fuente OK: Contexto / Voz — Tu músculo envejece antes que tu 
- Render OK → `newsletter/runs/2026-07-007-preview.html`
- Social pack: 4 archivos en `social/007/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Sin tabla Editorial bridge
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-07-007.md: 0 bridge(s) tipo A
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
