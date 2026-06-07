# 08 · Tecnología y Stack (CORE)

## Lo construido (real)
- Backend **FastAPI** + SQLite; generador de datos sintéticos (Faker, seed=42).
- **RAG funcional**: OpenAI `text-embedding-3-small` + **Pinecone** + GPT-4o-mini sobre 319 chunks de la knowledge base. Mejor pieza de ingeniería del repo, portable.
- `financial-engine.js` (motor financiero real, JS).
- Dashboards HTML (modelo financiero, diagnóstico Three.js, vision board, war room).

## Lo documentado pero NO construido
9 agentes ML (CNN/ViT, XGBoost, LightFM, MILP, GANs); stack "enterprise" (Kafka, Flink, BigQuery, dbt, Vertex, Feast, MLflow…). **Sobre-ingeniería para una clínica única pre-revenue.**

## Stack recomendado (alineado a `Arquitectura_PlugAndPlay_y_Matriz.md`)
Renta la plomería, construye el cerebro:
- Front: Framer/Next.js · Pagos: Stripe/Conekta + Kueski/Aplazo · WhatsApp: 360dialog/Yalo
- E-receta: Prescrypto · Labs: convenio + BloodGPT · Wearables: Terra/Rook · Skin AI: Haut.AI/Perfect Corp
- EHR backbone: Healthie (API) / Cerbo · **Cerebro: construir (Anthropic/OpenAI + pgvector)**

## Gaps técnicos en México (= foso)
No existe "OpenLoop mexicano" (red médica + credencialización as-a-service); no hay API de labs; péptidos sin canal legal limpio.
