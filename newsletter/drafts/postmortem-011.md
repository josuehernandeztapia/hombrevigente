# Post-mortem Pulso — 2026-08-011

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-08-13T15:01:57Z
- **Issue:** `newsletter/issues/2026-08-011.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº011 — El problema neuroquirúrgico #1 en homb
- TLDR presente
- Fuente OK: Accionable — El hematoma subdural crónico, bajo la
- Fuente OK: Frontera — Cuando la autofagia se apaga: por qué e
- Fuente OK: AI × Longevity — La IA que caza dianas farmacológi
- Fuente OK: Contexto / Voz — El eje óxido nítrico–cGMP reorden
- Tabla bridge: 0×A, 0×C, 0 vacías
- Render OK → `newsletter/runs/2026-08-011-preview.html`
- Social pack: 4 archivos en `social/011/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Ningún bridge tipo A — RAG no se enriquecerá
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-08-011.md: 0 bridge(s) tipo A
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
