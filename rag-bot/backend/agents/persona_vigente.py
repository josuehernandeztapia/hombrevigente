"""
PersonaVigente AI - MOCK Agent v3.0
Hiperpersonalización, scoring propensión, recomendaciones, detección churn

ACTUALIZADO 2025-10-15:
- Alineado 100% con servicios_completos.json (26 servicios)
- Implementa adherence_matrix del modelofinanciero.html
- Usa 4 arquetipos canónicos (carlos, eduardo, mantenimiento, transaccional)
- Integra membership tiers (access/elite)
- Considera BNPL propensity en recomendaciones

Fuente: 02_AGENTES_AI_CORE.md líneas 72-106
Algoritmo: LightFM (collaborative filtering) + GPT-4o mini (simulado con reglas)
"""
import json
import random
from typing import Dict, List, Optional


# Cargar servicios completos
def cargar_servicios():
    """Carga catálogo completo de 26 servicios con adherence matrix"""
    import sys
    from pathlib import Path
    servicios_path = Path(__file__).parent.parent.parent / "servicios_completos.json"
    with open(servicios_path, 'r') as f:
        data = json.load(f)
    return data


SERVICIOS_DATA = cargar_servicios()
SERVICIOS_CATALOGO = SERVICIOS_DATA['servicios']
ADHERENCE_MATRIX = SERVICIOS_DATA['adherence_matrix']
SERVICE_ADHERENCE = SERVICIOS_DATA['service_adherence']
MEMBERSHIP_TIERS = SERVICIOS_DATA['membership_tiers']
BNPL_CONFIG = SERVICIOS_DATA['bnpl_config']


def analizar_propension(cliente_data: Dict, historial_eventos: List[Dict] = None) -> Dict:
    """
    Analiza propensión de compra según arquetipo e historial

    Output (según wiki):
    - Propensión a compra: >70% = alto potencial
    - Churn Propensity Score: <0.60 = retener, >0.60 = riesgo
    - Recomendaciones personalizadas
    """

    # Usar propensión del cliente si existe
    propension_base = cliente_data.get('propension_compra', 0.50)
    churn_base = cliente_data.get('churn_propensity', 0.30)

    # Ajustar según historial
    if historial_eventos:
        n_eventos = len(historial_eventos)

        # Más eventos = mayor propensión, menor churn
        if n_eventos > 5:
            propension_base = min(1.0, propension_base + 0.15)
            churn_base = max(0.0, churn_base - 0.10)
        elif n_eventos < 2:
            propension_base = max(0.0, propension_base - 0.10)
            churn_base = min(1.0, churn_base + 0.15)

    # Clasificación según wiki
    if propension_base > 0.70:
        nivel_propension = "ALTO"
        mensaje_propension = "Cliente de alto valor con excelente propensión de compra"
    elif propension_base > 0.50:
        nivel_propension = "MEDIO"
        mensaje_propension = "Cliente con buena propensión, oportunidades de upsell"
    else:
        nivel_propension = "BAJO"
        mensaje_propension = "Cliente requiere nurturing y ofertas personalizadas"

    if churn_base < 0.60:
        nivel_churn = "BAJO RIESGO"
        mensaje_churn = "Cliente estable, enfocarse en retención preventiva"
    else:
        nivel_churn = "ALTO RIESGO"
        mensaje_churn = "⚠️ Cliente en riesgo de churn, activar protocolo de retención"

    return {
        'propension_compra': round(propension_base, 3),
        'nivel_propension': nivel_propension,
        'mensaje_propension': mensaje_propension,
        'churn_propensity': round(churn_base, 3),
        'nivel_churn': nivel_churn,
        'mensaje_churn': mensaje_churn
    }


