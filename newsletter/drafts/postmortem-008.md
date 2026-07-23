# Post-mortem Pulso — 2026-07-008

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-07-23T15:57:56Z
- **Issue:** `newsletter/issues/2026-07-008.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº008 — La IA que hace ciencia sola (y lo que 
- TLDR presente
- Fuente OK: Accionable — Dapagliflozin y el perfil de VLDL: lo
- Fuente OK: Frontera — El canal de cloruro lisosomal que contr
- Fuente OK: AI × Longevity — Un agente de IA hace investigació
- Fuente OK: Contexto / Voz — La paradoja PERK: cuando el estré
- Render OK → `newsletter/runs/2026-07-008-preview.html`
- Social pack: 4 archivos en `social/008/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Sin tabla Editorial bridge
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-07-008.md: 0 bridge(s) tipo A
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
