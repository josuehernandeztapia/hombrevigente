# Stack Tecnológico - Demo Investor

**Hombre Vigente - Ronda Seed $200-250K USD**

Todo el stack está seleccionado para ser **gratuito, rápido de implementar, y profesional para inversionistas**.

---

## 📊 VISTA GENERAL

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui        │
│                    (Deploy: Vercel)                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     │
┌────────────────────▼────────────────────────────────────────┐
│                        BACKEND                              │
│         FastAPI + Python 3.13 + Pydantic                    │
│                (Deploy: Railway/Render)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼─────┐ ┌───▼────────┐ ┌▼──────────┐
│   SQLite    │ │  3 Agentes │ │   JSON    │
│  (5.1 MB)   │ │     AI     │ │  Configs  │
└─────────────┘ └────────────┘ └───────────┘
```

---

## 🎨 FRONTEND (Semana 2)

### Next.js 14 (App Router)
**¿Qué es?** Framework de React para aplicaciones web modernas
**¿Para qué?** Construir el dashboard investor interactivo
**¿Por qué?**
- Renderizado híbrido (Server + Client Components)
- Performance excelente (Critical Web Vitals)
- SEO-friendly para landing page
- Deploy instantáneo en Vercel (gratis)

**Costo:** $0 (open source)
**Deploy:** Vercel (gratis para demos)

---

### TypeScript
**¿Qué es?** JavaScript con tipos estáticos
**¿Para qué?** Escribir código frontend con autocompletado y type-safety
**¿Por qué?**
- Previene errores en tiempo de desarrollo
- Mejor DX (Developer Experience)
- Documentación automática del código

**Costo:** $0 (open source)

---

### Tailwind CSS
**¿Qué es?** Framework CSS utility-first
**¿Para qué?** Estilizar la interfaz rápidamente
**¿Por qué?**
- Desarrollo 5x más rápido que CSS vanilla
- No inventar nombres de clases
- Bundle final optimizado (solo CSS usado)
- Responsive design fácil

**Costo:** $0 (open source)

**Ejemplo:**
```tsx
<div className="bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700">
  Botón bonito sin CSS custom
</div>
```

---

### shadcn/ui
**¿Qué es?** Biblioteca de componentes React (NO es npm package, es copy-paste)
**¿Para qué?** Componentes UI profesionales (tablas, gráficas, modals)
**¿Por qué?**
- Componentes listos para producción
- Basado en Radix UI (accesibilidad A+)
- Personalizable 100% (no es black box)
- Look & feel profesional para inversionistas

**Costo:** $0 (open source)

**Componentes que usaremos:**
- `<Card>` - Tarjetas de arquetipos
- `<Table>` - Tabla de clientes
- `<Button>` - Botones interactivos
- `<Dialog>` - Modals para diagnósticos
- `<Progress>` - Barra de Índice Vigente

---

### Recharts / Chart.js
**¿Qué es?** Biblioteca de gráficas para React
**¿Para qué?** Visualizar revenue, LTV/CAC, distribución arquetipos
**¿Por qué?**
- Gráficas interactivas (hover, zoom)
- Integración nativa con React
- Responsive

**Costo:** $0 (open source)

**Gráficas que haremos:**
- Bar chart: Revenue por arquetipo
- Pie chart: Distribución de servicios
- Line chart: Evolución Índice Vigente
- Scatter plot: LTV vs CAC

---

## 🔧 BACKEND (Semana 1 - YA COMPLETADO ✅)

### Python 3.13
**¿Qué es?** Lenguaje de programación
**¿Para qué?** Toda la lógica del backend y agentes AI
**¿Por qué?**
- Ecosystem ML/AI más maduro
- Fácil de leer (importante para demo)
- Pandas/NumPy para data processing
- Ya lo tienes instalado

**Costo:** $0 (open source)

---

### FastAPI
**¿Qué es?** Framework web moderno para APIs
**¿Para qué?** Crear la API REST que consume el frontend
**¿Por qué?**
- **MÁS RÁPIDO que Flask/Django** (basado en Starlette + Uvicorn)
- Documentación automática (Swagger UI en /docs)
- Validación automática con Pydantic
- Async/await nativo (importante para streaming diagnósticos)
- Type hints → autocomplete en IDE

**Costo:** $0 (open source)

**Endpoints que creamos:**
```python
POST /api/diagnostico       # Genera diagnóstico (8-12 seg)
GET  /api/persona/{id}      # Analiza cliente
POST /api/opti/pricing      # Pricing dinámico
GET  /api/analytics/revenue # Métricas
```

---

### Pydantic
**¿Qué es?** Librería de validación de datos
**¿Para qué?** Definir schemas de request/response
**¿Por qué?**
- Validación automática (si envías string en vez de int → error claro)
- Serialización/deserialización JSON automática
- Documentación automática en Swagger

**Costo:** $0 (open source)

**Ejemplo:**
```python
class DiagnosticoResponse(BaseModel):
    indice_vigente: float  # Must be float, validated automatically
    recomendaciones: List[str]  # Must be list of strings
