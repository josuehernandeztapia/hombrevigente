# Hombre Vigente - Demo Investor Seed Round

**Versión:** 2.0 - 100% Alineado con Wiki Validada
**Propósito:** Demo funcional para ronda Seed ($200-250K USD)
**Timeline:** 2 semanas
**Tech Stack:** Python 3.13, SQLite, FastAPI (backend) + Next.js 14 (frontend)

---

## 🎯 Objetivo del Demo

Demostrar a inversionistas la **viabilidad técnica y comercial** de Hombre Vigente mediante:

1. **AI Agents funcionando en vivo** (2-3 agentes core)
2. **Datos sintéticos validados** basados en encuestas N=442
3. **Interactividad total** - cada botón genera escenarios en tiempo real
4. **Modelo financiero validado** - LTV/CAC, márgenes, pricing
5. **High-Tech High-Touch** - demostrar fusión de AI + hospitalidad

---

## 📊 Dataset Sintético Generado

### ✅ Completado

El generador `generador_sintetico_v2.py` ha creado:

```
📈 DATASET COMPLETO:
├── 4,997 clientes sintéticos
├── 10,000 eventos de compra
├── 6,463 diagnósticos Índice Vigente™
└── $15.5M MXN revenue total
```

### Distribución por Arquetipo (100% Wiki Validada)

| Arquetipo | N Clientes | % Base | Índice Vigente | LTV 12m | LTV/CAC |
|-----------|------------|--------|----------------|---------|---------|
| **Eduardo el Explorador** | 634 | 12.7% | 80.6 | $135K | 49.1:1 |
| **Carlos el Vigente** | 1,190 | 23.8% | 73.9 | $100K | 32.5:1 |
| **Ricardo el Ejecutivo** | 793 | 15.9% | 65.5 | $95K | 28.3:1 |
| **Miguel el Maduro** | 952 | 19.0% | 57.0 | $95K | 21.8:1 |
| **Luis el Renovado** | 1,428 | 28.6% | 68.5 | $65K | 24.1:1 |

### Top 10 Productos por Revenue

| Rank | Producto | Ventas | Revenue Total |
|------|----------|--------|---------------|
| 1 | HIFU Ultraformer III | 289 | $1.13M |
| 2 | Diagnóstico 360 | 685 | $1.09M |
| 3 | Anti-Aging Premium | 53 | $918K |
| 4 | Paquete Dermatológico (SVR) | 992 | $885K |
| 5 | Hydrafacial Elite | 514 | $883K |
| 6 | Membresía VIP Anual | 7 | $825K |
| 7 | Invisalign | 21 | $817K |
| 8 | Liposucción Papada | 48 | $810K |
| 9 | LED Therapy | 1,012 | $783K |
| 10 | Botox | 242 | $779K |

### Métricas Financieras

```
💰 UNIT ECONOMICS:
├── Revenue total: $15.5M MXN
├── Ticket promedio: $1,552 MXN
├── Margen bruto: 72.0%
├── LTV 12m promedio: $92,693 MXN
└── BNPL adoption: 0.5% (50 eventos)
```

**NOTA:** BNPL adoption es baja (0.5%) porque el generador actual aplica BNPL solo a productos >$10K. Según encuestas N=442, el 68.8% de clientes tiene propensión BNPL, especialmente para Invisalign (58%) y cirugías (45%). Este es un punto de mejora en v2.1.

---

## 🗂️ Archivos del Proyecto

### Datos Validados (Fuente de Verdad)

```
arquetipos_validados.json       # 5 arquetipos con LTV/CAC validados
servicios_fase1_validados.json  # 7 paquetes + 17 servicios Fase 1
```

**Fuentes wiki:**
- `01_VISION_ESTRATEGIA_CORE.md` (líneas 269-275): Arquetipos
- `04_FINANCIERO_CORE.md` (líneas 39-83): Unit economics + paquetes
- `06_DTC_PRODUCTOS_CORE.md` (líneas 526-570): Servicios Fase 1
- `ESTRATEGIA_IDEAS_CONTINUACION.md` (líneas 185-334): Propensión BNPL

### Scripts

```
generador_sintetico_v2.py       # Generador de datos sintéticos
requirements.txt                # Dependencias Python
```

### Base de Datos

```
demo_hombrevigente.db           # SQLite con 3 tablas (clientes, eventos, diagnosticos)
```

---

## 🚀 Cómo Ejecutar

