# ADR: Integración de RAG en generación de acciones proactivas (Capa 4 + Capa 5)

**Fecha**: 2026-06-10  
**Contexto**: Durante la construcción del agente proactivo (Capa 5/6), se identificó la oportunidad de enriquecer las sugerencias de acciones (especialmente "low_progress") con contenido relevante del knowledge base vía RAG. Esto une la Capa 4 (RAG) con el routing proactivo, mejorando la calidad de los mensajes sin romper el "se corrige" (dry-run, gates, flags).

## Decisión

En `generate_action_for_signal` (para `low_progress`):
- Llamada best-effort a `rag_query_local` (use_llm=False para retrieval puro).
- Si el índice existe, se agrega un snippet corto del answer al `suggested_message`.
- Fallback silencioso si no hay índice, error, o no aplica (preserva comportamiento anterior 100%).
- El enrichment es opcional y controlable vía feature flag `RAG_LLM` (aunque el call es retrieval).
- La llamada genera su propia traza (fire-and-forget), contribuyendo a costos/observabilidad.

Esto se documentó en el golden proactivo (el "starts_with" es estable, el snippet es opcional), en tests/CI, y en el runbook.

## Alternativas consideradas

- Usar LLM en el enrichment (use_llm=true): descartado por costo y latencia innecesaria (el objetivo es evidencia del KB, no generación nueva).
- Hacer el enrichment obligatorio: descartado (rompe en entornos sin índice, como CI o dev sin embeddings).
- Enriquecer todas las señales: descartado (solo tiene sentido en casos donde el KB aporta valor, como low_progress; otras son más operativas).

## Re-activación / próximos pasos

- Si se agregan más signals que se beneficien de KB (ej. missing_labs con biomarcadores), extender el if.
- Monitorear en métricas / agent_status si el enrichment se usa y su impacto en "suggested_message".
- El golden y la calibración ya contemplan que el mensaje puede variar por el snippet.
- Posible: feature flag dedicada `PROACTIVE_RAG_ENRICHMENT` más granular.

## Trailer

Ratified-by: Autonomous step following Guía layers integration (Capa 4 into 5/6)  
Ratified-at: 2026-06-10  
Related: action_handler.py (generate_action_for_signal), rag_retrieval_local.py, data/proactive-golden.json, runbook.md, CI/nightly workflows, ADR-002 (se corrige/aprende)

---

Esta decisión une las capas de la Guía sin comprometer los mecanismos de corrección y aprendizaje ya construidos.