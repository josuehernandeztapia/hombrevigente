# Post-mortem Pulso — 2026-08-010

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-08-09T04:53:29Z
- **Issue:** `newsletter/issues/2026-08-010.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº010 — La IA que lee tu sistema inmune célula
- TLDR presente
- Fuente OK: Accionable — Los inhibidores de PCSK9 y la inflama
- Fuente OK: Frontera — Autofagia, TFEB y el riñón que envejece
- Fuente OK: AI × Longevidad — IDEAL-Age: un reloj inmunológico
- Fuente OK: Contexto / Voz — El eje NO-cGMP: la vasculatura qu
- Render OK → `newsletter/runs/2026-08-010-preview.html`
- Social pack: 4 archivos en `social/010/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Sin tabla Editorial bridge
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-08-010.md: 0 bridge(s) tipo A
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
