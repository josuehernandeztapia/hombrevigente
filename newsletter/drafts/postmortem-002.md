# Post-mortem Pulso — 2026-06-002

- **Modo:** `shadow` (sin publicación real)
- **Generado:** 2026-06-09T03:42:10Z
- **Issue:** `newsletter/issues/2026-06-002.md`

## Checklist automático

### ✅ Pass
- RAG patch dry-run: nada pendiente o ya aplicado
- Send: omitido (PULSO_MODE=shadow)

### ⚠️ Revisar (post-mortem humano)
- Parse issue: sin frontmatter YAML
- Render falló: Traceback (most recent call last):
  File "/home/runner/work/hombrevigente/hombrevigente/newsletter/render.py", line 41, in <module>
    out = render(Path(sys.argv[1]))
          ^^^^^^^^^^^^^^^^^^^^^
- Social pack: Social pack escrito en /home/runner/work/hombrevigente/hombrevigente/newsletter/social · 4 piezas
- Bridge export: Traceback (most recent call last):
  File "/home/runner/work/hombrevigente/hombrevigente/newsletter/bridge_export.py", line 275, in <module>
    main(

## Salida bridge export (dry-run)
```
Traceback (most recent call last):
  File "/home/runner/work/hombrevigente/hombrevigente/newsletter/bridge_export.py", line 275, in <module>
    main()
  File "/home/runner/work/hombrevigente/hombrevigente/newsletter/bridge_export.py", line 255, in main
    found = export_issue(p)
            ^^^^^^^^^^^^^^^
  File "/home/runner/work/hombrevigente/hombrevigente/newsletter/bridge_export.py", line 224, in export_issue
    meta, body = parse_issue(path)
                 ^^^^^^^^^^^^^^^^^
  File "/home/runner/work/hombrevigente/hombrevigente/newsletter/bridge_export.py", line 61, in parse_issue
    raise ValueError(f"{path} no tiene frontmatter YAML (---).")
ValueError: /home/runner/work/hombrevigente/hombrevigente/newsletter/issues/2026-06-002.md no tiene frontmatter YAML (---).
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
