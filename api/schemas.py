from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

# --- Modelos Base ---

class Metadata(BaseModel):
    module: str
    version: Union[str, int]
    description: Optional[str] = None

# --- Q1: Emociones ---
class Q1Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener 'analisis_por_publicacion' y 'resumen_global_emociones'")
    errors: List[str] = []

# --- Q2: Personalidad ---
class Q2Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener 'analisis_por_publicacion' (rasgos_aaker) y 'resumen_global_personalidad'")
    errors: List[str] = []

# --- Q3: Tópicos ---
class Q3Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener 'analisis_por_publicacion' (topicos) y 'topicos_principales'")
    errors: List[str] = []

# --- Q4: Marcos Narrativos ---
class Q4Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener 'analisis_por_publicacion' (distribucion_marcos) y 'analisis_agregado'")
    errors: List[str] = []

# --- Q5: Influenciadores ---
class Q5Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener 'analisis_influenciadores' y 'influenciadores_globales'")
    errors: List[str] = []

# --- Q6: Oportunidades ---
class Q6Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener lista 'oportunidades' con gap_score y competencia_score (Impacto)")
    errors: List[str] = []

# --- Q7: Sentimiento Detallado ---
class Q7Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener 'analisis_por_publicacion' y 'analisis_agregado' (normalizado)")
    errors: List[str] = []

# --- Q8: Temporal ---
class Q8Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener 'serie_temporal_semanal' y 'anomalias_detectadas'")
    errors: List[str] = []

# --- Q9: Recomendaciones ---
class Q9Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener 'lista_recomendaciones' con prioridad calculada")
    errors: List[str] = []

# --- Q10: Resumen Ejecutivo ---
class Q10Response(BaseModel):
    metadata: Metadata
    results: Dict[str, Any] = Field(..., description="Debe contener 'alerta_prioritaria', 'hallazgos_clave', 'kpis_principales'")
    errors: List[str] = []
