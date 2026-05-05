#!/usr/bin/env python3
"""
Generador de Datos Sintéticos - Hombre Vigente Demo Investor
Versión 2.0 - 100% Alineado con Wiki Validada

Genera datos sintéticos basados ÚNICAMENTE en:
- 5 arquetipos validados (N=442 encuestas)
- 7 paquetes Fase 1 + 17 servicios individuales validados
- Pricing y márgenes reales del modelo financiero
- Propensiones BNPL validadas por encuestas

Fuentes:
- 01_VISION_ESTRATEGIA_CORE.md (arquetipos)
- 04_FINANCIERO_CORE.md (unit economics)
- 06_DTC_PRODUCTOS_CORE.md (servicios Fase 1)
- ESTRATEGIA_IDEAS_CONTINUACION.md (propensión BNPL)
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random
import numpy as np
import pandas as pd
from faker import Faker

# Configuración
FAKE = Faker('es_MX')
Faker.seed(42)
random.seed(42)
np.random.seed(42)

N_CLIENTES = 5000
N_EVENTOS = 10000

# Archivos de entrada
ARQUETIPOS_FILE = "arquetipos_validados.json"
SERVICIOS_FILE = "servicios_fase1_validados.json"
DB_FILE = "demo_hombrevigente.db"


def cargar_datos_validados() -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Carga arquetipos y servicios validados desde JSON

    Returns:
        arquetipos: Lista de 5 arquetipos validados
        paquetes: Lista de 7 paquetes Fase 1
        servicios: Lista de 17 servicios individuales
    """
    with open(ARQUETIPOS_FILE, 'r', encoding='utf-8') as f:
        data_arq = json.load(f)
        arquetipos = data_arq['arquetipos']

    with open(SERVICIOS_FILE, 'r', encoding='utf-8') as f:
        data_srv = json.load(f)
        paquetes = data_srv['paquetes_fase1']
        servicios = data_srv['servicios_individuales_fase1']

    print(f"✅ Cargados: {len(arquetipos)} arquetipos, {len(paquetes)} paquetes, {len(servicios)} servicios")
    return arquetipos, paquetes, servicios


def crear_base_datos():
    """
    Crea el esquema SQLite para el demo

    Tablas:
    - clientes: Datos PII + arquetipo + scoring
    - eventos: Compras de paquetes/servicios
    - diagnosticos: Resultados de escaneos Índice Vigente
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tabla clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        cliente_id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        telefono TEXT,
        fecha_registro DATE NOT NULL,
        fecha_nacimiento DATE,
        edad INTEGER,
        ingreso_anual INTEGER,
        arquetipo_id TEXT NOT NULL,
        arquetipo_nombre TEXT NOT NULL,
        indice_vigente REAL,
        subscore_estructural REAL,
        subscore_piel REAL,
        subscore_biologico REAL,
        ltv_12m REAL,
        propension_compra REAL,
        churn_propensity REAL,
        propension_bnpl REAL,
        canal_origen TEXT,
        ciudad TEXT,
        codigo_postal TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabla eventos (compras)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        evento_id TEXT PRIMARY KEY,
        cliente_id TEXT NOT NULL,
        fecha_evento DATE NOT NULL,
        tipo_producto TEXT NOT NULL,
        producto_id TEXT NOT NULL,
        producto_nombre TEXT NOT NULL,
        categoria TEXT,
        precio_lista REAL NOT NULL,
        precio_pagado REAL NOT NULL,
        descuento_pct REAL DEFAULT 0,
        descuento_aplicado REAL DEFAULT 0,
        cogs REAL NOT NULL,
        margen_bruto REAL NOT NULL,
        margen_pct REAL NOT NULL,
        bnpl_aplicado BOOLEAN DEFAULT 0,
        bnpl_plazo_meses INTEGER,
        canal_venta TEXT,
        staff_id TEXT,
        duracion_min INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )
    """)

    # Tabla diagnósticos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diagnosticos (
        diagnostico_id TEXT PRIMARY KEY,
        cliente_id TEXT NOT NULL,
        fecha_diagnostico DATE NOT NULL,
        indice_vigente REAL NOT NULL,
        subscore_estructural REAL NOT NULL,
        subscore_piel REAL NOT NULL,
        subscore_biologico REAL NOT NULL,
        interpretacion TEXT,
        recomendaciones TEXT,
        hardware_usado TEXT,
        ml_model_version TEXT,
        processing_time_sec REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Base de datos creada: {DB_FILE}")