def recomendar_servicios(cliente_data: Dict, indice_vigente: float = None, top_n: int = 5) -> List[Dict]:
    """
    Recomienda servicios usando adherence_matrix del HTML

    LÓGICA v3.0 (ALINEADA CON HTML):
    1. Usa SERVICE_ADHERENCE (probabilidad específica por servicio × arquetipo)
    2. Aplica multiplicadores según:
       - Membership tier (elite/access)
       - BNPL propensity (para servicios >$2,500)
       - Índice Vigente (si bajo, priorizar tratamientos faciales/inyectables)
    3. Ordena por score final (adherence × multiplicadores)

    Args:
        cliente_data: Dict con arquetipo_id, ltv_12m, membership_tier, propension_bnpl
        indice_vigente: Score 0-100 del Índice Vigente™
        top_n: Número de servicios a recomendar

    Returns:
        Lista de servicios recomendados con score y razón
    """

    arquetipo_id = cliente_data.get('arquetipo_id', 'transaccional')
    membership_tier = cliente_data.get('membership_tier')  # 'elite', 'access', None
    propension_bnpl = cliente_data.get('propension_bnpl', 0.0)
    ltv_12m = cliente_data.get('ltv_12m', 65000)

    # Obtener adherence específica del arquetipo
    adherence_arquetipo = SERVICE_ADHERENCE.get(arquetipo_id, SERVICE_ADHERENCE['transaccional'])

    servicios_recomendados = []

    for srv in SERVICIOS_CATALOGO:
        servicio_id = srv['id']
        precio = srv['precio_lista']

        # Score base: adherence del arquetipo a este servicio específico
        adherence_score = adherence_arquetipo.get(servicio_id, 0.01)

        # Multiplicadores
        multiplicador = 1.0
        razones = []

        # 1. Membership tier aumenta adherence
        if membership_tier == 'elite':
            multiplicador *= 1.30  # Elite: +30% adherence
            razones.append("miembro Elite (prioridad)")
        elif membership_tier == 'access':
            multiplicador *= 1.15  # Access: +15% adherence
            razones.append("miembro Access")

        # 2. BNPL para servicios premium (>$2,500)
        if precio >= BNPL_CONFIG['min_price_threshold']:
            if propension_bnpl > 0.40:  # Alta propensión BNPL
                multiplicador *= 1.20
                razones.append("elegible para BNPL")

        # 3. Índice Vigente bajo → priorizar tratamientos faciales/inyectables
        if indice_vigente and indice_vigente < 65:
            if srv['categoria'] in ['Rejuvenecimiento y Facial', 'Aplicaciones de Precisión']:
                multiplicador *= 1.25
                razones.append("recomendado para mejorar Índice Vigente")

        # 4. Clientes de alto LTV → servicios premium
        if ltv_12m > 100000 and srv['tier'] in ['premium', 'surgery']:
            multiplicador *= 1.15
            razones.append("alineado a tu perfil de alto valor")

        # Score final
        score_final = adherence_score * multiplicador

        # Agregar razón base si no hay otras
        if not razones:
            adherence_pct = adherence_score * 100
            razones.append(f"alta adherence ({adherence_pct:.0f}%) para tu arquetipo")

        servicios_recomendados.append({
            'servicio_id': servicio_id,
            'nombre': srv['nombre'],
            'categoria': srv['categoria'],
            'precio': precio,
            'adherence_base': round(adherence_score, 3),
            'score': round(score_final, 3),
            'tier': srv['tier'],
            'repurchase_cycle_months': srv['repurchase_cycle_months'],
            'razon': " • ".join(razones)
        })

    # Ordenar por score final y retornar top N
    servicios_recomendados.sort(key=lambda x: x['score'], reverse=True)
    return servicios_recomendados[:top_n]


