# Post-mortem Pulso — 2026-07-009

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-07-30T15:54:46Z
- **Issue:** `newsletter/issues/2026-07-009.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº009 — Tu reloj epigenético responde a lo que
- TLDR presente
- Fuente OK: Accionable — Las estatinas y la inflamación sistém
- Fuente OK: Frontera — El interruptor del lisosoma que conecta
- Fuente OK: AI × Longevity — Veinte años de diseño de proteína
- Fuente OK: Contexto / Voz — Medir la edad biológica con lo qu
- Render OK → `newsletter/runs/2026-07-009-preview.html`
- Social pack: 4 archivos en `social/009/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Sin tabla Editorial bridge
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-07-009.md: 0 bridge(s) tipo A
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