```

---

### Uvicorn
**¿Qué es?** Servidor ASGI ultrarrápido
**¿Para qué?** Correr FastAPI en producción
**¿Por qué?**
- Async nativo (maneja 1000+ requests concurrentes)
- Hot reload en desarrollo
- Compatible con WebSockets (para streaming futuro)

**Costo:** $0 (open source)

---

## 💾 BASE DE DATOS

### SQLite
**¿Qué es?** Base de datos SQL en un solo archivo
**¿Para qué?** Almacenar los 5K clientes + 10K eventos + 6.5K diagnósticos
**¿Por qué?**
- **NO requiere servidor** (ideal para demos en laptop)
- Un solo archivo .db portable
- 100% compatible con PostgreSQL (migración fácil)
- Queries rápidas (<10ms para dataset)
- Ya viene con Python

**Costo:** $0 (incluido en Python)
**Tamaño DB:** 5.1 MB (cabe en USB)

**Alternativa producción:** PostgreSQL en Supabase (cuando escales)

---

## 🤖 AGENTES AI (SIMULADOS)

### Agente 1: DiagnósticoVigente
**Stack interno:**
- Lógica: Python puro
- Fórmula wiki: `0.4 × estructural + 0.3 × piel + 0.3 × biológico`
- Simula: 8-12 seg de procesamiento ML

**En producción usarías:**
- PyTorch + MONAI (vision models)
- TensorFlow (thermal CNN)
- OpenCV (image processing)
- Seek SDK (thermal camera)

**Costo demo:** $0
**Costo producción:** $150K USD desarrollo (según wiki)

---

### Agente 2: PersonaVigente
**Stack interno:**
- Lógica: Python + reglas basadas en wiki
- Input: Historial eventos + arquetipo
- Output: Propensión compra, churn risk, recomendaciones

**En producción usarías:**
- LightFM (collaborative filtering)
- GPT-4o mini (razonamiento)
- Qdrant (vector database)
- scikit-learn (ML)

**Costo demo:** $0
**Costo producción:** ~$30K USD desarrollo

---

### Agente 3: OptiVigente
**Stack interno:**
- Lógica: Pricing dinámico según utilización
- Reglas: Descuentos si <80% utilización
- Slots premium para clientes >70% propensión

**En producción usarías:**
- scikit-learn (ML para pricing)
- Google OR-Tools (optimización slots)
- TimescaleDB (time-series data)

**Costo demo:** $0
**Costo producción:** ~$25K USD desarrollo

---

## 📦 DATOS SINTÉTICOS

### Faker
**¿Qué es?** Generador de datos fake realistas
**¿Para qué?** Crear nombres, emails, teléfonos mexicanos
**¿Por qué?**
- Locale 'es_MX' para datos mexicanos
- PII realista sin privacidad issues
- Reproducible con seeds

**Costo:** $0 (open source)

---

### Pandas + NumPy
**¿Qué es?** Librerías de data science
**¿Para qué?** Procesar los 5K clientes + 10K eventos
**¿Por qué?**
- DataFrame = tabla SQL en memoria
- Operaciones vectorizadas (rápido)
- Integración perfecta con SQLite

**Costo:** $0 (open source)

---

## 🚀 DEPLOYMENT

### Vercel (Frontend)
**¿Qué es?** Plataforma de hosting para Next.js
**¿Para qué?** Hostear el dashboard investor
**¿Por qué?**
- Deploy en 30 segundos (git push)
- CDN global automático
- SSL gratis
- Preview deployments (cada commit = URL única)
- Optimizaciones automáticas

**Costo:** $0 (Hobby plan - 100GB bandwidth/mes gratis)
**URL:** `https://hombre-vigente-demo.vercel.app`

---

### Railway o Render (Backend)
**¿Qué es?** Plataforma de hosting para APIs
**¿Para qué?** Hostear FastAPI + SQLite
**¿Por qué?**
- $5-10/mes (o free tier con limitaciones)
- Deploy desde GitHub
- Logs en tiempo real
- Auto-scaling

**Costo:** $0-10/mes
**Alternativa:** Fly.io, Heroku

---

## 🔄 CI/CD

### GitHub
**¿Qué es?** Control de versiones + hosting código
**¿Para qué?** Almacenar código + trigger deploys
**¿Por qué?**
- Git = industry standard
- Integración directa con Vercel/Railway
- Cada push → deploy automático

