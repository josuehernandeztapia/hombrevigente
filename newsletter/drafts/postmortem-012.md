# Post-mortem Pulso — 2026-08-012

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-08-20T14:40:25Z
- **Issue:** `newsletter/issues/2026-08-012.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº012 — La simulación que compara 2 caminos pa
- TLDR presente
- Fuente OK: Accionable — Un modelo español pone precio a no ll
- Fuente OK: Frontera — El hueso que se cansa: senescencia de c
- Fuente OK: AI × Longevity — La IA que busca fármacos contra l
- Fuente OK: Contexto / Voz — Cuando el marco geroscience mira 
- Tabla bridge: 0×A, 0×C, 0 vacías
- Render OK → `newsletter/runs/2026-08-012-preview.html`
- Social pack: 4 archivos en `social/012/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Ningún bridge tipo A — RAG no se enriquecerá
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-08-012.md: 0 bridge(s) tipo A
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
