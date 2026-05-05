"""
Pydantic models para request/response de la API
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class DiagnosticoRequest(BaseModel):
    """Request para generar un nuevo diagnóstico"""
    cliente_id: Optional[str] = Field(None, description="ID del cliente. Si es None, se usa uno aleatorio")


class DiagnosticoResponse(BaseModel):
    """Response con resultado del diagnóstico"""
    diagnostico_id: str
    cliente_id: str
    cliente_nombre: str
    fecha_diagnostico: str
    indice_vigente: float
    subscore_estructural: float
    subscore_piel: float
    subscore_biologico: float
    interpretacion: str
    recomendaciones: List[str]
    hardware_usado: str
    processing_time_sec: float


class PersonaResponse(BaseModel):
    """Response del análisis PersonaVigente"""
    cliente_id: str
    arquetipo_nombre: str
    propension_compra: float
    churn_propensity: float
    ltv_12m: float
    servicios_recomendados: List[dict]
    razonamiento: str


class OptiPricingRequest(BaseModel):
    """Request para calcular pricing dinámico"""
    servicio_id: str
    cliente_id: str
    fecha_deseada: Optional[str] = None


class OptiPricingResponse(BaseModel):
    """Response con pricing optimizado"""
    servicio_nombre: str
    precio_lista: float
    precio_optimizado: float
    descuento_pct: float
    razon: str
    utilization_level: str  # "bajo", "medio", "alto"
    slots_disponibles: int
