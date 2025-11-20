"""
Pixely Partners API - FastAPI Server

Main entry point for the professional web API.
Exposes the 10 analysis modules as HTTP endpoints.
CONNECTED TO REAL ORCHESTRATOR MODULES - NOT A PLACEHOLDER.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
from contextlib import asynccontextmanager

# Importar dependencias y esquemas
from .dependencies import get_openai_client, get_config, get_current_user
from . import schemas, models, security
from .database import get_db

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
    Recibe username (email) y password, devuelve Access Token.
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
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserResponse, tags=["Authentication"])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Retorna la información del usuario actualmente logueado."""
    return current_user


# =============================================================================
# INDIVIDUAL MODULE ENDPOINTS (Q1-Q10)
# =============================================================================

@app.post("/analyze/q1", tags=["Modules"], response_model=schemas.Q1Response)
async def analyze_q1(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q1 - Análisis de Emociones."""
    try:
        logger.info("Starting Q1 - Emociones analysis")
        config = get_config()
        analyzer = Q1Emociones(client, config)
        result = await analyzer.analyze()
        logger.info("✅ Q1 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q1: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q1 Error: {str(e)}")


@app.post("/analyze/q2", tags=["Modules"], response_model=schemas.Q2Response)
async def analyze_q2(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q2 - Personalidad de Marca (Aaker)."""
    try:
        logger.info("Starting Q2 - Personalidad analysis")
        config = get_config()
        analyzer = Q2Personalidad(client, config)
        result = await analyzer.analyze()
        logger.info("✅ Q2 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q2: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q2 Error: {str(e)}")


@app.post("/analyze/q3", tags=["Modules"], response_model=schemas.Q3Response)
async def analyze_q3(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q3 - Análisis de Tópicos."""
    try:
        logger.info("Starting Q3 - Tópicos analysis")
        config = get_config()
        analyzer = Q3Topicos(client, config)
        result = await analyzer.analyze()
        logger.info("✅ Q3 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q3: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q3 Error: {str(e)}")


@app.post("/analyze/q4", tags=["Modules"], response_model=schemas.Q4Response)
async def analyze_q4(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q4 - Análisis de Marcos Narrativos."""
    try:
        logger.info("Starting Q4 - Marcos Narrativos analysis")
        config = get_config()
        analyzer = Q4MarcosNarrativos(client, config)
        result = await analyzer.analyze()
        logger.info("✅ Q4 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q4: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q4 Error: {str(e)}")


@app.post("/analyze/q5", tags=["Modules"], response_model=schemas.Q5Response)
async def analyze_q5(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q5 - Análisis de Influenciadores."""
    try:
        logger.info("Starting Q5 - Influenciadores analysis")
        config = get_config()
        analyzer = Q5Influenciadores(client, config)
        result = await analyzer.analyze()
        logger.info("✅ Q5 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q5: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q5 Error: {str(e)}")


@app.post("/analyze/q6", tags=["Modules"], response_model=schemas.Q6Response)
async def analyze_q6(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q6 - Análisis de Oportunidades."""
    try:
        logger.info("Starting Q6 - Oportunidades analysis")
        config = get_config()
        analyzer = Q6Oportunidades(client, config)
        result = await analyzer.analyze()
        logger.info("✅ Q6 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q6: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q6 Error: {str(e)}")


@app.post("/analyze/q7", tags=["Modules"], response_model=schemas.Q7Response)
async def analyze_q7(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q7 - Análisis de Sentimiento Detallado."""
    try:
        logger.info("Starting Q7 - Sentimiento Detallado analysis")
        config = get_config()
        analyzer = Q7SentimientoDetallado(client, config)
        result = await analyzer.analyze()
        logger.info("✅ Q7 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q7: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q7 Error: {str(e)}")


@app.post("/analyze/q8", tags=["Modules"], response_model=schemas.Q8Response)
async def analyze_q8(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q8 - Análisis Temporal."""
    try:
        logger.info("Starting Q8 - Temporal analysis")
        config = get_config()
        analyzer = Q8Temporal(client, config)
        result = await analyzer.analyze()
        logger.info("✅ Q8 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q8: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q8 Error: {str(e)}")


@app.post("/analyze/q9", tags=["Modules"], response_model=schemas.Q9Response)
async def analyze_q9(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q9 - Análisis de Recomendaciones."""
    try:
        logger.info("Starting Q9 - Recomendaciones analysis")
        config = get_config()
        analyzer = Q9Recomendaciones(client, config)
        result = await analyzer.analyze()
        logger.info("✅ Q9 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Error Q9: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q9 Error: {str(e)}")


@app.post("/analyze/q10", tags=["Modules"], response_model=schemas.Q10Response)
async def analyze_q10(client: AsyncOpenAI = Depends(get_openai_client)):
    """Execute Q10 - Resumen Ejecutivo."""
    try:
        logger.info("Starting Q10 - Resumen Ejecutivo analysis")
        config = get_config()
        # Q10 no usa cliente OpenAI, pasamos None
        analyzer = Q10ResumenEjecutivo(None, config)
        result = await analyzer.analyze()
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
