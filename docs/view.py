import streamlit as st # type: ignore
import json
import os


def draw_dashboard(data: dict):
    """
    Organiza y renderiza el dashboard principal de redes sociales.

    Args:
        data (dict): El payload completo de insights cargado desde el JSON.
    """
    st.header("Dashboard de Análisis")

    st.subheader("Insights de Contenido y Audiencia")
    try:
        # Render qualitative modules as labeled tabs
        qual_tabs = st.tabs(["😢 Emociones (Q1)", "👤 Personalidad (Q2)", "💬 Tópicos (Q3)"])

        # Q1
        try:
            from .view_components.qual.q1_view import display_q1_emotions
            with qual_tabs[0]:
                display_q1_emotions()
        except Exception:
            with qual_tabs[0]:
                st.info("Q1 no disponible")

        # Q2
        try:
            from .view_components.qual.q2_view import display_q2_personalidad
            with qual_tabs[1]:
                display_q2_personalidad()
        except Exception:
            with qual_tabs[1]:
                st.info("Q2 no disponible")

        # Q3
        try:
            from .view_components.qual.q3_topicos_view import display_q3_topicos
            with qual_tabs[2]:
                display_q3_topicos()
        except Exception:
            with qual_tabs[2]:
                st.info("Q3 no disponible")

    except Exception as e:
        st.warning(f"No se pudieron renderizar los módulos cualitativos: {e}")
