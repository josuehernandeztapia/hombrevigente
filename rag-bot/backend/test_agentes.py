#!/usr/bin/env python3
"""
Script de prueba rápida para los 3 agentes AI
Ejecuta sin necesidad de levantar FastAPI
"""
import sys
sys.path.append('..')

from agents import diagnostico_vigente, persona_vigente, opti_vigente
import database as db
import json


def test_diagnostico():
    """Prueba DiagnósticoVigente"""
    print("\n" + "="*70)
    print("🔬 TEST: DiagnósticoVigente AI")
    print("="*70)

    # Obtener un cliente aleatorio
    cliente = db.get_random_cliente()
    print(f"\n📋 Cliente: {cliente['nombre']} ({cliente['arquetipo_nombre']})")
    print(f"   Índice Vigente actual: {cliente['indice_vigente']}")

    # Ejecutar diagnóstico
    print("\n⏳ Ejecutando diagnóstico (sin simular tiempo)...")
    resultado = diagnostico_vigente.simular_diagnostico(cliente, simular_tiempo=False)

    print(f"\n✅ Diagnóstico completado:")
    print(f"   • Índice Vigente: {resultado['indice_vigente']}")
    print(f"   • Subscore Estructural: {resultado['subscore_estructural']}")
    print(f"   • Subscore Piel: {resultado['subscore_piel']}")
    print(f"   • Subscore Biológico: {resultado['subscore_biologico']}")
    print(f"   • Interpretación: {resultado['interpretacion']}")
    print(f"   • Recomendaciones: {resultado['recomendaciones']}")
    print(f"   • Hardware usado: {resultado['hardware_usado']}")
    print(f"   • Tiempo procesamiento: {resultado['processing_time_sec']} seg")

    return cliente


def test_persona(cliente):
    """Prueba PersonaVigente"""
    print("\n" + "="*70)
    print("🎯 TEST: PersonaVigente AI")
    print("="*70)

    # Obtener historial
    historial = db.get_eventos_by_cliente(cliente['cliente_id'])
    print(f"\n📊 Historial: {len(historial)} eventos de compra")

    # Ejecutar análisis
    analisis = persona_vigente.analizar_propension(cliente, historial)
    servicios_rec = persona_vigente.recomendar_servicios(
        cliente,
        indice_vigente=cliente['indice_vigente'],
        top_n=5
    )
    razonamiento = persona_vigente.generar_razonamiento(cliente, analisis)

    print(f"\n✅ Análisis completado:")
    print(razonamiento)

    print(f"\n🛍️  Servicios recomendados:")
    for srv in servicios_rec:
        print(f"   • {srv['nombre']} (${srv['precio']:,.0f}) - Score: {srv['score']}")
        print(f"     {srv['razon']}")


def test_opti(cliente):
    """Prueba OptiVigente"""
    print("\n" + "="*70)
    print("💰 TEST: OptiVigente AI")
    print("="*70)

    # Cargar un servicio de prueba
    with open('../servicios_fase1_validados.json', 'r') as f:
        data = json.load(f)
        servicio = data['servicios_individuales_fase1'][3]  # HIFU

    print(f"\n📦 Servicio: {servicio['nombre']}")
    print(f"   Precio lista: ${servicio['precio_lista']:,.0f}")

    # Calcular pricing dinámico
    resultado = opti_vigente.calcular_precio_dinamico(
        servicio=servicio,
        cliente=cliente,
        utilization_actual=0.65  # 65% utilización
    )

    print(f"\n✅ Pricing optimizado:")
    print(f"   • Precio lista: ${resultado['precio_lista']:,.0f}")
    print(f"   • Precio optimizado: ${resultado['precio_optimizado']:,.0f}")
    print(f"   • Descuento: {resultado['descuento_pct']}%")
    print(f"   • Razón: {resultado['razon']}")
    print(f"   • Utilización: {resultado['utilization_actual']}%")
    print(f"   • Slots disponibles: {resultado['slots_disponibles']}")

    # Asignar slot
    slot = opti_vigente.asignar_slot_optimo(servicio, cliente)
    print(f"\n📅 Slot asignado:")
    print(f"   • Fecha: {slot['fecha_sugerida']} a las {slot['hora_sugerida']}")
    print(f"   • Duración: {slot['duracion_estimada']} min")
    print(f"   • Prioridad: {slot['prioridad']}")
    print(f"   • {slot['mensaje']}")


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║            TEST DE AGENTES AI - HOMBRE VIGENTE                   ║
    ║            Demo Investor Seed Round                              ║
    ║                                                                  ║
    ║            Ejecutando pruebas de los 3 agentes...                ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Test 1: DiagnósticoVigente
        cliente = test_diagnostico()

        # Test 2: PersonaVigente
        test_persona(cliente)

        # Test 3: OptiVigente
        test_opti(cliente)

        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("="*70)
        print("\nLos 3 agentes AI están funcionando correctamente.")
        print("Puedes iniciar el servidor FastAPI con: python main.py\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
