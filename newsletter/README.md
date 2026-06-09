# Pulso Vigente — newsletter + redes

Newsletter de longevidad gestionada. Contenido en `issues/`, email vía **Resend**, redes orgánicas vía **Ayrshare** (carril auto). GitHub Actions orquesta; humano aprueba lo que lleva claims de salud.

## Pipeline completo

| Paso | Qué | Workflow / script |
|------|-----|-------------------|
| 1. Candidatos | Europe PMC + `watchlist.yml` | `harvest.py` · `newsletter-draft.yml` (jueves) |
| 2. Redacción auto | IA desde harvest + validación PMID | `draft_compose.py` (mismo workflow) |
| 2b. Tu revisión | Lees, dialogas, pides cambios | PR `newsletter/draft-NNN` · `rehearsal.py` |
| 3. Assets | Hero IA + social pack | `newsletter-assets.yml` (manual) · `image.py` · `social.py` |
| 4. Ensayo shadow | Pipeline completo sin publicar + post-mortem | `rehearsal.py` · `newsletter-rehearsal.yml` |
| 5. Email QA | Preview local | `render.py` → `newsletter/preview.html` |
| 6. Envío | Merge a `main` o dispatch | `newsletter-send.yml` · `send.py` |
| 7. Redes auto | Memes/frases sin claims | `social-auto.yml` (miércoles) · `publish.py` · `social/queue/` |
| 8. Bridge SSOT | Claims verificados → monografías RAG | `bridge_export.py` · `newsletter-editorial-bridge.yml` · `BRIDGE.md` |

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

## Shadow vs production

| Modo | Cómo | Efecto |
|------|------|--------|
| **Shadow** | `python newsletter/rehearsal.py <issue>` o Actions → *Newsletter rehearsal* | Corre render + social + bridge dry-run; escribe post-mortem; **no envía** |
| **Production** | Merge issue a `main` + secrets Resend/Ayrshare | Email + bridge CI reales |

El humano **no desaparece**: lees el borrador auto, dialogas cambios; el merge a `main` sigue siendo tu OK para enviar.

**Fase A (ahora):** jueves auto → **borrador a tu correo** → respondes `OK` en issue GitHub (o correcciones) → envío Plus automático.

### Aprobación por correo

1. Recibes `[BORRADOR Pulso NºNNN]` en `NEWSLETTER_APPROVAL_TO`.
2. Llega issue GitHub **Aprobar Pulso NºNNN** (notificación por email).
3. Responde al hilo con `OK` → merge PR + envío Plus.
4. O escribe correcciones → IA ajusta + nuevo borrador a tu correo → repites hasta `OK`.

Configura var `NEWSLETTER_APPROVAL_TO` (tu inbox). El merge a `main` sin `OK` **no envía** (gate `approved: true`).

## Probar local

```bash
pip install -r newsletter/requirements.txt

# Compose local (fallback sin API)
python newsletter/draft_compose.py \
  --candidates newsletter/drafts/candidates-2026-06-08.md \
  --out newsletter/issues/2026-06-002.md \
  --numero 002 --fecha 2026-06-12 --fallback-only

# Ensayo completo (post-mortem en newsletter/runs/)
python newsletter/rehearsal.py newsletter/issues/2026-06-001.md

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

`BRIDGE.md` — al cerrar un número, llena la tabla *Editorial bridge*; `bridge_export.py` exporta tipo **A** a `rag-bot/data/editorial-bridge-pending.json` y CI abre PR a monografías. Las preguntas de usuarios van por el **knowledge loop** del `rag-bot/`, no por Pulso.

```bash
python newsletter/bridge_export.py --issue newsletter/issues/2026-06-001.md
```

## Pre-merge

Ver `QA_CHECKLIST.md`. Importante: `issues/2026-06-001.md` es muestra; no merges a `main` con intención de enviar hasta QA de fuentes y secrets configurados.