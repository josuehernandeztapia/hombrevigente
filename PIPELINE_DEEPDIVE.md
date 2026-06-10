# HV Pipeline — Deep Dive técnico (SSOT RAG ↔ Newsletter ↔ RRSS)

> Referencia código-nivel del flujo end-to-end en `origin/main`.
> Cadena: **SSOT RAG → loop de actualización → consulta de fuentes → generación newsletter → correo de confirmación → OK → envío → publicación RRSS → (editorial bridge de vuelta al SSOT)**.
> Generado por auditoría de código (2026-06). Citas `archivo:función` aproximadas.

---

## 0. Mapa de bucles

Hay **dos bucles** que alimentan el SSOT del RAG y **un pipeline lineal** de newsletter que los cruza:

```
                    ┌──────────── SSOT RAG (monografías .md) ────────────┐
                    │  rag-bot/knowledge_base/{servicios,longevity}/*.md │
                    │  + FAQ_PROMOTED.md                                 │
                    └───────▲──────────────────────────▲─────────────────┘
        LOOP A (Q&A gaps)   │                          │   LOOP B (editorial bridge)
   decision_log.jsonl       │                          │   newsletter issue
     → gap_detector (Lun)   │                          │     → bridge_export
     → /admin/.../promote   │                          │     → process_editorial_bridge
     → process_promotions   │                          │     → PR a rag-bot
     → FAQ_PROMOTED.md ──────┘                          └────── monografía patcheada
                    │                                          │
                    └──────► embed_kb_local (nightly 08 UTC) ◄─┘
                                    │
                          embeddings_local.json + hv_kb_chunks (pgvector)
                                    │
                          retrieve() → score → gate → LLM  (ChatVigente)

PIPELINE NEWSLETTER (lineal):
 harvest (Jue) → draft_compose+LLM → issue.md → rehearsal(shadow) → PR
   → send_preview (email Resend + issue GH) → [OK | revise→loop]
   → merge main → send.py (Resend Broadcasts → Plus) + editorial-bridge + (social cron Mié)
```

---

## 1. SSOT del RAG

### 1.1 Formato de monografía (`kb_pipeline.py:68–103`)
La verdad cruda son `.md` en `rag-bot/knowledge_base/servicios/` (29) y `longevity/` (40 + `tarjetas/`), más `FAQ_PROMOTED.md`. Metadata extraída por regex del header/primeros 800 chars:

| Campo | Regex / fuente | Valores |
|---|---|---|
| `categoria` | `\*\*Categoría\*\*:\s*(.+)` | string |
| `avenida_hv` | `_normalize_avenida()` | `1` \| `2` \| `1-2` \| `unknown` |
| `evidencia_tier` | `_parse_tier()` (`\(E[0-5]\)` o `**Evidencia predominante**`) | `E0`–`E5` |
| `precio_base` | `\*\*Precio base\*\*:\s*\$?([\d,]+)` | int |
| `confianza` (tarjetas) | YAML | `alta` \| `media` \| `baja` |
| `flag_seguridad` (tarjetas) | YAML | `ninguno` \| `precaucion` \| `alto-riesgo` |
| `has_falta_fuente` | grep `[FALTA FUENTE]` | bool (excluye del índice) |

**Niveles de evidencia** (peso usado en scoring, `kb_pipeline.py:17`): `E0`=0.30, `E1`=0.85, `E2`=0.70, `E3`=0.80, `E4`=0.95, `E5`=0.90. (Ojo: no es monótono — E4/E5 mecanístico pesa más que E2.)

