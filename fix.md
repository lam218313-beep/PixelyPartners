# 📘 Guía de Implementación Técnica - Fase 2: API y Persistencia

**Proyecto:** Pixely Partners  
**Versión:** 1.0.0 (Transición a Arquitectura Orientada a Servicios)  
**Fecha:** 2025-10-xx  
**Estado:** API Funcional / Base de Datos en Diseño

---

## 🎯 Objetivo General
Transformar la herramienta de scripts locales en una **Plataforma Web Robusta** capaz de gestionar múltiples clientes (Multi-Tenant), persistir datos históricos y servir información a través de una API estandarizada.

---

## 1. La Capa de API (Implementada)

Hemos creado un servidor **FastAPI** que actúa como interfaz entre el mundo exterior y el motor de análisis (Orquestador).

### Estructura de Archivos Creada:
* **`api/main.py`**: Punto de entrada. Conecta los endpoints HTTP (`POST /analyze/q1`) con los módulos de lógica de negocio (`Q1Emociones`).
* **`api/schemas.py`**: Contratos de datos **Pydantic**. Asegura que la IA devuelva la estructura exacta que el Frontend espera (ej. valida que `gap_score` sea float).
* **`api/dependencies.py`**: Inyección de dependencias. Maneja la configuración y la creación del cliente `AsyncOpenAI`.

### Dependencias Añadidas:
```text
fastapi>=0.100.0
uvicorn>=0.20.0
python-multipart>=0.0.6
2. La Capa de Persistencia (Base de Datos)
Se ha seleccionado PostgreSQL como motor de base de datos relacional para soportar la gestión de usuarios, tenencia múltiple (multi-tenancy) y almacenamiento de resultados JSON complejos.

A. Infraestructura (Docker)
Se habilitó el servicio db en docker-compose.yml:

YAML

  db:
    image: postgres:15-alpine
    container_name: pixely_db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - db_data:/var/lib/postgresql/data
B. Conexión (api/database.py)
Este archivo establece el puente entre FastAPI y PostgreSQL usando SQLAlchemy.

Python

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# URL de conexión (Docker service name 'db' o localhost para dev)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://pixely_user:secret_password_123@localhost:5432/pixely_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
3. Modelado de Datos (ORM)
Se diseñó un esquema Multi-Tenant en api/models.py para garantizar la seguridad y aislamiento de datos entre agencias/clientes.

Entidades Principales:
Tenant (Organización): La entidad raíz. Todo usuario y dato pertenece a un Tenant.

User (Usuario): Analistas con acceso al sistema (Email, Password Hash, Role).

FichaCliente (Marca): La empresa que está siendo analizada (ej. "Nike").

SocialMediaPost: Publicaciones ingeridas.

SocialMediaInsight: Tabla maestra que almacena los resultados de los 10 módulos (Q1-Q10) en columnas JSON.

Código del Modelo (api/models.py):
Python

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    users = relationship("User", back_populates="tenant")
    clients = relationship("FichaCliente", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tenant = relationship("Tenant", back_populates="users")

class SocialMediaInsight(Base):
    __tablename__ = "social_media_insights"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("fichas_cliente.id"))
    
    # Resultados de IA (JSON estructurado)
    q1_emociones = Column(JSON)
    q2_personalidad = Column(JSON)
    q3_topicos = Column(JSON)
    q4_marcos_narrativos = Column(JSON)
    q5_influenciadores = Column(JSON)
    q6_oportunidades = Column(JSON)
    q7_sentimiento = Column(JSON)
    q8_temporal = Column(JSON)
    q9_recomendaciones = Column(JSON)
    q10_resumen = Column(JSON)
4. Próximos Pasos Críticos
Para finalizar la Fase 2, se deben ejecutar las siguientes tareas en orden:

Implementar Autenticación (api/auth.py):

Funciones para hashear contraseñas (bcrypt).

Generación de tokens JWT (Access Token).

Endpoints de Login y Registro.

Sistema de Migraciones (Alembic):

Inicializar Alembic para crear las tablas en PostgreSQL automáticamente.

Ejecutar alembic upgrade head al iniciar el contenedor.

Conectar Endpoints a BD:

Modificar api/main.py para que los resultados de análisis (await analyzer.analyze()) se guarden en la tabla SocialMediaInsight antes de retornarse.