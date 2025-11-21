"""
Pixely Partners - Frontend Dashboard

Streamlit-based dashboard for qualitative analysis (Q1-Q10).
Displays results from API with JWT authentication.
"""

import streamlit as st # type: ignore
import os
from api_client import APIClient, init_session_state, is_authenticated
from auth_view import display_login, display_user_info
from view_components.qual import (
    q1_view, q2_view, q3_view, q4_view, q5_view,
    q6_view, q7_view, q8_view, q9_view, q10_view
)

st.set_page_config(layout="wide", page_title="Pixely Partners Dashboard")

# Initialize session state
init_session_state()

# Check authentication
if not is_authenticated():
    display_login()
    st.stop()

# Sidebar navigation
st.sidebar.title("Pixely Partners")

# Display user info
display_user_info()

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
    api_base_url = os.environ.get("API_BASE_URL", "http://api:8000")
    st.info(f"🔗 API URL: `{api_base_url}`")

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
    
    # Get client info and last analysis timestamp
    client = APIClient()
    ficha_id = st.session_state.get("ficha_cliente_id")
    
    if not ficha_id:
        st.error("❌ No se encontró ID de cliente. Por favor cierra sesión e inicia sesión nuevamente.")
        st.stop()
    
    # Display last update timestamp
    ficha_data = client.get_ficha_cliente(ficha_id)
    if ficha_data:
        last_timestamp_str = ficha_data.get("last_analysis_timestamp")
        
        if last_timestamp_str:
            from datetime import datetime
            # Parse and calculate time difference
            try:
                last_dt = datetime.fromisoformat(last_timestamp_str.replace('Z', '+00:00'))
                time_diff = datetime.now(last_dt.tzinfo) - last_dt
                hours_ago = int(time_diff.total_seconds() / 3600)
                
                # Display timestamp with color coding
                if hours_ago < 24:
                    st.success(f"📅 **Última actualización:** hace {hours_ago} horas ({last_dt.strftime('%Y-%m-%d %H:%M')})")
                elif hours_ago < 48:
                    st.info(f"📅 **Última actualización:** hace {hours_ago} horas ({last_dt.strftime('%Y-%m-%d %H:%M')})")
                else:
                    days_ago = int(hours_ago / 24)
                    st.warning(f"📅 **Última actualización:** hace {days_ago} días ({last_dt.strftime('%Y-%m-%d %H:%M')})")
            except Exception as e:
                st.caption(f"ℹ️ Error al parsear timestamp: {e}")
        else:
            st.warning("⏳ **Esperando primer análisis automático** (se ejecuta cada 24h a las 6:00 AM)")
            
            # Option to trigger manual analysis
            if st.button("▶️ Ejecutar Análisis Manual"):
                with st.spinner("Ejecutando análisis... Esto puede tardar varios minutos."):
                    if client.trigger_analysis(ficha_id):
                        st.success("✅ Análisis completado exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al ejecutar análisis")
    
    # Store insights in session state for view components
    insights = client.get_insights(ficha_id)
    if insights:
        st.session_state.current_insights = insights
    else:
        st.warning("📭 No hay datos de análisis disponibles. El análisis se ejecuta automáticamente cada 24 horas.")
        st.stop()
    
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
