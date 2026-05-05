# Knowledge Base para ChatVigente: RAG Architecture

**Fecha**: 2025-10-15
**Observación del usuario**: "Obviamente habría un SSOT de todo lo relacionado con estética masculina, de donde podrían consultar o incluso hacer consultas externas (esto cambiaría el tipo de agente...)"

---

## 🎯 Impacto de esta Observación

**CORRECTO**: Esto **transforma completamente** la arquitectura de ChatVigente de:

❌ **Chatbot simple** (rule-based + scripted responses)
                ↓
✅ **RAG Agent** (Retrieval-Augmented Generation)

---

## 1. ¿Qué es un SSOT de Estética Masculina?

### Knowledge Base Propietaria:

```
📚 KNOWLEDGE BASE - Hombre Vigente
├─ Tratamientos (26 servicios)
│  ├─ HIFU (definición, beneficios, riesgos, precio, duración, contraindicaciones)
│  ├─ Botox (qué es, cómo funciona, zonas aplicación, efectos, duración)
│  ├─ RF Microneedling (tecnología, indicaciones, resultados esperados)
│  └─ ... (23 más)
│
├─ Condiciones Dermatológicas
│  ├─ Arrugas (tipos, causas, tratamientos recomendados)
│  ├─ Flacidez (grados, evaluación, opciones)
│  ├─ Manchas (clasificación, prevención, eliminación)
│  └─ ... (15+ condiciones)
│
├─ Protocolos Clínicos
│  ├─ Preparación pre-tratamiento
│  ├─ Cuidados post-tratamiento
│  ├─ Contraindicaciones
│  └─ Efectos secundarios comunes
│
├─ Arquetipos y Psicología
│  ├─ Carlos (motivaciones, objeciones típicas, lenguaje)
│  ├─ Eduardo (perfil psicográfico, triggers de compra)
│  ├─ Mantenimiento (comportamiento, expectativas)
│  └─ Transaccional (barreras, incentivos)
│
├─ Pricing y Financiamiento
│  ├─ Estructura de precios por servicio
│  ├─ Memberships (access/elite)
│  ├─ BNPL (elegibilidad, términos)
│  └─ Políticas de cancelación
│
├─ FAQs (100+ preguntas frecuentes)
│  ├─ "¿Duele el HIFU?"
│  ├─ "¿Cuánto dura el Botox?"
│  ├─ "¿Puedo hacer ejercicio después?"
│  └─ ...
│
└─ Fuentes Externas (opcional)
   ├─ Estudios clínicos (PubMed)
   ├─ Regulaciones FDA/COFEPRIS
   └─ Benchmarks competencia
```

---

## 2. Arquitectura RAG (Retrieval-Augmented Generation)

### Flujo Completo:

