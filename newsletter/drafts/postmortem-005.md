# Post-mortem Pulso — 2026-07-005

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-07-02T16:07:48Z
- **Issue:** `newsletter/issues/2026-07-005.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº005 — Los polifenoles no bajan tu colesterol
- TLDR presente
- Fuente OK: Accionable — Los polifenoles no bajan tu colestero
- Fuente OK: Frontera — Espermidina y hueso: un mecanismo precl
- Fuente OK: AI × Longevidad — La senescencia no es solo villan
- Fuente OK: Contexto / Voz — FAXAge: el ensayo que va a medir 
- Render OK → `newsletter/runs/2026-07-005-preview.html`
- Social pack: 4 archivos en `social/005/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Sin tabla Editorial bridge
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-07-005.md: 0 bridge(s) tipo A
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
