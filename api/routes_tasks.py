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


@router.patch("/tasks/{task_id}/notes/{note_id}", response_model=schemas_tasks.TaskNoteResponse)
def update_task_note(
    task_id: str,
    note_id: str,
    note_update: schemas_tasks.TaskNoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update the content of a note for a task.
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
    
    # Get note and verify it belongs to the task
    note = db.query(TaskNote).filter(
        TaskNote.id == note_id,
        TaskNote.task_id == task_id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota no encontrada"
        )
    
    # Update content
    note.content = note_update.content
    db.commit()
    db.refresh(note)
    
    return note


@router.delete("/tasks/{task_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_note(
    task_id: str,
    note_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a note from a task.
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
    
    # Get note and verify it belongs to the task
    note = db.query(TaskNote).filter(
        TaskNote.id == note_id,
        TaskNote.task_id == task_id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota no encontrada"
        )
    
    db.delete(note)
    db.commit()
    
    return None


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
    Generate enriched tasks from Q9 recommendations.
    Enriches each task with evidence from Q1-Q8 for strategic context.
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
    
    # Get latest insight with all Q data
    latest_insight = db.query(models.SocialMediaInsight).filter(
        models.SocialMediaInsight.cliente_id == ficha_id,
        models.SocialMediaInsight.q9_recomendaciones.isnot(None)
    ).order_by(models.SocialMediaInsight.created_at.desc()).first()
    
    if not latest_insight or not latest_insight.q9_recomendaciones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay recomendaciones Q9 disponibles"
        )
    
    # Extract all Q data for enrichment
    q_data = {
        "q1": latest_insight.q1_emociones.get("results", {}) if latest_insight.q1_emociones else {},
        "q3": latest_insight.q3_topicos.get("results", {}) if latest_insight.q3_topicos else {},
        "q4": latest_insight.q4_marcos_narrativos.get("results", {}) if latest_insight.q4_marcos_narrativos else {},
        "q5": latest_insight.q5_influenciadores.get("results", {}) if latest_insight.q5_influenciadores else {},
        "q6": latest_insight.q6_oportunidades.get("results", {}) if latest_insight.q6_oportunidades else {},
        "q8": latest_insight.q8_temporal.get("results", {}) if latest_insight.q8_temporal else {},
    }
    
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
    
    # Helper: Extract evidence summary
    def build_evidence_summary(q_data):
        """Build detailed evidence summary from Q1-Q8 with real data"""
        summary_parts = []
        
        # Q1: Emociones - Extract from analisis_por_publicacion
        if q_data["q1"] and "analisis_por_publicacion" in q_data["q1"]:
            posts = q_data["q1"]["analisis_por_publicacion"]
            if posts:
                # Aggregate emotions across all posts
                all_emotions = {}
                for post in posts:
                    emociones = post.get("emociones", {})
                    for emo, val in emociones.items():
                        all_emotions[emo] = all_emotions.get(emo, 0) + val
                
                # Get top 3 emotions
                top_emotions = sorted(all_emotions.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_emotions:
                    emo_text = ", ".join([f"{emo.capitalize()}: {val/len(posts):.1%}" for emo, val in top_emotions])
                    summary_parts.append(f"🎭 **Emociones dominantes:** {emo_text}")
        
        # Q3: Tópicos - Extract from analisis_agregado
        if q_data["q3"] and "analisis_agregado" in q_data["q3"]:
            topicos_list = q_data["q3"]["analisis_agregado"]
            if topicos_list and isinstance(topicos_list, list):
                # Get top 3-5 topics
                top_topicos = sorted(topicos_list, key=lambda x: x.get("frecuencia_relativa", 0), reverse=True)[:5]
                top_names = [t.get("topic", "") for t in top_topicos if t.get("topic")]
                if top_names:
                    summary_parts.append(f"📊 **Tópicos frecuentes:** {', '.join(top_names)}")
        
        # Q6: Oportunidades - Extract specific opportunities
        if q_data["q6"] and "oportunidades" in q_data["q6"]:
            oportunidades = q_data["q6"]["oportunidades"]
            if oportunidades:
                # Get top 2-3 opportunities by gap_score
                top_opps = sorted(oportunidades, key=lambda x: x.get("gap_score", 0), reverse=True)[:3]
                opp_names = [o.get("oportunidad", "") for o in top_opps if o.get("oportunidad")]
                if opp_names:
                    summary_parts.append(f"💎 **Oportunidades clave:** {', '.join(opp_names)}")
        
        # Q8: Anomalías temporales - Extract from resumen_global
        if q_data["q8"] and "resumen_global" in q_data["q8"]:
            resumen = q_data["q8"]["resumen_global"]
            serie = resumen.get("serie_temporal", [])
            if serie:
                # Count weeks with significant changes
                anomalias = [s for s in serie if abs(s.get("cambio_porcentaje", 0)) > 20]
                if anomalias:
                    summary_parts.append(f"⚠️ **Patrones temporales:** {len(anomalias)} semanas con cambios significativos (>20%)")
        
        if not summary_parts:
            return "Datos insuficientes para generar evidencia detallada"
        
        return "\n".join(summary_parts)
    
    evidence_summary = build_evidence_summary(q_data)
    
    # Create enriched tasks from recommendations with 4 per week distribution
    tasks_created = []
    
    # Sort recommendations by priority (impacto/esfuerzo ratio) descending
    sorted_recs = sorted(
        recommendations,
        key=lambda r: r.get("score_impacto", 50) / max(r.get("score_esfuerzo", 1), 1),
        reverse=True
    )
    
    # Distribute 4 tasks per week
    for idx, rec in enumerate(sorted_recs):
        # Calculate week: 4 tasks per week (0-3: week 1, 4-7: week 2, etc.)
        week = (idx // 4) + 1
        
        # Determine urgencia based on priority and week
        prioridad_score = rec.get("score_impacto", 50) / max(rec.get("score_esfuerzo", 1), 1)
        if week == 1 and prioridad_score > 2.0:
            urgencia = "CRÍTICA"
        elif week == 1 or prioridad_score > 1.5:
            urgencia = "ALTA"
        elif week == 2 or prioridad_score > 1.0:
            urgencia = "MEDIA-ALTA"
        elif week == 3:
            urgencia = "MEDIA"
        else:
            urgencia = "BAJA"
        
        # Build enriched description with evidence
        base_description = rec.get("descripcion", "Sin descripción detallada disponible.")
        
        # Add evidence section
        enriched_description = f"{base_description}\n\n---\n\n### 📊 Evidencia del Análisis\n\n{evidence_summary}"
        
        new_task = Task(
            id=str(uuid.uuid4()),
            ficha_cliente_id=ficha_id,
            title=rec.get("recomendacion", "Tarea sin título"),
            description=enriched_description,
            area_estrategica=rec.get("area_estrategica", "Operaciones"),
            urgencia=urgencia,
            score_impacto=rec.get("score_impacto", 50),
            score_esfuerzo=rec.get("score_esfuerzo", 50),
            prioridad=int(prioridad_score * 100),
            week=week
        )
        
        db.add(new_task)
        tasks_created.append(new_task)
    
    db.commit()
    
    return {
        "message": f"Se crearon {len(tasks_created)} hilos de trabajo enriquecidos desde Q9",
        "tasks_created": len(tasks_created),
        "distribution": {
            "week_1": sum(1 for t in tasks_created if t.week == 1),
            "week_2": sum(1 for t in tasks_created if t.week == 2),
            "week_3": sum(1 for t in tasks_created if t.week == 3),
            "week_4": sum(1 for t in tasks_created if t.week == 4)
        }
    }
