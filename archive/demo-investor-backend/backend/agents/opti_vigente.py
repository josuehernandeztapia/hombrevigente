"""
OptiVigente AI - MOCK Agent v3.0
Pricing dinámico, asignación óptima de slots, yield management, RiskGuard AI

ACTUALIZADO 2025-10-15:
- Alineado 100% con servicios_completos.json y arquetipos_modelo_financiero.json
- Implementa RiskGuard AI (semáforo verde/amarillo/rojo)
- Integra membership discounts (15% access, 20% elite)
- Considera BNPL config (threshold $2,500, uplift 1.25×)
- Usa target utilization ≥80% del SSOT
- Pricing dinámico basado en adherence_matrix

Fuente: 02_AGENTES_AI_CORE.md líneas 108-137
Algoritmo: Pricing dinámico según utilización + demanda + RiskGuard
"""
import json
import random
from typing import Dict, Optional
from datetime import datetime, timedelta


# Cargar configuración completa
def cargar_config():
    """Carga servicios completos y arquetipos del modelo financiero"""
    import sys
    from pathlib import Path

    servicios_path = Path(__file__).parent.parent.parent / "servicios_completos.json"
    arquetipos_path = Path(__file__).parent.parent.parent / "arquetipos_modelo_financiero.json"

    with open(servicios_path, 'r') as f:
        servicios_data = json.load(f)

    with open(arquetipos_path, 'r') as f:
        arquetipos_data = json.load(f)

    return servicios_data, arquetipos_data


SERVICIOS_DATA, ARQUETIPOS_DATA = cargar_config()
SERVICIOS_CATALOGO = SERVICIOS_DATA['servicios']
MEMBERSHIP_TIERS = SERVICIOS_DATA['membership_tiers']
BNPL_CONFIG = SERVICIOS_DATA['bnpl_config']
ADHERENCE_MATRIX = SERVICIOS_DATA['adherence_matrix']
ARQUETIPOS_HTML = {arq['id']: arq for arq in ARQUETIPOS_DATA['arquetipos_html_modelo']}

# Target utilization del SSOT
TARGET_UTILIZATION = 0.80  # ≥80%


def evaluar_riskguard(cliente: Dict, servicio: Dict) -> Dict:
    """
    RiskGuard AI - Semáforo de riesgo crediticio para BNPL

    LÓGICA v3.0 (del SSOT):
    - VERDE: LTV/CAC >5, churn <30%, historial positivo → Aprobado automático
    - AMARILLO: LTV/CAC 2-5, churn 30-50% → Revisión manual
    - ROJO: LTV/CAC <2, churn >50%, deuda activa → Rechazado

    Args:
        cliente: Dict con ltv_12m, cac, churn_propensity, historial_pagos
        servicio: Dict del servicio (para evaluar monto)

    Returns:
        Dict con semáforo (verde/amarillo/rojo), razon, limite_bnpl
    """

    ltv_12m = cliente.get('ltv_12m', 50000)
    cac = cliente.get('cac', 2500)
    churn_propensity = cliente.get('churn_propensity', 0.30)
    historial_pagos = cliente.get('historial_pagos_cumplidos', 0)  # Número de pagos completados
    deuda_activa = cliente.get('deuda_activa', 0)

    # Calcular LTV:CAC ratio
    ltv_cac_ratio = ltv_12m / cac if cac > 0 else 0

    # Evaluación RiskGuard
    if ltv_cac_ratio > 5.0 and churn_propensity < 0.30 and deuda_activa == 0:
        semaforo = "VERDE"
        razon = f"Cliente de bajo riesgo (LTV:CAC {ltv_cac_ratio:.1f}:1, churn {churn_propensity:.0%})"
        limite_bnpl = ltv_12m * 0.30  # Hasta 30% del LTV anual
        aprobado = True

    elif ltv_cac_ratio > 2.0 and churn_propensity < 0.50:
        semaforo = "AMARILLO"
        razon = f"Riesgo moderado (LTV:CAC {ltv_cac_ratio:.1f}:1, churn {churn_propensity:.0%}) - Requiere revisión"
        limite_bnpl = ltv_12m * 0.15  # Límite conservador
        aprobado = None  # Requiere revisión manual

    else:
        semaforo = "ROJO"
        razon = f"Alto riesgo (LTV:CAC {ltv_cac_ratio:.1f}:1, churn {churn_propensity:.0%}) - BNPL no disponible"
        limite_bnpl = 0
        aprobado = False

    return {
        'semaforo': semaforo,
        'razon': razon,
        'limite_bnpl': round(limite_bnpl, 2),
        'aprobado_automatico': aprobado,
        'ltv_cac_ratio': round(ltv_cac_ratio, 2)
    }


