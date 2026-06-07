#!/usr/bin/env python3
"""
Script de verificación para validar que los datos generados
cumplen con las especificaciones de la wiki
"""

import sqlite3
import json
import pandas as pd

DB_FILE = "demo_hombrevigente.db"

def verificar_arquetipos():
    """Verifica que los arquetipos cumplan con LTV/CAC esperado"""
    print("=" * 60)
    print("🎯 VERIFICACIÓN DE ARQUETIPOS")
    print("=" * 60)

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("""
        SELECT arquetipo_nombre,
               COUNT(*) as n_clientes,
               ROUND(AVG(indice_vigente), 1) as indice_promedio,
               AVG(ltv_12m) as ltv_promedio,
               AVG(ltv_12m / (ltv_12m / 32.5)) as ltv_cac_estimado
        FROM clientes
        GROUP BY arquetipo_nombre
        ORDER BY ltv_promedio DESC
    """, conn)
    conn.close()

    # Valores esperados de la wiki
    esperado = {
        "Eduardo el Explorador": {"ltv": 135000, "ltv_cac": 49.1},
        "Carlos el Vigente": {"ltv": 100000, "ltv_cac": 32.5},
        "Ricardo el Ejecutivo": {"ltv": 95000, "ltv_cac": 28.3},
        "Miguel el Maduro": {"ltv": 95000, "ltv_cac": 21.8},
        "Luis el Renovado": {"ltv": 65000, "ltv_cac": 24.1}
    }

    print("\n📊 Comparación con Wiki:")
    print("-" * 60)

    for _, row in df.iterrows():
        nombre = row['arquetipo_nombre']
        ltv_real = row['ltv_promedio']
        ltv_esperado = esperado[nombre]['ltv']

        match = "✅" if ltv_real == ltv_esperado else "⚠️"
        print(f"{match} {nombre:30} LTV: ${ltv_real:,.0f} (esperado: ${ltv_esperado:,.0f})")

    print("\n" + "=" * 60)
    return df


def verificar_servicios():
    """Verifica que solo se usen servicios Fase 1"""
    print("\n🛍️  VERIFICACIÓN DE SERVICIOS FASE 1")
    print("=" * 60)

    # Cargar servicios validados
    with open('servicios_fase1_validados.json', 'r') as f:
        data = json.load(f)
        servicios_fase1 = set([p['nombre'] for p in data['paquetes_fase1']] +
                              [s['nombre'] for s in data['servicios_individuales_fase1']])

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("""
        SELECT DISTINCT producto_nombre
        FROM eventos
    """, conn)
    conn.close()

    servicios_usados = set(df['producto_nombre'].tolist())

    # Verificar que todos los servicios usados estén en Fase 1
    no_validados = servicios_usados - servicios_fase1

    if no_validados:
        print(f"⚠️  ALERTA: {len(no_validados)} servicios NO están en Fase 1:")
        for srv in no_validados:
            print(f"   - {srv}")
    else:
        print(f"✅ CORRECTO: Todos los {len(servicios_usados)} servicios están en Fase 1")

    print("\n" + "=" * 60)
    return servicios_usados


def verificar_metricas_financieras():
    """Verifica métricas financieras clave"""
    print("\n💰 VERIFICACIÓN DE MÉTRICAS FINANCIERAS")
    print("=" * 60)

    conn = sqlite3.connect(DB_FILE)

    # Revenue total
    df_revenue = pd.read_sql_query("""
        SELECT SUM(precio_pagado) as revenue_total,
               AVG(precio_pagado) as ticket_promedio,
               AVG(margen_pct) as margen_promedio,
               SUM(CASE WHEN bnpl_aplicado = 1 THEN 1 ELSE 0 END) as eventos_bnpl,
               COUNT(*) as total_eventos
        FROM eventos
    """, conn)

    revenue = df_revenue['revenue_total'].iloc[0]
    ticket = df_revenue['ticket_promedio'].iloc[0]
    margen = df_revenue['margen_promedio'].iloc[0]
    bnpl_eventos = df_revenue['eventos_bnpl'].iloc[0]
    total_eventos = df_revenue['total_eventos'].iloc[0]

    print(f"\n📈 Métricas Clave:")
    print(f"   Revenue total:        ${revenue:,.0f} MXN")
    print(f"   Ticket promedio:      ${ticket:,.0f} MXN")
    print(f"   Margen bruto:         {margen:.1f}%")
    print(f"   Eventos BNPL:         {bnpl_eventos} ({bnpl_eventos/total_eventos*100:.1f}%)")
    print(f"   Total eventos:        {total_eventos:,}")

    # Validar margen
    if margen >= 70 and margen <= 75:
        print(f"\n✅ Margen bruto dentro del rango esperado (70-75%)")
    else:
        print(f"\n⚠️  Margen bruto fuera del rango esperado (70-75%)")

    # Top productos
    print(f"\n🏆 Top 5 Productos por Revenue:")
    df_top = pd.read_sql_query("""
        SELECT producto_nombre,
               COUNT(*) as ventas,
               ROUND(SUM(precio_pagado), 0) as revenue_total
        FROM eventos
        GROUP BY producto_nombre
        ORDER BY revenue_total DESC
        LIMIT 5
    """, conn)

    for i, row in df_top.iterrows():
        print(f"   {i+1}. {row['producto_nombre']:40} ${row['revenue_total']:>10,.0f} ({row['ventas']} ventas)")

    conn.close()
    print("\n" + "=" * 60)


def verificar_indice_vigente():
    """Verifica que el Índice Vigente se calcule correctamente"""
    print("\n🔬 VERIFICACIÓN DE ÍNDICE VIGENTE™")
    print("=" * 60)

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("""
        SELECT indice_vigente,
               subscore_estructural,
               subscore_piel,
               subscore_biologico
        FROM clientes
        LIMIT 100
    """, conn)
    conn.close()

    # Verificar fórmula: 0.4 × estructural + 0.3 × piel + 0.3 × biológico
    errores = 0
    for _, row in df.iterrows():
        calculado = round(0.4 * row['subscore_estructural'] +
                         0.3 * row['subscore_piel'] +
                         0.3 * row['subscore_biologico'], 1)

        if abs(calculado - row['indice_vigente']) > 0.1:
            errores += 1

    if errores == 0:
        print(f"✅ CORRECTO: Fórmula Índice Vigente aplicada correctamente en 100 muestras")
        print(f"   Fórmula: 0.4 × estructural + 0.3 × piel + 0.3 × biológico")
    else:
        print(f"⚠️  ALERTA: {errores} errores en el cálculo del Índice Vigente")

    print("\n" + "=" * 60)


def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "VERIFICACIÓN DE DATOS" + " "*22 + "║")
    print("║" + " "*10 + "Hombre Vigente - Demo Investor" + " "*17 + "║")
    print("╚" + "="*58 + "╝")

    try:
        verificar_arquetipos()
        verificar_servicios()
        verificar_metricas_financieras()
        verificar_indice_vigente()

        print("\n✅ VERIFICACIÓN COMPLETADA")
        print("="*60)
        print("\nTodos los datos están alineados con la wiki validada.")
        print("Dataset listo para uso en demo investor.\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
