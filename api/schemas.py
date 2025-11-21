from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import uuid

# --- Modelos Base ---

class Metadata(BaseModel):
    module: str
    version: Union[str, int]
    description: Optional[str] = None

# --- Schemas para guardar resultados de análisis ---

class AnalysisResultCreate(BaseModel):
    """Schema para crear/actualizar resultados de análisis desde orchestrator"""
    ficha_cliente_id: str = Field(..., description="UUID del cliente")
    module_name: str = Field(..., description="Nombre del módulo (Q1, Q2, ..., Q10)")
    results: Dict[str, Any] = Field(..., description="Resultados completos del análisis")

class AnalysisResultResponse(BaseModel):
    """Schema de respuesta al guardar resultados"""
    success: bool
    message: str
    insight_id: Optional[str] = None
    
    class Config:
        from_attributes = True

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

# =============================================================================
# AUTENTICACIÓN Y USUARIOS
# =============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    """Datos para registrar un nuevo usuario y su organización."""
    email: str
    password: str
    full_name: str
    tenant_name: str  # Nombre de la agencia/empresa

class UserResponse(BaseModel):
    """Datos públicos del usuario devueltos por la API."""
    id: Any
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    tenant_id: Any
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Datos para actualizar un usuario existente."""
    full_name: Optional[str] = None
    role: Optional[str] = None  # admin, analyst, viewer
    is_active: Optional[bool] = None
    password: Optional[str] = None  # Si se proporciona, se actualiza


class UserListResponse(BaseModel):
    """Lista de usuarios con paginación."""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int


# =============================================================================
# FICHAS CLIENTE (Brands)
# =============================================================================

class FichaClienteCreate(BaseModel):
    """Datos para crear una nueva ficha de cliente/marca."""
    brand_name: str
    industry: Optional[str] = None
    brand_archetype: Optional[str] = None
    tone_of_voice: Optional[str] = None
    target_audience: Optional[str] = None
    competitors: Optional[List[str]] = None

class FichaClienteResponse(BaseModel):
    """Respuesta con datos de una ficha cliente."""
    id: Any
    tenant_id: Any
    brand_name: str
    industry: Optional[str] = None
    brand_archetype: Optional[str] = None
    tone_of_voice: Optional[str] = None
    target_audience: Optional[str] = None
    competitors: Optional[List[str]] = None
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# =============================================================================
# SOCIAL MEDIA POSTS
# =============================================================================

class SocialMediaPostCreate(BaseModel):
    """Datos para crear/ingerir un post."""
    ficha_cliente_id: Any
    platform: str  # "instagram", "tiktok", "twitter", etc.
    post_url: str
    author_username: str
    post_text: Optional[str] = None
    posted_at: Optional[datetime] = None
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    shares_count: Optional[int] = 0
    views_count: Optional[int] = 0

class SocialMediaPostResponse(BaseModel):
    """Respuesta con datos de un post."""
    id: Any
    ficha_cliente_id: Any
    platform: str
    post_url: str
    author_username: str
    post_text: Optional[str] = None
    posted_at: Optional[datetime] = None
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None
    shares_count: Optional[int] = None
    views_count: Optional[int] = None
    ingested_at: datetime
    
    class Config:
        from_attributes = True

# =============================================================================
# INSIGHTS (Analysis Results)
# =============================================================================

class InsightResponse(BaseModel):
    """Respuesta con resultados de análisis guardados."""
    id: Any
    ficha_cliente_id: Any
    analysis_type: str  # "Q1", "Q2", etc.
    q1_emociones: Optional[Dict[str, Any]] = None
    q2_personalidad: Optional[Dict[str, Any]] = None
    q3_topicos: Optional[Dict[str, Any]] = None
    q4_marcos_narrativos: Optional[Dict[str, Any]] = None
    q5_influenciadores: Optional[Dict[str, Any]] = None
    q6_oportunidades: Optional[Dict[str, Any]] = None
    q7_sentimiento: Optional[Dict[str, Any]] = None
    q8_temporal: Optional[Dict[str, Any]] = None
    q9_recomendaciones: Optional[Dict[str, Any]] = None
    q10_resumen: Optional[Dict[str, Any]] = None
    analyzed_at: datetime
    
    class Config:
        from_attributes = True