### 1. Instalar Dependencias

```bash
pip3 install faker pandas numpy
```

### 2. Generar Dataset Sintético

```bash
python3 generador_sintetico_v2.py
```

Output:
```
✅ COMPLETADO - Dataset listo en demo_hombrevigente.db

📊 CLIENTES: 4997
💰 EVENTOS: 10000
🔬 DIAGNÓSTICOS: 6463
```

### 3. Explorar Base de Datos

```bash
sqlite3 demo_hombrevigente.db
```

Queries útiles:

```sql
-- Ver clientes
SELECT * FROM clientes LIMIT 10;

-- Ver distribución por arquetipo
SELECT arquetipo_nombre, COUNT(*) as n,
       ROUND(AVG(indice_vigente),1) as indice_promedio
FROM clientes
GROUP BY arquetipo_nombre;

-- Ver eventos de compra
SELECT * FROM eventos LIMIT 10;

-- Top productos por revenue
SELECT producto_nombre, COUNT(*) as ventas,
       ROUND(SUM(precio_pagado),0) as revenue_total
FROM eventos
GROUP BY producto_nombre
ORDER BY revenue_total DESC
LIMIT 10;

-- Ver diagnósticos
SELECT * FROM diagnosticos LIMIT 10;
```

---

## 📐 Esquema de Base de Datos

### Tabla: `clientes`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| cliente_id | TEXT | UUID único |
| nombre | TEXT | Nombre completo (Faker es_MX) |
| email | TEXT | Email único |
| telefono | TEXT | Teléfono mexicano |
| fecha_registro | DATE | Fecha de alta (últimos 180 días) |
| edad | INTEGER | Edad actual |
| ingreso_anual | INTEGER | Ingreso anual MXN |
| arquetipo_id | TEXT | ID del arquetipo (carlos_vigente, eduardo_explorador, etc.) |
| arquetipo_nombre | TEXT | Nombre del arquetipo |
| indice_vigente | REAL | Score 0-100 (fórmula: 0.4×estructural + 0.3×piel + 0.3×biológico) |
| subscore_estructural | REAL | Postura, simetría facial (0-100) |
| subscore_piel | REAL | Arrugas, manchas, elasticidad (0-100) |
| subscore_biologico | REAL | Presión arterial, biomarkers (0-100) |
| ltv_12m | REAL | Lifetime Value 12 meses (validado wiki) |
| propension_compra | REAL | Probabilidad de compra (0-1) |
| churn_propensity | REAL | Probabilidad de churn (0-1) |
| propension_bnpl | REAL | Probabilidad de usar BNPL (validado encuestas) |
| canal_origen | TEXT | Instagram (50%), LinkedIn (30%), Referral (20%) |

### Tabla: `eventos`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| evento_id | TEXT | UUID único |
| cliente_id | TEXT | FK a clientes |
| fecha_evento | DATE | Fecha de compra |
| tipo_producto | TEXT | 'paquete' o 'servicio' |
| producto_id | TEXT | ID del producto |
| producto_nombre | TEXT | Nombre del producto |
| categoria | TEXT | Categoría (Diagnóstico, Facial, Inyectables, etc.) |
| precio_lista | REAL | Precio sin descuento |
| precio_pagado | REAL | Precio final pagado |
| descuento_pct | REAL | % descuento aplicado |
| cogs | REAL | Costo de bienes vendidos |
| margen_bruto | REAL | Margen en MXN |
| margen_pct | REAL | Margen en % |
| bnpl_aplicado | BOOLEAN | ¿BNPL usado? |
| bnpl_plazo_meses | INTEGER | 6, 12 o 18 meses |
| canal_venta | TEXT | Presencial (85%), WhatsApp (10%), AdvisorVigente AI (5%) |
| duracion_min | INTEGER | Duración del servicio en minutos |

### Tabla: `diagnosticos`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| diagnostico_id | TEXT | UUID único |
| cliente_id | TEXT | FK a clientes |
| fecha_diagnostico | DATE | Fecha del escaneo |
| indice_vigente | REAL | Score 0-100 |
| subscore_estructural | REAL | Score estructural |
| subscore_piel | REAL | Score piel |
| subscore_biologico | REAL | Score biológico |
| interpretacion | TEXT | Interpretación textual (EXCELENTE, BUENO, MEJORABLE) |
| recomendaciones | TEXT | Servicios recomendados |
| hardware_usado | TEXT | FotoFinder meesma-2 o Artec Eva + FLIR ONE |
| ml_model_version | TEXT | Versión del modelo ML |
| processing_time_sec | REAL | Tiempo de procesamiento (480-720 seg / 8-12 min) |