### 1.2 Chunking (`kb_pipeline.py:106–176`)
- **Tarjetas**: 1 chunk único (no se divide); si `[FALTA FUENTE]` → se descarta entera.
- **Monografías**: se hace `body.split("## Auditoría citas")[0]` (descarta el bloque de auditoría), luego split por `\n## ` → secciones. Filtros: `len(section.strip()) < 50` → skip; `[FALTA FUENTE]` → skip. Cada sección se prefija con `# {título_doc}`.
- **content_hash** = `sha256(text.utf-8).hexdigest()` (64 hex) → clave de re-embed diferencial.
- Dict de chunk: `{id: "{doc}_section_{i}", text, content_hash, metadata{kb_type, doc_subtype, categoria, avenida_hv, evidencia_tier, precio_base, confianza, flag_seguridad, section_title, section_index, service_id, source_file, ...}}`.
- **FAQ_PROMOTED** (`:219–258`): bloques `## …` con `P:`/`R:`, ruta `**Ruta KB:** (\w+)`; metadata fija `tier=E3, avenida=1, confianza=media, doc_subtype=faq_promoted`.

### 1.3 Índices derivados
**Local** (`embed_kb_local.py`): modelo `text-embedding-3-small`, **1536 dims**, batch 64, sleep 0.3s. Re-embed diferencial: si `content_hash` no cambió, reutiliza el embedding previo. Salida `knowledge_base/embeddings_local.json`:
```json
{ "version":1, "model":"text-embedding-3-small", "dimensions":1536,
  "generated_at":"…", "source":"all",
  "stats":{"total_chunks":N,"embedded_new":N,"reused":N},
  "chunks":[ {"id","text","content_hash","metadata",{…},"embedding":[…1536…]} ] }
```
**Pgvector** (`embed_kb_pgvector.py`, migración `001_hv_kb_embeddings.sql`): tabla `hv_kb_chunks` (`id PK, text, content_hash, kb_type CHECK, avenida_hv, evidencia_tier, embedding vector(1536), is_active, …`), índice `ivfflat (embedding vector_cosine_ops) lists=50` + GIN FTS. Upsert `ON CONFLICT (id) DO UPDATE … WHERE content_hash IS DISTINCT FROM EXCLUDED` (sync diferencial). Log de corridas en `hv_embedding_runs`.

### 1.4 Modos de fallo
| Condición | Comportamiento |
|---|---|
| Sin `OPENAI_API_KEY` | `embed_kb_local` → SystemExit; retrieval cae a léxico (módulo recuperado) |
| Sin DB postgres | `is_pgvector_configured()`→False → salta sync pgvector |
| Sección <50 chars / `[FALTA FUENTE]` | chunk descartado |
| Chunk sin embedding en sync pgvector | error exit(1) (exige `embed_kb_local --source all` primero) |

---

## 2. Consulta de fuentes (retrieval) + gates

### 2.1 Routing (`rag_retrieval_local.py:98–106`)
`detect_kb_route(query)`: cuenta matches de `LONGEVITY_HINTS` (nmn, nad+, fisetina, bpc-157, ghk, litio, leptina, ciática, discopatía, inflammaging, senolític, péptido, 25(OH)D, apo b…) vs `SERVICIOS_HINTS` (hifu, botox, sculptra, láser, precio, sesión…). Mayor → ruta; empate → `all`.

### 2.2 Gates duros (`confidence_gate.py` vía `check_gates`, `:109–140`)
Se evalúan ANTES del retrieval, sobre `gate_probe_text(query, frozen_context)`. Si dispara → respuesta = mensaje del gate, `gate_path="blocked"`, sin LLM:

| Gate | Patrón (regex) | Disparo | Acción |
|---|---|---|---|
| Péptidos inyectables | `bpc-157\|tb-500\|tesamorelin\|inyectable\|magistral…` | match | **blocked** `avenida_2_peptido` → deriva médico |
| Psiquiatría | `PSYCH_GATE(litio\|bipolar\|psiquiatr)` **AND** (`cerluten\|khavinson\|neuromodul` **OR** `ayuno\|16:8\|intermitente`) | combinado | **blocked** `gate_psiquiatria` |
| Oncología + senolíticos | `ONCO(oncológ\|cáncer activo\|tumor)` **AND** `SENOLYTIC(fisetina\|d+q\|dasatinib\|quercetina)` | combinado | **blocked** `gate_oncologia` |