**Costo:** $0 (repos públicos)

---

## 🛠️ HERRAMIENTAS DE DESARROLLO

### VS Code
**¿Qué es?** Editor de código
**¿Para qué?** Escribir frontend + backend
**¿Por qué?**
- Gratis
- Extensions: Python, Tailwind CSS IntelliSense, Prettier
- Integración con Claude Code (el que estás usando ahora)

**Costo:** $0

---

### Postman / Thunder Client
**¿Qué es?** Cliente HTTP para probar APIs
**¿Para qué?** Probar endpoints FastAPI sin frontend
**¿Por qué?**
- Visualizar JSON responses
- Guardar colecciones de requests
- Compartir con equipo

**Costo:** $0 (plan free)

**Alternativa:** Usa Swagger UI en `/docs` (ya incluido en FastAPI)

---

## 📊 STACK COMPLETO - RESUMEN

### Lo que YA TIENES (✅ Completado)

| Tecnología | Propósito | Costo |
|------------|-----------|-------|
| **Python 3.13** | Backend language | $0 |
| **FastAPI** | API REST framework | $0 |
| **Pydantic** | Data validation | $0 |
| **Uvicorn** | ASGI server | $0 |
| **SQLite** | Base de datos (5K clientes) | $0 |
| **Faker** | Datos sintéticos | $0 |
| **Pandas** | Data processing | $0 |
| **NumPy** | Computación numérica | $0 |

**Archivos creados:** 9 Python files + 3 docs
**Líneas de código:** ~2,000 líneas
**Status:** ✅ **FUNCIONANDO - Probado**

---

### Lo que FALTA (Semana 2)

| Tecnología | Propósito | Costo | Tiempo |
|------------|-----------|-------|--------|
| **Next.js 14** | Frontend framework | $0 | 3-4 días |
| **TypeScript** | Type safety | $0 | - |
| **Tailwind CSS** | Styling | $0 | 1 día |
| **shadcn/ui** | UI components | $0 | 1 día |
| **Recharts** | Gráficas | $0 | 1 día |
| **Vercel** | Deploy frontend | $0 | 30 min |
| **Railway** | Deploy backend | $0-10 | 30 min |

**Archivos a crear:** ~15-20 React components
**Líneas de código:** ~1,500 líneas
**Tiempo estimado:** 5-7 días con LLMs

---

## 💰 COSTO TOTAL DEL DEMO

| Categoría | Demo | Producción |
|-----------|------|------------|
| **Backend desarrollo** | $0 | $205K USD |
| **Frontend desarrollo** | $0 | $50K USD |
| **Hosting (año 1)** | $0-120 | $2,400 |
| **Hardware diagnóstico** | $0 (simulado) | $868 USD |
| **TOTAL** | **$0-120** | **$258K USD** |

**Ahorro del demo:** 99.95% 🎉

---

## 🎯 DECISIONES CLAVE DEL STACK

### ¿Por qué NO usamos?

**❌ Django:** Más lento que FastAPI, over-engineered para API simple
**❌ PostgreSQL ahora:** Overkill para 5K registros, SQLite es suficiente
**❌ React puro:** Next.js da SSR + routing + optimizaciones gratis
**❌ Material UI:** shadcn/ui más moderno y customizable
**❌ Express.js:** Python mejor ecosystem para ML/AI
**❌ MongoDB:** Datos relacionales → SQL mejor fit

---

## 🚀 PRÓXIMOS PASOS

### Esta Semana (Backend ✅)
- [x] FastAPI + 3 agentes
- [x] SQLite + datos sintéticos
- [x] Testing + documentación

### Próxima Semana (Frontend)
- [ ] Setup Next.js 14 + TypeScript
- [ ] Componentes base (Layout, Nav, Cards)
- [ ] Páginas: Dashboard, Clientes, Analytics
- [ ] Integración con API FastAPI
- [ ] Deploy Vercel + Railway

### Demo Final (2 semanas)
- [ ] Dashboard interactivo funcionando
- [ ] 3 agentes demostrables en vivo
- [ ] Pitch deck con screenshots
- [ ] URL pública para inversionistas

---

## 📚 RECURSOS DE APRENDIZAJE

**Si quieres aprender más:**

- FastAPI docs: https://fastapi.tiangolo.com
- Next.js docs: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com/docs
- shadcn/ui: https://ui.shadcn.com
- Vercel deploy: https://vercel.com/docs

**Tiempo estimado de lectura:** 2-3 horas para entender el stack completo

---

**Última actualización:** 2025-10-15
**Versión:** 1.0
**Status:** Backend ✅ | Frontend ⏳
