# Pulso Vigente — newsletter + redes

Newsletter de longevidad gestionada. Contenido en `issues/`, email vía **Resend**, redes orgánicas vía **Ayrshare** (carril auto). GitHub Actions orquesta; humano aprueba lo que lleva claims de salud.

## Pipeline completo

| Paso | Qué | Workflow / script |
|------|-----|-------------------|
| 1. Candidatos | Europe PMC + `watchlist.yml` | `harvest.py` · `newsletter-draft.yml` (jueves, abre PR) |
| 2. Redacción | Tú verificas fuentes (`EDITORIAL.md`) | `issues/YYYY-MM-NNN.md` |
| 3. Assets | Hero IA + social pack | `newsletter-assets.yml` (manual) · `image.py` · `social.py` |
| 4. Email QA | Preview local | `render.py` → `newsletter/preview.html` |
| 5. Envío | Merge a `main` o dispatch | `newsletter-send.yml` · `send.py` |
| 6. Redes auto | Memes/frases sin claims | `social-auto.yml` (miércoles) · `publish.py` · `social/queue/` |
| 7. Bridge SSOT | Claims verificados → monografías RAG | Manual · `BRIDGE.md` (al cerrar el número; Q&A aparte) |

## Dos carriles (compliance)

- **`lane: auto`** — `social/queue/`. Bajo riesgo, sin claims. Se publica solo (claim-guard + `publish.py`).
- **`lane: gated`** — Números de Pulso + piezas con ciencia. Tu aprobación; social pack en `social/<numero>/` para copiar/programar.

Regla: ¿hace afirmación de salud? → gated. Si no → puede ser auto.

## Setup (dueño — una vez)

### Resend (email)
1. Dominio `hombrevigente.com` verificado (SPF/DKIM/DMARC). From: `updates.hombrevigente.com`, reply-to: `contacto@hombrevigente.com`.
2. Audiences `plus` y `free`.
3. GitHub Secrets/vars: `RESEND_API_KEY`, `RESEND_AUDIENCE_PLUS`, `RESEND_AUDIENCE_FREE`, `NEWSLETTER_FROM`.

### Ayrshare (redes orgánicas auto)
1. Cuenta + conectar IG/FB/X/LinkedIn (TikTok si aplica).
2. Secret: `AYRSHARE_API_KEY`.

### OpenAI (opcional — hero IA)
- Secret: `OPENAI_API_KEY`. Sin ella, `image.py` imprime el prompt y sigue.

## Probar local

```bash
pip install -r newsletter/requirements.txt

# QA visual email (sin credenciales)
python newsletter/render.py newsletter/issues/2026-06-001.md
open newsletter/preview.html

# Social pack
python newsletter/social.py newsletter/issues/2026-06-001.md

# Hero IA (degrada sin OPENAI_API_KEY)
python newsletter/image.py newsletter/issues/2026-06-001.md

# Envío (requiere Resend; DRY_RUN crea broadcast sin enviar)
export RESEND_API_KEY="re_xxx"
export NEWSLETTER_FROM="Pulso Vigente <pulso@updates.hombrevigente.com>"
export RESEND_AUDIENCE_PLUS="aud_xxx"
DRY_RUN=1 python newsletter/send.py newsletter/issues/2026-06-001.md

# Post auto (requiere Ayrshare o DRY_RUN=1)
DRY_RUN=1 python newsletter/publish.py newsletter/social/queue/2026-06-11-frase-vigente.md
```

## Reglas editoriales

`EDITORIAL.md` — **fuente primaria verificada o no entra.**

## Bridge editorial (Pulso → SSOT)

`BRIDGE.md` — al cerrar un número, enriquecer monografías RAG (tipo **A**). Las preguntas de usuarios van por el **knowledge loop** del `rag-bot/`, no por Pulso.

## Pre-merge

Ver `QA_CHECKLIST.md`. Importante: `issues/2026-06-001.md` es muestra; no merges a `main` con intención de enviar hasta QA de fuentes y secrets configurados.