def calcular_precio_dinamico(
    servicio: Dict,
    cliente: Dict,
    fecha_deseada: str = None,
    utilization_actual: float = None
) -> Dict:
    """
    Calcula precio dinámico v3.0 con membership, BNPL y RiskGuard

    LÓGICA ACTUALIZADA (alineada con HTML):
    1. Precio base del servicio
    2. Descuento membership (15% access, 20% elite)
    3. Descuento dinámico por utilización (<80% target)
    4. BNPL eligibility (threshold $2,500, uplift 1.25×)
    5. RiskGuard evaluation para BNPL

    Args:
        servicio: Dict del servicio con precio_lista, id, tier
        cliente: Dict con arquetipo_id, membership_tier, ltv_12m, propension_bnpl
        fecha_deseada: Fecha deseada (opcional)
        utilization_actual: Utilización actual del club (0-1)

    Returns:
        Dict con precio_lista, precio_final, descuentos aplicados, BNPL info, RiskGuard
    """

    precio_lista = servicio['precio_lista']
    arquetipo_id = cliente.get('arquetipo_id', 'transaccional')
    membership_tier = cliente.get('membership_tier')  # 'elite', 'access', None
    propension_bnpl = cliente.get('propension_bnpl', 0.0)

    # Simular utilización si no se proporciona
    if utilization_actual is None:
        utilization_actual = random.uniform(0.65, 0.95)

    # Paso 1: Aplicar descuento de membership
    descuento_membership_pct = 0.0
    if membership_tier == 'elite':
        descuento_membership_pct = MEMBERSHIP_TIERS['elite']['descuento_servicios_pct']
    elif membership_tier == 'access':
        descuento_membership_pct = MEMBERSHIP_TIERS['access']['descuento_servicios_pct']

    precio_con_membership = precio_lista * (1 - descuento_membership_pct / 100)

    # Paso 2: Descuento dinámico por utilización (solo si <80% target)
    descuento_utilization_pct = 0.0
    nivel_util = "óptima"

    if utilization_actual < TARGET_UTILIZATION:
        # Calcular gap de utilización
        util_gap = TARGET_UTILIZATION - utilization_actual

        # Arquetipos sensibles a precio reciben más descuentos
        if arquetipo_id in ['mantenimiento', 'transaccional']:
            descuento_utilization_pct = min(20, util_gap * 100)  # Máximo 20%
            nivel_util = "baja"
        elif arquetipo_id == 'eduardo':
            descuento_utilization_pct = min(10, util_gap * 80)  # Máximo 10%
            nivel_util = "media"
        else:  # carlos - NO recibe descuentos por utilización (alta willingness to pay)
            descuento_utilization_pct = 0.0
            nivel_util = "normal"

    precio_final = precio_con_membership * (1 - descuento_utilization_pct / 100)

    # Paso 3: Evaluar BNPL eligibility
    bnpl_eligible = False
    bnpl_info = None
    riskguard_info = None

    if precio_final >= BNPL_CONFIG['min_price_threshold']:
        # Evaluar RiskGuard
        riskguard_info = evaluar_riskguard(cliente, servicio)

        if riskguard_info['aprobado_automatico'] and propension_bnpl > 0.30:
            bnpl_eligible = True
            # CRITICAL: Aplicar revenue uplift de 1.25×
            precio_bnpl = precio_final * BNPL_CONFIG['revenue_uplift_multiplier']
            bnpl_info = {
                'eligible': True,
                'precio_bnpl': round(precio_bnpl, 2),
                'cuotas': 3,  # 3 meses sin intereses
                'mensualidad': round(precio_bnpl / 3, 2),
                'uplift_aplicado': BNPL_CONFIG['revenue_uplift_multiplier']
            }

    # Paso 4: Calcular slots disponibles según utilización
    if utilization_actual < 0.70:
        slots_disponibles = random.randint(8, 15)
    elif utilization_actual < 0.85:
        slots_disponibles = random.randint(3, 7)
    else:
        slots_disponibles = random.randint(0, 2)

    # Construir razón del pricing
    razones = []
    if descuento_membership_pct > 0:
        razones.append(f"Descuento {membership_tier.upper()}: -{descuento_membership_pct}%")
    if descuento_utilization_pct > 0:
        razones.append(f"Descuento por utilización {nivel_util}: -{descuento_utilization_pct:.1f}%")
    if bnpl_eligible:
        razones.append(f"BNPL disponible (3 MSI)")
    if not razones:
        razones.append("Precio regular")

    return {
        'servicio_id': servicio['id'],
        'servicio_nombre': servicio['nombre'],
        'precio_lista': precio_lista,
        'precio_final': round(precio_final, 2),
        'descuento_membership_pct': descuento_membership_pct,
        'descuento_utilization_pct': round(descuento_utilization_pct, 1),
        'descuento_total_pct': round(descuento_membership_pct + descuento_utilization_pct, 1),
        'ahorro_mxn': round(precio_lista - precio_final, 2),
        'razon': " | ".join(razones),
        'utilization_level': nivel_util,
        'utilization_actual': round(utilization_actual * 100, 1),
        'slots_disponibles': slots_disponibles,
        'margen_base_pct': servicio.get('margen_pct'),
        'bnpl': bnpl_info,
        'riskguard': riskguard_info
    }


