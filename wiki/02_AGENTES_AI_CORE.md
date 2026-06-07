# 02 · Agentes AI (CORE)

## Estado real
Lo documentado: 6-9 "agentes propietarios". Lo construido: backend FastAPI + generador de datos sintéticos (Faker seed=42) + RAG sobre la knowledge base. Los "agentes" son specs + mocks (reglas + `random.uniform()`), no modelos entrenados. El diagnóstico CNN+térmico es simulación de front-end.

## Agentes (como visión; marcar build vs mock)
| Agente | Función | Estado |
|--------|---------|--------|
| **DiagnosticoVigente** | Visión (foto/RGB+térmico) → Índice de Vigencia | Mock/simulado |
| **PersonaVigente** | Segmentación/arquetipo del cliente | Mock |
| **OptiVigente** | Optimización de agenda/precio/descuento (MILP) | Pseudocódigo (ver GAP encuesta) |
| **RiskGuard** | Scoring de riesgo (Z-Score + Monte Carlo) + pisos de margen | Pseudocódigo |
| **ChatVigente** | RAG conversacional sobre servicios | **Real (OpenAI+Pinecone)** |
| **SafetyVigente** | Predicción de incidentes clínicos | Concepto |
| **AssetVigente / AdvisorVigente / Virtual Try-On** | Inventario / asesoría / GAN estética | Concepto |

## Lo reutilizable de verdad
**ChatVigente / pipeline RAG** (text-embedding-3-small + Pinecone + GPT-4o-mini sobre 319 chunks) — funciona y es portable: cambiar KB estético por monografías de péptidos/protocolos y re-embeber.

## Recomendación
No presentar "9 agentes IA" como existentes (no resiste due diligence). Construir 1 motor de protocolo real (LLM + pgvector) como IP; el resto, comprar (ver `Arquitectura_PlugAndPlay_y_Matriz.md`).