def calcular_indice_vigente(estructural: float, piel: float, biologico: float) -> float:
    """
    Calcula Índice Vigente según fórmula oficial:
    Índice Vigente = 0.4 × estructural + 0.3 × piel + 0.3 × biológico

    Args:
        estructural: Score 0-100 (postura, simetría facial)
        piel: Score 0-100 (arrugas, manchas, elasticidad)
        biologico: Score 0-100 (presión arterial, biomarkers)

    Returns:
        Índice Vigente: Score 0-100
    """
    # Usar float para evitar errores de redondeo
    return float(round(0.4 * estructural + 0.3 * piel + 0.3 * biologico, 1))


def generar_clientes(arquetipos: List[Dict]) -> pd.DataFrame:
    """
    Genera N clientes sintéticos respetando distribución de arquetipos

    Distribución validada:
    - Carlos el Vigente: 15%
    - Eduardo el Explorador: 8%
    - Miguel el Maduro: 12%
    - Luis el Renovado: 18%
    - Ricardo el Ejecutivo: 10%
    - Otros arquetipos: 37% (no modelados en demo)

    Returns:
        DataFrame con clientes sintéticos
    """
    clientes = []

    # Calcular distribución de arquetipos
    total_peso = sum(arq['peso_poblacion'] for arq in arquetipos)

    for arq in arquetipos:
        # Número de clientes para este arquetipo
        n_arq = int(N_CLIENTES * arq['peso_poblacion'] / total_peso)

        for _ in range(n_arq):
            # Generar edad dentro del rango del arquetipo
            edad = random.randint(arq['edad_min'], arq['edad_max'])
            fecha_nacimiento = datetime.now() - timedelta(days=edad*365)

            # Generar ingreso dentro del rango
            ingreso = random.randint(
                arq['ingreso_anual_min'],
                arq['ingreso_anual_max']
            )

            # Generar subscores con ruido gaussiano
            subscore_est = np.clip(
                random.gauss(
                    (arq['subscores']['estructural_min'] + arq['subscores']['estructural_max']) / 2,
                    5
                ),
                arq['subscores']['estructural_min'],
                arq['subscores']['estructural_max']
            )

            subscore_piel = np.clip(
                random.gauss(
                    (arq['subscores']['piel_min'] + arq['subscores']['piel_max']) / 2,
                    5
                ),
                arq['subscores']['piel_min'],
                arq['subscores']['piel_max']
            )

            subscore_bio = np.clip(
                random.gauss(
                    (arq['subscores']['biologico_min'] + arq['subscores']['biologico_max']) / 2,
                    5
                ),
                arq['subscores']['biologico_min'],
                arq['subscores']['biologico_max']
            )

            # Calcular Índice Vigente
            indice = calcular_indice_vigente(subscore_est, subscore_piel, subscore_bio)

            # Propensión de compra: mayor score = mayor propensión
            propension_compra = (indice / 100) * random.uniform(0.85, 1.0)

            # Canal origen: Instagram 50%, LinkedIn 30%, Referral 20%
            canal = random.choices(
                ['Instagram', 'LinkedIn', 'Referral'],
                weights=[0.50, 0.30, 0.20]
            )[0]

            cliente = {
                'cliente_id': str(uuid.uuid4()),
                'nombre': FAKE.name_male(),
                'email': FAKE.email(),
                'telefono': FAKE.phone_number(),
                'fecha_registro': FAKE.date_between(start_date='-180d', end_date='today'),
                'fecha_nacimiento': fecha_nacimiento.date(),
                'edad': edad,
                'ingreso_anual': ingreso,
                'arquetipo_id': arq['id'],
                'arquetipo_nombre': arq['nombre'],
                'indice_vigente': indice,
                'subscore_estructural': round(subscore_est, 1),
                'subscore_piel': round(subscore_piel, 1),
                'subscore_biologico': round(subscore_bio, 1),
                'ltv_12m': arq['ltv_12m'],
                'propension_compra': round(propension_compra, 3),
                'churn_propensity': arq['churn_propensity'],
                'propension_bnpl': arq['propension_bnpl'],
                'canal_origen': canal,
                'ciudad': FAKE.city(),
                'codigo_postal': FAKE.postcode()
            }

            clientes.append(cliente)

    df = pd.DataFrame(clientes)
    print(f"\n✅ Generados {len(df)} clientes")
    print("\nDistribución por arquetipo:")
    print(df['arquetipo_nombre'].value_counts())
    print(f"\nÍndice Vigente promedio: {df['indice_vigente'].mean():.1f}")
    print(f"Propensión compra promedio: {df['propension_compra'].mean():.3f}")

    return df


