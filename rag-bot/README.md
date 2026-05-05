# 🚀 Hombre Vigente - Demo Investor Seed Round

**Carpeta DEMO** - Aislada de la wiki principal

Esta carpeta contiene todo el código y datos para el **demo funcional** dirigido a inversionistas para la ronda Seed ($200-250K USD).

---

## 📁 Estructura de Archivos

```
DEMO/
├── README.md                          # Este archivo
├── README_DEMO_INVESTOR.md            # Documentación completa del demo
├── arquetipos_validados.json          # 5 arquetipos con LTV/CAC validados
├── servicios_fase1_validados.json     # 7 paquetes + 17 servicios Fase 1
├── generador_sintetico_v2.py          # Script generador de datos sintéticos
├── requirements.txt                   # Dependencias Python
└── demo_hombrevigente.db              # Base de datos SQLite (5K clientes, 10K eventos)
```

---

## ⚡ Quick Start

### 1. Instalar dependencias

```bash
cd DEMO
pip3 install -r requirements.txt
```

### 2. Generar dataset sintético

```bash
python3 generador_sintetico_v2.py
```

Output esperado:
```
✅ COMPLETADO - Dataset listo en demo_hombrevigente.db

📊 CLIENTES: ~5000
💰 EVENTOS: ~10000
🔬 DIAGNÓSTICOS: ~6500
💰 REVENUE TOTAL: ~$15M MXN
```

### 3. Explorar base de datos

```bash
sqlite3 demo_hombrevigente.db
```

Queries útiles:
```sql
-- Ver arquetipos
SELECT arquetipo_nombre, COUNT(*) as n,
       ROUND(AVG(indice_vigente),1) as indice_promedio
FROM clientes
GROUP BY arquetipo_nombre;

-- Top productos por revenue
SELECT producto_nombre, COUNT(*) as ventas,
       ROUND(SUM(precio_pagado),0) as revenue_total
FROM eventos
GROUP BY producto_nombre
ORDER BY revenue_total DESC
LIMIT 10;
```

---

## 📖 Documentación Completa

Ver **[README_DEMO_INVESTOR.md](README_DEMO_INVESTOR.md)** para:
- Arquitectura completa del demo
- Esquema de base de datos
- Lógica del generador
- Validaciones con wiki
- Roadmap (Backend FastAPI + Frontend Next.js)

---

## 🎯 Objetivo del Demo

Demostrar a inversionistas:
1. **AI Agents funcionando** (DiagnósticoVigente, PersonaVigente, OptiVigente)
2. **Modelo validado** con encuestas N=442
3. **Unit economics** - LTV/CAC ratios de 21.8:1 hasta 49.1:1
4. **Interactividad total** - cada botón genera escenarios en vivo
5. **High-Tech High-Touch** - fusión de AI + hospitalidad masculina

---

## ✅ Datos 100% Validados

Todo está alineado con la wiki:
- ✅ 5 arquetipos de `01_VISION_ESTRATEGIA_CORE.md`
- ✅ Unit economics de `04_FINANCIERO_CORE.md`
- ✅ Servicios Fase 1 de `06_DTC_PRODUCTOS_CORE.md`
- ✅ Propensión BNPL de `ESTRATEGIA_IDEAS_CONTINUACION.md` (encuestas N=442)

---

## 🔄 Próximos Pasos

### Fase Actual: ✅ Datos Sintéticos Generados

### Siguiente: Backend FastAPI (Semana 1)
- API REST con endpoints `/clientes`, `/eventos`, `/diagnosticos`
- WebSocket para streaming de diagnósticos
- 3 AI agents simulados

### Después: Frontend Next.js (Semana 2)
- Dashboard investor con métricas en vivo
- Simulador interactivo de diagnósticos
- Deploy en Vercel (gratis)

---

**Versión:** 2.0
**Última actualización:** 2025-10-15
**Status:** ✅ Fase 1 completa