```
┌─────────────────────────────────────────────────────────┐
│  1. INGESTA DE CONOCIMIENTO (One-time / Periodic)      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Documentos Fuente:                                     │
│  • PDFs (fichas técnicas tratamientos)                  │
│  • Markdown (Wiki interna)                              │
│  • Tablas (servicios_completos.json)                    │
│  • Scraped data (estudios clínicos)                     │
│                                                         │
│                    ↓                                    │
│                                                         │
│  Procesamiento:                                         │
│  • Chunking (512-1024 tokens por chunk)                │
│  • Embedding (text-embedding-3-small de OpenAI)         │
│  • Metadata (categoría, fecha, fuente, relevancia)      │
│                                                         │
│                    ↓                                    │
│                                                         │
│  Almacenamiento:                                        │
│  • Qdrant (vector database)                             │
│  • 1,500-5,000 chunks iniciales                         │
│  • Indexación semántica                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  2. RUNTIME - Query del Usuario                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Cliente: "¿Qué es HIFU y me sirve?"                    │
│                                                         │
│                    ↓                                    │
│                                                         │
│  A. Query Embedding                                     │
│     • Convertir pregunta a vector (1536 dims)           │
│     • OpenAI text-embedding-3-small                     │
│                                                         │
│                    ↓                                    │
│                                                         │
│  B. Semantic Search (Qdrant)                            │
│     • Buscar top-K chunks más similares (K=5-10)        │
│     • Cosine similarity > 0.75                          │
│     • Filtrar por metadata relevante                    │
│                                                         │
│     Chunks recuperados:                                 │
│     1. "HIFU definición técnica" (score: 0.92)          │
│     2. "HIFU beneficios clínicos" (score: 0.89)         │
│     3. "HIFU vs alternativas" (score: 0.85)             │
│     4. "HIFU indicaciones por edad" (score: 0.82)       │
│     5. "HIFU pricing y duración" (score: 0.78)          │
│                                                         │
│                    ↓                                    │
│                                                         │
│  C. Context Enrichment                                  │
│     • Agregar datos del cliente (PersonaVigente)        │
│     • Agregar Índice Vigente (DiagnósticoVigente)       │
│     • Agregar pricing personalizado (OptiVigente)       │
│                                                         │
│     Context final:                                      │
│     • Knowledge: 5 chunks (2,500 tokens)                │
│     • Cliente: arquetipo carlos, edad 42, Índice 71     │
│     • Pricing: $3,040 (con Elite)                       │
│                                                         │
│                    ↓                                    │
│                                                         │
│  D. LLM Generation (GPT-4o mini)                        │
│                                                         │
│     Prompt:                                             │
│     """                                                 │
│     Eres un asesor experto en estética masculina.       │
│                                                         │
│     CONTEXTO CONOCIMIENTO:                              │
│     {chunks_recuperados}                                │
│                                                         │
│     CONTEXTO CLIENTE:                                   │
│     - Nombre: Carlos                                    │
│     - Edad: 42 años                                     │
│     - Arquetipo: Carlos (ejecutivo premium)             │
│     - Índice Vigente: 71/100                            │
│     - Subscore estructural: 68 (mejorable)              │
│     - Membership: Elite                                 │
│                                                         │
│     PREGUNTA: "¿Qué es HIFU y me sirve?"                │
│                                                         │
│     INSTRUCCIONES:                                      │
│     1. Explica HIFU en términos simples                 │
│     2. Indica si es adecuado para este cliente          │
│     3. Menciona precio personalizado                    │
│     4. Da expectativas realistas                        │
│     5. Termina con call-to-action                       │
│     """                                                 │
│                                                         │
│                    ↓                                    │
│                                                         │
│  E. Respuesta Generada                                  │
│                                                         │
│     "HIFU (High-Intensity Focused Ultrasound)           │
│      es un tratamiento no invasivo que usa              │
│      ultrasonido para tensar la piel profunda...        │
│                                                         │
│      Para ti, Carlos, ✅ SÍ es muy recomendable:        │
│      • Tu Índice actual 71 puede mejorar a 82           │
│      • Tu subscore estructural 68 indica flacidez       │
│      • Clientes similares mejoran +11 puntos            │
│                                                         │
│      Inversión: $3,040 (con descuento Elite)            │
│                                                         │
│      ¿Agendamos diagnóstico gratuito?"                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Stack Tecnológico RAG

### Componentes:

```javascript
{
  // 1. Vector Database
  vectorDB: "Qdrant Cloud",
  alternativas: ["Pinecone", "Weaviate", "Chroma"],
  costo_qdrant: "$25-95/mes (según volumen)",

  // 2. Embedding Model
  embedding: "text-embedding-3-small (OpenAI)",
  dimensiones: 1536,
  costo: "$0.02 / 1M tokens",
  velocidad: "~1ms por query",

  // 3. LLM para generación
  llm: "GPT-4o mini",
  costo: "$0.15 / 1M input tokens, $0.60 / 1M output",
  context_window: "128K tokens",

  // 4. Orchestration
  framework: "LangChain / LlamaIndex",
  backend: "FastAPI (Python)",

  // 5. Chunking Strategy
  chunk_size: "512-1024 tokens",
  overlap: "50-100 tokens",
  metadata: ["categoria", "fecha", "fuente", "idioma"],

  // 6. Retrieval Config
  top_k: 5,  // Recuperar top 5 chunks
  similarity_threshold: 0.75,
  rerank: true,  // Re-rankear con modelo adicional

  // 7. Caching
  cache_layer: "Redis",
  ttl: "24 horas",
  hit_rate_target: ">60%"
}
```

---

## 4. Tipos de Queries que Mejoran con RAG

### Tipo A: Educación sobre Tratamientos
```
Cliente: "¿Qué es Sculptra y cómo funciona?"

SIN RAG (rule-based):
❌ "Sculptra es un tratamiento inyectable. ¿Te gustaría reservar?"
   (Respuesta genérica, sin detalles)

CON RAG:
✅ "Sculptra es un bioestimulador de colágeno (ácido poli-L-láctico)
   que se inyecta en dermis profunda. A diferencia de fillers que
   dan volumen inmediato, Sculptra estimula tu propio colágeno
   durante 3-6 meses, con resultados que duran 2+ años.

   Para ti (Carlos, 42 años, Índice 71):
   • Ideal para mejorar subscore estructural (68)
   • Clientes similares mejoran +8-12 puntos
   • Requiere 2-3 sesiones (espaciadas 4-6 semanas)
   • Inversión: $11,000/sesión ($8,800 con Elite)

   Ventaja vs Botox: Resultados más naturales y duraderos.

   ¿Te gustaría ver antes/después de casos similares?"
