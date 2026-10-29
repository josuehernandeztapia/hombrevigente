# Post-mortem Pulso — 2026-10-020

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-10-29T19:28:40Z
- **Issue:** `newsletter/issues/2026-10-020.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº020 — La autofagia que frena la senescencia 
- TLDR presente
- Fuente OK: Accionable — Tu LDL-C puede estar "normal" y tu ri
- Fuente OK: Frontera — Una vía de "limpieza celular" frena la 
- Fuente OK: AI × Longevity — Un circuito de splicing redefine 
- Fuente OK: Contexto / Voz — El envejecimiento vascular cerebr
- Tabla bridge: 0×A, 0×C, 0 vacías
- Render OK → `newsletter/runs/2026-10-020-preview.html`
- Social pack: 4 archivos en `social/020/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Ningún bridge tipo A — RAG no se enriquecerá
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-10-020.md: 0 bridge(s) tipo A
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