def generar_eventos(
    clientes_df: pd.DataFrame,
    arquetipos: List[Dict],
    paquetes: List[Dict],
    servicios: List[Dict]
) -> pd.DataFrame:
    """
    Genera N eventos de compra respetando preferencias por arquetipo

    Lógica:
    1. Cada cliente tiene 1-5 eventos según su propensión de compra
    2. Productos elegidos según preferencias del arquetipo
    3. BNPL aplicado según propensión y precio del producto
    4. Descuentos aplicados a arquetipos de menor LTV (Luis, Miguel)

    Returns:
        DataFrame con eventos sintéticos
    """
    eventos = []

    # Crear lookup de arquetipos
    arq_lookup = {arq['id']: arq for arq in arquetipos}

    # Todos los productos (paquetes + servicios individuales)
    productos = []
    for paq in paquetes:
        productos.append({
            'tipo': 'paquete',
            'id': paq['id'],
            'nombre': paq['nombre'],
            'precio': paq['precio_lista'],
            'cogs': paq['cogs'],
            'margen_pct': paq['margen_pct'],
            'duracion_min': paq['duracion_min'],
            'categoria': 'Paquete',
            'arquetipos_target': paq['arquetipos_target']
        })

    for srv in servicios:
        productos.append({
            'tipo': 'servicio',
            'id': srv['id'],
            'nombre': srv['nombre'],
            'precio': srv['precio_lista'],
            'cogs': srv['cogs'],
            'margen_pct': srv['margen_pct'],
            'duracion_min': srv['duracion_min'],
            'categoria': srv['categoria'],
            'arquetipos_target': srv['arquetipos_target']
        })

    for _, cliente in clientes_df.iterrows():
        arq = arq_lookup[cliente['arquetipo_id']]

        # Número de eventos según propensión de compra
        if cliente['propension_compra'] > 0.75:
            n_eventos_cliente = random.randint(3, 5)
        elif cliente['propension_compra'] > 0.50:
            n_eventos_cliente = random.randint(2, 4)
        else:
            n_eventos_cliente = random.randint(1, 2)

        # Productos preferidos del arquetipo
        productos_preferidos = [
            p for p in productos
            if cliente['arquetipo_id'] in p['arquetipos_target']
            or 'todos' in p['arquetipos_target']
        ]

        if not productos_preferidos:
            productos_preferidos = productos  # Fallback

        for i in range(n_eventos_cliente):
            # Elegir producto ponderado por precio (más caros = menos probable)
            producto = random.choices(
                productos_preferidos,
                weights=[1 / (p['precio'] / 1000 + 1) for p in productos_preferidos]
            )[0]

            # Fecha evento (después de registro)
            fecha_evento = FAKE.date_between(
                start_date=cliente['fecha_registro'],
                end_date='today'
            )

            # Aplicar descuento según arquetipo
            # Luis el Renovado y Miguel el Maduro reciben más descuentos
            if cliente['arquetipo_id'] in ['luis_renovado', 'miguel_maduro']:
                if random.random() < 0.40:  # 40% chance descuento
                    descuento_pct = random.uniform(10, 20)
                else:
                    descuento_pct = 0
            elif cliente['arquetipo_id'] == 'eduardo_explorador':
                # Eduardo nunca recibe descuentos (alta disposición a pagar)
                descuento_pct = 0
            else:
                if random.random() < 0.15:  # 15% chance descuento
                    descuento_pct = random.uniform(5, 15)
                else:
                    descuento_pct = 0

            precio_lista = producto['precio']
            descuento_aplicado = precio_lista * (descuento_pct / 100)
            precio_pagado = precio_lista - descuento_aplicado

            # BNPL: aplicar según propensión y precio
            bnpl_aplicado = False
            bnpl_plazo = None

            if precio_lista >= 10000:  # Solo productos >$10K
                # Probabilidad BNPL = propensión arquetipo × factor precio
                prob_bnpl = cliente['propension_bnpl']

                # Para Invisalign ($40K): 58% propensión adicional
                if producto['id'] == 'invisalign':
                    prob_bnpl = min(0.58, prob_bnpl + 0.30)
                # Para cirugías ($15K-$20K): 45% propensión adicional
                elif producto['id'] == 'liposuccion_papada':
                    prob_bnpl = min(0.45, prob_bnpl + 0.25)

                if random.random() < prob_bnpl:
                    bnpl_aplicado = True
                    # Plazo según precio: $10-20K = 6m, $20-40K = 12m, >$40K = 18m
                    if precio_lista < 20000:
                        bnpl_plazo = 6
                    elif precio_lista < 40000:
                        bnpl_plazo = 12
                    else:
                        bnpl_plazo = 18

            # Canal venta: 85% presencial, 15% WhatsApp/AdvisorVigente
            canal_venta = random.choices(
                ['Presencial', 'WhatsApp', 'AdvisorVigente AI'],
                weights=[0.85, 0.10, 0.05]
            )[0]

            # Staff ID (simulado)
            staff_id = f"STAFF-{random.randint(1, 15):03d}"

            evento = {
                'evento_id': str(uuid.uuid4()),
                'cliente_id': cliente['cliente_id'],
                'fecha_evento': fecha_evento,
                'tipo_producto': producto['tipo'],
                'producto_id': producto['id'],
                'producto_nombre': producto['nombre'],
                'categoria': producto['categoria'],
                'precio_lista': precio_lista,
                'precio_pagado': precio_pagado,
                'descuento_pct': round(descuento_pct, 2),
                'descuento_aplicado': round(descuento_aplicado, 2),
                'cogs': producto['cogs'],
                'margen_bruto': round(precio_pagado - producto['cogs'], 2),
                'margen_pct': round((precio_pagado - producto['cogs']) / precio_pagado * 100, 2),
                'bnpl_aplicado': bnpl_aplicado,
                'bnpl_plazo_meses': bnpl_plazo,
                'canal_venta': canal_venta,
                'staff_id': staff_id,
                'duracion_min': producto['duracion_min']
            }

            eventos.append(evento)

            # Limite de eventos totales
            if len(eventos) >= N_EVENTOS:
                break

        if len(eventos) >= N_EVENTOS:
            break

    df = pd.DataFrame(eventos)
    print(f"\n✅ Generados {len(df)} eventos")
    print(f"\nRevenue total: ${df['precio_pagado'].sum():,.0f} MXN")
    print(f"Margen bruto promedio: {df['margen_pct'].mean():.1f}%")
    print(f"Descuento promedio: {df['descuento_pct'].mean():.1f}%")
    print(f"BNPL aplicado: {df['bnpl_aplicado'].sum()} eventos ({df['bnpl_aplicado'].sum()/len(df)*100:.1f}%)")

    print("\nTop 5 productos por revenue:")
    top_productos = df.groupby('producto_nombre')['precio_pagado'].sum().sort_values(ascending=False).head(5)
    print(top_productos)

    return df