```

---

### Tipo B: Comparaciones Complejas
```
Cliente: "¿Cuál es mejor para mí: HIFU o Lifting con Hilos PDO?"

SIN RAG:
❌ "Ambos son excelentes. ¿Prefieres agendar para alguno?"

CON RAG:
✅ "Analicé tu perfil (Carlos, 42 años, Índice 71):

   HIFU:
   • Mejor para: Flacidez leve-moderada (tu caso)
   • Invasividad: Ninguna (sin agujas)
   • Downtime: 0 días
   • Resultados: 2-3 meses (duran 12-18 meses)
   • Precio: $3,040 (Elite)
   • ✅ Recomendado para ti

   Lifting Hilos PDO:
   • Mejor para: Flacidez severa (no tu caso)
   • Invasividad: Mínima (microagujas)
   • Downtime: 3-5 días
   • Resultados: Inmediatos (duran 18-24 meses)
   • Precio: $3,040 (Elite)
   • ⚠️ Podría ser excesivo para tu nivel

   RECOMENDACIÓN: Empieza con HIFU. Si en 6 meses
   quieres más definición, considera hilos como segundo paso.

   ¿Agendamos diagnóstico para confirmar?"
```

---

### Tipo C: Contraindicaciones y Riesgos
```
Cliente: "Tengo marcapasos, ¿puedo hacerme HIFU?"

SIN RAG:
❌ "Deja verificarlo con el doctor. ¿Tu número?"
   (Escala a humano innecesariamente)

CON RAG:
✅ "⚠️ IMPORTANTE: HIFU está CONTRAINDICADO si tienes:
   • Marcapasos o implantes electrónicos
   • Implantes metálicos en zona tratamiento
   • Embarazo
   • Infecciones activas en piel

   Tu marcapasos es una contraindicación absoluta para HIFU.

   ALTERNATIVAS SEGURAS para ti:
   1. Botox (sin contraindicación)
   2. Fillers (sin contraindicación)
   3. RF Microneedling (requiere evaluación médica)

   Te conectaré con el Dr. López para evaluar opciones
   seguras personalizadas. ¿Prefieres llamada o WhatsApp?"
```

---

### Tipo D: Consultas Externas (Future)
```
Cliente: "Leí un estudio que dice que HIFU puede dañar nervios"

SIN RAG (sin acceso externo):
❌ "HIFU es seguro cuando lo hace un profesional."

CON RAG + External Search:
✅ "Entiendo tu preocupación. Analicé la literatura:

   📚 Evidencia Científica (PubMed):
   • Estudio: 'HIFU Safety in Facial Rejuvenation' (2023)
   • Muestra: 5,000 pacientes, seguimiento 2 años
   • Incidencia lesión nerviosa: 0.02% (1 en 5,000)
   • Todas temporales, recuperación <3 meses

   🔬 Protocolo Hombre Vigente:
   • Mapeo térmico pre-tratamiento (Imaging Module)
   • Identificación precisa de nervios faciales
   • Ajuste parámetros según anatomía
   • Monitoreo temperatura tiempo real

   📊 Nuestros Datos:
   • 1,200+ sesiones HIFU realizadas
   • 0 casos de lesión nerviosa permanente
   • 2 casos de hormigueo temporal (<48h)
   • Satisfacción: 96% (CSAT 4.8/5)

   El riesgo existe (como en cualquier procedimiento médico)
   pero es extremadamente bajo con tecnología adecuada
   y especialista certificado.

   ¿Te gustaría hablar con el Dr. López para resolver dudas?"
```

---

## 5. Fuentes del Knowledge Base

### A. Fuentes Internas (Propietarias):

```
1. Documentación Técnica
   • servicios_completos.json (26 servicios)
   • Protocolos clínicos (preparación, cuidados)
   • Políticas (cancelación, BNPL, memberships)

2. Data Histórica
   • 5,000 diagnósticos (DiagnósticoVigente)
   • 27,000 eventos (transacciones)
   • Feedback clientes (CSAT, reviews)

3. Wiki Interna
   • 73 archivos Markdown analizados
   • Arquetipos (perfiles psicográficos)
   • Best practices ventas

4. Estudios de Caso
   • Antes/después con métricas
   • Índice Vigente mejoras promedio
   • Testimonios segmentados por arquetipo
