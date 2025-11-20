"""
Pixely Partners API - FastAPI Server

Main entry point for the professional web API.
Exposes the 10 analysis modules as HTTP endpoints.
"""

import time
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from . import schemas
from .dependencies import (
    get_settings,
    get_openai_client,
    get_settings_dependency,
    OpenAIClientManager,
    Settings
)

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
    logger.info("🚀 Pixely Partners API Starting...")
    settings = get_settings()
    logger.info(f"API Version: {settings.API_VERSION}")
    logger.info(f"OpenAI Model: {settings.OPENAI_MODEL}")
    logger.info(f"Available Modules: {', '.join(settings.AVAILABLE_MODULES)}")
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Pixely Partners API Shutting down...")
    await OpenAIClientManager.close_client()
    logger.info("API Shutdown complete")


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
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
    """
    Root endpoint - minimal health check.
    
    Returns:
        Welcome message
    """
    return {
        "message": "Pixely Partners API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"], response_model=schemas.HealthCheckResponse)
async def health_check():
    """
    Detailed health check endpoint.
    
    Returns:
        HealthCheckResponse with status and available modules
    """
    return schemas.HealthCheckResponse(
        status="healthy",
        version=settings.API_VERSION,
        modules_available=settings.AVAILABLE_MODULES,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/status", tags=["Health"])
async def get_status(settings: Settings = Depends(get_settings_dependency)):
    """
    Get API configuration and status.
    
    Returns:
        Configuration dictionary
    """
    return {
        "status": "running",
        "config": settings.to_dict(),
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# ANALYSIS ENDPOINTS
# =============================================================================

@app.post("/analyze", tags=["Analysis"], response_model=schemas.AnalysisResult)
async def analyze(
    request: schemas.AnalysisRequest,
    background_tasks: BackgroundTasks,
    openai_client = Depends(get_openai_client)
) -> schemas.AnalysisResult:
    """
    Execute a single analysis module.
    
    Args:
        request: AnalysisRequest with module code and client info
        background_tasks: FastAPI background tasks queue
        openai_client: Injected OpenAI AsyncOpenAI client
    
    Returns:
        AnalysisResult with module output
    
    Raises:
        HTTPException: If module execution fails
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received analysis request: module={request.module}, client={request.client_name}")
        
        # TODO: Call orchestrator module
        # For now, return mock response
        execution_time = (time.time() - start_time) * 1000
        
        return schemas.AnalysisResult(
            module=request.module,
            version=1,
            status="success",
            data={"message": f"Module {request.module} execution placeholder"},
            errors=[],
            execution_time_ms=execution_time
        )
    
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/pipeline", tags=["Analysis"], response_model=schemas.PipelineResult)
async def run_pipeline(
    client_name: str,
    background_tasks: BackgroundTasks,
    openai_client = Depends(get_openai_client)
) -> schemas.PipelineResult:
    """
    Execute the complete analysis pipeline (all 10 modules).
    
    Args:
        client_name: Name of the client/brand to analyze
        background_tasks: FastAPI background tasks queue
        openai_client: Injected OpenAI AsyncOpenAI client
    
    Returns:
        PipelineResult with results from all modules
    
    Raises:
        HTTPException: If pipeline execution fails
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received pipeline request: client={client_name}")
        
        # TODO: Call orchestrator with "all" modules
        # For now, return mock response
        execution_time = (time.time() - start_time) * 1000
        
        return schemas.PipelineResult(
            status="success",
            total_modules=10,
            successful_modules=10,
            failed_modules=0,
            results={},  # TODO: Populate with actual results
            total_execution_time_ms=execution_time
        )
    
    except Exception as e:
        logger.error(f"Error in pipeline endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )


# =============================================================================
# MODULE-SPECIFIC ENDPOINTS (Q1-Q10)
# =============================================================================

@app.get("/q1/emociones", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q1_emociones():
    """Get Q1 Emotions Analysis result."""
    # TODO: Load from output JSON or re-run if needed
    return schemas.AnalysisResult(
        module="q1",
        version=1,
        status="success",
        data={"placeholder": "Q1 Emotions Analysis"},
        errors=[]
    )


@app.get("/q2/personalidad", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q2_personalidad():
    """Get Q2 Brand Personality (Aaker) result."""
    # TODO: Load from output JSON or re-run if needed
    return schemas.AnalysisResult(
        module="q2",
        version=1,
        status="success",
        data={"placeholder": "Q2 Brand Personality"},
        errors=[]
    )


@app.get("/q3/temas", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q3_temas():
    """Get Q3 Topics Analysis result."""
    return schemas.AnalysisResult(
        module="q3",
        version=1,
        status="success",
        data={"placeholder": "Q3 Topics Analysis"},
        errors=[]
    )


@app.get("/q4/marcos", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q4_marcos():
    """Get Q4 Narrative Frameworks result."""
    return schemas.AnalysisResult(
        module="q4",
        version=1,
        status="success",
        data={"placeholder": "Q4 Narrative Frameworks"},
        errors=[]
    )


@app.get("/q5/influenciadores", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q5_influenciadores():
    """Get Q5 Influencers Analysis result."""
    return schemas.AnalysisResult(
        module="q5",
        version=1,
        status="success",
        data={"placeholder": "Q5 Influencers Analysis"},
        errors=[]
    )


@app.get("/q6/oportunidades", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q6_oportunidades():
    """Get Q6 Opportunities Analysis result."""
    return schemas.AnalysisResult(
        module="q6",
        version=1,
        status="success",
        data={"placeholder": "Q6 Opportunities Analysis"},
        errors=[]
    )


@app.get("/q7/sentimiento", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q7_sentimiento():
    """Get Q7 Detailed Sentiment Analysis result."""
    return schemas.AnalysisResult(
        module="q7",
        version=1,
        status="success",
        data={"placeholder": "Q7 Detailed Sentiment"},
        errors=[]
    )


@app.get("/q8/temporal", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q8_temporal():
    """Get Q8 Temporal Analysis result."""
    return schemas.AnalysisResult(
        module="q8",
        version=1,
        status="success",
        data={"placeholder": "Q8 Temporal Analysis"},
        errors=[]
    )


@app.get("/q9/recomendaciones", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q9_recomendaciones():
    """Get Q9 Recommendations result."""
    return schemas.AnalysisResult(
        module="q9",
        version=1,
        status="success",
        data={"placeholder": "Q9 Recommendations"},
        errors=[]
    )


@app.get("/q10/resumen", tags=["Modules"], response_model=schemas.AnalysisResult)
async def get_q10_resumen():
    """Get Q10 Executive Summary result."""
    return schemas.AnalysisResult(
        module="q10",
        version=1,
        status="success",
        data={"placeholder": "Q10 Executive Summary"},
        errors=[]
    )


# =============================================================================
# ERROR HANDLING
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
            "status_code": 500
        },
    )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Pixely Partners API on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
        log_level="info"
    )
