import os
from typing import Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .database import get_db
from . import models, schemas
from .security import SECRET_KEY, ALGORITHM

# Cargar .env explícitamente
load_dotenv()

# Esquema OAuth2 (le dice a Swagger UI dónde enviar el token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """
    Valida el token JWT y recupera el usuario actual de la BD.
    Lanza 401 si el token es inválido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user