```

### B. Fuentes Externas (Futuras):

```
1. Literatura Científica
   • PubMed (estudios clínicos)
   • FDA/COFEPRIS (aprobaciones, warnings)
   • Journals dermatológicos

2. Competencia
   • Precios mercado (benchmarking)
   • Servicios ofrecidos
   • Marketing claims

3. Regulaciones
   • NOM-241 (establecimientos salud)
   • COFEPRIS (dispositivos médicos)
   • LFPDPPP (datos personales)
```

---

## 6. Implementación para el Demo

### Opción A: RAG Real (Recomendado)

**Esfuerzo**: ⭐⭐⭐ (MEDIO - 20-30 horas)

**Stack**:
- Qdrant Cloud (vector DB)
- OpenAI Embeddings + GPT-4o mini
- LangChain (orchestration)
- FastAPI backend

**Pasos**:
1. Preparar knowledge base (10h)
   - Extraer info de 26 servicios
   - Crear chunks con metadata
   - Generar embeddings

2. Setup Qdrant + LangChain (4h)
   - Crear colección en Qdrant
   - Ingerir chunks
   - Configurar retrieval

3. Integrar con ChatVigente (6h)
   - Endpoint `/chat/rag`
   - Context enrichment (PersonaVigente, etc.)
   - Response generation

**Pros**:
- ✅ Demo real e interactivo
- ✅ WOW factor máximo
- ✅ Muestra capacidad técnica real
- ✅ Inversores pueden hacer preguntas reales

**Contras**:
- ⚠️ Requiere 3-4 días desarrollo
- ⚠️ Costos APIs ($50-100 para demo)
- ⚠️ Requiere knowledge base real

---

### Opción B: Mock RAG (UI Simulado)

**Esfuerzo**: ⭐⭐ (BAJO - 8-12 horas)

**Implementación**:
- UI que simula búsqueda en Qdrant
- Respuestas pre-generadas con contexto
- Panel lateral mostrando chunks recuperados

**Pros**:
- ✅ Rápido (1-2 días)
- ✅ Muestra el concepto claramente
- ✅ Sin costos de APIs
- ✅ Sin riesgo de fallos

**Contras**:
- ⚠️ No interactivo (scripted)
- ⚠️ Menor credibilidad técnica

---

## 7. Ejemplo de UI Demo RAG

```
┌─────────────────────────────────────────────────────────────┐
│  ChatVigente AI - RAG Architecture Demo                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Chat WhatsApp]                          [Sistema RAG]     │
│  ┌───────────────────────────┐  ┌────────────────────────┐ │
│  │                           │  │ 1. Query Embedding      │ │
│  │ Cliente (10:00 AM)        │  │ ✅ Vector generado      │ │
│  │ ¿Qué es HIFU y me sirve?  │  │    (1536 dims)         │ │
│  │                           │  │                        │ │
│  │ ChatVigente (10:00 AM)    │  │ 2. Semantic Search     │ │
│  │ [🔄 Buscando en KB...]     │  │ ✅ Qdrant search       │ │
│  │ [🔍 5 chunks recuperados]  │  │                        │ │
│  │                           │  │ Chunks encontrados:    │ │
│  │ HIFU (High-Intensity      │  │ • "HIFU definición"    │ │
│  │ Focused Ultrasound) es un │  │   (score: 0.92)       │ │
│  │ tratamiento no invasivo   │  │ • "HIFU beneficios"    │ │
│  │ que usa ultrasonido...    │  │   (score: 0.89)       │ │
│  │                           │  │ • "HIFU vs opciones"   │ │
│  │ Para ti (Carlos, 42):     │  │   (score: 0.85)       │ │
│  │ ✅ SÍ es recomendable:     │  │                        │ │
│  │ • Índice: 71 → objetivo 82│  │ 3. Context Enrichment  │ │
│  │ • Subscore: 68 (mejorable)│  │ ✅ PersonaVigente      │ │
│  │ • Clientes +11 pts        │  │   arquetipo: carlos   │ │
│  │                           │  │ ✅ DiagnósticoVigente  │ │
│  │ Inversión: $3,040 (Elite) │  │   Índice: 71          │ │
│  │                           │  │ ✅ OptiVigente         │ │
│  │ ¿Agendamos diagnóstico?   │  │   precio: $3,040      │ │
│  │                           │  │                        │ │
│  └───────────────────────────┘  │ 4. LLM Generation      │ │
│                                  │ ✅ GPT-4o mini         │ │
│                                  │   tokens: 2,800       │ │
│                                  │   latency: 1.2s       │ │
│                                  └────────────────────────┘ │
│                                                             │
│  [Knowledge Base Stats]                                     │
│  • Total chunks: 1,847                                      │
│  • Categorías: Tratamientos (26), FAQs (120), Protocolos   │
│  • Última actualización: Hoy 09:00 AM                       │
│  • Cache hit rate: 68%                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Costos de Operación RAG

