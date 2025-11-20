import os
from typing import Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Cargar .env explícitamente
load_dotenv()

def get_openai_client() -> AsyncOpenAI:
    """
    Dependency para inyectar el cliente de OpenAI en los endpoints.
    Lee la API Key directamente del entorno.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    # No lanzamos error aquí para permitir que el servidor arranque,
    # pero fallará al invocar si no hay key.
    return AsyncOpenAI(api_key=api_key)

def get_config() -> Dict[str, Any]:
    """
    Provee la configuración básica para los analizadores.
    """
    return {
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        # Directorio donde se buscan/guardan jsons temporales si fuera necesario
        "outputs_dir": os.getenv("PIXELY_OUTPUTS_DIR", "orchestrator/outputs"),
        "ingested_data_path": os.getenv("INGESTED_DATA_PATH", "orchestrator/outputs/ingested_data.json")
    }
