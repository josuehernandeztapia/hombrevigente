# Backend FastAPI - Hombre Vigente

**Demo Investor Seed Round** con 3 agentes AI simulados

---

## 🚀 Quick Start

### 1. Instalar dependencias

```bash
cd DEMO/backend
pip3 install fastapi uvicorn pydantic
```

### 2. Probar agentes (sin levantar servidor)

```bash
python3 test_agentes.py
```

Output esperado:
```
✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE

Los 3 agentes AI están funcionando correctamente.
```

### 3. Iniciar servidor FastAPI

```bash
python3 main.py
```

El servidor estará disponible en:
- **API:** http://localhost:8000
- **Docs (Swagger):** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

---

## 🤖 Los 3 Agentes AI

Todos los agentes están **100% alineados con la arquitectura documentada en la wiki** (`02_AGENTES_AI_CORE.md` y `AGENTES_AI_IDEAS.md`).

### 1. DiagnósticoVigente AI

**Función:** Análisis multi-modal (RGB + IR) → Índice Vigente™ (0-100) → Recomendaciones

**Endpoint:** `POST /api/diagnostico`

**Request:**
```json
{
  "cliente_id": "opcional - si no se provee, usa un cliente aleatorio"
}
```

**Response:**
```json
{
  "diagnostico_id": "uuid",
  "cliente_id": "uuid",
  "cliente_nombre": "Carlos Ejemplo",
  "fecha_diagnostico": "2025-10-15",
  "indice_vigente": 72.5,
  "subscore_estructural": 75.0,
  "subscore_piel": 68.0,
  "subscore_biologico": 73.0,
  "interpretacion": "BUENO: Índice Vigente dentro de rango saludable...",
  "recomendaciones": ["HIFU", "Botox", "Hydrafacial"],
  "hardware_usado": "FotoFinder meesma-2 + FLIR ONE",
  "processing_time_sec": 9.2
}
```

**Algoritmo (según wiki):**
```python
Índice Vigente = 0.4 × estructural + 0.3 × piel + 0.3 × biológico
```

**Simula:**
- Procesamiento ML de 8-12 segundos
- Hardware: 70% FotoFinder, 30% Artec Eva
- Recomendaciones basadas en subscores bajos

---

### 2. PersonaVigente AI

**Función:** Hiperpersonalización, scoring propensión compra, detección churn

**Endpoint:** `GET /api/persona/{cliente_id}`

**Response:**
```json
{
  "cliente_id": "uuid",
  "arquetipo_nombre": "Carlos el Vigente",
  "propension_compra": 0.850,
  "churn_propensity": 0.180,
  "ltv_12m": 100000,
  "servicios_recomendados": [
    {
      "servicio_id": "botox",
      "nombre": "Botox",
      "precio": 3250,
      "score": 0.7,
      "razon": "Recomendado: cliente de alto valor, tratamiento de alto impacto"
    }
  ],
  "razonamiento": "Análisis PersonaVigente para Carlos el Vigente..."
}
```

**Lógica (según wiki):**
- Propensión >70% = alto potencial
- Churn <0.60 = retención estable
- Recomendaciones filtradas por arquetipo target

---

### 3. OptiVigente AI

**Función:** Pricing dinámico, asignación óptima de slots, yield management

**Endpoint:** `POST /api/opti/pricing`

**Request:**
```json
{
  "servicio_id": "hifu",
  "cliente_id": "uuid",
  "fecha_deseada": "2025-10-20"
}
```

**Response:**
```json
{
  "servicio_nombre": "HIFU Ultraformer III",
  "precio_lista": 4000,
  "precio_optimizado": 3400,
  "descuento_pct": 15.0,
  "razon": "Descuento por baja utilización (65%)",
  "utilization_level": "bajo",
  "slots_disponibles": 11
}
```

**Lógica (según wiki):**
- Utilización <80% → descuentos 15-25%
- Eduardo el Explorador → NUNCA recibe descuentos
- Luis el Renovado → descuentos 10-20% (40% probabilidad)
- Clientes alta propensión (>70%) → slots premium

---

## 📁 Estructura del Backend

```
backend/
├── main.py                   # FastAPI app principal
├── database.py               # Conexión SQLite + queries
├── models.py                 # Pydantic schemas (request/response)
├── test_agentes.py           # Script de prueba rápida
├── agents/
│   ├── diagnostico_vigente.py   # Agente 1: Diagnóstico
│   ├── persona_vigente.py       # Agente 2: Personalización
│   └── opti_vigente.py          # Agente 3: Optimización
└── README.md                 # Este archivo
```

---

## 🔌 Endpoints Disponibles

### Agentes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/diagnostico` | Genera diagnóstico con DiagnósticoVigente AI |
| GET | `/api/persona/{cliente_id}` | Analiza cliente con PersonaVigente AI |
| POST | `/api/opti/pricing` | Calcula pricing dinámico con OptiVigente AI |

### Datos (exploración)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/clientes` | Lista clientes (filtros: limit, arquetipo) |
| GET | `/api/clientes/{cliente_id}` | Detalles de un cliente + historial |
| GET | `/api/analytics/revenue` | Métricas de revenue por arquetipo |

### Utilidades

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Info de la API |
| GET | `/health` | Health check |
| GET | `/docs` | Documentación Swagger |

---

## 🧪 Ejemplos de Uso

### 1. Generar diagnóstico para cliente aleatorio

```bash
curl -X POST http://localhost:8000/api/diagnostico \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 2. Analizar un cliente específico

```bash
curl http://localhost:8000/api/persona/{cliente_id}
```

### 3. Calcular pricing dinámico

```bash
curl -X POST http://localhost:8000/api/opti/pricing \
  -H "Content-Type: application/json" \
  -d '{
    "servicio_id": "hifu",
    "cliente_id": "{cliente_id}"
  }'
```

### 4. Ver analytics de revenue

```bash
curl http://localhost:8000/api/analytics/revenue
```

---

## ✅ Validación con Wiki

Todos los agentes implementan la lógica documentada en:

| Agente | Fuente Wiki | Líneas |
|--------|-------------|--------|
| DiagnósticoVigente | `02_AGENTES_AI_CORE.md` | 39-68 |
| PersonaVigente | `02_AGENTES_AI_CORE.md` | 72-106 |
| OptiVigente | `02_AGENTES_AI_CORE.md` | 108-137 |

**Arquitectura detallada:** `AGENTES_AI_IDEAS.md` (40-60 ideas por agente)

---

## 🎯 Para el Demo Investor

**Demos interactivos que puedes mostrar:**

1. **"Generar diagnóstico en vivo"**
   - Click botón → API call → Streaming 8-12 seg → Resultado
   - Muestra: Índice Vigente, subscores, recomendaciones

2. **"Análisis de cliente premium"**
   - Seleccionar Eduardo el Explorador
   - Mostrar: Propensión 85%, LTV $135K, servicios premium recomendados

3. **"Pricing dinámico en acción"**
   - Comparar precio para Eduardo (sin descuento) vs Luis (con descuento)
   - Mostrar: Utilización del club influye en pricing

**Próximo paso:** Frontend Next.js que consume esta API

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

```bash
pip3 install fastapi uvicorn pydantic
```

### Error: "No such file or directory: demo_hombrevigente.db"

Asegúrate de haber generado la base de datos primero:

```bash
cd ..  # Volver a /DEMO
python3 generador_sintetico_v2.py
```

### Error: "Address already in use"

El puerto 8000 ya está ocupado. Cambia el puerto en `main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
```

---

**Versión:** 1.0
**Última actualización:** 2025-10-15
**Status:** ✅ Funcionando - Listo para demo
