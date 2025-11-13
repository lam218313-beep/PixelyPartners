"""
Pixely Partners - Frontend Dashboard

Streamlit-based dashboard for qualitative analysis (Q1-Q10).
Displays results from orchestrator analysis modules.
"""

import streamlit as st # type: ignore
import json
import os
from view_components._outputs import get_outputs_dir
from view_components.qual import (
    q1_view, q2_view, q3_view, q4_view, q5_view,
    q6_view, q7_view, q8_view, q9_view, q10_view
)

st.set_page_config(layout="wide", page_title="Pixely Partners Dashboard")

# Sidebar navigation
st.sidebar.title("Pixely Partners")

page = st.sidebar.radio(
    "Navegación",
    [
        "Pixely Partners",
        "Wiki",
        "Dashboard",
        "Análisis de Redes",
        "Hilos de Trabajo",
    ],
)

# Main content
if page == "Pixely Partners":
    st.title("Pixely Partners")
    st.write(
        """
        ## Dashboard de Análisis Cualitativo
        
        Bienvenido a Pixely Partners, un sistema nativo de análisis single-client
        que proporciona insights profundos sobre la audiencia y el rendimiento
        del contenido en redes sociales.
        
        ### Módulos Disponibles en Análisis de Redes:
        - **😢 Emociones** - Análisis emocional usando el modelo Plutchik
        - **👤 Personalidad** - Perfil de personalidad usando framework Aaker
        - **💬 Tópicos** - Modelado de tópicos principales
        - **📜 Marcos Narrativos** - Análisis de narrativas (Entman)
        - **🌟 Influenciadores** - Identificación de voces clave
        - **🚀 Oportunidades** - Detección de oportunidades de mejora
        - **🔍 Sentimiento** - Análisis detallado de sentimientos
        - **⏰ Temporal** - Análisis de tendencias en el tiempo
        - **📝 Recomendaciones** - Recomendaciones accionables
        - **📊 Resumen Ejecutivo** - Síntesis y KPIs principales
        
        Selecciona **Análisis de Redes** en el menú de la izquierda para comenzar.
        """
    )

    # Show outputs directory info
    outputs_dir = get_outputs_dir()
    st.info(f"📁 Outputs Directory: `{outputs_dir}`")

elif page == "Wiki":
    st.title("📚 Wiki - Documentación")
    st.write(
        """
        ### Centro de Documentación
        
        Aquí encontrarás toda la documentación sobre los análisis y frameworks utilizados.
        
        **Próximamente:** Se agregará documentación detallada de cada módulo de análisis.
        """
    )

elif page == "Dashboard":
    st.title("📊 Dashboard Principal")
    st.write(
        """
        ### Panel de Control
        
        Monitoreo general del sistema y métricas principales.
        
        **Próximamente:** Se agregará un dashboard de métricas consolidadas.
        """
    )

elif page == "Análisis de Redes":
    st.title("🔍 Análisis de Redes Sociales")
    
    # Horizontal tabs for analyses
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "😢 Emociones",
        "👤 Personalidad",
        "💬 Tópicos",
        "📜 Marcos",
        "🌟 Influenciadores",
        "🚀 Oportunidades",
        "🔍 Sentimiento",
        "⏰ Temporal",
        "📝 Recomendaciones",
        "📊 Resumen"
    ])
    
    with tab1:
        q1_view.display_q1_emociones()
    
    with tab2:
        q2_view.display_q2_personalidad()
    
    with tab3:
        q3_view.display_q3_topicos()
    
    with tab4:
        q4_view.display_q4_marcos_narrativos()
    
    with tab5:
        q5_view.display_q5_influenciadores()
    
    with tab6:
        q6_view.display_q6_oportunidades()
    
    with tab7:
        q7_view.display_q7_sentimiento()
    
    with tab8:
        q8_view.display_q8_temporal()
    
    with tab9:
        q9_view.display_q9_recomendaciones()
    
    with tab10:
        q10_view.display_q10_resumen_ejecutivo()

elif page == "Hilos de Trabajo":
    st.title("🧵 Hilos de Trabajo")
    st.write(
        """
        ### Gestión de Tareas y Workflows
        
        Centro de coordinación para hilos de trabajo y tareas en progreso.
        
        **Próximamente:** Se agregará un sistema de gestión de hilos de trabajo.
        """
    )