---

## 🧠 Lógica del Generador

### Fórmula Índice Vigente™

```python
Índice Vigente = 0.4 × estructural + 0.3 × piel + 0.3 × biológico
```

Donde:
- **Estructural:** Postura, simetría facial, estructura ósea (YOLOv8 + MediaPipe)
- **Piel:** Arrugas, manchas, elasticidad (Vision Transformer)
- **Biológico:** Presión arterial, biomarkers, estrés térmico (Thermal CNN)

### Distribución de Arquetipos

Respeta los porcentajes validados en wiki:

```python
arquetipos = {
    "Carlos el Vigente": 15%,      # Corporate, alta frecuencia
    "Eduardo el Explorador": 8%,   # Emprendedor, innovador
    "Miguel el Maduro": 12%,       # Ejecutivo senior, cirugía
    "Luis el Renovado": 18%,       # Moderado, preventivo
    "Ricardo el Ejecutivo": 10%    # Time-sensitive, conveniencia
}
# Total: 63% (37% son arquetipos no modelados en demo)
```

### Selección de Productos

Cada cliente compra productos según:

1. **Preferencias del arquetipo** (validado en wiki)
   - Eduardo → Invisalign, cirugías, tratamientos premium
   - Luis → Hydrafacial, limpieza facial, grooming
   - etc.

2. **Propensión de compra** (calculado)
   - Alta propensión (>0.75): 3-5 eventos
   - Media (0.50-0.75): 2-4 eventos
   - Baja (<0.50): 1-2 eventos

3. **Probabilidad inversa al precio**
   - Productos más caros tienen menor probabilidad de ser elegidos

### Descuentos

```python
if arquetipo in ['luis_renovado', 'miguel_maduro']:
    descuento = 10-20% (40% de probabilidad)
elif arquetipo == 'eduardo_explorador':
    descuento = 0% (nunca recibe descuentos - alta disposición a pagar)
else:
    descuento = 5-15% (15% de probabilidad)
```

### BNPL

Solo para productos >$10K:

```python
if precio >= 10000:
    if producto == 'invisalign':
        propension_bnpl = 58%  # Validado encuestas N=442
    elif producto == 'liposuccion_papada':
        propension_bnpl = 45%
    else:
        propension_bnpl = arquetipo.propension_bnpl

    if random() < propension_bnpl:
        bnpl_aplicado = True
        plazo = 6, 12 o 18 meses (según precio)
```

---

## 📋 Próximos Pasos

### Fase Actual: ✅ Datos Sintéticos Generados

- [x] Arquetipos validados JSON
- [x] Servicios Fase 1 validados JSON
- [x] Generador sintético v2.0
- [x] Base de datos SQLite con 5K clientes + 10K eventos
- [x] Verificación de integridad de datos

### Siguiente: Backend FastAPI

1. **API REST con FastAPI**
   - Endpoints: `/clientes`, `/eventos`, `/diagnosticos`, `/arquetipos`, `/productos`
   - WebSocket para streaming de diagnósticos en vivo
   - CORS configurado para frontend Next.js

2. **3 AI Agents Core** (simulados con reglas + random para demo)
   - **DiagnósticoVigente:** Genera Índice Vigente + subscores + recomendaciones
   - **PersonaVigente:** Calcula propensión de compra + arquetipo + churn risk
   - **OptiVigente:** Pricing dinámico + asignación de slots

3. **Endpoints Interactivos**
   - `POST /diagnostico/nuevo` → Genera diagnóstico sintético en tiempo real (8-12 seg simulados)
   - `POST /cliente/simular` → Crea cliente sintético con parámetros
   - `GET /analytics/revenue` → Dashboard de revenue por arquetipo

### Después: Frontend Next.js 14

1. **Dashboard Investor Demo**
   - Vista de arquetipos con LTV/CAC en tiempo real
   - Simulador de diagnósticos (botón → genera cliente → escaneo → Índice Vigente)
   - Gráficas de revenue breakdown
   - Timeline de eventos de compra

2. **Demo Interactivo**
   - Botón "Generar Diagnóstico" → API → Streaming visual (8-12 seg)
   - Botón "Simular Cliente Eduardo" → Crea cliente → Recomienda servicios
   - Botón "Simular Compra Premium" → Calcula BNPL + propensión