### 2.3 Retrieval + scoring (`retrieve()` `:226–277`)
`retrieve(query, index, kb_route="all", top_k=5, avenida_max="1", min_confidence="medium")`:
1. `embed_query(query)` (text-embedding-3-small) tras `strip_command_words()`.
2. Filtra chunks: por `kb_route`; descarta `has_falta_fuente`, `flag_seguridad="alto-riesgo"` (longevity), `avenida_hv="2"` si `avenida_max="1"`.
3. **Cosine** `_cosine(a,b)= dot/(‖a‖‖b‖)`.
4. **Score compuesto** (`_combined_score`, `:160`): `0.7·cosine + 0.3·tier_w` donde `tier_w=TIER_WEIGHTS[tier]` (default 0.65); para tarjetas `tier_w=max(tier_w, CONFIDENCE_WEIGHTS[confianza])` (`alta`0.95/`media`0.75/`baja`0.50). Pesos env: `HV_SCORE_COSINE_WEIGHT=0.7`, `HV_SCORE_META_WEIGHT=0.3`.
5. Devuelve top_k ordenado.

### 2.4 Decisión de path (`confidence_gate.py:36–70`)
Sobre `top_score`: `≥ HV_COSINE_HIGH(0.70)` → **auto** (LLM directo); `≥ HV_COSINE_MIN(0.55)` → **caveat** (LLM + disclaimer "_con la evidencia disponible…_"); `< 0.55` → **escalate** ("no encontré", sin LLM).

### 2.5 query_preprocess (`query_preprocess.py:39–45`)
`strip_command_words()` elimina comandos de visualización ("muéstrame","foto de"), precios ("cuánto cuesta","precio de"), filler ("qué es","explícame","por favor") → normaliza whitespace. Mejora la calidad del embedding.

### 2.6 System prompt (`prompts.py`, `build_system_prompt`)
Modular: `PERSONA_BASE` (español MX, premium, máx 3-4 párrafos, nunca "soy IA") + `RULES_CRITICAS` (solo contexto; prohibido inventar precios/dosis/PMIDs; prohibido prescribir/curar/diagnosticar) + ROL (concierge/longevity/servicios) + `DISCLOSURE` por ruta (longevity cierra con "_Información educativa… no sustituye valoración médica_" + cita tier; servicios solo precios en contexto). Caveat inicial inyectado si `confidence=medium/low`.

---

## 3. Loop A — actualización de conocimiento (Q&A gaps)

### 3.1 Decision log (`decision_log.py:36–57`)
Cada query RAG escribe un `RagDecisionEntry` JSONL en `data/decision_log.jsonl` (env `HV_DECISION_LOG_PATH`), gateado por `HV_DECISION_LOG_ENABLED` (default true, fail-open). Campos: `query`(redactada ≤200), `query_normalized`, `kb_route`, `gate_path`, `gate_code`, `top_score`, `confidence`, `chunks_used`, `top_service`, `latency_ms`, `beta_id`, `turn_number`, `channel`, `entry_id`(uuid12), `timestamp`. Redacta emails/phones/keys antes de serializar.

### 3.2 Gap detector (`knowledge_gap_detector.py`)
- Cluster key = `strip_command_words(query_normalized).lower()` (agrupa variantes).
- `is_gap_row()`: gap si `gate_path∈{escalate,blocked}` **OR** `chunks_used==0` **OR** `top_score < HV_COSINE_MIN(0.55)`.
- Reporte `docs/qa/knowledge-gaps-{YYYY-W##}.md` con por-gap: frecuencia, max score, rutas KB, gate paths, variantes.
- **Cron**: `0 16 * * 1` (Lun 16 UTC, `rag-bot-knowledge-gaps.yml`) → corre `scripts/generate_knowledge_gaps_report.py --from-prod` → PR (labels `knowledge-loop`).

