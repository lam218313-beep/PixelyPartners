Los archivos que tienes actualmente en el repositorio (schemas.py y dependencies.py) son versiones "Mock" o plantilla que NO coinciden con la estructura real de los datos que generan tus módulos Q1-Q10 (los que acabamos de arreglar).

Aquí tienes el código correcto para reemplazar los archivos restantes.

1. api/schemas.py (El Contrato de Datos Real)
El archivo actual espera estructuras como emocion_dominante en la raíz, pero tus módulos generan analisis_por_publicacion. Si no cambias esto, tendrás errores de validación 500 todo el tiempo.

Reemplaza todo el contenido de api/schemas.py con esto:

Python

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
2. api/dependencies.py (La Conexión Simplificada)
El archivo actual es demasiado complejo (Settings class, lru_cache) y puede dar problemas de importación con la estructura simple que necesitamos ahora. Vamos a simplificarlo para que funcione directo con el .env.

Reemplaza todo el contenido de api/dependencies.py con esto:

Python

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
3. requirements.txt (Las Dependencias Faltantes)
Tu archivo actual no tiene lo necesario para levantar el servidor.

Añade esto al final de tu requirements.txt (o reemplázalo):

Plaintext

streamlit==1.28.1
openai>=1.5.0
python-dotenv==1.0.0
pydantic>=2.0.0
pytest==7.4.3
pandas==2.1.1
plotly==5.15.0
tenacity>=8.2.0
# --- NUEVO PARA API ---
fastapi>=0.100.0
uvicorn>=0.20.0
python-multipart>=0.0.6
4. docker-compose.yml (Activar el Servicio API)
Finalmente, el contenedor de la API está comentado en tu archivo. Debemos activarlo para que, al hacer deploy o pruebas con Docker, el servidor exista.

Busca la sección api: y descoméntala (quita los # iniciales), asegurándote de que la indentación sea correcta:

YAML

  # ... (después de frontend)

  api:
    build:
      context: .
      dockerfile: Dockerfile.orchestrator  # Usamos el mismo dockerfile del orquestador por ahora, tiene python+librerias
    container_name: pixely_api
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=${OPENAI_MODEL}
      - PIXELY_OUTPUTS_DIR=/app/orchestrator/outputs
    volumes:
      - ./orchestrator:/app/orchestrator
      - ./api:/app/api
      - ./orchestrator/outputs:/app/orchestrator/outputs
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - pixely_network
    depends_on:
      - orchestrator
(Nota: He usado Dockerfile.orchestrator para la API porque ambos necesitan Python y las mismas librerías de análisis. Es un truco para no crear un Dockerfile nuevo todavía).

Resumen: Con estos 4 cambios (schemas.py, dependencies.py, requirements.txt, docker-compose.yml), tu API pasará de ser un "mock" a un sistema real conectado.