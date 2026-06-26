# Post-mortem Pulso — 2026-06-004

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-06-26T23:14:13Z
- **Issue:** `newsletter/issues/2026-06-004.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº004 — Qué pasa en el cuerpo cuando eliminas 
- TLDR presente
- Fuente OK: Accionable — Inhibidores de PCSK9 en trasplante ca
- Fuente OK: Frontera — Senolíticos en ratones viejos: inmunida
- Fuente OK: AI × Longevity — IA modela la bifurcación del dest
- Fuente OK: Contexto / Voz — Satisfacción con la vida como dia
- Render OK → `newsletter/runs/2026-06-004-preview.html`
- Social pack: 4 archivos en `social/004/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Sin tabla Editorial bridge
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-06-004.md: 0 bridge(s) tipo A
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