### 3.3 Promote endpoint (`knowledge_promote.py`)
`POST /admin/knowledge/promote` (auth `x-admin-pin` vs `HV_ADMIN_PIN`; dev sin pin si `ENVIRONMENT!=production`). Body `{question≥5, answer≥5, kb_route, target_section="FAQ_PROMOTED", from_log_id?, notes?}`. Stage → `data/knowledge-promotions-pending.json` con `{id:"promo-{ms}-{hex}", submitted_at, question, answer, kb_route, target_section, from_log_id, notes}`. Idempotente por `from_log_id`.

### 3.4 Process promotions (`scripts/process_knowledge_promotions.py`)
- `append_faq()` → `FAQ_PROMOTED.md` (`## pregunta[:60]` + `**Ruta KB:**` + `P:`/`R:`). Idempotente (skip si `P: {q}` ya existe).
- `append_golden()` → `docs/qa/golden-set-hv-rag.md` (`### P-NNN`, criticidad P1, ruta esperada).
- **Cron**: `0 15 * * *` (diario 15 UTC, `rag-bot-process-promotions.yml`) → process → `sync_golden_set --validate` → `golden_runner --gates-only` → PR.

### 3.5 Cierre (`rag-bot-nightly.yml`)
**Cron `0 8 * * *`** o push a `knowledge_base/**`/golden: `embed_kb_local.py --source all` re-embede (recoge FAQ_PROMOTED y monografías patcheadas) + `golden_runner --full`.

---

## 4. Generación del newsletter ("Pulso Vigente")

### 4.1 Harvest (`harvest.py`)
- **Europe PMC** `…/europepmc/webservices/rest/search?query=…&format=json&pageSize=12&resultType=lite`, query `({terms}) AND (FIRST_PDATE:[since TO until]) AND SRC:MED`. 13 temas SSOT + 4 AI×longevity (de `watchlist.yml`).
- Score: journal alto impacto (n engl j med/nature/science/cell/lancet/jama/nature aging…) **+3**, RCT/clinical trial **+2**, review **+1**, recencia `max(0, 3 - días//10)`.
- Salida `drafts/candidates-YYYY-MM-DD.md` (⭐ alto impacto · título · journal · fecha · PMID/DOI/link). **Metadatos reales de PMC, sin fabricación.**
- **Cron Jue 14 UTC** (`newsletter-draft.yml`) o dispatch.

### 4.2 Draft compose (`draft_compose.py` + `llm_client.py`)
- Parse candidates → selecciona 4 bloques por scoring por-tipo: **accionable** (+6 pilot/RCT/in-vivo/human, +8 lípidos/apoB), **frontera** (+5 reprogramming/senescence, −6 virus/covid), **AI** (+5 si topic AI, +4 LLM/multi-omics), **contexto** (+4 review/framework).
- Prompt **system**: redactor Pulso, español premium sin hype, "NUNCA inventes PMIDs/DOIs", prohibido "cura/trata/previene/diagnóstico/garantiza", salida solo markdown+frontmatter. **user**: `Nº{n}` + `EDITORIAL.md[:2000]` + ejemplo previo + picks JSON + estructura obligatoria (TLDR, 🟢 Accionable, 🔬 Frontera, 🤖 AI×Longevity, 🌍 Contexto, Plus + Bottom line, tabla Editorial bridge 4 filas, disclaimer).
- `validate_sources()`: cada `PMID(\d+)` / `10.\d{4,}/\S+` citado debe estar en el harvest; falla si no, o si no cita ningún PMID → `fallback_compose()` (plantilla mecánica, `compose: auto-fallback`).
- **Frontmatter**: `numero, fecha, subject(curiosity-gap), preheader, audiencia: plus, approved: false, approval_status: pending`.
- **LLM** (`llm_client.chat_complete`): provider `PULSO_COMPOSE_PROVIDER=auto` → Anthropic `claude-sonnet-4-20250514` (si `ANTHROPIC_API_KEY`) si no OpenAI `gpt-4o`; `max_tokens=8192, temperature=0.4, timeout=180s`. Override `PULSO_COMPOSE_MODEL`.
- Salida `issues/YYYY-MM-NNN.md`.

