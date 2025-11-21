import os
from typing import Dict, Any, List
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

def get_posts_and_comments_from_db(
    ficha_cliente_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Load posts and comments from database for a specific client.
    
    This replaces the file-based approach and enables multi-client analysis.
    
    Args:
        ficha_cliente_id: UUID of the client
        db: Database session
        
    Returns:
        Dict with keys:
            - new_posts: List of post dicts (link, platform, created_at, content, likes, etc.)
            - new_comments: List of comment dicts (link, comment_text, ownerUsername, likes, etc.)
            - ficha_cliente_id: UUID for API calls
            - client_ficha: Client information (brand_name, archetype, etc.)
    """
    # Fetch ficha_cliente
    ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.id == ficha_cliente_id
    ).first()
    
    if not ficha:
        raise HTTPException(status_code=404, detail=f"Client {ficha_cliente_id} not found")
    
    # Fetch posts for this client
    posts = db.query(models.SocialMediaPost).filter(
        models.SocialMediaPost.cliente_id == ficha_cliente_id
    ).all()
    
    # Convert posts to dict format expected by analyzers
    new_posts = []
    for post in posts:
        new_posts.append({
            "link": post.post_url,
            "platform": post.platform or "instagram",
            "created_at": post.post_date.isoformat() if post.post_date else None,
            "post_date": post.post_date.isoformat() if post.post_date else None,
            "timestamp": post.post_date.isoformat() if post.post_date else None,
            "content": post.content_text or "",
            "likes": post.likes or 0,
            "shares": post.shares or 0,
            "comments_count": post.comments_count or 0,
            "engagement_rate": post.engagement_rate or "0%"
        })
    
    # Fetch comments for all posts of this client
    new_comments = []
    for post in posts:
        comments = db.query(models.Comentario).filter(
            models.Comentario.post_id == post.id
        ).all()
        
        for comment in comments:
            new_comments.append({
                "link": post.post_url,  # Link to parent post
                "comment_text": comment.text,
                "ownerUsername": comment.owner_username or "unknown",
                "timestamp": comment.timestamp.isoformat() if comment.timestamp else None,
                "likes": comment.likes or 0
            })
    
    # Build client_ficha dict
    client_ficha = {
        "client_name": ficha.brand_name,
        "brand_archetype": ficha.brand_archetype or "Unknown",
        "tone_of_voice": ficha.tone_of_voice or "Neutral",
        "target_audience": ficha.target_audience or "",
        "competitors": ficha.competitors or []
    }
    
    return {
        "new_posts": new_posts,
        "new_comments": new_comments,
        "ficha_cliente_id": str(ficha_cliente_id),
        "client_ficha": client_ficha,
        **get_config()  # Include base config (openai_model, etc.)
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