### Estimación Mensual (1,000 consultas):

```javascript
{
  // Vector Database (Qdrant Cloud)
  qdrant: {
    plan: "Free (1M vectors) → Startup ($25/mes)",
    storage: "~2GB (5,000 chunks)",
    queries: "Ilimitadas"
  },

  // Embeddings (OpenAI)
  embeddings: {
    ingestion: "$0.50 (one-time, 500K tokens)",
    queries: "$0.02 / 1K consultas (1M tokens query)",
    mensual: "$2"
  },

  // LLM Generation (GPT-4o mini)
  generation: {
    input: "$0.15 / 1M tokens × 2.8K avg = $0.42 / 1K consultas",
    output: "$0.60 / 1M tokens × 500 avg = $0.30 / 1K consultas",
    mensual: "$72 (1,000 consultas)"
  },

  // Caching (Redis Cloud)
  cache: {
    plan: "Free (30MB) → Essentials ($7/mes)",
    hit_rate: "60-70% (reduce costos LLM 60%)"
  },

  // TOTAL MENSUAL
  total: {
    sin_cache: "$99/mes (1,000 consultas)",
    con_cache: "$45/mes (1,000 consultas con 60% hit rate)",
    por_consulta: "$0.045"
  },

  // Escalamiento
  escalamiento_10k_consultas: "$420/mes",
  escalamiento_100k_consultas: "$3,800/mes"
}
```

---

## 9. Roadmap de Knowledge Base

### Fase 0 (Demo - 2 semanas):
```
✅ Knowledge Base básico
   • 26 servicios (definiciones, precios)
   • 50 FAQs
   • Protocolos básicos
   • Total: ~1,500 chunks

✅ RAG funcional
   • Qdrant Free tier
   • OpenAI embeddings + GPT-4o mini
   • LangChain orchestration

✅ UI Demo
   • Chat interface
   • Panel RAG stats en tiempo real
```

### Fase 1 (6 meses):
```
🔄 Expansión KB
   • +100 FAQs
   • Estudios de caso (antes/después)
   • Testimonios categorizados
   • Total: ~5,000 chunks

🔄 Multi-idioma
   • Inglés (para expansión US)
   • Mantener español

🔄 Caching inteligente
   • Redis para queries frecuentes
   • Hit rate >70%
```

### Fase 2 (12-18 meses):
```
🔮 Fuentes externas
   • PubMed API (estudios clínicos)
   • FDA/COFEPRIS (regulaciones)
   • Competitive intelligence

🔮 Fine-tuning LLM
   • Modelo custom con data propietaria
   • Reducir costos 80%
   • Mejorar accuracy +15%

🔮 Multimodal
   • Imágenes (antes/después)
   • Videos (procedimientos)
   • 3D models (anatomía facial)
```

---

## 10. Conclusión

### ✅ Recomendación: Implementar RAG Real para Demo

**Por qué**:

1. **Diferenciador brutal**:
   - Competencia: chatbots rule-based (limitados)
   - Hombre Vigente: RAG agent con knowledge propietario
   - **10× más sofisticado**

2. **Demuestra expertise**:
   - No solo reservas, sino **educación experta**
   - Consulta 1,500+ chunks de conocimiento
   - Respuestas personalizadas por arquetipo

3. **Escalable**:
   - Agregar nuevos tratamientos: +1 documento
   - Sin reprogramar reglas
   - Knowledge base crece orgánicamente

4. **Inversores lo entenderán**:
   - RAG es tecnología de moda (ChatGPT, Claude)
   - "AI que consulta nuestra base de conocimiento propietaria"
   - Moat claro vs competencia

**Esfuerzo**: 20-30 horas (viable en 2 semanas con prioridad)

**Costo demo**: ~$100 (worth it para seed round $200-250K)

---

**Next Steps**:
1. ✅ Confirmar implementación RAG
2. ⏳ Preparar knowledge base (extraer de wiki + servicios)
3. ⏳ Setup Qdrant + LangChain
4. ⏳ Integrar con ChatVigente mock UI
5. ⏳ Demo con 3-5 queries reales

---

**Generado por**: Claude Code
**Fecha**: 2025-10-15
