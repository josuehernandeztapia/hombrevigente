"""
Hombre Vigente - Backend FastAPI
Demo Investor Seed Round

API con 3 agentes AI simulados:
- DiagnósticoVigente
- PersonaVigente
- OptiVigente
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json

# Importar utilidades locales
import database as db
from agents import diagnostico_vigente, persona_vigente, opti_vigente
import models

# Inicializar FastAPI
app = FastAPI(
    title="Hombre Vigente API",
    description="Backend demo con 3 agentes AI simulados para investor pitch",
    version="1.0.0"
)

# CORS (permitir frontend en localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS DE AGENTES
# ============================================================================

@app.post("/api/diagnostico", response_model=models.DiagnosticoResponse)
async def generar_diagnostico(request: models.DiagnosticoRequest):
    """
    Genera un nuevo diagnóstico usando DiagnósticoVigente AI

    - Si se proporciona cliente_id, usa ese cliente
    - Si no, genera diagnóstico para un cliente aleatorio
    - Simula procesamiento ML de 8-12 segundos
    """
    # Obtener cliente
    if request.cliente_id:
        cliente = db.get_cliente_by_id(request.cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
    else:
        cliente = db.get_random_cliente()

    # Ejecutar agente DiagnósticoVigente
    resultado = diagnostico_vigente.simular_diagnostico(
        cliente_data=cliente,
        simular_tiempo=True  # Simula 8-12 seg
    )

    # Guardar en BD
    db.insert_diagnostico(resultado)

    # Convertir recomendaciones de string a lista
    recomendaciones_list = resultado['recomendaciones'].split('; ')

    return models.DiagnosticoResponse(
        diagnostico_id=resultado['diagnostico_id'],
        cliente_id=resultado['cliente_id'],
        cliente_nombre=cliente['nombre'],
        fecha_diagnostico=resultado['fecha_diagnostico'],
        indice_vigente=resultado['indice_vigente'],
        subscore_estructural=resultado['subscore_estructural'],
        subscore_piel=resultado['subscore_piel'],
        subscore_biologico=resultado['subscore_biologico'],
        interpretacion=resultado['interpretacion'],
        recomendaciones=recomendaciones_list,
        hardware_usado=resultado['hardware_usado'],
        processing_time_sec=resultado['processing_time_sec']
    )


@app.get("/api/persona/{cliente_id}", response_model=models.PersonaResponse)
async def analizar_persona(cliente_id: str):
    """
    Analiza un cliente con PersonaVigente AI

    Retorna:
    - Propensión de compra
    - Riesgo de churn
    - Servicios recomendados
    - Razonamiento del análisis
    """
    # Obtener cliente
    cliente = db.get_cliente_by_id(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Obtener historial
    historial = db.get_eventos_by_cliente(cliente_id)

    # Ejecutar agente PersonaVigente
    analisis = persona_vigente.analizar_propension(cliente, historial_eventos=historial)

    # Obtener servicios recomendados
    servicios_rec = persona_vigente.recomendar_servicios(
        cliente,
        indice_vigente=cliente.get('indice_vigente'),
        top_n=5
    )

    # Generar razonamiento
    razonamiento = persona_vigente.generar_razonamiento(cliente, analisis)

    return models.PersonaResponse(
        cliente_id=cliente_id,
        arquetipo_nombre=cliente['arquetipo_nombre'],
        propension_compra=analisis['propension_compra'],
        churn_propensity=analisis['churn_propensity'],
        ltv_12m=cliente['ltv_12m'],
        servicios_recomendados=servicios_rec,
        razonamiento=razonamiento
    )


@app.post("/api/opti/pricing", response_model=models.OptiPricingResponse)
async def calcular_pricing_dinamico(request: models.OptiPricingRequest):
    """
    Calcula precio optimizado usando OptiVigente AI

    Considera:
    - Utilización actual del club
    - Arquetipo del cliente
    - Demanda histórica del servicio
    """
    # Obtener cliente
    cliente = db.get_cliente_by_id(request.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Cargar catálogo de servicios
    with open('../servicios_fase1_validados.json', 'r') as f:
        data = json.load(f)
        servicios = data['servicios_individuales_fase1']

    # Buscar servicio
    servicio = next((s for s in servicios if s['id'] == request.servicio_id), None)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    # Ejecutar agente OptiVigente
    resultado = opti_vigente.calcular_precio_dinamico(
        servicio=servicio,
        cliente=cliente,
        fecha_deseada=request.fecha_deseada
    )

    return models.OptiPricingResponse(
        servicio_nombre=resultado['servicio_nombre'],
        precio_lista=resultado['precio_lista'],
        precio_optimizado=resultado['precio_optimizado'],
        descuento_pct=resultado['descuento_pct'],
        razon=resultado['razon'],
        utilization_level=resultado['utilization_level'],
        slots_disponibles=resultado['slots_disponibles']
    )


# ============================================================================
# ENDPOINTS DE DATOS (para explorar)
# ============================================================================

@app.get("/api/clientes")
async def listar_clientes(limit: int = 10, arquetipo: Optional[str] = None):
    """Lista clientes con filtros opcionales"""
    clientes = db.get_clientes(limit=limit, arquetipo=arquetipo)
    return {"clientes": clientes, "total": len(clientes)}


@app.get("/api/clientes/{cliente_id}")
async def obtener_cliente(cliente_id: str):
    """Obtiene detalles de un cliente específico"""
    cliente = db.get_cliente_by_id(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Agregar historial
    eventos = db.get_eventos_by_cliente(cliente_id)
    diagnosticos = db.get_diagnosticos_by_cliente(cliente_id)

    return {
        "cliente": cliente,
        "eventos": eventos,
        "diagnosticos": diagnosticos
    }


@app.get("/api/analytics/revenue")
async def obtener_analytics():
    """Obtiene métricas de revenue y analytics"""
    return db.get_analytics_revenue()


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Hombre Vigente API - Demo Investor",
        "version": "1.0.0",
        "docs": "/docs",
        "agentes": [
            "DiagnósticoVigente AI",
            "PersonaVigente AI",
            "OptiVigente AI"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "database": "connected"}


# ============================================================================
# EJECUTAR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          HOMBRE VIGENTE - BACKEND API                    ║
    ║          Demo Investor Seed Round                        ║
    ║                                                          ║
    ║          3 Agentes AI Simulados:                         ║
    ║          • DiagnósticoVigente                            ║
    ║          • PersonaVigente                                ║
    ║          • OptiVigente                                   ║
    ║                                                          ║
    ║          Docs: http://localhost:8000/docs                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
