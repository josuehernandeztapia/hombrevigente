# ChatVigente vs AdvisorVigente: ¿Quién responde qué?

**Fecha**: 2025-10-15
**Pregunta del usuario**: "¿Quién responde dudas sobre servicios (ej. '¿Qué es HIFU?', '¿Aplicaría para mí?')?"

---

## TL;DR - Respuesta Rápida

**Para el DEMO de inversores: Usar SOLO ChatVigente**

**Razón**: ChatVigente y AdvisorVigente se están consolidando en UN SOLO agente llamado **ChatVigente AI** en las versiones más recientes del SSOT.

---

## 1. Diferencia Conceptual (Histórica)

### ChatVigente AI (Original)
**Rol**: "Operador telefónico digital"

**Funciones**:
- ✅ Gestión de reservas/cancelaciones
- ✅ Recordatorios automáticos
- ✅ Políticas (cancelación, no-show)
- ✅ Flujos transaccionales
- ❌ NO educación profunda
- ❌ NO asesoría personalizada

**Ejemplo**:
```
Cliente: "Quiero reservar HIFU"
ChatVigente: "Perfecto! Tengo disponible:
              • Viernes 2pm
              • Lunes 10am
              ¿Cuál prefieres?"
```

**Características**:
- Respuestas rápidas (<30 seg)
- Rule-based + ML hybrid
- Tasa resolución 78% sin humano
- Dialogflow CX (intents predefinidos)

---

### AdvisorVigente AI (Original)
**Rol**: "Asesor experto personal"

**Funciones**:
- ✅ Educación sobre tratamientos
- ✅ Recomendaciones personalizadas
- ✅ Contexto historial completo
- ✅ Respuestas profundas basadas en perfil
- ❌ NO gestión operativa (reservas)

**Ejemplo**:
```
Cliente: "¿Qué es HIFU y me sirve?"

AdvisorVigente: "HIFU (High-Intensity Focused Ultrasound)
                 es un tratamiento no invasivo que usa
                 ultrasonido para tensar la piel.

                 Veo que eres Carlos, 42 años, Índice 71.

                 HIFU te serviría porque:
                 • Tu subscore estructural es 68 (mejorable)
                 • Clientes como tú mejoran +11 puntos
                 • Duración: 60-90 min
                 • Sin downtime
                 • Resultados en 2-3 meses

                 Precio: $3,800 (con tu membership Elite: $3,040)

                 ¿Te gustaría agendar diagnóstico gratuito?"
```

**Características**:
- Respuestas educativas profundas
- Contexto completo (Feast + BigQuery)
- GPT-4o mini + RAG (knowledge base)
- Personalizado por arquetipo

---

## 2. Evolución en el SSOT

### 📊 Análisis de Documentos Recientes:

Al revisar los documentos más recientes del SSOT, encontré que **ChatVigente** y **AdvisorVigente** están convergiendo:

```javascript
// De AGENTES_Y_IDEAS_COMPLETAS.md (línea 5-10)

Agentes AI Internos:
1. DiagnósticoVigente AI
2. PersonaVigente AI
3. OptiVigente AI
4. RiskGuard AI
5. ChatVigente AI          ← Aparece como agente principal
6. AdvisorVigente AI       ← Aparece DESPUÉS como subtipo
```

**Pero en archivos más recientes**:

```javascript
// De 03_OPERACIONES_CORE.md (línea 45)

Touchpoints:
- ChatVigente responde FAQs (80% IA, 20% humano)
- ChatVigente + OptiVigente asignan slot
- AdvisorVigente WhatsApp → Consulta adicional

// De MARKETING_IDEAS_PARTE1.md

- WhatsApp: Conversaciones personalizadas con AdvisorVigente AI
```

**Interpretación**: AdvisorVigente está siendo **subsumido** en ChatVigente como una funcionalidad avanzada.

---

## 3. Arquitectura Unificada (Propuesta)

### ChatVigente AI v3.0 (Unificado)

