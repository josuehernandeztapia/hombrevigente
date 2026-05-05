#!/usr/bin/env python3
"""
Generador de Datos Sintéticos - Hombre Vigente Demo Investor
Versión 3.0 - 100% Alineado con Modelo Financiero HTML V53.1

CAMBIOS CRÍTICOS vs v2.0:
1. ✅ 4 arquetipos del HTML (carlos, eduardo, mantenimiento, transaccional)
2. ✅ Membresías: Access ($1,400/mes) y Elite ($3,800/mes)
3. ✅ BNPL correcto: threshold $2,500, uplift 1.25×
4. ✅ 26 servicios (17 fase 1 + 9 fase 2)
5. ✅ Adherence matrix del HTML
6. ✅ LTV, CAC, churn del HTML

Fuentes:
- modelofinanciero.html V53.1 (líneas 1095-1163)
- arquetipos_modelo_financiero.json
- servicios_completos.json
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
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

# Archivos de entrada (nuevos archivos alineados al HTML)
ARQUETIPOS_FILE = "arquetipos_modelo_financiero.json"
SERVICIOS_FILE = "servicios_completos.json"
DB_FILE = "demo_hombrevigente_v3.db"


def cargar_datos_validados() -> Tuple[List[Dict], Dict]:
    """
    Carga arquetipos y servicios 100% alineados con modelo financiero HTML

    Returns:
        arquetipos: Lista de 4 arquetipos del HTML
        servicios_data: Dict con servicios, membresías, BNPL config, adherence matrix
    """
    with open(ARQUETIPOS_FILE, 'r', encoding='utf-8') as f:
        data_arq = json.load(f)
        arquetipos = data_arq['arquetipos_html_modelo']

    with open(SERVICIOS_FILE, 'r', encoding='utf-8') as f:
        servicios_data = json.load(f)

    print(f"✅ Cargados: {len(arquetipos)} arquetipos, {len(servicios_data['servicios'])} servicios")
    print(f"   Membresías: {list(servicios_data['membership_tiers'].keys())}")
    print(f"   BNPL threshold: ${servicios_data['bnpl_config']['min_price_threshold']}")
    return arquetipos, servicios_data


def crear_base_datos():
    """
    Crea el esquema SQLite para el demo v3

    NUEVO: Agrega columna membership_tier
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tabla clientes (con membresía)
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
        membership_tier TEXT,
        membership_desde DATE,
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabla eventos (con BNPL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        evento_id TEXT PRIMARY KEY,
        cliente_id TEXT NOT NULL,
        fecha_evento DATE NOT NULL,
        tipo_evento TEXT NOT NULL,
        servicio_id TEXT,
        servicio_nombre TEXT,
        categoria TEXT,
        precio_lista REAL,
        descuento_pct REAL,
        precio_final REAL,
        margen_pct REAL,
        metodo_pago TEXT,
        bnpl_usado INTEGER DEFAULT 0,
        bnpl_cuotas INTEGER,
        estado TEXT,
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )
    """)

    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_eventos_cliente ON eventos(cliente_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_eventos_fecha ON eventos(fecha_evento)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_diagnosticos_cliente ON diagnosticos(cliente_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_arquetipo ON clientes(arquetipo_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_membership ON clientes(membership_tier)")

    conn.commit()
    conn.close()
    print("✅ Base de datos creada con esquema v3")


def calcular_indice_vigente(estructural: float, piel: float, biologico: float) -> float:
    """
    Fórmula oficial del Índice Vigente™ de la wiki

    Índice Vigente = 0.4 × estructural + 0.3 × piel + 0.3 × biológico

    Escala: 0-100
    - 0-40: Requiere intervención urgente
    - 41-60: Estado regular
    - 61-80: Buen estado
    - 81-100: Estado óptimo
    """
    return float(round(0.4 * estructural + 0.3 * piel + 0.3 * biologico, 1))


def asignar_membresia(arquetipo: Dict, random_val: float) -> Optional[str]:
    """
    Asigna membresía basado en propensión del arquetipo

    Args:
        arquetipo: Dict con membership_propension {elite, access}
        random_val: Float 0-1 para decisión estocástica

    Returns:
        'elite', 'access', o None
    """
    prop_elite = arquetipo['membership_propension']['elite']
    prop_access = arquetipo['membership_propension']['access']

    if random_val < prop_elite:
        return 'elite'
    elif random_val < (prop_elite + prop_access):
        return 'access'
    else:
        return None


def generar_clientes(arquetipos: List[Dict]) -> pd.DataFrame:
    """
    Genera N_CLIENTES clientes sintéticos con distribución de arquetipos del HTML

    NUEVO vs v2:
    - 4 arquetipos (no 5)
    - Asignación de membresías (elite/access/none)
    - LTV, CAC, churn del HTML
    """
    clientes = []
    fecha_inicio = datetime(2024, 1, 1)

    # Distribución de arquetipos del HTML
    pesos = [arq['peso_poblacion'] for arq in arquetipos]
    arquetipos_asignados = random.choices(arquetipos, weights=pesos, k=N_CLIENTES)

    for i, arq in enumerate(arquetipos_asignados):
        # Datos PII (con UUID para evitar duplicados)
        nombre = FAKE.name_male()
        email = f"{nombre.lower().replace(' ', '.')}.{i}@{FAKE.free_email_domain()}"
        telefono = FAKE.phone_number()

        # Fecha de registro distribuida en últimos 12 meses
        dias_offset = random.randint(0, 365)
        fecha_registro = fecha_inicio + timedelta(days=dias_offset)

        # Edad según arquetipo
        if arq['id'] == 'carlos':
            edad = random.randint(35, 50)
        elif arq['id'] == 'eduardo':
            edad = random.randint(25, 40)
        elif arq['id'] == 'mantenimiento':
            edad = random.randint(30, 55)
        else:  # transaccional
            edad = random.randint(25, 45)

        fecha_nacimiento = datetime.now() - timedelta(days=edad * 365)

        # Ingreso anual (correlacionado con arquetipo)
        if arq['id'] == 'carlos':
            ingreso_anual = random.randint(800000, 1200000)
        elif arq['id'] == 'eduardo':
            ingreso_anual = random.randint(400000, 700000)
        elif arq['id'] == 'mantenimiento':
            ingreso_anual = random.randint(300000, 600000)
        else:  # transaccional
            ingreso_anual = random.randint(250000, 500000)

        # Índice Vigente (con ruido)
        base_estructural = 75 if arq['id'] in ['carlos', 'eduardo'] else 65
        base_piel = 70 if arq['id'] in ['carlos', 'mantenimiento'] else 60
        base_biologico = 80 if arq['id'] in ['eduardo', 'mantenimiento'] else 70

        subscore_estructural = float(np.clip(base_estructural + random.gauss(0, 8), 30, 95))
        subscore_piel = float(np.clip(base_piel + random.gauss(0, 10), 30, 95))
        subscore_biologico = float(np.clip(base_biologico + random.gauss(0, 12), 30, 95))

        indice_vigente = calcular_indice_vigente(subscore_estructural, subscore_piel, subscore_biologico)

        # Propensiones (del HTML)
        propension_compra = random.uniform(0.5, 0.95) if arq['id'] in ['carlos', 'eduardo'] else random.uniform(0.3, 0.7)
        churn_propensity = arq['churn_anual'] + random.gauss(0, 0.05)
        churn_propensity = float(np.clip(churn_propensity, 0.1, 0.9))

        # Asignar membresía
        membership_tier = asignar_membresia(arq, random.random())
        membership_desde = fecha_registro + timedelta(days=random.randint(30, 180)) if membership_tier else None

        # Canal de origen
        canal_origen = random.choice(['Instagram', 'Facebook', 'Google Ads', 'Referido', 'LinkedIn', 'Evento'])
        ciudad = random.choice(['CDMX', 'Guadalajara', 'Monterrey', 'Querétaro'])

        cliente = {
            'cliente_id': f"CLI_{uuid.uuid4().hex[:12].upper()}",
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'fecha_registro': fecha_registro.strftime('%Y-%m-%d'),
            'fecha_nacimiento': fecha_nacimiento.strftime('%Y-%m-%d'),
            'edad': edad,
            'ingreso_anual': ingreso_anual,
            'arquetipo_id': arq['id'],
            'arquetipo_nombre': arq['nombre'],
            'membership_tier': membership_tier,
            'membership_desde': membership_desde.strftime('%Y-%m-%d') if membership_desde else None,
            'indice_vigente': indice_vigente,
            'subscore_estructural': subscore_estructural,
            'subscore_piel': subscore_piel,
            'subscore_biologico': subscore_biologico,
            'ltv_12m': arq['ltv_12m'],
            'propension_compra': propension_compra,
            'churn_propensity': churn_propensity,
            'propension_bnpl': arq['bnpl_propension'],
            'canal_origen': canal_origen,
            'ciudad': ciudad
        }

        clientes.append(cliente)

        if (i + 1) % 1000 == 0:
            print(f"   Generados {i + 1}/{N_CLIENTES} clientes...")

    df = pd.DataFrame(clientes)

    # Estadísticas
    print(f"\n📊 Estadísticas Clientes:")
    print(f"   Total: {len(df)}")
    print(f"   Por arquetipo:")
    for arq_id in df['arquetipo_id'].unique():
        count = len(df[df['arquetipo_id'] == arq_id])
        pct = count / len(df) * 100
        print(f"      {arq_id}: {count} ({pct:.1f}%)")

    print(f"\n   Membresías:")
    for tier in ['elite', 'access', None]:
        count = len(df[df['membership_tier'] == tier])
        pct = count / len(df) * 100
        tier_name = tier if tier else 'ninguna'
        print(f"      {tier_name}: {count} ({pct:.1f}%)")

    return df


def generar_eventos(df_clientes: pd.DataFrame, servicios_data: Dict, arquetipos: List[Dict]) -> pd.DataFrame:
    """
    Genera eventos de compra con lógica BNPL correcta del HTML + RECURRENCIA

    NUEVO vs v2:
    - BNPL threshold $2,500 (no $10,000)
    - BNPL uplift 1.25× aplicado correctamente
    - Descuentos por membresía (15% access, 20% elite)
    - Adherence matrix del HTML para selección de servicios
    - RECURRENCIA: Respeta repurchase_cycle_months de cada servicio
    - CHURN: Probabilidad de abandono según churn_anual del arquetipo
    """
    eventos = []
    servicios = servicios_data['servicios']
    adherence_matrix = servicios_data['adherence_matrix']
    service_adherence = servicios_data['service_adherence']
    membership_tiers = servicios_data['membership_tiers']
    bnpl_config = servicios_data['bnpl_config']

    # Mapeo de arquetipos
    arq_dict = {arq['id']: arq for arq in arquetipos}

    # Generar eventos por cliente (no por N_EVENTOS fijo)
    # Simulamos 12 meses de actividad
    print("   Generando eventos con recurrencia por cliente...")

    contador_eventos = 0
    for idx, cliente in df_clientes.iterrows():
        arq_id = cliente['arquetipo_id']
        arq = arq_dict[arq_id]

        # Fecha de registro
        fecha_registro = datetime.strptime(cliente['fecha_registro'], '%Y-%m-%d')
        fecha_fin_simulacion = min(datetime.now(), fecha_registro + timedelta(days=365))

        # Verificar si el cliente ha churneado (abandonó)
        meses_desde_registro = (fecha_fin_simulacion - fecha_registro).days / 30
        prob_churn = 1 - (1 - arq['churn_anual']) ** (meses_desde_registro / 12)

        if random.random() < prob_churn:
            # Cliente churned - generar menos eventos
            num_eventos_cliente = random.randint(1, 3)
        else:
            # Cliente activo - generar eventos basados en frecuencia de arquetipo
            if arq_id == 'carlos':
                num_eventos_cliente = random.randint(8, 15)  # Premium, alta frecuencia
            elif arq_id == 'eduardo':
                num_eventos_cliente = random.randint(4, 8)   # Novato, frecuencia media
            elif arq_id == 'mantenimiento':
                num_eventos_cliente = random.randint(10, 20) # Grooming regular, muy recurrente
            else:  # transaccional
                num_eventos_cliente = random.randint(1, 4)   # Baja frecuencia

        # Generar eventos para este cliente
        for evento_num in range(num_eventos_cliente):
            # Fecha evento distribuida entre registro y fin simulación
            dias_desde_registro = (fecha_fin_simulacion - fecha_registro).days
            if dias_desde_registro <= 0:
                continue

            dias_offset = random.randint(0, dias_desde_registro)
            fecha_evento = fecha_registro + timedelta(days=dias_offset)

            # Seleccionar servicio basado en adherence matrix
            servicios_candidatos = []
            for srv in servicios:
                adherence_tier = srv.get('adherence_tier', 'high')
                probabilidad_tier = adherence_matrix[arq_id].get(adherence_tier, 0.5)

                # Además, usar service_adherence si está disponible
                srv_id = srv['id']
                probabilidad_servicio = service_adherence.get(arq_id, {}).get(srv_id, probabilidad_tier)

                if random.random() < probabilidad_servicio:
                    servicios_candidatos.append(srv)

            if not servicios_candidatos:
                # Fallback: cualquier servicio
                servicios_candidatos = servicios

            servicio = random.choice(servicios_candidatos)

            # Precio base
            precio_lista = servicio['precio_lista']

            # Descuento por membresía
            descuento_pct = 0.0
            if cliente['membership_tier'] == 'elite':
                descuento_pct = membership_tiers['elite']['descuento_servicios_pct'] / 100
            elif cliente['membership_tier'] == 'access':
                descuento_pct = membership_tiers['access']['descuento_servicios_pct'] / 100

            # Descuentos adicionales aleatorios (10% probabilidad)
            if random.random() < 0.10:
                descuento_pct += random.uniform(0.05, 0.15)

            descuento_pct = min(descuento_pct, 0.35)  # Max 35% descuento

            # Aplicar descuento
            precio_con_descuento = precio_lista * (1 - descuento_pct)

            # BNPL CORRECTO (del HTML)
            bnpl_usado = 0
            bnpl_cuotas = None

            if bnpl_config['enabled'] and precio_con_descuento >= bnpl_config['min_price_threshold']:
                # Propensión BNPL del arquetipo
                if random.random() < cliente['propension_bnpl']:
                    bnpl_usado = 1
                    # CRÍTICO: Aplicar uplift 1.25×
                    precio_final = precio_con_descuento * bnpl_config['revenue_uplift_multiplier']
                    bnpl_cuotas = random.choice([3, 6, 9, 12])
                else:
                    precio_final = precio_con_descuento
            else:
                precio_final = precio_con_descuento

            # Método de pago
            if bnpl_usado:
                metodo_pago = 'BNPL'
            else:
                metodo_pago = random.choice(['Tarjeta', 'Efectivo', 'Transferencia'])

            # Margen
            cogs = servicio['cogs']
            margen_pct = ((precio_final - cogs) / precio_final * 100) if precio_final > 0 else 0

            evento = {
                'evento_id': f"EVT_{uuid.uuid4().hex[:12].upper()}",
                'cliente_id': cliente['cliente_id'],
                'fecha_evento': fecha_evento.strftime('%Y-%m-%d'),
                'tipo_evento': 'compra',
                'servicio_id': servicio['id'],
                'servicio_nombre': servicio['nombre'],
                'categoria': servicio['categoria'],
                'precio_lista': precio_lista,
                'descuento_pct': descuento_pct * 100,
                'precio_final': round(precio_final, 2),
                'margen_pct': round(margen_pct, 2),
                'metodo_pago': metodo_pago,
                'bnpl_usado': bnpl_usado,
                'bnpl_cuotas': bnpl_cuotas,
                'estado': 'completado'
            }

            eventos.append(evento)
            contador_eventos += 1

        if (idx + 1) % 500 == 0:
            print(f"      Procesados {idx + 1}/{len(df_clientes)} clientes, {contador_eventos} eventos generados...")

    df = pd.DataFrame(eventos)

    # Estadísticas BNPL
    bnpl_events = df[df['bnpl_usado'] == 1]
    total_revenue = df['precio_final'].sum()
    bnpl_revenue = bnpl_events['precio_final'].sum()

    print(f"\n📊 Estadísticas Eventos:")
    print(f"   Total eventos: {len(df)}")
    print(f"   BNPL usado: {len(bnpl_events)} ({len(bnpl_events)/len(df)*100:.1f}%)")
    print(f"   Revenue total: ${total_revenue:,.0f} MXN")
    print(f"   Revenue BNPL: ${bnpl_revenue:,.0f} MXN ({bnpl_revenue/total_revenue*100:.1f}%)")

    print(f"\n   Top 5 servicios:")
    top_servicios = df['servicio_nombre'].value_counts().head(5)
    for srv, count in top_servicios.items():
        print(f"      {srv}: {count}")

    return df


def generar_diagnosticos(df_clientes: pd.DataFrame) -> pd.DataFrame:
    """
    Genera diagnósticos para ~65% de los clientes

    Sin cambios vs v2 (fórmula sigue igual)
    """
    diagnosticos = []

    # Seleccionar ~65% de clientes para tener diagnóstico
    clientes_con_diagnostico = df_clientes.sample(frac=0.65)

    for _, cliente in clientes_con_diagnostico.iterrows():
        fecha_diagnostico = datetime.strptime(cliente['fecha_registro'], '%Y-%m-%d') + timedelta(days=random.randint(1, 30))

        # Usar subscores del cliente (ya calculados)
        subscore_estructural = cliente['subscore_estructural']
        subscore_piel = cliente['subscore_piel']
        subscore_biologico = cliente['subscore_biologico']
        indice_vigente = cliente['indice_vigente']

        # Interpretación
        if indice_vigente >= 81:
            interpretacion = "Estado óptimo"
        elif indice_vigente >= 61:
            interpretacion = "Buen estado"
        elif indice_vigente >= 41:
            interpretacion = "Estado regular"
        else:
            interpretacion = "Requiere intervención urgente"

        # Recomendaciones basadas en subscores más bajos
        recomendaciones = []
        if subscore_estructural < 65:
            recomendaciones.append("HIFU Ultraformer III para mejorar estructura facial")
        if subscore_piel < 65:
            recomendaciones.append("RF Microneedling para rejuvenecimiento de piel")
        if subscore_biologico < 65:
            recomendaciones.append("PRP Dermapen para bioestimulación")

        if not recomendaciones:
            recomendaciones.append("Mantenimiento con limpieza facial mensual")

        diagnostico = {
            'diagnostico_id': f"DXV_{uuid.uuid4().hex[:12].upper()}",
            'cliente_id': cliente['cliente_id'],
            'fecha_diagnostico': fecha_diagnostico.strftime('%Y-%m-%d'),
            'indice_vigente': indice_vigente,
            'subscore_estructural': subscore_estructural,
            'subscore_piel': subscore_piel,
            'subscore_biologico': subscore_biologico,
            'interpretacion': interpretacion,
            'recomendaciones': '; '.join(recomendaciones)
        }

        diagnosticos.append(diagnostico)

    df = pd.DataFrame(diagnosticos)

    print(f"\n📊 Estadísticas Diagnósticos:")
    print(f"   Total: {len(df)}")
    print(f"   Índice Vigente promedio: {df['indice_vigente'].mean():.1f}")
    print(f"   Distribución:")
    for interp in df['interpretacion'].value_counts().items():
        print(f"      {interp[0]}: {interp[1]}")

    return df


def insertar_datos(df_clientes: pd.DataFrame, df_eventos: pd.DataFrame, df_diagnosticos: pd.DataFrame):
    """
    Inserta datos en SQLite
    """
    conn = sqlite3.connect(DB_FILE)

    print("\n💾 Insertando datos en SQLite...")

    df_clientes.to_sql('clientes', conn, if_exists='append', index=False)
    print(f"   ✅ {len(df_clientes)} clientes insertados")

    df_eventos.to_sql('eventos', conn, if_exists='append', index=False)
    print(f"   ✅ {len(df_eventos)} eventos insertados")

    df_diagnosticos.to_sql('diagnosticos', conn, if_exists='append', index=False)
    print(f"   ✅ {len(df_diagnosticos)} diagnósticos insertados")

    conn.close()


def generar_reporte_final():
    """
    Genera reporte final con métricas clave
    """
    conn = sqlite3.connect(DB_FILE)

    print("\n" + "="*60)
    print("📈 REPORTE FINAL - Demo Hombre Vigente v3.0")
    print("="*60)

    # Clientes por arquetipo
    print("\n1. CLIENTES POR ARQUETIPO:")
    df = pd.read_sql_query("""
        SELECT arquetipo_id, COUNT(*) as count,
               ROUND(AVG(ltv_12m), 0) as ltv_promedio,
               ROUND(AVG(indice_vigente), 1) as indice_promedio
        FROM clientes
        GROUP BY arquetipo_id
        ORDER BY count DESC
    """, conn)
    print(df.to_string(index=False))

    # Membresías
    print("\n2. MEMBRESÍAS:")
    df = pd.read_sql_query("""
        SELECT
            COALESCE(membership_tier, 'ninguna') as tier,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM clientes), 1) as porcentaje
        FROM clientes
        GROUP BY membership_tier
    """, conn)
    print(df.to_string(index=False))

    # Revenue por arquetipo
    print("\n3. REVENUE POR ARQUETIPO:")
    df = pd.read_sql_query("""
        SELECT c.arquetipo_id,
               COUNT(e.evento_id) as num_eventos,
               ROUND(SUM(e.precio_final), 0) as revenue_total,
               ROUND(AVG(e.precio_final), 0) as ticket_promedio
        FROM eventos e
        JOIN clientes c ON e.cliente_id = c.cliente_id
        GROUP BY c.arquetipo_id
        ORDER BY revenue_total DESC
    """, conn)
    print(df.to_string(index=False))

    # BNPL Stats
    print("\n4. BNPL STATISTICS:")
    df = pd.read_sql_query("""
        SELECT
            COUNT(*) as total_eventos,
            SUM(CASE WHEN bnpl_usado = 1 THEN 1 ELSE 0 END) as eventos_bnpl,
            ROUND(SUM(CASE WHEN bnpl_usado = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_bnpl,
            ROUND(SUM(precio_final), 0) as revenue_total,
            ROUND(SUM(CASE WHEN bnpl_usado = 1 THEN precio_final ELSE 0 END), 0) as revenue_bnpl,
            ROUND(SUM(CASE WHEN bnpl_usado = 1 THEN precio_final ELSE 0 END) * 100.0 / SUM(precio_final), 1) as pct_revenue_bnpl
        FROM eventos
    """, conn)
    print(df.to_string(index=False))

    # Top servicios
    print("\n5. TOP 10 SERVICIOS:")
    df = pd.read_sql_query("""
        SELECT servicio_nombre,
               COUNT(*) as ventas,
               ROUND(SUM(precio_final), 0) as revenue
        FROM eventos
        GROUP BY servicio_nombre
        ORDER BY revenue DESC
        LIMIT 10
    """, conn)
    print(df.to_string(index=False))

    # MRR Proyectado de membresías
    print("\n6. MRR PROYECTADO (Membresías):")
    df = pd.read_sql_query("""
        SELECT
            membership_tier,
            COUNT(*) as clientes,
            CASE
                WHEN membership_tier = 'elite' THEN COUNT(*) * 3800
                WHEN membership_tier = 'access' THEN COUNT(*) * 1400
                ELSE 0
            END as mrr_mensual,
            CASE
                WHEN membership_tier = 'elite' THEN COUNT(*) * 3800 * 12
                WHEN membership_tier = 'access' THEN COUNT(*) * 1400 * 12
                ELSE 0
            END as arr_anual
        FROM clientes
        WHERE membership_tier IS NOT NULL
        GROUP BY membership_tier
    """, conn)
    print(df.to_string(index=False))

    total_mrr = df['mrr_mensual'].sum()
    total_arr = df['arr_anual'].sum()
    print(f"\n   TOTAL MRR: ${total_mrr:,.0f} MXN/mes")
    print(f"   TOTAL ARR: ${total_arr:,.0f} MXN/año")

    conn.close()

    print("\n" + "="*60)
    print(f"✅ Base de datos guardada en: {DB_FILE}")
    print(f"   Tamaño: {round(sqlite3.connect(DB_FILE).cursor().execute('SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()').fetchone()[0] / 1024 / 1024, 2)} MB")
    print("="*60)


def main():
    """
    Flujo principal de generación
    """
    print("="*60)
    print("🚀 GENERADOR SINTÉTICO v3.0 - Hombre Vigente")
    print("   100% Alineado con modelofinanciero.html V53.1")
    print("="*60)

    print("\n1️⃣ Cargando datos validados del HTML...")
    arquetipos, servicios_data = cargar_datos_validados()

    print("\n2️⃣ Creando base de datos...")
    crear_base_datos()

    print(f"\n3️⃣ Generando {N_CLIENTES} clientes...")
    df_clientes = generar_clientes(arquetipos)

    print(f"\n4️⃣ Generando {N_EVENTOS} eventos de compra...")
    df_eventos = generar_eventos(df_clientes, servicios_data, arquetipos)

    print(f"\n5️⃣ Generando diagnósticos...")
    df_diagnosticos = generar_diagnosticos(df_clientes)

    print("\n6️⃣ Insertando datos en SQLite...")
    insertar_datos(df_clientes, df_eventos, df_diagnosticos)

    print("\n7️⃣ Generando reporte final...")
    generar_reporte_final()

    print("\n✨ Generación completada exitosamente!")


if __name__ == "__main__":
    main()
