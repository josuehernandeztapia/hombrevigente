# Diseño — Hombre Vigente

Prototipos de alta fidelidad y SSOT de copy/tokens del producto.

| Ruta | Contenido | Uso |
|------|-----------|-----|
| [`handoff/`](handoff/) | Journey interactivo: Mapa + landing + 6 flujos + `hv-data.jsx` + inventario + `COMPLIANCE.md` | Desarrollo / demo con archivos separados |
| [`deck/`](deck/) | Flujo del producto con capturas (HTML → imprimir PDF) | Pitch, aliado médico, onboarding interno |
| [`reel/`](reel/) | Reel 9:16 autoplay (un HTML autocontenido) | Stories, LinkedIn, eventos |
| [`KICKOFF.md`](KICKOFF.md) | Brief dev M0–M5 (stack, milestones, compliance) | Arranque equipo / Claude Code |

**Demo interactivo:** `open handoff/Mapa\ Vigente.html`

**Deck PDF:** `open deck/Flujo-producto.html` → Imprimir / Guardar como PDF

**Reel:** `open reel/Reel-Vigente-9x16.html` (toca para pausar)

**Reel MP4 (Instagram):** `cd reel && npm install && npx playwright install chromium && brew install ffmpeg && npm run export` → `reel/Reel-Vigente-9x16.mp4`

### Demo offline (~12 MB, fuera de git)

`Hombre Vigente.zip` en Downloads = HTML autocontenidos (sin depender de `.jsx` externos). Útil para compartir por AirDrop/Drive. No está en el repo por tamaño; el equivalente desarrollable es `handoff/`.

Operación actual (MVP-0 manual): `estrategia_2026/MVP0_Doctrina.md`. Evidencia RAG: `rag-bot/knowledge_base/longevity/00_MARCO_SSOT_EVIDENCIA_Y_COMPLIANCE.md`.