```
┌─────────────────────────────────────────────────────────┐
│              ChatVigente AI (Unificado)                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  MODO 1: Transaccional (80% casos)                      │
│  • Reservas, cancelaciones, políticas                   │
│  • Dialogflow CX (rule-based)                           │
│  • Response time: <30 seg                               │
│                                                         │
│  MODO 2: Asesoría (20% casos)                           │
│  • Educación tratamientos                               │
│  • Recomendaciones personalizadas                       │
│  • GPT-4o mini + RAG (knowledge base)                   │
│  • Contexto Feast + BigQuery                            │
│  • Response time: 1-2 min                               │
│                                                         │
│  Decisión de Modo:                                      │
│  IF query tiene {"qué es", "cómo funciona", "me sirve"}│
│     → MODO 2 (Asesoría)                                 │
│  ELSE                                                   │
│     → MODO 1 (Transaccional)                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Casos de Uso: ¿Quién responde qué?

### Caso A: "¿Qué es HIFU?"
**Agente**: ChatVigente (MODO 2 - Asesoría)

**Flujo**:
```
1. Intent detection: "educacion_tratamiento"
2. ChatVigente activa MODO 2
3. Consulta knowledge base (RAG)
4. Consulta PersonaVigente (perfil cliente)
5. Genera respuesta educativa + personalizada
```

**Respuesta**:
```
HIFU (High-Intensity Focused Ultrasound) es un lifting
no invasivo que usa ultrasonido para tensar la piel.

✨ Beneficios:
• Sin cirugía ni agujas
• Resultados en 2-3 meses
• Dura 12-18 meses
• Sin downtime

💰 Precio: $3,800 MXN

👤 Para ti (Carlos, 42 años):
Clientes como tú mejoran +11 puntos en Índice Vigente.
Tu subscore estructural (68) lo hace ideal.

¿Te gustaría agendar diagnóstico gratuito?
```

---

### Caso B: "¿HIFU aplicaría para mí?"
**Agente**: ChatVigente (MODO 2 - Asesoría)

**Flujo**:
```
1. Intent detection: "eligibilidad_tratamiento"
2. ChatVigente consulta:
   - DiagnósticoVigente (último Índice Vigente)
   - PersonaVigente (arquetipo, propensión)
   - OptiVigente (pricing personalizado)
3. Genera recomendación personalizada
```

**Respuesta**:
```
Analicé tu perfil:

✅ SÍ, HIFU es ideal para ti porque:
• Tu Índice actual: 71/100
• Tu subscore estructural: 68 (mejorable)
• Tu edad: 42 años (rango óptimo 35-55)
• Clientes como tú (Carlos) mejoran +11 puntos

📊 Expectativa realista:
• Índice actual: 71 → objetivo 82
• Mejora visible: 2-3 meses
• Inversión: $3,040 (con descuento Elite 20%)

💳 Opciones pago:
• Contado: $3,040
• BNPL: 3 MSI x $1,267/mes (elegible)

¿Agendamos diagnóstico para confirmar?
```

---

### Caso C: "Quiero reservar para mañana"
**Agente**: ChatVigente (MODO 1 - Transaccional)

**Flujo**:
```
1. Intent detection: "reserva_cita"
2. ChatVigente consulta OptiVigente (slots)
3. Respuesta rápida sin contexto profundo
```

**Respuesta**:
```
Perfecto! Disponibilidad mañana:

📅 Mañana Jueves 16-Oct
• 10:00 AM (60 min)
• 2:00 PM (60 min)
• 5:00 PM (60 min)

¿Cuál prefieres?
```

---

### Caso D: "¿Por qué es tan caro?"
**Agente**: ChatVigente (MODO 2 - Asesoría)

**Flujo**:
```
1. Intent detection: "objeccion_precio"
2. ChatVigente genera explicación de valor
3. Contextualiza con arquetipo
```

**Respuesta**:
```
Entiendo tu pregunta. Te explico el valor:

💎 HIFU $3,800 incluye:
• 1 sesión completa (60-90 min)
• Tecnología médica certificada FDA
• Especialista certificado
• Seguimiento 3 meses

📊 ROI para clientes como tú:
• Inversión: $3,800
• Mejora promedio: +11 puntos Índice
• ROI: $345/punto
• Duración efecto: 12-18 meses
• Costo mensual equivalente: $253/mes

🏆 vs Competencia:
• Clínicas tradicionales: $5K-7K
• Sin tecnología propietaria
• Sin seguimiento
• Sin medición objetiva

Como miembro Elite, tu precio es $3,040 (ahorro $760).