def generar_diagnosticos(clientes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera diagnósticos Índice Vigente para clientes

    Cada cliente tiene 1-3 diagnósticos según engagement

    Returns:
        DataFrame con diagnósticos sintéticos
    """
    diagnosticos = []

    for _, cliente in clientes_df.iterrows():
        # Clientes con alta propensión tienen más diagnósticos
        if cliente['propension_compra'] > 0.70:
            n_diag = random.randint(2, 3)
        else:
            n_diag = 1

        for i in range(n_diag):
            # Primer diagnóstico = registro, siguientes = trimestral
            if i == 0:
                fecha_diag = cliente['fecha_registro']
            else:
                fecha_diag = cliente['fecha_registro'] + timedelta(days=90*i + random.randint(-15, 15))

            # Simular mejora gradual en Índice Vigente
            mejora = i * random.uniform(2, 5)
            indice = min(100, cliente['indice_vigente'] + mejora)

            # Subscores también mejoran
            subscore_est = min(100, cliente['subscore_estructural'] + mejora * 0.8)
            subscore_piel = min(100, cliente['subscore_piel'] + mejora * 1.2)
            subscore_bio = min(100, cliente['subscore_biologico'] + mejora * 1.0)

            # Interpretación según score
            if indice >= 75:
                interpretacion = "EXCELENTE: Índice Vigente superior. Continuar con programa de mantenimiento."
            elif indice >= 60:
                interpretacion = "BUENO: Índice Vigente dentro de rango saludable. Oportunidades de mejora identificadas."
            else:
                interpretacion = "MEJORABLE: Índice Vigente indica áreas de atención prioritaria."

            # Recomendaciones según subscores
            recomendaciones = []
            if subscore_est < 70:
                recomendaciones.append("Lifting no invasivo (HIFU, Hilos PDO)")
            if subscore_piel < 65:
                recomendaciones.append("Rejuvenecimiento facial (Hydrafacial, PRP)")
            if subscore_bio < 65:
                recomendaciones.append("Evaluación nutricional y suplementación")

            if not recomendaciones:
                recomendaciones.append("Mantenimiento preventivo")

            # Hardware usado: 70% FotoFinder, 30% Artec Eva
            hardware = random.choices(
                ['FotoFinder meesma-2 + FLIR ONE', 'Artec Eva + FLIR ONE'],
                weights=[0.70, 0.30]
            )[0]

            # ML model version
            ml_version = random.choice(['v1.2.0', 'v1.2.1', 'v1.3.0'])

            # Processing time: 8-12 min
            processing_time = random.uniform(480, 720)

            diagnostico = {
                'diagnostico_id': str(uuid.uuid4()),
                'cliente_id': cliente['cliente_id'],
                'fecha_diagnostico': fecha_diag,
                'indice_vigente': round(indice, 1),
                'subscore_estructural': round(subscore_est, 1),
                'subscore_piel': round(subscore_piel, 1),
                'subscore_biologico': round(subscore_bio, 1),
                'interpretacion': interpretacion,
                'recomendaciones': '; '.join(recomendaciones),
                'hardware_usado': hardware,
                'ml_model_version': ml_version,
                'processing_time_sec': round(processing_time, 1)
            }

            diagnosticos.append(diagnostico)

    df = pd.DataFrame(diagnosticos)
    print(f"\n✅ Generados {len(df)} diagnósticos")
    print(f"Índice Vigente promedio: {df['indice_vigente'].mean():.1f}")
    print(f"Processing time promedio: {df['processing_time_sec'].mean()/60:.1f} min")

    return df


def guardar_en_sqlite(clientes_df: pd.DataFrame, eventos_df: pd.DataFrame, diagnosticos_df: pd.DataFrame):
    """
    Guarda los DataFrames en SQLite
    """
    conn = sqlite3.connect(DB_FILE)

    clientes_df.to_sql('clientes', conn, if_exists='replace', index=False)
    eventos_df.to_sql('eventos', conn, if_exists='replace', index=False)
    diagnosticos_df.to_sql('diagnosticos', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

    print(f"\n✅ Datos guardados en {DB_FILE}")


def mostrar_estadisticas():
    """
    Muestra estadísticas finales del dataset generado
    """
    conn = sqlite3.connect(DB_FILE)

    print("\n" + "="*60)
    print("ESTADÍSTICAS FINALES - DEMO HOMBRE VIGENTE")
    print("="*60)

    # Clientes
    df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    print(f"\n📊 CLIENTES: {len(df_clientes)}")
    print(f"   - Índice Vigente promedio: {df_clientes['indice_vigente'].mean():.1f}")
    print(f"   - LTV 12m promedio: ${df_clientes['ltv_12m'].mean():,.0f} MXN")
    print(f"   - Edad promedio: {df_clientes['edad'].mean():.1f} años")
    print(f"   - Ingreso promedio: ${df_clientes['ingreso_anual'].mean():,.0f} MXN/año")

    # Eventos
    df_eventos = pd.read_sql_query("SELECT * FROM eventos", conn)
    print(f"\n💰 EVENTOS: {len(df_eventos)}")
    print(f"   - Revenue total: ${df_eventos['precio_pagado'].sum():,.0f} MXN")
    print(f"   - Ticket promedio: ${df_eventos['precio_pagado'].mean():,.0f} MXN")
    print(f"   - Margen bruto: {df_eventos['margen_pct'].mean():.1f}%")
    print(f"   - BNPL: {df_eventos['bnpl_aplicado'].sum()} eventos ({df_eventos['bnpl_aplicado'].sum()/len(df_eventos)*100:.1f}%)")

    # Diagnósticos
    df_diag = pd.read_sql_query("SELECT * FROM diagnosticos", conn)
    print(f"\n🔬 DIAGNÓSTICOS: {len(df_diag)}")
    print(f"   - Índice Vigente promedio: {df_diag['indice_vigente'].mean():.1f}")
    print(f"   - Processing time promedio: {df_diag['processing_time_sec'].mean()/60:.1f} min")

    # Top arquetipos
    print("\n🎯 TOP ARQUETIPOS POR REVENUE:")
    top_arq = df_eventos.merge(df_clientes[['cliente_id', 'arquetipo_nombre']], on='cliente_id')
    top_arq_revenue = top_arq.groupby('arquetipo_nombre')['precio_pagado'].sum().sort_values(ascending=False)
    for arq, revenue in top_arq_revenue.items():
        print(f"   - {arq}: ${revenue:,.0f} MXN")

    # Top productos
    print("\n🏆 TOP 5 PRODUCTOS POR REVENUE:")
    top_prod = df_eventos.groupby('producto_nombre')['precio_pagado'].sum().sort_values(ascending=False).head(5)
    for i, (prod, revenue) in enumerate(top_prod.items(), 1):
        print(f"   {i}. {prod}: ${revenue:,.0f} MXN")

    conn.close()
    print("\n" + "="*60)


def main():
    """
    Pipeline principal
    """
    print("="*60)
    print("GENERADOR DE DATOS SINTÉTICOS - HOMBRE VIGENTE")
    print("Versión 2.0 - 100% Validado con Wiki")
    print("="*60)

    # 1. Cargar datos validados
    print("\n[1/6] Cargando datos validados...")
    arquetipos, paquetes, servicios = cargar_datos_validados()

    # 2. Crear base de datos
    print("\n[2/6] Creando base de datos SQLite...")
    crear_base_datos()

    # 3. Generar clientes
    print(f"\n[3/6] Generando {N_CLIENTES} clientes sintéticos...")
    clientes_df = generar_clientes(arquetipos)

    # 4. Generar eventos
    print(f"\n[4/6] Generando {N_EVENTOS} eventos de compra...")
    eventos_df = generar_eventos(clientes_df, arquetipos, paquetes, servicios)

    # 5. Generar diagnósticos
    print("\n[5/6] Generando diagnósticos Índice Vigente...")
    diagnosticos_df = generar_diagnosticos(clientes_df)

    # 6. Guardar en SQLite
    print("\n[6/6] Guardando datos en SQLite...")
    guardar_en_sqlite(clientes_df, eventos_df, diagnosticos_df)

    # Mostrar estadísticas finales
    mostrar_estadisticas()

    print(f"\n✅ COMPLETADO - Dataset listo en {DB_FILE}")
    print(f"\n📝 Próximos pasos:")
    print(f"   1. Ejecutar: sqlite3 {DB_FILE}")
    print(f"   2. Explorar: SELECT * FROM clientes LIMIT 10;")
    print(f"   3. Construir FastAPI backend usando esta DB")
    print(f"   4. Construir Next.js frontend para demo inversor")


if __name__ == "__main__":
    main()