### 4.3 Hero / assets (`prompt_from_issue.py` + `image.py`)
Extrae theme/tldr/accionable → `BRAND_TEMPLATE` ("near-black #0B0B0C, bronce/oro, abstracto, sin texto/personas/medical imagery"). `_llm_prompts()` (gpt-4o-mini, `response_format=json_object`) → `{unsplash_query, slide_themes}`. `image.py`: OpenAI Images `gpt-image-1`, 1536×1024 → `assets/{numero}.png`. **Sin key → imprime prompt (degrada limpio)**. Trigger `newsletter-assets.yml` (manual).

### 4.4 Rehearsal / shadow (`rehearsal.py`)
`check_sources()` (cada bloque debe tener `*Fuente:*` + PMID/DOI), `check_bridge()` (cuenta filas A/C/vacías de la tabla). Corre render + social pack + bridge-export + RAG patch en **dry-run**; envío omitido si `PULSO_MODE=shadow`. Postmortem `runs/{stem}-postmortem.md` (✅ Pass / ⚠️ Revisar). Copia a `drafts/postmortem-{n}.md`.

---

## 5. Correo de confirmación + aprobación

### 5.1 Token HMAC (`approval_token.py` + `rag-bot/newsletter_approval_token.py`, idénticos)
`make_token`: firma `{issue_path}|{action}|{exp}` con HMAC-SHA256 sobre `NEWSLETTER_APPROVAL_SECRET`, `TTL=96h`, formato `{exp}.{sig}`. `verify_token`: chequea `exp` y `hmac.compare_digest` (timing-safe).

### 5.2 send_preview (`approval.py:67–137`)
Al cerrar `newsletter-draft.yml`:
1. `render(path)` (Jinja2 `templates/email.html` + markdown→HTML) → `{subject, audiencia, html}`.
2. Botón = `approval_url(rel_path,"approve")` → `{BASE_URL}/newsletter/approve?issue=…&action=approve&token={exp}.{sig}`.
3. Email **Resend** `POST /emails` (`Bearer RESEND_API_KEY`), `from=NEWSLETTER_FROM`, `to=[NEWSLETTER_APPROVAL_TO]`, subject `"[BORRADOR Pulso Nº{n}] {subject} — responde OK para enviar"`.
4. `create_github_issue()`: issue "Aprobar Pulso Nº{n}", labels `pulso-approval`,`newsletter`; estado en `approvals/{n}.json` `{numero, issue_path, github_issue, pr, status:pending}`.

### 5.3 Workflow de aprobación (`newsletter-approval.yml`)
3 triggers: `issue_comment` (título empieza "Aprobar Pulso") · `repository_dispatch` type `pulso-approval` (desde Fly, vía botón) · `workflow_dispatch`. **Parsing**: 1ª línea útil (ignora `^>`/`^On `), lowercase+trim; `ok|ok.|aprobar|aprobar.` → **approve**, resto → **revise** (body = correcciones). Checkout `newsletter/draft-{n}` (merge `origin/main -X theirs`).

### 5.4 Approve (`approval.mark_approved` + workflow)
`approved=true, approval_status=approved` → `gh pr merge {PR} --merge --delete-branch` → cierra issue ("✅ Aprobado y enviado a Plus"). El botón del email pega a Fly `GET /newsletter/approve` (`api/main.py:558`), que `verify_token` y `newsletter_approval_dispatch.dispatch_pulso_approval()` → `repository_dispatch` event.

### 5.5 Revise (`approval_revise.py`)
`approval_revision += 1`, `approval_status=revising`; LLM (system "Editor Pulso, mantén structure+PMIDs", `temperature=0.3`, user = correcciones + EDITORIAL[:1200] + borrador) → reescribe; preserva metadata; `send_preview()` de nuevo. **Loop hasta OK.**

---

