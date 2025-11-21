"""
Pixely Partners API - FastAPI Server

Main entry point for the professional web API.
Exposes the 10 analysis modules as HTTP endpoints.
CONNECTED TO REAL ORCHESTRATOR MODULES - NOT A PLACEHOLDER.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
from contextlib import asynccontextmanager

# Importar dependencias y esquemas
from .dependencies import get_openai_client, get_config, get_current_user, get_posts_and_comments_from_db
from . import schemas, models, security
from .database import get_db

# Import task routes
from . import routes_tasks

# --- IMPORTAR TUS MÓDULOS REALES ---
from orchestrator.analysis_modules.q1_emociones import Q1Emociones
from orchestrator.analysis_modules.q2_personalidad import Q2Personalidad
from orchestrator.analysis_modules.q3_topicos import Q3Topicos
from orchestrator.analysis_modules.q4_marcos_narrativos import Q4MarcosNarrativos
from orchestrator.analysis_modules.q5_influenciadores import Q5Influenciadores
from orchestrator.analysis_modules.q6_oportunidades import Q6Oportunidades
from orchestrator.analysis_modules.q7_sentimiento_detallado import Q7SentimientoDetallado
from orchestrator.analysis_modules.q8_temporal import Q8Temporal
from orchestrator.analysis_modules.q9_recomendaciones import Q9Recomendaciones
from orchestrator.analysis_modules.q10_resumen_ejecutivo import Q10ResumenEjecutivo

# Configurar Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# LIFECYCLE EVENTS
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle FastAPI startup and shutdown events.
    
    Startup: Initialize clients and resources
    Shutdown: Clean up connections
    """
    # STARTUP
    logger.info("🚀 Pixely Partners API Starting (PRODUCTION MODE - CONNECTED)...")
    config = get_config()
    logger.info(f"API Version: 1.0.0")
    logger.info(f"OpenAI Model: {config['openai_model']}")
    logger.info(f"Orchestrator Outputs: {config['outputs_dir']}")
    logger.info("✅ All 10 Q modules connected")
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Pixely Partners API Shutting down...")
    logger.info("API Shutdown complete")


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="Pixely Partners Analytics API",
    description="API conectada al motor de análisis real (Q1-Q10)",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to known origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include task management router
app.include_router(routes_tasks.router)


# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - minimal health check."""
    return {
        "message": "Pixely Partners API v2",
        "mode": "production_connected",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    config = get_config()
    return {
        "status": "healthy",
        "version": "1.0.0",
        "mode": "production_connected",
        "modules_available": [
            "Q1-Emociones", "Q2-Personalidad", "Q3-Tópicos", 
            "Q4-MarcosNarrativos", "Q5-Influenciadores", "Q6-Oportunidades",
            "Q7-SentimientoDetallado", "Q8-Temporal", "Q9-Recomendaciones", "Q10-ResumenEjecutivo"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# ENDPOINTS DE AUTENTICACIÓN
# =============================================================================

@app.post("/register", response_model=schemas.UserResponse, tags=["Authentication"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario y su organización (Tenant).
    """
    # 1. Verificar si el usuario ya existe
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Verificar o Crear Tenant (Organización)
    # Nota: En un SaaS real, esto validaría unicidad. Aquí simplificamos.
    db_tenant = db.query(models.Tenant).filter(models.Tenant.name == user.tenant_name).first()
    if not db_tenant:
        db_tenant = models.Tenant(name=user.tenant_name)
        db.add(db_tenant)
        db.commit()
        db.refresh(db_tenant)
    
    # 3. Crear Usuario
    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        tenant_id=db_tenant.id,
        role="admin"  # El primer usuario es admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint de Login (OAuth2 standard).
    Recibe username (email) y password, devuelve Access Token con info de usuario.
    """
    # 1. Buscar usuario
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Validar contraseña
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generar Token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # 4. Get first ficha_cliente for this tenant (if any)
    first_ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.tenant_id == user.tenant_id
    ).first()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_email": user.email,
        "tenant_id": str(user.tenant_id),
        "ficha_cliente_id": str(first_ficha.id) if first_ficha else None
    }


@app.get("/users/me", response_model=schemas.UserResponse, tags=["Authentication"])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Retorna la información del usuario actualmente logueado."""
    return current_user


# =============================================================================
# USER MANAGEMENT ENDPOINTS (CRUD)
# =============================================================================

@app.get("/users", response_model=schemas.UserListResponse, tags=["User Management"])
def list_users(
    page: int = 1,
    per_page: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos los usuarios del tenant actual (con paginación).
    Solo accesible para admin.
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can list users")
    
    # Calcular offset
    offset = (page - 1) * per_page
    
    # Obtener usuarios del mismo tenant
    query = db.query(models.User).filter(
        models.User.tenant_id == current_user.tenant_id
    )
    
    total = query.count()
    users = query.offset(offset).limit(per_page).all()
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@app.get("/users/{user_id}", response_model=schemas.UserResponse, tags=["User Management"])
def get_user(
    user_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene información de un usuario específico.
    Solo accesible para admin.
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can view user details")
    
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.tenant_id == current_user.tenant_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@app.post("/users", response_model=schemas.UserResponse, tags=["User Management"])
def create_user(
    user_data: schemas.UserCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario en el tenant actual.
    Solo accesible para admin.
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    # Verificar que el email no exista
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Crear usuario en el mismo tenant que el admin
    hashed_password = security.get_password_hash(user_data.password)
    new_user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        tenant_id=current_user.tenant_id,  # Mismo tenant que el admin
        role="viewer"  # Por defecto viewer, admin puede cambiar después
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Admin {current_user.email} created user {new_user.email}")
    return new_user


@app.patch("/users/{user_id}", response_model=schemas.UserResponse, tags=["User Management"])
def update_user(
    user_id: str,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza un usuario existente.
    Solo accesible para admin.
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can update users")
    
    # Buscar usuario en el mismo tenant
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.tenant_id == current_user.tenant_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Actualizar campos proporcionados
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    
    if user_update.role is not None:
        if user_update.role not in ["admin", "analyst", "viewer"]:
            raise HTTPException(status_code=400, detail="Invalid role")
        user.role = user_update.role
    
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    if user_update.password is not None:
        user.hashed_password = security.get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Admin {current_user.email} updated user {user.email}")
    return user


@app.delete("/users/{user_id}", tags=["User Management"])
def delete_user(
    user_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario.
    Solo accesible para admin.
    No se puede eliminar a sí mismo.
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    # No permitir auto-eliminación
    if str(current_user.id) == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    # Buscar usuario en el mismo tenant
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.tenant_id == current_user.tenant_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"Admin {current_user.email} deleted user {user.email}")
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.email} deleted successfully"}


# =============================================================================
# FICHAS CLIENTE ENDPOINTS (Brands Management)
# =============================================================================

@app.post("/fichas_cliente", response_model=schemas.FichaClienteResponse, tags=["Fichas Cliente"])
def create_ficha_cliente(
    ficha: schemas.FichaClienteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea una nueva ficha de cliente/marca para el tenant del usuario."""
    new_ficha = models.FichaCliente(
        tenant_id=current_user.tenant_id,
        brand_name=ficha.brand_name,
        industry=ficha.industry,
        brand_archetype=ficha.brand_archetype,
        tone_of_voice=ficha.tone_of_voice,
        target_audience=ficha.target_audience,
        competitors=ficha.competitors
    )
    db.add(new_ficha)
    db.commit()
    db.refresh(new_ficha)
    return new_ficha


@app.get("/fichas_cliente", response_model=List[schemas.FichaClienteResponse], tags=["Fichas Cliente"])
def list_fichas_cliente(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todas las fichas de cliente del tenant del usuario."""
    fichas = db.query(models.FichaCliente).filter(
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).all()
    return fichas


@app.get("/fichas_cliente/{ficha_id}", response_model=schemas.FichaClienteResponse, tags=["Fichas Cliente"])
def get_ficha_cliente(
    ficha_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene detalles de una ficha específica."""
    ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.id == ficha_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha not found")
    return ficha


@app.delete("/fichas_cliente/{ficha_id}", tags=["Fichas Cliente"])
def delete_ficha_cliente(
    ficha_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina una ficha de cliente."""
    ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.id == ficha_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha not found")
    
    db.delete(ficha)
    db.commit()
    return {"message": "Ficha deleted successfully"}


@app.patch("/fichas_cliente/{ficha_id}/last_analysis_timestamp", tags=["Fichas Cliente"])
def update_last_analysis_timestamp(
    ficha_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el timestamp de la última ejecución del orchestrator.
    Solo puede ser llamado por el usuario orchestrator (admin).
    """
    import os
    
    # Verificar que solo el orchestrator puede actualizar este campo
    orchestrator_email = os.environ.get("ORCHESTRATOR_USER", "admin")
    if current_user.email != orchestrator_email and current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only orchestrator or admin can update last_analysis_timestamp"
        )
    
    # Buscar la ficha
    ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.id == ficha_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha not found")
    
    # Actualizar timestamp
    from datetime import datetime
    ficha.last_analysis_timestamp = datetime.utcnow()
    db.commit()
    db.refresh(ficha)
    
    return {
        "message": "last_analysis_timestamp updated successfully",
        "last_analysis_timestamp": ficha.last_analysis_timestamp.isoformat(),
        "ficha_id": str(ficha.id)
    }


# =============================================================================
# SOCIAL MEDIA POSTS ENDPOINTS (Data Ingestion)
# =============================================================================

@app.post("/social_media_posts", response_model=schemas.SocialMediaPostResponse, tags=["Social Media"])
def create_social_media_post(
    post: schemas.SocialMediaPostCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingesta un nuevo post de redes sociales asociado a una ficha cliente."""
    # Verificar que la ficha pertenezca al tenant del usuario
    ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.id == post.ficha_cliente_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha cliente not found")
    
    new_post = models.SocialMediaPost(
        ficha_cliente_id=post.ficha_cliente_id,
        platform=post.platform,
        post_url=post.post_url,
        author_username=post.author_username,
        post_text=post.post_text,
        posted_at=post.posted_at,
        likes_count=post.likes_count,
        comments_count=post.comments_count,
        shares_count=post.shares_count,
        views_count=post.views_count
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/social_media_posts", response_model=List[schemas.SocialMediaPostResponse], tags=["Social Media"])
def list_social_media_posts(
    ficha_cliente_id: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista posts de redes sociales. Opcional: filtrar por ficha_cliente_id."""
    query = db.query(models.SocialMediaPost).join(
        models.FichaCliente,
        models.SocialMediaPost.ficha_cliente_id == models.FichaCliente.id
    ).filter(
        models.FichaCliente.tenant_id == current_user.tenant_id
    )
    
    if ficha_cliente_id:
        query = query.filter(models.SocialMediaPost.ficha_cliente_id == ficha_cliente_id)
    
    posts = query.all()
    return posts


# =============================================================================
# INSIGHTS ENDPOINTS (Analysis Results)
# =============================================================================

@app.get("/insights/{ficha_cliente_id}", response_model=schemas.InsightResponse, tags=["Insights"])
def get_insights(
    ficha_cliente_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el último insight para un cliente específico."""
    # Buscar el insight más reciente para este cliente
    insight = db.query(models.SocialMediaInsight).join(
        models.FichaCliente,
        models.SocialMediaInsight.cliente_id == models.FichaCliente.id
    ).filter(
        models.FichaCliente.tenant_id == current_user.tenant_id,
        models.SocialMediaInsight.cliente_id == ficha_cliente_id
    ).order_by(models.SocialMediaInsight.created_at.desc()).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="No analysis found for this client")
    
    return insight


# =============================================================================
# ORCHESTRATOR ANALYSIS RESULTS ENDPOINT
# =============================================================================

@app.post("/analysis_results", response_model=schemas.AnalysisResultResponse, tags=["Orchestrator"])
async def save_analysis_results(
    data: schemas.AnalysisResultCreate,
    db: Session = Depends(get_db)
):
    """
    Endpoint para que el orchestrator guarde resultados de análisis.
    
    Este endpoint recibe los resultados de Q1-Q10 desde el orchestrator
    y los almacena en la tabla social_media_insights.
    
    Args:
        data: AnalysisResultCreate con ficha_cliente_id, module_name y results
        db: Database session
    
    Returns:
        AnalysisResultResponse con success, message e insight_id
    """
    try:
        logger.info(f"📥 Receiving analysis results for {data.module_name} - Client: {data.ficha_cliente_id}")
        
        # Validar que el cliente existe
        ficha = db.query(models.FichaCliente).filter(
            models.FichaCliente.id == data.ficha_cliente_id
        ).first()
        
        if not ficha:
            raise HTTPException(
                status_code=404, 
                detail=f"FichaCliente {data.ficha_cliente_id} not found"
            )
        
        # Mapeo de módulos a columnas de la tabla
        module_column_map = {
            "Q1": "q1_emociones",
            "Q2": "q2_personalidad",
            "Q3": "q3_topicos",
            "Q4": "q4_marcos_narrativos",
            "Q5": "q5_influenciadores",
            "Q6": "q6_oportunidades",
            "Q7": "q7_sentimiento",
            "Q8": "q8_temporal",
            "Q9": "q9_recomendaciones",
            "Q10": "q10_resumen"
        }
        
        column_name = module_column_map.get(data.module_name)
        if not column_name:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid module_name: {data.module_name}. Must be Q1-Q10"
            )
        
        # Buscar insight existente para este cliente (último análisis)
        insight = db.query(models.SocialMediaInsight).filter(
            models.SocialMediaInsight.cliente_id == data.ficha_cliente_id
        ).order_by(
            models.SocialMediaInsight.analysis_date.desc()
        ).first()
        
        # Si no existe o es antiguo (más de 1 día), crear nuevo
        if not insight or (datetime.utcnow() - insight.analysis_date).days >= 1:
            insight = models.SocialMediaInsight(
                cliente_id=data.ficha_cliente_id,
                analysis_date=datetime.utcnow(),
                total_posts_analyzed=0,
                total_comments_analyzed=0,
                analysis_status="in_progress"
            )
            db.add(insight)
            db.flush()  # Para obtener el ID
            logger.info(f"✨ Created new insight record: {insight.id}")
        
        # Actualizar la columna correspondiente al módulo
        setattr(insight, column_name, data.results)
        logger.info(f"✅ Updated {column_name} in insight {insight.id}")
        
        # Actualizar metadata si disponible
        if "metadata" in data.results:
            results_data = data.results.get("results", {})
            if "analisis_por_publicacion" in results_data:
                insight.total_posts_analyzed = len(results_data["analisis_por_publicacion"])
        
        # Commit
        db.commit()
        db.refresh(insight)
        
        return schemas.AnalysisResultResponse(
            success=True,
            message=f"{data.module_name} results saved successfully",
            insight_id=str(insight.id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error saving {data.module_name} results: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error saving analysis results: {str(e)}"
        )


# =============================================================================
# INDIVIDUAL MODULE ENDPOINTS (Q1-Q10)
# =============================================================================

async def _save_analysis_to_db(
    db: Session,
    ficha_cliente_id: str,
    tenant_id: Any,
    analysis_type: str,
    field_name: str,
    results: Dict[str, Any]
):
    """Helper para guardar resultados de análisis en BD."""
    # Verificar que la ficha pertenezca al tenant
    ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.id == ficha_cliente_id,
        models.FichaCliente.tenant_id == tenant_id
    ).first()
    
    if not ficha:
        raise HTTPException(status_code=404, detail="Ficha cliente not found")
    
    # Buscar o crear insight
    insight = db.query(models.SocialMediaInsight).filter(
        models.SocialMediaInsight.ficha_cliente_id == ficha_cliente_id
    ).first()
    
    if insight:
        setattr(insight, field_name, results)
        insight.analysis_type = analysis_type
    else:
        insight = models.SocialMediaInsight(
            ficha_cliente_id=ficha_cliente_id,
            analysis_type=analysis_type,
            **{field_name: results}
        )
        db.add(insight)
    
    db.commit()
    db.refresh(insight)
    return insight


@app.post("/analyze/q1", tags=["Modules"], response_model=schemas.Q1Response)
async def analyze_q1(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q1 - Análisis de Emociones y guardar en BD."""
    try:
        logger.info(f"Starting Q1 - Emociones analysis for client {ficha_cliente_id}")
        
        # Load data from database for this specific client
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        
        analyzer = Q1Emociones(client, config)
        result = await analyzer.analyze()
        
        # Guardar en BD
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q1", "q1_emociones", result["results"]
        )
        
        logger.info("✅ Q1 completed and saved successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q1: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q1 Error: {str(e)}")


@app.post("/analyze/q2", tags=["Modules"], response_model=schemas.Q2Response)
async def analyze_q2(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q2 - Personalidad de Marca (Aaker)."""
    try:
        logger.info(f"Starting Q2 - Personalidad analysis for client {ficha_cliente_id}")
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        
        analyzer = Q2Personalidad(client, config)
        result = await analyzer.analyze()
        
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q2", "q2_personalidad", result["results"]
        )
        
        logger.info("✅ Q2 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q2: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q2 Error: {str(e)}")


@app.post("/analyze/q3", tags=["Modules"], response_model=schemas.Q3Response)
async def analyze_q3(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q3 - Análisis de Tópicos."""
    try:
        logger.info(f"Starting Q3 - Tópicos analysis for client {ficha_cliente_id}")
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        
        analyzer = Q3Topicos(client, config)
        result = await analyzer.analyze()
        
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q3", "q3_topicos", result["results"]
        )
        
        logger.info("✅ Q3 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q3: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q3 Error: {str(e)}")


@app.post("/analyze/q4", tags=["Modules"], response_model=schemas.Q4Response)
async def analyze_q4(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q4 - Análisis de Marcos Narrativos."""
    try:
        logger.info(f"Starting Q4 - Marcos Narrativos analysis for client {ficha_cliente_id}")
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        analyzer = Q4MarcosNarrativos(client, config)
        result = await analyzer.analyze()
        
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q4", "q4_marcos_narrativos", result["results"]
        )
        
        logger.info("✅ Q4 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q4: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q4 Error: {str(e)}")


@app.post("/analyze/q5", tags=["Modules"], response_model=schemas.Q5Response)
async def analyze_q5(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q5 - Análisis de Influenciadores."""
    try:
        logger.info(f"Starting Q5 - Influenciadores analysis for client {ficha_cliente_id}")
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        analyzer = Q5Influenciadores(client, config)
        result = await analyzer.analyze()
        
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q5", "q5_influenciadores", result["results"]
        )
        
        logger.info("✅ Q5 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q5: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q5 Error: {str(e)}")


@app.post("/analyze/q6", tags=["Modules"], response_model=schemas.Q6Response)
async def analyze_q6(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q6 - Análisis de Oportunidades."""
    try:
        logger.info(f"Starting Q6 - Oportunidades analysis for client {ficha_cliente_id}")
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        analyzer = Q6Oportunidades(client, config)
        result = await analyzer.analyze()
        
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q6", "q6_oportunidades", result["results"]
        )
        
        logger.info("✅ Q6 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q6: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q6 Error: {str(e)}")


@app.post("/analyze/q7", tags=["Modules"], response_model=schemas.Q7Response)
async def analyze_q7(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q7 - Análisis de Sentimiento Detallado."""
    try:
        logger.info(f"Starting Q7 - Sentimiento Detallado analysis for client {ficha_cliente_id}")
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        analyzer = Q7SentimientoDetallado(client, config)
        result = await analyzer.analyze()
        
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q7", "q7_sentimiento", result["results"]
        )
        
        logger.info("✅ Q7 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q7: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q7 Error: {str(e)}")


@app.post("/analyze/q8", tags=["Modules"], response_model=schemas.Q8Response)
async def analyze_q8(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q8 - Análisis Temporal."""
    try:
        logger.info(f"Starting Q8 - Temporal analysis for client {ficha_cliente_id}")
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        analyzer = Q8Temporal(client, config)
        result = await analyzer.analyze()
        
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q8", "q8_temporal", result["results"]
        )
        
        logger.info("✅ Q8 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q8: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q8 Error: {str(e)}")


@app.post("/analyze/q9", tags=["Modules"], response_model=schemas.Q9Response)
async def analyze_q9(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q9 - Análisis de Recomendaciones."""
    try:
        logger.info(f"Starting Q9 - Recomendaciones analysis for client {ficha_cliente_id}")
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        analyzer = Q9Recomendaciones(client, config)
        result = await analyzer.analyze()
        
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q9", "q9_recomendaciones", result["results"]
        )
        
        logger.info("✅ Q9 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q9: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q9 Error: {str(e)}")


@app.post("/analyze/q10", tags=["Modules"], response_model=schemas.Q10Response)
async def analyze_q10(
    ficha_cliente_id: str,
    client: AsyncOpenAI = Depends(get_openai_client),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute Q10 - Resumen Ejecutivo."""
    try:
        logger.info(f"Starting Q10 - Resumen Ejecutivo analysis for client {ficha_cliente_id}")
        config = get_posts_and_comments_from_db(ficha_cliente_id, db)
        logger.info(f"Loaded {len(config['new_posts'])} posts and {len(config['new_comments'])} comments from DB")
        # Q10 no usa cliente OpenAI, pasamos None
        analyzer = Q10ResumenEjecutivo(None, config)
        result = await analyzer.analyze()
        
        await _save_analysis_to_db(
            db, ficha_cliente_id, current_user.tenant_id,
            "Q10", "q10_resumen", result["results"]
        )
        
        logger.info("✅ Q10 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q10: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q10 Error: {str(e)}")


# =============================================================================
# PIPELINE ENDPOINT - Execute all modules in sequence
# =============================================================================

@app.post("/pipeline", tags=["Pipeline"])
async def run_full_pipeline(client: AsyncOpenAI = Depends(get_openai_client)):
    """
    Execute the complete analysis pipeline (all 10 modules in sequence).
    
    Returns:
        Dict with results from all modules
    """
    logger.info("🚀 Starting full pipeline (Q1-Q10)")
    
    config = get_config()
    results: Dict[str, Any] = {}
    errors: Dict[str, str] = {}
    successful = 0
    failed = 0
    
    # Q1
    try:
        logger.info("[1/10] Running Q1...")
        analyzer = Q1Emociones(client, config)
        results["q1"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q1 failed: {e}")
        errors["q1"] = str(e)
        failed += 1
    
    # Q2
    try:
        logger.info("[2/10] Running Q2...")
        analyzer = Q2Personalidad(client, config)
        results["q2"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q2 failed: {e}")
        errors["q2"] = str(e)
        failed += 1
    
    # Q3
    try:
        logger.info("[3/10] Running Q3...")
        analyzer = Q3Topicos(client, config)
        results["q3"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q3 failed: {e}")
        errors["q3"] = str(e)
        failed += 1
    
    # Q4
    try:
        logger.info("[4/10] Running Q4...")
        analyzer = Q4MarcosNarrativos(client, config)
        results["q4"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q4 failed: {e}")
        errors["q4"] = str(e)
        failed += 1
    
    # Q5
    try:
        logger.info("[5/10] Running Q5...")
        analyzer = Q5Influenciadores(client, config)
        results["q5"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q5 failed: {e}")
        errors["q5"] = str(e)
        failed += 1
    
    # Q6
    try:
        logger.info("[6/10] Running Q6...")
        analyzer = Q6Oportunidades(client, config)
        results["q6"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q6 failed: {e}")
        errors["q6"] = str(e)
        failed += 1
    
    # Q7
    try:
        logger.info("[7/10] Running Q7...")
        analyzer = Q7SentimientoDetallado(client, config)
        results["q7"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q7 failed: {e}")
        errors["q7"] = str(e)
        failed += 1
    
    # Q8
    try:
        logger.info("[8/10] Running Q8...")
        analyzer = Q8Temporal(client, config)
        results["q8"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q8 failed: {e}")
        errors["q8"] = str(e)
        failed += 1
    
    # Q9
    try:
        logger.info("[9/10] Running Q9...")
        analyzer = Q9Recomendaciones(client, config)
        results["q9"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q9 failed: {e}")
        errors["q9"] = str(e)
        failed += 1
    
    # Q10
    try:
        logger.info("[10/10] Running Q10...")
        analyzer = Q10ResumenEjecutivo(None, config)
        results["q10"] = await analyzer.analyze()
        successful += 1
    except Exception as e:
        logger.error(f"Q10 failed: {e}")
        errors["q10"] = str(e)
        failed += 1
    
    logger.info(f"✅ Pipeline complete: {successful} successful, {failed} failed")
    
    return {
        "status": "success" if failed == 0 else "partial",
        "total_modules": 10,
        "successful_modules": successful,
        "failed_modules": failed,
        "results": results,
        "errors": errors if errors else None,
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    import os
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "1"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Pixely Partners API on {host}:{port}")
    logger.info("🚀 CONNECTED TO REAL ORCHESTRATOR MODULES")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )






