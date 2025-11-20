"""
Pixely Partners API - Database Configuration

Establece la conexión con PostgreSQL usando SQLAlchemy.
Provee el dependency get_db() para FastAPI.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión: Intenta leer de .env, si no usa el default de Docker
# NOTA: "db" es el nombre del servicio en docker-compose
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://pixely_user:secret_password_123@db:5432/pixely_db"
)

# En local (fuera de docker), 'db' no resuelve. Fallback a localhost.
if "db" in DATABASE_URL and os.environ.get("RUN_ENV") == "local":
    DATABASE_URL = DATABASE_URL.replace("@db:", "@localhost:")

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