## 6. Envío del newsletter (`send.py`, `newsletter-send.yml`)
Trigger: **push a main + `newsletter/issues/**`** (detecta nuevo issue por `git diff`) o dispatch.
Flujo:
1. `_already_sent(path)` (lee `approvals/{n}.json.sent_at`) → omite salvo `FORCE_RESEND=1`.
2. `render(path)`.
3. Gate: si no `FORCE_SEND=1` y `approved!=true` → omite.
4. **Resend Broadcasts**: `POST /broadcasts` `{audience_id: RESEND_AUDIENCE_PLUS|_FREE, from, subject, html}` → `bid`; luego `POST /broadcasts/{bid}/send` (salvo `DRY_RUN=1`).
5. `_record_sent(path, bid)` → `{numero, issue_path, sent_at, broadcast_id}` (idempotencia).
Modos: `DRY_RUN=1` (crea sin enviar), `PULSO_MODE=shadow` (valida render sin API), `FORCE_SEND`/`FORCE_RESEND`.

---

## 7. Publicación en RRSS

### 7.1 Carril AUTO (`publish.py`, `social-auto.yml` cron **Mié 16 UTC** `0 16 * * 3`)
- Fuente `social/queue/*.md` con `lane:auto`; `--due` filtra `date<=hoy`, descarta los que tienen `.posted`.
- **Claim-guard** regex (`:32-37`): bloquea `cura|trata|previene|diagnostic|garantiza|reviert|milagro|elimina la enfermedad|100%|sana|adelgaza garantizado` → NO publica, marca revisión humana.
- **Ayrshare** `POST /api/post` `{post, platforms(PLATFORM_MAP: x→twitter, instagram, facebook, tiktok, linkedin), mediaUrls}` (`Bearer AYRSHARE_API_KEY`). Marker `.posted` (ISO).

### 7.2 Carril GATED (`publish_social.py`)
Hero: sube `assets/{n}.png` a Ayrshare `/api/media/upload`; fallback GitHub raw (`HV_NEWSLETTER_ASSETS_BASE/BRANCH`, repo `josuehernandeztapia/hombrevigente`). Caption: regex `## Caption\n(.*?)(?:\n\n_|$)` de `social/{n}/instagram-facebook.md`. `idempotencyKey = pulso-{n}-ig-{tag}`. Aprobación implícita = editar+commitear.

### 7.3 Generador (`social.py`)
De `issues/{n}.md` produce 4 archivos en `social/{n}/`: `x-thread.md` (≤280/tweet), `instagram-facebook.md` (carrusel + `## Caption`), `linkedin.md`, `tiktok-script.md`. Extrae TLDR (`\*\*TLDR:\*\*`), Bottom line, bloques (`^## `, descarta tabla bridge), Fuente, Lente Vigente. Header `<!-- REVISAR Y VERIFICAR FUENTES ANTES DE PUBLICAR -->`.

---

## 8. Loop B — Editorial bridge (vuelta al SSOT)

### 8.1 Export (`bridge_export.py`)
Parsea tabla `## Editorial bridge` (cols `bloque|topic_ssot|monografía|pmid/doi|nivel E|bridge`). Filtra **tipo A** (claim accionable + PMID/DOI; `A/C` ambiguo → skip; tipo C = solo Pulso). `TOPIC_MONOGRAPHY` mapea topic→archivo (`inflammaging`→`02_inflammaging.md`, `nad_nmn_sirtuinas`→`03_nad_sirtuinas.md`, `glp1_metabolismo`→`17_…`, `lipidos_apob`→`25_…`; sin mapeo → rechaza). Stage `rag-bot/data/editorial-bridge-pending.json` `{id, issue_path, numero, fecha, bloque, bridge_type:A, topic_ssot, monografia, pmid_doi, evidence_level, title, fuente, summary, exported_at, status:pending}`.

### 8.2 Apply (`rag-bot/scripts/process_editorial_bridge.py`)
Inserta antes de la primera ancla `## ⚠️ Límites | ## 📖 FAQ | ## 🔗 Integración | ## 🏷️ Plantilla` (o al final) una sección:
```
### Evidencia reciente (Pulso Nº{n} · {fecha})
- **{title}** — *{journal_year}*. {pmid_doi} · {E}.
  - {summary}
  - Límite: en investigación / preclínico; no establece efecto en personas.   ← solo E1/E2
```
Idempotente por PMID/DOI (`already_present`). Auto-disclaimer si `E1/E2`.

