# Post-mortem Pulso — 2026-10-018

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-10-15T18:07:19Z
- **Issue:** `newsletter/issues/2026-10-018.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº018 — Tu autofagia se rompe distinto según t
- TLDR presente
- Fuente OK: Accionable — La autofagia se descompone distinto e
- Fuente OK: Frontera — Células T diseñadas que cazan células s
- Fuente OK: AI × Longevity — La IA ya puede leer la edad de tu
- Fuente OK: Contexto / Voz — Mapeando dos décadas de investiga
- Tabla bridge: 0×A, 0×C, 0 vacías
- Render OK → `newsletter/runs/2026-10-018-preview.html`
- Social pack: 4 archivos en `social/018/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Ningún bridge tipo A — RAG no se enriquecerá
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-10-018.md: 0 bridge(s) tipo A
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
