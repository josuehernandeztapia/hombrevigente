# Post-mortem Pulso — 2026-08-013

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-08-27T23:41:27Z
- **Issue:** `newsletter/issues/2026-08-013.md`

## Checklist automático

### ✅ Pass
- Frontmatter YAML parseable
- Subject: Pulso Vigente Nº013 — Un agente de IA ya diseña y corre sus 
- TLDR presente
- Fuente OK: Accionable — Lo que confirma (otra vez) el meta-an
- Fuente OK: Frontera — Un mapa teórico conecta el "estrés redu
- Fuente OK: AI × Longevity — Cuando el investigador ya no es (
- Fuente OK: Contexto / Voz — Llevar la "edad biológica" del la
- Tabla bridge: 0×A, 0×C, 0 vacías
- Render OK → `newsletter/runs/2026-08-013-preview.html`
- Social pack: 4 archivos en `social/013/`
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Ningún bridge tipo A — RAG no se enriquecerá
- Bridge export: 0 entradas tipo A

## Salida bridge export (dry-run)
```
2026-08-013.md: 0 bridge(s) tipo A
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
