"""
Pydantic schemas for task management
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum
from uuid import UUID


class TaskStatus(str, Enum):
    """Task status options"""
    PENDIENTE = "PENDIENTE"
    EN_CURSO = "EN_CURSO"
    HECHO = "HECHO"
    REVISADO = "REVISADO"


class TaskNoteBase(BaseModel):
    """Base schema for task note"""
    content: str = Field(..., min_length=1, max_length=5000)


class TaskNoteCreate(TaskNoteBase):
    """Schema for creating a task note"""
    pass


class TaskNoteUpdate(TaskNoteBase):
    """Schema for updating a task note"""
    pass


class TaskNoteResponse(TaskNoteBase):
    """Schema for task note response"""
    id: str
    task_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    """Base schema for task"""
    title: str
    description: Optional[str] = None
    area_estrategica: Optional[str] = None
    urgencia: Optional[str] = None
    score_impacto: Optional[int] = None
    score_esfuerzo: Optional[int] = None
    prioridad: Optional[int] = None
    week: int = Field(..., ge=1, le=4)


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    status: Optional[TaskStatus] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: str
    ficha_cliente_id: Union[str, UUID]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    notes: List[TaskNoteResponse] = []

    @field_validator('ficha_cliente_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string"""
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class TasksByWeekResponse(BaseModel):
    """Schema for tasks grouped by week"""
    week_1: List[TaskResponse]
    week_2: List[TaskResponse]
    week_3: List[TaskResponse]
    week_4: List[TaskResponse]
    total_tasks: int
    completed_tasks: int
