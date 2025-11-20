"""
Pixely Partners API - Pydantic Schemas

Data contracts for all API requests/responses.
Ensures type safety, validation, and documentation.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator


# =============================================================================
# INPUT SCHEMAS (Request Bodies)
# =============================================================================

class AnalysisRequest(BaseModel):
    """
    Request schema for triggering an analysis module.
    
    The user specifies which module(s) to run and provides the client data.
    """
    module: str = Field(
        ...,
        description="Module code (q1-q10) or 'all' to run complete pipeline",
        example="q1"
    )
    client_name: str = Field(
        ...,
        description="Name of the client/brand being analyzed",
        example="PixelyBrand"
    )
    ingested_data_path: Optional[str] = Field(
        None,
        description="Path to ingested_data.json (if not in default location)",
        example="/data/my_client.json"
    )
    
    @validator('module')
    def validate_module(cls, v):
        """Ensure module is valid (q1-q10 or 'all')."""
        valid_modules = [f"q{i}" for i in range(1, 11)] + ["all"]
        if v not in valid_modules:
            raise ValueError(f"Module must be one of {valid_modules}, got {v}")
        return v


# =============================================================================
# OUTPUT SCHEMAS (Response Bodies)
# =============================================================================

class AnalysisResult(BaseModel):
    """
    Standard response schema for any analysis module.
    
    Contains metadata, results, and error information.
    """
    module: str = Field(..., description="Module code executed")
    version: int = Field(..., description="Module version")
    status: str = Field(..., description="Execution status: 'success' or 'failed'")
    data: Dict[str, Any] = Field(..., description="Module output (structure varies by module)")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")


class PipelineResult(BaseModel):
    """
    Response schema for complete pipeline execution (all modules).
    
    Contains results from all 10 modules and summary statistics.
    """
    status: str = Field(..., description="Overall execution status")
    total_modules: int = Field(..., description="Total modules executed")
    successful_modules: int = Field(..., description="Number of successful modules")
    failed_modules: int = Field(..., description="Number of failed modules")
    results: Dict[str, AnalysisResult] = Field(..., description="Results keyed by module code")
    total_execution_time_ms: Optional[float] = Field(None, description="Total execution time")


class HealthCheckResponse(BaseModel):
    """
    Response schema for health check endpoint.
    """
    status: str = Field(..., description="API status: 'healthy' or 'unhealthy'")
    version: str = Field(..., description="API version")
    modules_available: List[str] = Field(..., description="List of available analysis modules")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


# =============================================================================
# DETAILED MODULE SCHEMAS (Optional - for advanced use)
# =============================================================================

class Q1EmocionesResult(BaseModel):
    """Q1: Emotions Analysis Result."""
    emocion_dominante: Dict[str, Any]
    emociones_secundarias: List[Dict[str, Any]]
    resumen_global: Dict[str, Any]


class Q2PersonalidadResult(BaseModel):
    """Q2: Brand Personality (Aaker) Result."""
    analisis_por_publicacion: List[Dict[str, Any]]
    resumen_global_personalidad: Dict[str, float]
    analisis_agregado: Dict[str, float]


class Q3TemasResult(BaseModel):
    """Q3: Topics Analysis Result."""
    temas_principales: List[Dict[str, Any]]
    resumen_global: Dict[str, Any]


class Q4MarcosNarrativosResult(BaseModel):
    """Q4: Narrative Frameworks Result."""
    marcos_detectados: List[Dict[str, Any]]
    matriz_marcos: Dict[str, Any]


class Q5InfluenciadoresResult(BaseModel):
    """Q5: Influencers Analysis Result."""
    influenciadores_principales: List[Dict[str, Any]]
    resumen_global: Dict[str, Any]


class Q6OportunidadesResult(BaseModel):
    """Q6: Opportunities Analysis Result."""
    oportunidades: List[Dict[str, Any]]
    resumen_global: Dict[str, Any]


class Q7SentimientoDetalladoResult(BaseModel):
    """Q7: Detailed Sentiment Analysis Result."""
    analisis_por_publicacion: List[Dict[str, Any]]
    analisis_agregado: Dict[str, Any]
    resumen_global: Dict[str, Any]


class Q8TemporalResult(BaseModel):
    """Q8: Temporal Analysis Result."""
    serie_temporal_semanal: List[Dict[str, Any]]
    resumen_global: Dict[str, Any]


class Q9RecomendacionesResult(BaseModel):
    """Q9: Recommendations Analysis Result."""
    lista_recomendaciones: List[Dict[str, Any]]
    resumen_global: Dict[str, Any]


class Q10ResumenEjecutivoResult(BaseModel):
    """Q10: Executive Summary Result."""
    alerta_prioritaria: str
    hallazgos_clave: List[str]
    implicaciones_estrategicas: str
    resumen_general: str
    kpis_principales: Dict[str, Any]
    urgencias_por_prioridad: Dict[str, List[str]]


# =============================================================================
# ERROR SCHEMAS
# =============================================================================

class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error description")
    status_code: int = Field(..., description="HTTP status code")
