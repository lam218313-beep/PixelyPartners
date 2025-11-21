"""Q5 View: Influencers Analysis"""
import streamlit as st # type: ignore
import pandas as pd
import json
import os
import plotly.graph_objects as go  # type: ignore
from view_components.data_loader import load_q5_data as api_load_q5
from view_components.compat_loader import load_from_api_or_file

def load_q5_data():
    """Load Q5 data from API or local file (backward compatibility)."""
    return load_from_api_or_file(api_load_q5, "q5_influenciadores.json", "Q5")

def display_q5_influenciadores():
    st.title("🌟 Q5: Análisis de Influenciadores Clave")
    
    st.markdown("""
    ### ¿Qué es este análisis?
    El **Análisis de Influenciadores** identifica las VOCES MÁS PODEROSAS en tu conversación. No es por seguidores (eso es lo que hacen los influencer networks), sino por IMPACTO: ¿Quién alcanza a más gente? ¿Quién es más credible? ¿Quién tiene más peso en las decisiones de otros?
    
    ### ¿Por qué es relevante para tu negocio?
    Un comentario de la persona correcta puede generar 100x más impacto que de la persona equivocada. Este análisis te permite:
    - **Identificar embajadores naturales:** Quiénes ya aman tu marca y tienen influencia (verde en el gráfico)
    - **Detectar detractores peligrosos:** Quiénes critican tu marca Y tienen capacidad de daño (rojo)
    - **Priorizar conversaciones:** ¿Respondo a este comentario? Depende de quién lo escribió
    - **Diseñar partnerships:** Trabajar con los influenciadores correctos > gastar fortuna en campañas genéricas
    - **Monitorear cambios:** ¿El influenciador X cambió de "promotor" a "detractor"? Eso es red alert
    - **Medir amplificación:** Ver cómo tus mensajes se propagan a través de la red
    
    ### El dato de fondo
    Usamos Network Analysis + Sentiment para calcular "centralidad" (cuánta gente está conectada a través de ellos) × "polaridad" (qué tan positivos son). El resultado = poder real, no seguidores vanity.
    """)
    
    data = load_q5_data()
    if data is None:
        return
    
    results = data.get("results", {})
    
    # Get data from detallado structure
    top_influencers = results.get("top_influenciadores_detallado", [])
    
    if top_influencers:
        df_inf = pd.DataFrame(top_influencers)
        
        # ========================================================================
        # GRÁFICO 1: INFLUENCIA GENERAL (TOP 5 POR CENTRALIDAD COLOREADO)
        # ========================================================================
        st.header("📊 Gráfico 1: Influenciadores por Centralidad")
        st.markdown("""
        **📊 Qué estamos viendo:**
        Los 5 influenciadores más centrales en la conversación, coloreados por su actitud hacia tu marca.
        
        **🔍 Cómo se midió:**
        Score de centralidad = frecuencia de participación × engagement recibido × alcance de la red.
        
        **💡 Para qué se usa:**
        Identificar rápidamente tus aliados más poderosos (verde) y críticos influyentes (rojo) para priorizar acciones.
        
        **📌 Tips:**
        Los influenciadores en verde son tus embajadores naturales. Los en rojo necesitan atención estratégica.
        """)
        
        df_top = df_inf.nlargest(5, 'score_centralidad')
        
        # Color based on polaridad_dominante
        colors = ['#2ecc71' if pol == 'Promotor' else '#e74c3c' 
                 for pol in df_top['polaridad_dominante']]
        
        fig = go.Figure([go.Bar(
            x=df_top['username'],
            y=df_top['score_centralidad'],
            marker_color=colors,
            text=df_top['polaridad_dominante'],
            textposition='outside'
        )])
        fig.update_layout(
            title="Top 5 Influenciadores (Verde=Promotor, Rojo=Detractor)",
            xaxis_title="Usuario",
            yaxis_title="Score de Centralidad",
            showlegend=False,
            xaxis_tickangle=-45,
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # ========================================================================
        # GRÁFICO 2: FILTRO DE ACCIÓN ESTRATÉGICA (SELECTOR PROMOTORES/DETRACTORES)
        # ========================================================================
        st.header("📊 Gráfico 2: Filtro Estratégico por Polaridad")
        st.markdown("""
        **📊 Qué estamos viendo:**
        Los Top 5 influenciadores dentro de cada categoría (Promotores o Detractores).
        
        **🔍 Cómo se midió:**
        Polaridad dominante = clasificación del sentimiento general del usuario hacia la marca (Promotor/Detractor).
        
        **💡 Para qué se usa:**
        Segmentar influenciadores por su actitud facilita campañas dirigidas:
        - Promotores: amplificar su mensaje, crear relaciones embajador
        - Detractores: mitigación de daño, conversión de sentimiento
        
        **📌 Tips:**
        Verifica el alcance y sentimiento detallado en la tabla abajo para priorizar contactos.
        """)
        
        polarities = sorted(df_inf['polaridad_dominante'].unique())
        selected_polarity = st.selectbox(
            "Selecciona categoría para ver Top 5:",
            polarities,
            key="polarity_selector"
        )
        
        df_filtered = df_inf[df_inf['polaridad_dominante'] == selected_polarity].nlargest(5, 'score_centralidad')
        
        if len(df_filtered) > 0:
            polarity_color = '#2ecc71' if selected_polarity == 'Promotor' else '#e74c3c'
            
            fig_filter = go.Figure([go.Bar(
                y=df_filtered['username'],
                x=df_filtered['score_centralidad'],
                orientation='h',
                marker_color=polarity_color
            )])
            fig_filter.update_layout(
                title=f"Top 5 {selected_polarity}es (Ordenados por Centralidad)",
                xaxis_title="Score de Centralidad",
                yaxis_title="Usuario",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_filter, use_container_width=True)
            
            # Show table
            st.markdown("**Detalle de influenciadores:**")
            display_df = df_filtered[['username', 'score_centralidad', 'alcance', 'sentimiento']].copy()
            display_df['score_centralidad'] = display_df['score_centralidad'].round(3)
            display_df['sentimiento'] = display_df['sentimiento'].round(2)
            display_df['alcance'] = display_df['alcance'].astype(int)
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info(f"No {selected_polarity}es found")
        
        # ========================================================================
        # GRÁFICO 3: EVIDENCIA NARRATIVA (COMENTARIOS CON EXPANDIBLES)
        # ========================================================================
        st.header("📊 Gráfico 3: Evidencia Narrativa")
        st.markdown("""
        **📊 Qué estamos viendo:**
        El comentario más representativo de cada influenciador, que captura su postura hacia tu marca.
        
        **� Cómo se midió:**
        Comentario evidencia = fragmento del feedback más representativo según polaridad y engagement.
        
        **� Para qué se usa:**
        Comprender el "por qué" detrás de cada influenciador. Los testimonios reales son más convincentes que métricas.
        
        **� Tips:**
        Lee los comentarios para entender motivaciones. Busca patrones: ¿qué aspectos destacan promotores vs detractores?
        """)
        
        selected_influencer = st.selectbox(
            "Selecciona un influenciador para ver su comentario más influyente:",
            df_inf['username'].tolist(),
            key="influencer_selector"
        )
        
        influencer_data = df_inf[df_inf['username'] == selected_influencer].iloc[0]
        
        # Display influencer metrics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score de Centralidad", f"{influencer_data.get('score_centralidad', 0):.3f}")
        with col2:
            polarity_display = influencer_data.get('polaridad_dominante', 'N/A')
            st.metric("Polaridad", polarity_display)
        with col3:
            st.metric("Sentimiento", f"{influencer_data.get('sentimiento', 0):.2f}")
        
        # Display comment evidence in expandible
        st.markdown("**Comentario más influyente:**")
        with st.expander("💬 Click para ver el comentario completo", expanded=True):
            comment_text = influencer_data.get('comentario_evidencia', 'No hay comentario disponible')
            st.markdown(f"> *{comment_text}*")
        
        # Additional metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Alcance Estimado", f"{influencer_data.get('alcance', 0):,}")
        with col2:
            st.metric("Tipo de Influencia", "Alto" if influencer_data.get('score_centralidad', 0) > 0.7 else "Medio")
        with col3:
            st.metric("Categoría", selected_polarity)
    else:
        st.info("No influencers data available")
