"""
Database models for task management system (Hilos de Trabajo)
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


class TaskStatus(str, enum.Enum):
    """Task status enum"""
    PENDIENTE = "PENDIENTE"
    EN_CURSO = "EN_CURSO"
    HECHO = "HECHO"
    REVISADO = "REVISADO"


class TaskWeek(int, enum.Enum):
    """Task week enum"""
    WEEK_1 = 1
    WEEK_2 = 2
    WEEK_3 = 3
    WEEK_4 = 4


class Task(Base):
    """Task model for client action items"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    ficha_cliente_id = Column(UUID(as_uuid=True), ForeignKey("fichas_cliente.id"), nullable=False, index=True)
    
    # Task content
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)  # Descripción detallada de 5 líneas
    area_estrategica = Column(String(100))
    urgencia = Column(String(50))
    score_impacto = Column(Integer)
    score_esfuerzo = Column(Integer)
    prioridad = Column(Integer)
    week = Column(Integer, nullable=False)  # 1, 2, 3, or 4
    
    # Task state
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDIENTE)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    ficha = relationship("FichaCliente", back_populates="tasks")
    notes = relationship("TaskNote", back_populates="task", cascade="all, delete-orphan")


class TaskNote(Base):
    """Notes/comments for tasks"""
    __tablename__ = "task_notes"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, index=True)
    
    # Note content
    content = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="notes")