def generar_razonamiento(cliente_data: Dict, analisis: Dict) -> str:
    """Genera explicación en lenguaje natural del análisis con contexto v3.0"""

    arquetipo_id = cliente_data.get('arquetipo_id', 'transaccional')
    arquetipo_nombre = cliente_data.get('arquetipo_nombre', 'Cliente')
    ltv = cliente_data.get('ltv_12m', 0)
    propension = analisis['propension_compra']
    churn = analisis['churn_propensity']
    membership_tier = cliente_data.get('membership_tier')

    # Contexto de membership
    membership_texto = ""
    if membership_tier == 'elite':
        descuento = MEMBERSHIP_TIERS['elite']['descuento_servicios_pct']
        membership_texto = f"\n• Miembro Elite: {descuento}% descuento en servicios + acceso BNPL exclusivo"
    elif membership_tier == 'access':
        descuento = MEMBERSHIP_TIERS['access']['descuento_servicios_pct']
        membership_texto = f"\n• Miembro Access: {descuento}% descuento en servicios"

    # Estrategia personalizada por arquetipo
    if arquetipo_id == 'carlos':
        estrategia = "Prioridad en booking, ofertas de servicios premium y cirugías estéticas"
    elif arquetipo_id == 'eduardo':
        estrategia = "Educación sobre tratamientos, ofertas de servicios de alta frecuencia (grooming)"
    elif arquetipo_id == 'mantenimiento':
        estrategia = "Membership Access recomendada, enfoque en servicios recurrentes (corte, barba)"
    else:  # transaccional
        estrategia = "Promociones agresivas, descuentos en primer servicio para activación"

    razonamiento = f"""
Análisis PersonaVigente v3.0 para {arquetipo_nombre}:

• Arquetipo: {arquetipo_id.upper()}
• LTV 12m proyectado: ${ltv:,.0f} MXN
• Propensión de compra: {propension:.1%} ({analisis['nivel_propension']})
• Riesgo de churn: {churn:.1%} ({analisis['nivel_churn']}){membership_texto}

{analisis['mensaje_propension']}.
{analisis['mensaje_churn']}.

Estrategia recomendada: {estrategia}
    """.strip()

    return razonamiento


# Para testing
if __name__ == "__main__":
    # Test caso 1: Carlos (alto valor, Elite)
    cliente_carlos = {
        'cliente_id': 'test-carlos-001',
        'nombre': 'Carlos Ejecutivo',
        'arquetipo_id': 'carlos',
        'arquetipo_nombre': 'Carlos el Ejecutivo',
        'propension_compra': 0.85,
        'churn_propensity': 0.12,
        'ltv_12m': 135000,
        'membership_tier': 'elite',
        'propension_bnpl': 0.50
    }

    # Test caso 2: Eduardo (explorador, Access)
    cliente_eduardo = {
        'cliente_id': 'test-eduardo-001',
        'nombre': 'Eduardo Explorador',
        'arquetipo_id': 'eduardo',
        'arquetipo_nombre': 'Eduardo el Explorador',
        'propension_compra': 0.65,
        'churn_propensity': 0.25,
        'ltv_12m': 85000,
        'membership_tier': 'access',
        'propension_bnpl': 0.20
    }

    print("="*80)
    print("🎯 PersonaVigente AI v3.0 - Testing con adherence_matrix del HTML")
    print("="*80)

    for cliente in [cliente_carlos, cliente_eduardo]:
        print(f"\n{'='*80}")
        print(f"CLIENTE: {cliente['nombre']} ({cliente['arquetipo_id'].upper()})")
        print(f"{'='*80}")

        analisis = analizar_propension(cliente, historial_eventos=[1, 2, 3, 4, 5, 6])
        servicios = recomendar_servicios(cliente, indice_vigente=72.0, top_n=8)
        razonamiento = generar_razonamiento(cliente, analisis)

        print(razonamiento)
        print("\n" + "-"*80)
        print("SERVICIOS RECOMENDADOS (ordenados por score de adherence):")
        print("-"*80)
        for i, srv in enumerate(servicios, 1):
            print(f"{i}. {srv['nombre']:30s} ${srv['precio']:>7,} MXN")
            print(f"   Tier: {srv['tier']:12s} | Adherence: {srv['adherence_base']:.1%} | Score: {srv['score']:.3f}")
            print(f"   Razón: {srv['razon']}")
            print()

    print("="*80)
    print("✅ PersonaVigente AI v3.0 - Alineado 100% con servicios_completos.json")
    print("="*80)