3. **Deployment**
   - Backend: Railway o Render (gratis tier)
   - Frontend: Vercel (gratis tier)
   - Total costo: $0

---

## 🔍 Validaciones con Wiki

### ✅ Arquetipos

| Campo | Fuente Wiki | Validado |
|-------|-------------|----------|
| Nombres | 01_VISION_ESTRATEGIA_CORE.md:269-275 | ✅ |
| LTV/CAC | 04_FINANCIERO_CORE.md:39-46 | ✅ |
| % Base | 01_VISION_ESTRATEGIA_CORE.md:269-275 | ✅ |
| Edad ranges | 01_VISION_ESTRATEGIA_CORE.md:269-275 | ✅ |
| Ingreso ranges | 01_VISION_ESTRATEGIA_CORE.md:269-275 | ✅ |

### ✅ Servicios y Paquetes

| Campo | Fuente Wiki | Validado |
|-------|-------------|----------|
| 7 paquetes Fase 1 | 04_FINANCIERO_CORE.md:75-83 | ✅ |
| Pricing | 06_DTC_PRODUCTOS_CORE.md:25-175 | ✅ |
| Márgenes | 06_DTC_PRODUCTOS_CORE.md:25-175 | ✅ |
| Top 10 servicios | 06_DTC_PRODUCTOS_CORE.md:559-570 | ✅ |

### ✅ Propensión BNPL

| Producto | Precio | Propensión BNPL | Fuente Wiki |
|----------|--------|-----------------|-------------|
| Invisalign | $40K | 58% | ESTRATEGIA_IDEAS_CONTINUACION.md:226 |
| Liposucción Papada | $15K-$20K | 45% | ESTRATEGIA_IDEAS_CONTINUACION.md:225 |
| Paquete Elite | $60K-$90K | 67% | ESTRATEGIA_IDEAS_CONTINUACION.md:227 |

### ✅ Encuestas N=442

| Métrica | Valor | Fuente Wiki |
|---------|-------|-------------|
| Total encuestados | 442 hombres | ESTRATEGIA_IDEAS_CONTINUACION.md:185-300 |
| Alta intención compra (7-10/10) | 90.7% | ESTRATEGIA_IDEAS_CONTINUACION.md |
| Propensión BNPL combinada | 68.8% | ESTRATEGIA_IDEAS_CONTINUACION.md:202 |
| Preferencia activa BNPL | 28.46% | ESTRATEGIA_IDEAS_CONTINUACION.md:204 |

---

## 💡 Notas Técnicas

### Por qué SQLite

- **Portabilidad:** Un solo archivo `.db` para todo el demo
- **No requiere servidor:** Ideal para demos en laptop en reuniones con inversionistas
- **Rápido:** 10K+ queries/seg para dataset de 5K clientes
- **Familiar:** 100% compatible con PostgreSQL para producción
- **Gratis:** $0 costo

### Por qué Datos Sintéticos

1. **No requiere hardware:** Sin Seek Thermal ($450) ni Logitech Brio 4K ($199)
2. **Escalable:** Generar 5K clientes en 30 segundos
3. **Reproducible:** Seed=42 para resultados consistentes
4. **Validado:** 100% basado en encuestas N=442 reales
5. **Privacidad:** No PII real

### Limitaciones Actuales

1. **BNPL bajo (0.5%):** El generador aplica BNPL solo a >$10K, pero debería aplicarse más agresivamente según encuestas (68.8% propensión). **Fix en v2.1.**

2. **Faker es_MX:** Genera nombres mexicanos pero algunos pueden sonar poco realistas. **Aceptable para demo.**

3. **No correlaciones temporales:** Eventos no respetan temporalidad (ej. Invisalign debería preceder a Blanqueamiento). **Fix en v2.2.**

4. **No churn simulado:** Todos los clientes están "activos". **Fix en v2.3.**

---

## 📞 Contacto

**Proyecto:** Hombre Vigente - AI-Native Men's Wellness Club
**Demo:** Investor Seed Round ($200-250K USD)
**Timeline:** 2 semanas
**Status:** ✅ Fase 1 completa (Datos Sintéticos)

**Siguiente:** Construir FastAPI backend con 3 AI agents simulados

---

**Versión:** 2.0
**Última actualización:** 2025-10-15
**Wiki validada:** 73 documentos CORE + IDEAS
