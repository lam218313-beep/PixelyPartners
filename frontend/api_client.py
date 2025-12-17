"""
API Client for Pixely Partners Frontend

Handles authentication and API communication with the backend.
"""

import httpx
import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class APIClient:
    """Client for communicating with Pixely Partners API."""
    
    def __init__(self, base_url: str = "http://api:8000"):
        self.base_url = base_url
        self.timeout = 30.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        token = st.session_state.get("access_token")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and get access token.
        
        Returns:
            Dict with access_token, token_type, and user info
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.post(
                    "/token",
                    data={"username": username, "password": password}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Usuario o contraseña incorrectos")
            raise ValueError(f"Error de autenticación: {e}")
        except Exception as e:
            raise ValueError(f"Error de conexión: {e}")
    
    def get_ficha_cliente(self, ficha_id: str) -> Optional[Dict[str, Any]]:
        """Get ficha cliente data."""
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.get(
                    f"/fichas_cliente/{ficha_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"Error al obtener ficha cliente: {e}")
            return None
    
    def get_insights(self, ficha_id: str) -> Optional[Dict[str, Any]]:
        """Get all insights for a client."""
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.get(
                    f"/insights/{ficha_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            st.error(f"Error al obtener insights: {e}")
            return None
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return None
    
    def trigger_analysis(self, ficha_id: str) -> bool:
        """
        Trigger manual analysis for a client.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=120.0) as client:
                response = client.post(
                    "/analyze/trigger",
                    json={"ficha_cliente_id": ficha_id},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return True
        except Exception as e:
            st.error(f"Error al ejecutar análisis: {e}")
            return False
    
    # ========================================================================
    # TASK MANAGEMENT METHODS
    # ========================================================================
    
    def get_tasks(self, ficha_id: str) -> Optional[Dict[str, Any]]:
        """
        Get all tasks for a client, grouped by week.
        
        Returns:
            Dict with week_1, week_2, week_3, week_4, total_tasks, completed_tasks
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.get(
                    f"/api/v1/fichas/{ficha_id}/tasks",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            st.error(f"Error al obtener tareas: {e}")
            return None
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return None
    
    def update_task_status(self, task_id: str, new_status: str) -> Optional[Dict[str, Any]]:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            new_status: New status (PENDIENTE, EN_CURSO, HECHO, REVISADO)
        
        Returns:
            Updated task data
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.patch(
                    f"/api/v1/tasks/{task_id}",
                    json={"status": new_status},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"Error al actualizar tarea: {e}")
            return None
    
    def add_task_note(self, task_id: str, content: str) -> Optional[Dict[str, Any]]:
        """
        Add a note/comment to a task.
        
        Args:
            task_id: Task ID
            content: Note content
        
        Returns:
            Created note data
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.post(
                    f"/api/v1/tasks/{task_id}/notes",
                    json={"content": content},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"Error al agregar nota: {e}")
            return None
    
    def get_task_notes(self, task_id: str) -> Optional[list]:
        """
        Get all notes for a task.
        
        Args:
            task_id: Task ID
        
        Returns:
            List of notes
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.get(
                    f"/api/v1/tasks/{task_id}/notes",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"Error al obtener notas: {e}")
            return None

    def update_task_note(self, task_id: str, note_id: str, content: str) -> Optional[Dict[str, Any]]:
        """
        Update a task note's content.
        
        Args:
            task_id: Task ID
            note_id: Note ID
            content: New content
        
        Returns:
            Updated note data
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.patch(
                    f"/api/v1/tasks/{task_id}/notes/{note_id}",
                    json={"content": content},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"Error al actualizar nota: {e}")
            return None

    def delete_task_note(self, task_id: str, note_id: str) -> bool:
        """
        Delete a task note.
        
        Args:
            task_id: Task ID
            note_id: Note ID
        
        Returns:
            True if deleted
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.delete(
                    f"/api/v1/tasks/{task_id}/notes/{note_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return True
        except Exception as e:
            st.error(f"Error al eliminar nota: {e}")
            return False
    
    def generate_tasks_from_q9(self, ficha_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate tasks from Q9 recommendations.
        
        Args:
            ficha_id: Client ID
        
        Returns:
            Dict with generation results
        """
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.post(
                    f"/api/v1/fichas/{ficha_id}/tasks/generate-from-q9",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"Error al generar tareas: {e}")
            return None


def init_session_state():
    """Initialize session state variables."""
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    
    if "token_type" not in st.session_state:
        st.session_state.token_type = None
    
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    
    if "tenant_id" not in st.session_state:
        st.session_state.tenant_id = None
    
    if "ficha_cliente_id" not in st.session_state:
        st.session_state.ficha_cliente_id = None
    
    if "ficha_cliente_name" not in st.session_state:
        st.session_state.ficha_cliente_name = None


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("access_token") is not None


def logout():
    """Clear session state and logout user."""
    st.session_state.access_token = None
    st.session_state.token_type = None
    st.session_state.user_email = None
    st.session_state.tenant_id = None
    st.session_state.ficha_cliente_id = None
    st.session_state.ficha_cliente_name = None
