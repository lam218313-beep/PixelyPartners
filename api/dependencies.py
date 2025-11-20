"""
Pixely Partners API - Dependencies

Centralized configuration, environment variables, and OpenAI client setup.
"""

import os
import logging
from typing import Optional
from functools import lru_cache

from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION CLASS
# =============================================================================

class Settings:
    """
    Central configuration management.
    
    Reads from environment variables with sensible defaults.
    """
    
    # API Configuration
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "Pixely Partners - Analysis Engine"
    API_DESCRIPTION: str = "Professional API for social media analysis with 10 specialized modules"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TIMEOUT: int = int(os.getenv("OPENAI_TIMEOUT", "30"))
    
    # Orchestrator Configuration
    ORCHESTRATOR_OUTPUT_DIR: str = os.getenv("PIXELY_OUTPUTS_DIR", "orchestrator/outputs")
    INGESTED_DATA_PATH: str = os.getenv("INGESTED_DATA_PATH", "orchestrator/data/ingested_data.json")
    
    # Server Configuration
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    WORKERS: int = int(os.getenv("API_WORKERS", "4"))
    
    # Module Configuration
    AVAILABLE_MODULES: list = [f"q{i}" for i in range(1, 11)]
    
    def __init__(self):
        """Validate configuration on initialization."""
        if not self.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. API will fail on OpenAI calls.")
        
        if not os.path.exists(self.ORCHESTRATOR_OUTPUT_DIR):
            logger.warning(f"Output directory does not exist: {self.ORCHESTRATOR_OUTPUT_DIR}")
            os.makedirs(self.ORCHESTRATOR_OUTPUT_DIR, exist_ok=True)
        
        logger.info(f"Settings initialized: API v{self.API_VERSION}")
    
    def to_dict(self) -> dict:
        """Return settings as dictionary (excluding sensitive data)."""
        return {
            "api_version": self.API_VERSION,
            "debug": self.DEBUG,
            "openai_model": self.OPENAI_MODEL,
            "available_modules": self.AVAILABLE_MODULES,
            "host": self.HOST,
            "port": self.PORT,
        }


# =============================================================================
# SINGLETON CONFIGURATION INSTANCE
# =============================================================================

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get global settings instance (singleton with caching).
    
    Returns:
        Settings instance
    """
    return Settings()


# =============================================================================
# OPENAI CLIENT MANAGEMENT
# =============================================================================

class OpenAIClientManager:
    """
    Manages OpenAI AsyncOpenAI client with connection pooling and error handling.
    """
    
    _instance: Optional[AsyncOpenAI] = None
    
    @classmethod
    def get_client(cls) -> AsyncOpenAI:
        """
        Get or create AsyncOpenAI client (singleton).
        
        Returns:
            AsyncOpenAI client instance
        """
        if cls._instance is None:
            settings = get_settings()
            cls._instance = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=settings.OPENAI_TIMEOUT
            )
            logger.info("OpenAI AsyncOpenAI client initialized")
        
        return cls._instance
    
    @classmethod
    async def close_client(cls) -> None:
        """Close the OpenAI client connection."""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
            logger.info("OpenAI AsyncOpenAI client closed")


# =============================================================================
# DEPENDENCY INJECTION FUNCTIONS
# =============================================================================

async def get_openai_client() -> AsyncOpenAI:
    """
    FastAPI dependency: provide OpenAI client to routes.
    
    Usage in routes:
        @app.get("/analyze")
        async def analyze(client: AsyncOpenAI = Depends(get_openai_client)):
            ...
    
    Returns:
        AsyncOpenAI client instance
    """
    return OpenAIClientManager.get_client()


def get_settings_dependency() -> Settings:
    """
    FastAPI dependency: provide settings to routes.
    
    Usage in routes:
        @app.get("/status")
        def status(settings: Settings = Depends(get_settings_dependency)):
            ...
    
    Returns:
        Settings instance
    """
    return get_settings()


# =============================================================================
# INITIALIZATION
# =============================================================================

# Initialize settings on module import
settings = get_settings()

if __name__ == "__main__":
    # Print configuration for debugging
    print("=" * 80)
    print("PIXELY PARTNERS API - CONFIGURATION")
    print("=" * 80)
    for key, value in settings.to_dict().items():
        print(f"{key:.<40} {value}")
    print("=" * 80)