¿Tiene sentido ahora?
```

---

## 5. Decisión para el DEMO

### ✅ Recomendación: Un SOLO agente "ChatVigente AI"

**Razones**:

1. **Simplicidad arquitectura**:
   - Más fácil de explicar a inversores
   - Un agente con dos modos vs dos agentes separados

2. **Alineado con SSOT reciente**:
   - Documentos más nuevos usan "ChatVigente" como término principal
   - AdvisorVigente aparece como funcionalidad, no agente separado

3. **Mejor UX**:
   - Cliente habla con UN SOLO chatbot
   - El bot decide internamente qué modo usar
   - Sin confusión de "¿con quién estoy hablando?"

4. **Más realista**:
   - En producción, sería un solo sistema con context switching
   - Splitting artificial solo complica demo

---

## 6. Implementación en Demo

### UI Propuesta:

```
┌─────────────────────────────────────────────────────────┐
│  ChatVigente AI - Conserje Digital 24/7                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Selector de Flujo]                                    │
│  ○ Flujo A: Reserva transaccional                       │
│  ● Flujo B: Educación + Asesoría (SELECCIONADO)         │
│  ○ Flujo C: Retención automática                        │
│                                                         │
│  ┌────────────────────────────────────────────────┐    │
│  │  Chat WhatsApp                                 │    │
│  ├────────────────────────────────────────────────┤    │
│  │                                                │    │
│  │  Cliente (10:00 AM)                            │    │
│  │  Hola! ¿Qué es HIFU y me serviría?             │    │
│  │                                                │    │
│  │  ChatVigente (10:00 AM)                        │    │
│  │  [🔄 Modo Asesoría activado...]                │    │
│  │  [🔍 Consultando tu perfil...]                  │    │
│  │                                                │    │
│  │  HIFU (High-Intensity Focused Ultrasound)      │    │
│  │  es un lifting no invasivo con ultrasonido.    │    │
│  │                                                │    │
│  │  ✨ Beneficios:                                 │    │
│  │  • Sin cirugía ni agujas                       │    │
│  │  • Resultados en 2-3 meses                     │    │
│  │  • Dura 12-18 meses                            │    │
│  │                                                │    │
│  │  👤 Para ti (Carlos, 42 años):                  │    │
│  │  ✅ SÍ aplicaría porque:                        │    │
│  │  • Tu Índice: 71 → objetivo 82                 │    │
│  │  • Subscore estructural: 68 (mejorable)        │    │
│  │  • Clientes similares: +11 puntos              │    │
│  │                                                │    │
│  │  💰 Inversión: $3,040 (Elite -20%)             │    │
│  │                                                │    │
│  │  ¿Agendamos diagnóstico gratuito?              │    │
│  │                                                │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
│  [Sistema en Tiempo Real]                               │
│  ┌────────────────────────────────────────────────┐    │
│  │ ChatVigente AI - Estado                        │    │
│  │ • Modo: ASESORÍA (GPT-4o mini + RAG)           │    │
│  │ • Intent: "educacion_tratamiento"              │    │
│  │ • Confidence: 98%                              │    │
│  │                                                │    │
│  │ Integraciones activas:                         │    │
│  │ ✅ DiagnósticoVigente (Índice: 71, subscore: 68)│    │
│  │ ✅ PersonaVigente (arquetipo: carlos)           │    │
│  │ ✅ OptiVigente (precio: $3,040 con Elite)       │    │
│  │ ✅ Knowledge Base (HIFU: definición, beneficios)│    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Lógica de Decisión de Modo

### Reglas de Intent Detection:

```python
def determine_mode(user_query: str, context: Dict) -> str:
    """
    Decide si usar MODO 1 (Transaccional) o MODO 2 (Asesoría)
    """

    # Keywords que indican necesidad de asesoría
    advisory_keywords = [
        "qué es", "cómo funciona", "me sirve", "aplicaría",
        "mejor opción", "recomiendas", "diferencia entre",
        "vale la pena", "resultados", "efectos", "riesgos"
    ]

    # Keywords que indican intención transaccional
    transactional_keywords = [
        "reservar", "agendar", "cancelar", "reprogramar",
        "confirmar", "disponibilidad", "horarios", "precio solo"
    ]

    query_lower = user_query.lower()

    # Prioridad: Asesoría sobre transaccional
    for keyword in advisory_keywords:
        if keyword in query_lower:
            return "ASESORIA"

    for keyword in transactional_keywords:
        if keyword in query_lower:
            return "TRANSACCIONAL"

    # Default: Asesoría (better safe than sorry)
    return "ASESORIA"
```

---

## 8. Conclusión

### Para el Demo de Inversores:

**✅ Usar UN SOLO agente: ChatVigente AI**

**Con dos modos internos**:
- **Modo 1 (Transaccional)**: Reservas, políticas, operaciones
- **Modo 2 (Asesoría)**: Educación, recomendaciones personalizadas

**Responde a la pregunta original**:
- "¿Qué es HIFU?" → ChatVigente Modo 2
- "¿Aplicaría para mí?" → ChatVigente Modo 2 (consulta PersonaVigente + DiagnósticoVigente)

**Ventajas**:
- ✅ Arquitectura más limpia
- ✅ Mejor UX (un solo bot)
- ✅ Alineado con SSOT reciente
- ✅ Más fácil de explicar a inversores
- ✅ Demuestra context switching inteligente

---

**Generado por**: Claude Code
**Fecha**: 2025-10-15
