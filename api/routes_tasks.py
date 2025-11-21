"""
API endpoints for task management (Hilos de Trabajo)
"""

import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import get_db
from .dependencies import get_current_user
from . import models, schemas_tasks
from .models_tasks import Task, TaskNote, TaskStatus as TaskStatusEnum

router = APIRouter(prefix="/api/v1", tags=["tasks"])


# ============================================================================
# TASK CRUD OPERATIONS
# ============================================================================

@router.get("/fichas/{ficha_id}/tasks", response_model=schemas_tasks.TasksByWeekResponse)
def get_tasks_by_ficha(
    ficha_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all tasks for a ficha_cliente, grouped by week.
    """
    # Verify ficha exists and belongs to user's tenant
    ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.id == ficha_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not ficha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ficha de cliente no encontrada"
        )
    
    # Get all tasks for this ficha
    tasks = db.query(Task).filter(
        Task.ficha_cliente_id == ficha_id
    ).order_by(Task.prioridad.desc()).all()
    
    # Group by week
    week_1 = [t for t in tasks if t.week == 1]
    week_2 = [t for t in tasks if t.week == 2]
    week_3 = [t for t in tasks if t.week == 3]
    week_4 = [t for t in tasks if t.week == 4]
    
    # Count completed tasks
    completed_count = sum(1 for t in tasks if t.status in [TaskStatusEnum.HECHO, TaskStatusEnum.REVISADO])
    
    return schemas_tasks.TasksByWeekResponse(
        week_1=week_1,
        week_2=week_2,
        week_3=week_3,
        week_4=week_4,
        total_tasks=len(tasks),
        completed_tasks=completed_count
    )


@router.post("/fichas/{ficha_id}/tasks", response_model=schemas_tasks.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    ficha_id: str,
    task_data: schemas_tasks.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new task for a ficha_cliente.
    """
    # Verify ficha exists
    ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.id == ficha_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not ficha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ficha de cliente no encontrada"
        )
    
    # Create task
    new_task = Task(
        id=str(uuid.uuid4()),
        ficha_cliente_id=ficha_id,
        **task_data.model_dump()
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task


@router.patch("/tasks/{task_id}", response_model=schemas_tasks.TaskResponse)
def update_task_status(
    task_id: str,
    task_update: schemas_tasks.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update task status (Pendiente, En Curso, Hecho, Revisado).
    """
    # Get task and verify access
    task = db.query(Task).join(models.FichaCliente).filter(
        Task.id == task_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    # Update status
    if task_update.status:
        task.status = task_update.status
        task.updated_at = datetime.utcnow()
        
        # Set completed_at if status is HECHO or REVISADO
        if task_update.status in [TaskStatusEnum.HECHO, TaskStatusEnum.REVISADO]:
            if not task.completed_at:
                task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
    
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a task.
    """
    # Get task and verify access
    task = db.query(Task).join(models.FichaCliente).filter(
        Task.id == task_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    db.delete(task)
    db.commit()
    
    return None


# ============================================================================
# TASK NOTES OPERATIONS
# ============================================================================

@router.post("/tasks/{task_id}/notes", response_model=schemas_tasks.TaskNoteResponse, status_code=status.HTTP_201_CREATED)
def add_task_note(
    task_id: str,
    note_data: schemas_tasks.TaskNoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Add a note/comment to a task.
    """
    # Verify task exists and user has access
    task = db.query(Task).join(models.FichaCliente).filter(
        Task.id == task_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    # Create note
    new_note = TaskNote(
        id=str(uuid.uuid4()),
        task_id=task_id,
        content=note_data.content
    )
    
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    
    return new_note


@router.get("/tasks/{task_id}/notes", response_model=List[schemas_tasks.TaskNoteResponse])
def get_task_notes(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all notes for a task.
    """
    # Verify task exists and user has access
    task = db.query(Task).join(models.FichaCliente).filter(
        Task.id == task_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    notes = db.query(TaskNote).filter(
        TaskNote.task_id == task_id
    ).order_by(TaskNote.created_at.desc()).all()
    
    return notes


# ============================================================================
# UTILITY: GENERATE TASKS FROM Q9 RECOMMENDATIONS
# ============================================================================

@router.post("/fichas/{ficha_id}/tasks/generate-from-q9", response_model=dict)
def generate_tasks_from_q9(
    ficha_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate tasks from Q9 recommendations for a ficha.
    Distributes recommendations across 4 weeks based on urgency.
    """
    # Verify ficha exists
    ficha = db.query(models.FichaCliente).filter(
        models.FichaCliente.id == ficha_id,
        models.FichaCliente.tenant_id == current_user.tenant_id
    ).first()
    
    if not ficha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ficha de cliente no encontrada"
        )
    
    # Get latest insight with Q9 data
    latest_insight = db.query(models.SocialMediaInsight).filter(
        models.SocialMediaInsight.cliente_id == ficha_id,
        models.SocialMediaInsight.q9_recomendaciones.isnot(None)
    ).order_by(models.SocialMediaInsight.created_at.desc()).first()
    
    if not latest_insight or not latest_insight.q9_recomendaciones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay recomendaciones Q9 disponibles"
        )
    
    # Extract recommendations
    q9_data = latest_insight.q9_recomendaciones
    recommendations = q9_data.get("results", {}).get("lista_recomendaciones", [])
    
    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay recomendaciones en Q9"
        )
    
    # Delete existing tasks for this ficha
    db.query(Task).filter(Task.ficha_cliente_id == ficha_id).delete()
    
    # Create tasks from recommendations
    tasks_created = []
    for rec in recommendations:
        # Determine week based on urgency
        urgencia = rec.get("urgencia", "MEDIA")
        if urgencia == "CRÍTICA":
            week = 1
        elif urgencia == "ALTA":
            week = 1
        elif urgencia == "MEDIA-ALTA":
            week = 2
        elif urgencia == "MEDIA":
            week = 3
        else:
            week = 4
        
        new_task = Task(
            id=str(uuid.uuid4()),
            ficha_cliente_id=ficha_id,
            title=rec.get("recomendacion", "Tarea sin título"),
            area_estrategica=rec.get("area_estrategica"),
            urgencia=urgencia,
            score_impacto=rec.get("score_impacto"),
            score_esfuerzo=rec.get("score_esfuerzo"),
            prioridad=int(rec.get("prioridad", 0) * 100),  # Convert to integer
            week=week
        )
        
        db.add(new_task)
        tasks_created.append(new_task)
    
    db.commit()
    
    return {
        "message": f"Se crearon {len(tasks_created)} tareas desde las recomendaciones Q9",
        "tasks_created": len(tasks_created),
        "distribution": {
            "week_1": sum(1 for t in tasks_created if t.week == 1),
            "week_2": sum(1 for t in tasks_created if t.week == 2),
            "week_3": sum(1 for t in tasks_created if t.week == 3),
            "week_4": sum(1 for t in tasks_created if t.week == 4)
        }
    }