### 8.3 PR de vuelta (`newsletter-editorial-bridge.yml`)
Trigger push main + `newsletter/issues/**`: `bridge_export` → `process_editorial_bridge` → si hay cambios, `create-pull-request` a rama `rag-bot/editorial-bridge-{run}` (labels `editorial-bridge`,`rag-bot`). **No auto-merge** (review humano). Al mergear, el nightly re-embede.

---

## 9. Tablas de referencia

### 9.1 Crons (UTC)
| Cuándo | Workflow | Acción |
|---|---|---|
| Lun 16:00 | rag-bot-knowledge-gaps | gap report (Loop A) |
| Mar–Dom — | — | — |
| Diario 08:00 | rag-bot-nightly | re-embed + golden full |
| Diario 15:00 | rag-bot-process-promotions | aplica promotions (Loop A) |
| Jue 14:00 | newsletter-draft | harvest + compose + preview email |
| Mié 16:00 | social-auto | publica queue lane:auto |
| push main+issues | newsletter-send / editorial-bridge | envío Resend + bridge a SSOT (Loop B) |

### 9.2 Secrets / env
| Secret/var | Usado en |
|---|---|
| `OPENAI_API_KEY` | embeddings, retrieval, hero, compose fallback |
| `ANTHROPIC_API_KEY` | compose/revise (provider prioritario) |
| `RESEND_API_KEY`, `RESEND_AUDIENCE_PLUS`/`_FREE`, `NEWSLETTER_FROM` | preview + envío |
| `NEWSLETTER_APPROVAL_SECRET` | token HMAC del botón |
| `NEWSLETTER_APPROVAL_TO`, `NEWSLETTER_APPROVAL_BASE_URL` | inbox editor + URL Fly |
| `AYRSHARE_API_KEY` | RRSS |
| `HV_ADMIN_PIN` | endpoint promote |
| `HV_DATABASE_URL`/`DATABASE_URL` | pgvector |
| Calibración: `HV_COSINE_HIGH=0.70`, `HV_COSINE_MIN=0.55`, `HV_SCORE_COSINE_WEIGHT=0.7`, `HV_SCORE_META_WEIGHT=0.3` | retrieval |

### 9.3 Idempotencia (todas file/marker-based, no transaccionales)
| Etapa | Mecanismo |
|---|---|
| Promote | `from_log_id` en pending.json |
| FAQ append | skip si `P: {q}` existe |
| Envío email | `sent_at`+`broadcast_id` en `approvals/{n}.json` |
| RRSS auto | marker `.posted` |
| RRSS gated | `idempotencyKey=pulso-{n}-ig-{tag}` |
| Bridge apply | `already_present` por PMID/DOI |

---

## 10. Observaciones / riesgos
1. **Dos stagings separados** (no se mezclan): `knowledge-promotions-pending.json` (Loop A, Q&A) vs `editorial-bridge-pending.json` (Loop B, claims).
2. **Humano siempre en el loop**: aprobación email/issue antes de enviar; claim-guard antes de RRSS auto; PR (no auto-merge) en el bridge de vuelta al SSOT.
3. **Idempotencia file-based** en todo el pipeline (§9.3): suficiente para crons single-writer, pero no transaccional — misma clase de hardening que el C1 de pending-actions ([issue #31]).
4. **`push main + issues/**` dispara dos workflows** (send + bridge): depende de `_already_sent`/`approved` para no reenviar en re-merges.
5. **Tier weights no monótonos** (E3>E2): intencional (E2 incluye preclínico), pero conviene tenerlo presente al calibrar.
6. **Retrieval degrada a léxico** sin `OPENAI_API_KEY` (módulo recuperado), pero el SSOT/embeddings exigen la key para indexar.
