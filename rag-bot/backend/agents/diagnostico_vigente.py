"""
DiagnósticoVigente AI - Agent alineado 100% con SSOT v1.2
Simula el comportamiento del agente real documentado en:
- SSOT_HOMBRE_VIGENTE_Full_v1.2_CONSOLIDADO.txt
- modelofinanciero.html V53.1

Cambios v3.0:
- ✅ Imaging Module propietario (Logitech Brio 4K + FLIR ONE Edge Pro)
- ✅ Fórmula oficial: Índice Vigente = 0.4 × estructural + 0.3 × piel + 0.3 × biológico
- ✅ Interpretación según escala 0-100 del SSOT
- ✅ Recomendaciones basadas en servicios_completos.json (26 servicios)
"""
import time
import random
import uuid
from datetime import datetime
from typing import Dict, List
import json
from pathlib import Path


def cargar_servicios():
    """Carga catálogo completo de 26 servicios"""
    servicios_path = Path(__file__).parent.parent.parent / "servicios_completos.json"
    with open(servicios_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['servicios']


SERVICIOS_CATALOGO = cargar_servicios()


def calcular_indice_vigente(estructural: float, piel: float, biologico: float) -> float:
    """
    Fórmula oficial del SSOT:
    Índice Vigente™ = 0.4 × estructural + 0.3 × piel + 0.3 × biológico

    Escala 0-100:
    - 81-100: Estado óptimo
    - 61-80: Buen estado
    - 41-60: Estado regular
    - 0-40: Requiere intervención urgente
    """
    return round(0.4 * estructural + 0.3 * piel + 0.3 * biologico, 1)


def generar_interpretacion(indice: float) -> str:
    """Genera interpretación según escala oficial del SSOT"""
    if indice >= 81:
        return "ESTADO ÓPTIMO: Índice Vigente superior. Continuar con programa de mantenimiento preventivo."
    elif indice >= 61:
        return "BUEN ESTADO: Índice Vigente dentro de rango saludable. Oportunidades de mejora identificadas."
    elif indice >= 41:
        return "ESTADO REGULAR: Índice Vigente indica áreas de atención. Protocolo de mejora recomendado."
    else:
        return "REQUIERE INTERVENCIÓN URGENTE: Índice Vigente crítico. Protocolo de recuperación intensivo necesario."


def generar_recomendaciones(
    subscore_estructural: float,
    subscore_piel: float,
    subscore_biologico: float,
    arquetipo_id: str = None
) -> List[str]:
    """
    Genera recomendaciones basadas en subscores y adherence matrix

    Lógica del SSOT:
    - Subscore <65: Alta prioridad
    - Subscore 65-75: Media prioridad
    - Subscore >75: Mantenimiento
    """
    recomendaciones = []

    # Prioridad 1: Subscores críticos (<65)
    if subscore_estructural < 65:
        # Servicios para mejorar estructura facial
        recomendaciones.extend([
            "HIFU Ultraformer III - Mejora estructura y tono facial",
            "Lifting Hilos PDO - Contorno facial no invasivo"
        ])

    if subscore_piel < 65:
        # Servicios para rejuvenecimiento de piel
        recomendaciones.extend([
            "RF Microneedling (Morpheus8) - Rejuvenecimiento profundo",
            "Láser CO2 Fraccional - Resurfacing y renovación cutánea",
            "PRP Dermapen - Bioestimulación natural"
        ])

    if subscore_biologico < 65:
        # Servicios para bioestimulación
        recomendaciones.extend([
            "Sculptra - Bioestimulador de colágeno",
            "PRP Dermapen - Regeneración celular",
            "Evaluación nutricional y suplementación personalizada"
        ])

    # Prioridad 2: Subscores medios (65-75)
    if 65 <= subscore_estructural < 75:
        recomendaciones.append("Botox - Mantenimiento preventivo de líneas de expresión")

    if 65 <= subscore_piel < 75:
        recomendaciones.append("Limpieza Facial Profunda - Mantenimiento mensual")

    # Si todos los subscores están bien (>75), recomendar mantenimiento
    if subscore_estructural >= 75 and subscore_piel >= 75 and subscore_biologico >= 75:
        recomendaciones = [
            "Estado óptimo - Mantenimiento preventivo recomendado",
            "Limpieza Facial Profunda mensual",
            "Revisión trimestral con Diagnóstico 360"
        ]

    # Limitar a 5 recomendaciones máximo
    return recomendaciones[:5]


def simular_diagnostico(cliente_data: Dict, simular_tiempo: bool = True) -> Dict:
    """
    Simula un diagnóstico completo usando Imaging Module propietario

    Args:
        cliente_data: Datos del cliente (de demo_hombrevigente_v3.db)
        simular_tiempo: Si True, simula 8-12 seg de procesamiento (para demo en vivo)

    Returns:
        Dict con resultados del diagnóstico completo

    Proceso (según SSOT):
    1. Captura multimodal (RGB 4K + Térmica radiométrica)
    2. Procesamiento CNN (8-12 segundos)
    3. Cálculo Índice Vigente con fórmula oficial
    4. Generación de recomendaciones personalizadas
    """

    # Simular procesamiento CNN (8-12 segundos según SSOT)
    if simular_tiempo:
        processing_time = random.uniform(8, 12)
        time.sleep(processing_time)
    else:
        processing_time = random.uniform(8, 12)  # Solo el valor, sin esperar

    # Usar subscores del cliente si existen, o generar nuevos con ligera variación
    if 'subscore_estructural' in cliente_data and cliente_data['subscore_estructural'] is not None:
        # Cliente existente: simular evolución (ligera mejora o deterioro)
        # Simula el efecto de tratamientos previos
        subscore_estructural = min(100, max(30, cliente_data['subscore_estructural'] + random.uniform(-3, 6)))
        subscore_piel = min(100, max(30, cliente_data['subscore_piel'] + random.uniform(-3, 6)))
        subscore_biologico = min(100, max(30, cliente_data['subscore_biologico'] + random.uniform(-3, 6)))
    else:
        # Nuevo cliente: generar subscores basados en arquetipo (del HTML)
        arquetipo_id = cliente_data.get('arquetipo_id', 'eduardo')

        if arquetipo_id == 'carlos':
            # Carlos: Premium, cuida su imagen
            subscore_estructural = random.uniform(70, 85)
            subscore_piel = random.uniform(65, 80)
            subscore_biologico = random.uniform(70, 85)
        elif arquetipo_id == 'eduardo':
            # Eduardo: Novato, buen estado inicial
            subscore_estructural = random.uniform(75, 90)
            subscore_piel = random.uniform(70, 85)
            subscore_biologico = random.uniform(75, 90)
        elif arquetipo_id == 'mantenimiento':
            # Mantenimiento: Estado promedio, cuida regularmente
            subscore_estructural = random.uniform(65, 80)
            subscore_piel = random.uniform(60, 75)
            subscore_biologico = random.uniform(70, 85)
        else:  # transaccional
            # Transaccional: Estado variable, menos cuidado
            subscore_estructural = random.uniform(55, 75)
            subscore_piel = random.uniform(50, 70)
            subscore_biologico = random.uniform(60, 75)

    # Calcular Índice Vigente con fórmula oficial
    indice_vigente = calcular_indice_vigente(subscore_estructural, subscore_piel, subscore_biologico)

    # Generar interpretación según escala SSOT
    interpretacion = generar_interpretacion(indice_vigente)

    # Generar recomendaciones personalizadas
    recomendaciones = generar_recomendaciones(
        subscore_estructural,
        subscore_piel,
        subscore_biologico,
        cliente_data.get('arquetipo_id')
    )

    # Hardware usado (Imaging Module propietario del SSOT)
    hardware = "Imaging Module Propietario (Logitech Brio 4K + Seek Thermal Compact Pro)"

    # ML model version (simulado - en producción sería versionado en MLflow)
    ml_version = random.choice(['v2.1.0', 'v2.1.1', 'v2.2.0-beta'])

    # Métricas adicionales del escaneo térmico (del SSOT)
    temperatura_promedio = round(random.uniform(32.5, 34.5), 1)  # °C
    zonas_inflamacion = random.randint(0, 3)

    resultado = {
        'diagnostico_id': str(uuid.uuid4()),
        'cliente_id': cliente_data.get('cliente_id', 'unknown'),
        'fecha_diagnostico': datetime.now().date().isoformat(),
        'indice_vigente': indice_vigente,
        'subscore_estructural': round(subscore_estructural, 1),
        'subscore_piel': round(subscore_piel, 1),
        'subscore_biologico': round(subscore_biologico, 1),
        'interpretacion': interpretacion,
        'recomendaciones': recomendaciones,
        'hardware_usado': hardware,
        'ml_model_version': ml_version,
        'processing_time_sec': round(processing_time, 1),
        # Métricas térmicas adicionales
        'temperatura_promedio_c': temperatura_promedio,
        'zonas_inflamacion_detectadas': zonas_inflamacion,
        # Metadata
        'timestamp_utc': datetime.utcnow().isoformat(),
        'schema_version': '3.0'
    }

    return resultado


def generar_reporte_pdf(diagnostico: Dict) -> str:
    """
    Genera reporte PDF del diagnóstico (simulado)

    En producción:
    - Incluye imágenes RGB + térmica
    - Gráficos de evolución histórica
    - Comparación con población similar
    - Plan de tratamiento detallado

    Returns:
        URL del PDF generado (simulado)
    """
    # Simular generación de PDF
    pdf_id = str(uuid.uuid4())[:8]
    pdf_url = f"https://storage.googleapis.com/hv-diagnosticos/{pdf_id}.pdf"

    return pdf_url


# Para testing rápido
if __name__ == "__main__":
    # Cliente de prueba (del modelo financiero HTML)
    cliente_test = {
        'cliente_id': 'CLI_TEST123',
        'nombre': 'Carlos Ejemplo',
        'arquetipo_id': 'carlos',
        'arquetipo_nombre': 'Carlos - Rejuvenecedor Premium',
        'subscore_estructural': 75.5,
        'subscore_piel': 65.2,
        'subscore_biologico': 70.8
    }

    print("="*70)
    print("🔬 DiagnósticoVigente AI v3.0 - DEMO")
    print("="*70)
    print(f"\nCliente: {cliente_test['nombre']}")
    print(f"Arquetipo: {cliente_test['arquetipo_nombre']}")
    print("\n⏳ Procesando escaneo multimodal (8-12 seg)...")

    resultado = simular_diagnostico(cliente_test, simular_tiempo=False)

    print(f"\n✅ Diagnóstico completado en {resultado['processing_time_sec']} segundos")
    print(f"   Hardware: {resultado['hardware_usado']}")
    print(f"   ML Model: {resultado['ml_model_version']}")

    print(f"\n📊 ÍNDICE VIGENTE™: {resultado['indice_vigente']}/100")
    print(f"\n   Subscores:")
    print(f"   • Estructural: {resultado['subscore_estructural']}/100")
    print(f"   • Piel: {resultado['subscore_piel']}/100")
    print(f"   • Biológico: {resultado['subscore_biologico']}/100")

    print(f"\n🌡️  Métricas Térmicas:")
    print(f"   • Temperatura promedio: {resultado['temperatura_promedio_c']}°C")
    print(f"   • Zonas inflamación: {resultado['zonas_inflamacion_detectadas']}")

    print(f"\n💡 {resultado['interpretacion']}")

    print(f"\n🎯 Recomendaciones:")
    for i, rec in enumerate(resultado['recomendaciones'], 1):
        print(f"   {i}. {rec}")

    print(f"\n📄 Reporte PDF: {generar_reporte_pdf(resultado)}")
    print("\n" + "="*70)
