# QA Checklist — Newsletter + Social (antes de mergear `feat/newsletter`)

Revisar en orden. No mergees a `main` hasta que A–G estén en verde.

---

## ⚠️ 0. Riesgos de "auto-disparo" — LÉELO PRIMERO
Dos workflows pueden **enviar/publicar solos** al mergear o por calendario. Antes del merge:

- [ ] **`newsletter-send.yml` se dispara al hacer push de `newsletter/issues/**` a `main`.** Al mergear el scaffold (que incluye `issues/2026-06-001.md`) **intentará enviar el número 001** si `RESEND_API_KEY` está configurado.
  - Mitigación: **NO configures los secrets de Resend hasta que quieras enviar de verdad** (sin key el job termina en verde y omite envío), **o** mueve `2026-06-001.md` fuera de `issues/` (es una muestra) hasta tener un número real QA'd.
- [ ] **`social-auto.yml` corre los miércoles** y publicaría el post de `social/queue/` si `AYRSHARE_API_KEY` está configurado. Confirma que el ejemplo `frase-vigente` es intencional o muévelo/edítalo. Sin key, no postea.

---

## A. Estructura y código
- [ ] Existen: `newsletter/{EDITORIAL.md,watchlist.yml,harvest.py,render.py,send.py,social.py,image.py,publish.py,requirements.txt,README.md,templates/email.html}`.
- [ ] Workflows: `.github/workflows/{newsletter-send,newsletter-draft,newsletter-assets,social-auto}.yml`.
- [ ] `pip install -r newsletter/requirements.txt` sin errores.
- [ ] `python newsletter/render.py newsletter/issues/2026-06-001.md` → genera `newsletter/preview.html`; ábrelo: marca correcta, disclaimer y unsubscribe presentes.
- [ ] `python newsletter/social.py newsletter/issues/2026-06-001.md` → crea `social/001/` con 4 piezas.
- [ ] `DRY_RUN=1 python newsletter/publish.py newsletter/social/queue/2026-06-11-frase-vigente.md` → pasa.
- [ ] `newsletter/drafts/` vacío o solo candidatos reales del harvest (no commitear stubs vacíos).

## B. Compliance (lo que protege la marca)
- [ ] El número 001 **no** usa "diagnóstico/cura/trata/predictivo/garantiza"; usa "optimización / se asocia / se estudia".
- [ ] Cada item de ciencia tiene **fuente primaria** (PMID/DOI/registro), no solo un PR.
- [ ] El bloque "AI × Longevity" sigue como placeholder o ya tiene item **verificado** (no claim sin fuente).
- [ ] Disclaimer presente en el footer del email y al pie del número.
- [ ] Claim-guard probado: un post con "cura/100%" es **rechazado** (`DRY_RUN=1 publish.py` sobre un post de prueba).
- [ ] Imágenes (si las hay): abstractas, sin texto, sin personas-como-pacientes, sin antes/después.

## C. Secrets y variables (GitHub → Settings → Actions)
- [ ] Secret `RESEND_API_KEY` (solo cuando vayan a enviar de verdad — ver §0).
- [ ] Vars `RESEND_AUDIENCE_PLUS`, `RESEND_AUDIENCE_FREE`, `NEWSLETTER_FROM`.
- [ ] Secret `OPENAI_API_KEY` (opcional — solo para hero IA).
- [ ] Secret `AYRSHARE_API_KEY` (solo cuando quieran auto-postear).
- [ ] Ninguna key commiteada en el repo (revisar diff).

## D. Resend
- [ ] Dominio `hombrevigente.com` verificado (SPF/DKIM/DMARC en DNS).
- [ ] Envío desde subdominio `updates.hombrevigente.com`; reply-to `contacto@hombrevigente.com`.
- [ ] Audiences `plus` y `free` creadas; sus IDs en las vars.
- [ ] Prueba real controlada: `DRY_RUN=1 python newsletter/send.py …` crea el broadcast sin enviar (con key de prueba).

## E. Ayrshare
- [ ] Cuenta creada; IG/FB/X/TikTok/LinkedIn conectados en el panel.
- [ ] `AYRSHARE_API_KEY` en Secrets.
- [ ] Prueba real controlada: un post auto a **una** red primero, no a todas.
- [ ] `image_url` (si se usa) es una URL **pública** (raw.githubusercontent o bucket).

## F. Workflows
- [ ] `newsletter-draft.yml`: corre `harvest.py` y abre PR (no envía). Cron jueves OK.
- [ ] `newsletter-send.yml`: dispara en push de issues + dispatch. Sin `RESEND_API_KEY` omite envío (`exit 0`).
- [ ] `newsletter-assets.yml`: solo manual; genera social + hero, commitea a la rama.
- [ ] `social-auto.yml`: cron miércoles; sin `AYRSHARE_API_KEY` no postea (`exit 0`); commitea marcadores `.posted`.
- [ ] `permissions: contents: write` (y `pull-requests: write` en draft) presentes donde hace falta.

## G. Git (pre-merge)
- [ ] Commit **solo** del newsletter (NO `git add -A` — hay WIP del peer):
  ```
  git add newsletter/ .github/workflows/newsletter-send.yml \
          .github/workflows/newsletter-draft.yml .github/workflows/newsletter-assets.yml \
          .github/workflows/social-auto.yml .gitignore
  ```
- [ ] PR abierto, CI verde, revisado.
- [ ] Decisión consciente sobre §0 antes de mergear.

---
*Regla de oro: en la duda, no envíes/publiques. Fuente primaria o no entra. El claim-guard y el `lane: gated` existen para salvarte — no los desactives.*