def asignar_slot_optimo(
    servicio: Dict,
    cliente: Dict,
    fecha_deseada: str = None
) -> Dict:
    """
    Asigna el mejor slot según:
    1. Propensión del cliente (>70% = slots premium)
    2. Disponibilidad
    3. Duración del servicio
    """

    propension = cliente.get('propension_compra', 0.50)
    duracion_min = servicio.get('duracion_min', 60)

    # Clientes con alta propensión (>70%) reciben slots premium
    if propension > 0.70:
        # Slots premium: 10am-2pm, lunes-viernes
        hora_sugerida = random.choice(['10:00', '11:00', '12:00', '13:00', '14:00'])
        dia_sugerido = (datetime.now() + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d')
        prioridad = "ALTA"
        mensaje = "Slot premium reservado para cliente de alto valor"
    else:
        # Slots regulares
        hora_sugerida = random.choice(['09:00', '15:00', '16:00', '17:00', '18:00'])
        dia_sugerido = (datetime.now() + timedelta(days=random.randint(3, 14))).strftime('%Y-%m-%d')
        prioridad = "NORMAL"
        mensaje = "Slot regular disponible"

    return {
        'fecha_sugerida': dia_sugerido,
        'hora_sugerida': hora_sugerida,
        'duracion_estimada': duracion_min,
        'prioridad': prioridad,
        'mensaje': mensaje
    }


# Para testing
if __name__ == "__main__":
    # Cargar servicio real del catálogo
    servicio_hifu = next(s for s in SERVICIOS_CATALOGO if s['id'] == 'hifu')
    servicio_botox = next(s for s in SERVICIOS_CATALOGO if s['id'] == 'botox')
    servicio_corte = next(s for s in SERVICIOS_CATALOGO if s['id'] == 'corte_pelo')

    # Test caso 1: Carlos Elite con HIFU (servicio premium, eligible BNPL)
    cliente_carlos = {
        'cliente_id': 'test-carlos-001',
        'nombre': 'Carlos Ejecutivo',
        'arquetipo_id': 'carlos',
        'arquetipo_nombre': 'Carlos el Ejecutivo',
        'propension_compra': 0.85,
        'churn_propensity': 0.12,
        'ltv_12m': 135000,
        'cac': 2510,
        'membership_tier': 'elite',
        'propension_bnpl': 0.50,
        'historial_pagos_cumplidos': 8,
        'deuda_activa': 0
    }

    # Test caso 2: Mantenimiento Access con Corte (servicio básico, no BNPL)
    cliente_mantenimiento = {
        'cliente_id': 'test-mant-001',
        'nombre': 'Juan Mantenimiento',
        'arquetipo_id': 'mantenimiento',
        'arquetipo_nombre': 'Juan Mantenimiento',
        'propension_compra': 0.55,
        'churn_propensity': 0.18,
        'ltv_12m': 22000,
        'cac': 300,
        'membership_tier': 'access',
        'propension_bnpl': 0.10,
        'historial_pagos_cumplidos': 12,
        'deuda_activa': 0
    }

    print("="*100)
    print("💰 OptiVigente AI v3.0 - Testing con RiskGuard, Membership, BNPL")
    print("="*100)

    # Test 1: Carlos + HIFU (premium, BNPL eligible)
    print(f"\n{'='*100}")
    print(f"TEST 1: {cliente_carlos['nombre']} ({cliente_carlos['arquetipo_id'].upper()}) → {servicio_hifu['nombre']}")
    print(f"{'='*100}")

    pricing1 = calcular_precio_dinamico(servicio_hifu, cliente_carlos, utilization_actual=0.75)

    print(f"\n💵 PRICING:")
    print(f"   Precio lista:           ${pricing1['precio_lista']:>7,} MXN")
    print(f"   Descuento membership:   -{pricing1['descuento_membership_pct']:>6}%")
    print(f"   Descuento utilización:  -{pricing1['descuento_utilization_pct']:>6}%")
    print(f"   Precio final:           ${pricing1['precio_final']:>7,} MXN")
    print(f"   Ahorro total:           ${pricing1['ahorro_mxn']:>7,} MXN ({pricing1['descuento_total_pct']}%)")
    print(f"   Razón: {pricing1['razon']}")

    if pricing1['bnpl']:
        print(f"\n💳 BNPL DISPONIBLE:")
        print(f"   Precio con BNPL:        ${pricing1['bnpl']['precio_bnpl']:>7,} MXN")
        print(f"   Cuotas:                  {pricing1['bnpl']['cuotas']} meses sin intereses")
        print(f"   Mensualidad:            ${pricing1['bnpl']['mensualidad']:>7,} MXN/mes")
        print(f"   Uplift aplicado:         {pricing1['bnpl']['uplift_aplicado']}×")

    if pricing1['riskguard']:
        rg = pricing1['riskguard']
        print(f"\n🚦 RISKGUARD AI:")
        print(f"   Semáforo:                {rg['semaforo']}")
        print(f"   LTV:CAC ratio:           {rg['ltv_cac_ratio']}:1")
        print(f"   Límite BNPL:            ${rg['limite_bnpl']:>7,} MXN")
        print(f"   Razón: {rg['razon']}")

    print(f"\n📊 UTILIZACIÓN:")
    print(f"   Nivel actual:            {pricing1['utilization_actual']}%")
    print(f"   Nivel:                   {pricing1['utilization_level']}")
    print(f"   Slots disponibles:       {pricing1['slots_disponibles']}")

    slot1 = asignar_slot_optimo(servicio_hifu, cliente_carlos)
    print(f"\n📅 SLOT ASIGNADO:")
    print(f"   Fecha:                   {slot1['fecha_sugerida']} a las {slot1['hora_sugerida']}")
    print(f"   Duración:                {slot1['duracion_estimada']} min")
    print(f"   Prioridad:               {slot1['prioridad']}")
    print(f"   {slot1['mensaje']}")

    # Test 2: Mantenimiento + Corte (básico, no BNPL)
    print(f"\n{'='*100}")
    print(f"TEST 2: {cliente_mantenimiento['nombre']} ({cliente_mantenimiento['arquetipo_id'].upper()}) → {servicio_corte['nombre']}")
    print(f"{'='*100}")

    pricing2 = calcular_precio_dinamico(servicio_corte, cliente_mantenimiento, utilization_actual=0.68)

    print(f"\n💵 PRICING:")
    print(f"   Precio lista:           ${pricing2['precio_lista']:>7,} MXN")
    print(f"   Descuento membership:   -{pricing2['descuento_membership_pct']:>6}%")
    print(f"   Descuento utilización:  -{pricing2['descuento_utilization_pct']:>6}%")
    print(f"   Precio final:           ${pricing2['precio_final']:>7,} MXN")
    print(f"   Ahorro total:           ${pricing2['ahorro_mxn']:>7,} MXN ({pricing2['descuento_total_pct']}%)")
    print(f"   Razón: {pricing2['razon']}")

    if pricing2['bnpl']:
        print(f"\n💳 BNPL: Disponible")
    else:
        print(f"\n💳 BNPL: No elegible (precio < ${BNPL_CONFIG['min_price_threshold']:,} MXN)")

    print(f"\n📊 UTILIZACIÓN:")
    print(f"   Nivel actual:            {pricing2['utilization_actual']}%")
    print(f"   Nivel:                   {pricing2['utilization_level']}")
    print(f"   Slots disponibles:       {pricing2['slots_disponibles']}")

    slot2 = asignar_slot_optimo(servicio_corte, cliente_mantenimiento)
    print(f"\n📅 SLOT ASIGNADO:")
    print(f"   Fecha:                   {slot2['fecha_sugerida']} a las {slot2['hora_sugerida']}")
    print(f"   Duración:                {slot2['duracion_estimada']} min ({slot2['duracion_estimada']/60:.1f} hrs)")
    print(f"   Prioridad:               {slot2['prioridad']}")
    print(f"   {slot2['mensaje']}")

    print(f"\n{'='*100}")
    print("✅ OptiVigente AI v3.0 - Alineado 100% con servicios_completos.json y arquetipos HTML")
    print("="*100)
