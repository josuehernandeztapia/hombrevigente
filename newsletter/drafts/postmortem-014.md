# Post-mortem Pulso — 2026-09-014

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-09-03T17:40:23Z
- **Issue:** `newsletter/issues/2026-09-014.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº014 — El momento exacto para bajar tu LDL (s
- TLDR presente
- Fuente OK: Accionable — Bajar el LDL *antes* de la angioplast
- Fuente OK: Frontera — Limpiar células senescentes protege el 
- Fuente OK: AI × Longevity — Un agente de IA diseña y ejecuta 
- Fuente OK: Contexto / Voz — "Oxygenaging": un nuevo marco fis
- Tabla bridge: 0×A, 0×C, 0 vacías
- Render OK → `newsletter/runs/2026-09-014-preview.html`
- Social pack: 4 archivos en `social/014/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Ningún bridge tipo A — RAG no se enriquecerá
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-09-014.md: 0 bridge(s) tipo A
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
