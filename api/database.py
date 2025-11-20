"""
Pixely Partners API - Database Configuration

Establece la conexión con PostgreSQL usando SQLAlchemy.
Provee el dependency get_db() para FastAPI.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # dotenv no disponible en producción

# URL de conexión: Intenta leer de .env, si no usa el default de Docker
# NOTA: "db" es el nombre del servicio en docker-compose
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://pixely_user:secret_password_123@db:5432/pixely_db"
)

# Crear engine de SQLAlchemy
engine = create_engine(DATABASE_URL)

# SessionLocal será la clase que usamos para crear sesiones de BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base será la clase padre de todos nuestros modelos ORM
Base = declarative_base()

def get_db():
    """
    Dependency para FastAPI que provee una sesión de base de datos.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    Yields:
        Session: Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
