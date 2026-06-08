# Cola de publicación orgánica — carril AUTO

Posts de **bajo riesgo, sin claims de salud** que se autopublican vía Ayrshare en
calendario (`social-auto.yml`), **sin aprobación humana**. Memes, frases, behind-the-scenes,
curaduría, datos curiosos.

## Formato de un post
```
---
lane: auto                       # OBLIGATORIO. Solo 'auto' se autopublica.
platforms: [instagram, facebook, x]   # x|twitter, instagram, facebook, tiktok, linkedin
date: 2026-06-11                 # se publica cuando date <= hoy
image_url: ""                    # URL pública (ej. raw.githubusercontent tras commitear) — opcional
---
Texto del post… #hashtags
```

## Dos cerrojos (no negociables)
1. **`lane: auto`** — cualquier otra cosa (`gated`) NO se autopublica; va a tu aprobación.
2. **Claim-guard** — si el texto contiene lenguaje de salud (cura/trata/previene/diagnostica/
   garantiza/revierte/100%/milagro…), `publish.py` **se niega** y lo manda a revisión humana.
   Regla: si hace una afirmación de salud, NO es carril auto.

## Carril GATED (tu aprobación)
Los números de **Pulso Vigente** y cualquier pieza con ciencia/claims van por el flujo de PR
(`newsletter-send.yml` / social pack) — esos sí los apruebas tú.

## Imágenes
Ayrshare necesita una **URL pública** en `image_url`. Para usar un hero generado: commitéalo y
usa su URL `raw.githubusercontent.com/...`, o súbelo a un bucket.

## Marcadores
Al publicar, se crea `<post>.posted` para no repetir. No lo borres.
