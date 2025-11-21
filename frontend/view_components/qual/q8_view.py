"""Q8 View: Temporal Behavior Analysis with Anomaly Detection"""
import streamlit as st # type: ignore
import pandas as pd
import json
import os
from datetime import datetime
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
from view_components.data_loader import load_q8_data as api_load_q8
from view_components.compat_loader import load_from_api_or_file

def load_q8_data():
    """Load Q8 data from API or local file (backward compatibility)."""
    return load_from_api_or_file(api_load_q8, "q8_temporal.json", "Q8")

def get_sentiment_color(sentiment_type):
    """Map sentiment type to color"""
    color_map = {
        'Positivo': '#2ecc71',
        'Negativo': '#e74c3c',
        'Neutral': '#95a5a6'
    }
    return color_map.get(sentiment_type, '#3498db')

def display_q8_temporal():
    st.title("📈 Q8: Comportamiento Temporal & Detección de Anomalías")
    
    data = load_q8_data()
    if data is None:
        return
    
    results = data.get("results", {})
    serie_temporal = results.get("serie_temporal_semanal", [])
    anomalias = results.get("anomalias_detectadas", [])
    resumen = results.get("resumen_global", {})
    distribucion_topicos = results.get("distribucion_topicos_por_semana", {})
    
    if not serie_temporal:
        st.info("No temporal data available")
        return
    
    # Convert to DataFrame
    df_temporal = pd.DataFrame(serie_temporal)
    df_temporal['fecha_semana'] = pd.to_datetime(df_temporal['fecha_semana'])
    df_temporal = df_temporal.sort_values('fecha_semana')
    
    # ========================================================================
    # GRÁFICO 1: LÍNEAS + SCATTER SUPERPUESTO (Anomalías)
    # ========================================================================
    st.header("📊 Gráfico 1: Tendencia Temporal + Anomalías Detectadas")
    st.markdown("""
    **📊 Qué estamos viendo:**
    Una serie temporal de 8 semanas mostrando la evolución del Sentimiento Positivo (línea verde) vs Negativo (línea roja).
    Los marcadores grandes indican ANOMALÍAS: cambios abruptos que señalan eventos significativos.
    
    **🔍 Cómo se midió:**
    - Se agregaron comentarios por semana
    - Se calculó el % de comentarios Positivo/Negativo
    - Se detectaron semanas con cambios > 25% como anomalías
    
    **💡 Para qué se usa:**
    Identificar el CUÁNDO ocurrieron los eventos críticos.
    Las líneas muestran tendencias; los marcadores señalan dónde intervenir.
    
    **📌 Tips:**
    - Picos verdes (arriba) = Oportunidades para amplificar
    - Picos rojos (abajo) = Crisis que requieren respuesta inmediata
    - Busca patrones: ¿Qué precede a cada pico?
    """)
    
    # Create figure with secondary y-axis
    fig_temporal = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add positive sentiment line
    fig_temporal.add_trace(
        go.Scatter(
            x=df_temporal['fecha_semana'],
            y=df_temporal['porcentaje_positivo'] * 100,
            name='Sentimiento Positivo',
            mode='lines+markers',
            line=dict(color='#2ecc71', width=3),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Positivo: %{y:.0f}%<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Add negative sentiment line
    fig_temporal.add_trace(
        go.Scatter(
            x=df_temporal['fecha_semana'],
            y=df_temporal['porcentaje_negativo'] * 100,
            name='Sentimiento Negativo',
            mode='lines+markers',
            line=dict(color='#e74c3c', width=3),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Negativo: %{y:.0f}%<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Add anomaly markers (scatter plot superpuesto)
    # Safely filter anomalies, handling NaN values
    if 'es_anomalia' in df_temporal.columns:
        mask = df_temporal['es_anomalia'].fillna(False).astype(bool)
        df_anomalias = df_temporal[mask]
    else:
        df_anomalias = pd.DataFrame()
    for idx, anomalia in df_anomalias.iterrows():
        sentiment = anomalia['porcentaje_positivo'] if anomalia['porcentaje_positivo'] > anomalia['porcentaje_negativo'] else anomalia['porcentaje_negativo']
        color = '#2ecc71' if anomalia['porcentaje_positivo'] > anomalia['porcentaje_negativo'] else '#e74c3c'
        
        fig_temporal.add_trace(
            go.Scatter(
                x=[anomalia['fecha_semana']],
                y=[sentiment * 100],
                mode='markers',
                marker=dict(size=20, color=color, symbol='star', line=dict(color='gold', width=3)),
                name='Anomalía',
                hovertemplate=f"<b>ANOMALÍA: {anomalia['topico_dominante']}</b><br>%{{x|%Y-%m-%d}}<br>Tópico: {anomalia['topico_dominante']}<extra></extra>",
                showlegend=False
            ),
            secondary_y=False
        )
    
    # Add engagement on secondary axis
    fig_temporal.add_trace(
        go.Scatter(
            x=df_temporal['fecha_semana'],
            y=df_temporal['engagement'],
            name='Engagement',
            mode='lines',
            line=dict(color='#3498db', width=2, dash='dash'),
            opacity=0.6,
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Engagement: %{y}<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig_temporal.update_xaxes(title_text="Semana")
    fig_temporal.update_yaxes(title_text="Sentimiento (%)", secondary_y=False)
    fig_temporal.update_yaxes(title_text="Engagement (interacciones)", secondary_y=True)
    fig_temporal.update_layout(
        title="Evolución Semanal de Sentimiento + Anomalías",
        height=500,
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    # ========================================================================
    # GRÁFICO 2: MARCADORES CONTEXTUALES (Coloración + Tooltip)
    # ========================================================================
    st.header("📊 Gráfico 2: Marcadores Contextuales & Tópicos Dominantes")
    st.markdown("""
    **📊 Qué estamos viendo:**
    Amplificación de las anomalías: cada marcador representa una semana anómala.
    El COLOR indica si fue POSITIVA (verde) o NEGATIVA (roja).
    Al pasar el cursor, se muestra el TÓPICO que dominó esa semana.
    
    **🔍 Cómo se midió:**
    - Se clasificó cada anomalía por sentimiento dominante
    - Se extrajeron los tópicos principales de cada semana
    - Se vinculó cada tópico con la URL de la publicación viral
    
    **💡 Para qué se usa:**
    Entender QUÉ TEMA causó cada pico/caída.
    No es solo "se fue negativo" → es "Problema de Calidad fue negativo".
    
    **📌 Tips:**
    - Busca patrones de tópicos: ¿Se repiten problemas?
    - Verifica las URLs virales para leer comentarios originales
    - Prepara respuestas según el tópico dominante
    """)
    
    # Create contextual markers chart
    fig_markers = go.Figure()
    
    for anomalia in anomalias:
        fecha = pd.to_datetime(anomalia['fecha'])
        color = '#2ecc71' if anomalia['sentimiento_dominante'] == 'Positivo' else '#e74c3c'
        
        fig_markers.add_trace(
            go.Scatter(
                x=[fecha],
                y=[anomalia['porcentaje_cambio']],
                mode='markers+text',
                marker=dict(size=25, color=color, symbol='diamond', line=dict(color='gold', width=2)),
                text=[anomalia['topico_dominante']],
                textposition='top center',
                textfont=dict(size=11, color='black'),
                name=anomalia['topico_dominante'],
                hovertemplate=(
                    f"<b>{anomalia['topico_dominante']}</b><br>"
                    f"Sentimiento: {anomalia['sentimiento_dominante']}<br>"
                    f"Cambio: {anomalia['porcentaje_cambio']:+d}%<br>"
                    f"<b>Post Viral:</b> {anomalia['post_url_viral']}<extra></extra>"
                )
            )
        )
    
    fig_markers.update_layout(
        title="Anomalías Detectadas: Tópicos Dominantes y Cambio de Sentimiento",
        xaxis_title="Fecha",
        yaxis_title="Cambio en Sentimiento (%)",
        height=400,
        hovermode='closest',
        showlegend=False
    )
    
    st.plotly_chart(fig_markers, use_container_width=True)
    
    # ========================================================================
    # GRÁFICO 3: PANEL DE DIAGNÓSTICO (Cards de Alerta)
    # ========================================================================
    st.header("📊 Gráfico 3: Panel de Diagnóstico - Top 3 Anomalías")
    st.markdown("""
    **📊 Qué estamos viendo:**
    Las 3 anomalías más significativas presentadas como ALERTAS.
    Cada alerta muestra: Tópico → Causa → URL viral.
    
    **🔍 Cómo se midió:**
    - Se rankean anomalías por cambio de sentimiento (magnitud)
    - Se extrae la descripción cualitativa de cada evento
    - Se vincula la post_url para acceso inmediato
    
    **💡 Para qué se usa:**
    Toma de decisiones inmediata.
    Un ejecutivo puede leer 3 alertas y actuar en 2 minutos.
    
    **📌 Tips:**
    - Haz clic en la URL para leer comentarios reales
    - Prioriza por cambio % (mayor = mayor impacto)
    - Prepara respuesta según la causa primaria
    """)
    
    # Display anomaly cards
    for i, anomalia in enumerate(anomalias, 1):
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                color = '#2ecc71' if anomalia['sentimiento_dominante'] == 'Positivo' else '#e74c3c'
                st.markdown(f"<div style='background-color:{color};color:white;padding:15px;border-radius:8px;text-align:center;font-size:20px;font-weight:bold;'>#{i}</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                **🎯 Tópico:** {anomalia['topico_dominante']}
                
                **📊 Sentimiento:** {anomalia['sentimiento_dominante']} ({anomalia['porcentaje_cambio']:+d}%)
                
                **📝 Descripción:** {anomalia['descripcion']}
                
                **🔍 Causa Primaria:** {anomalia['causa_primaria']}
                
                **🔗 [Acceder a Post Viral →]({anomalia['post_url_viral']})** | Fecha: {anomalia['fecha']}
                """)
            
            with col3:
                icon = "🔥" if anomalia['sentimiento_dominante'] == 'Negativo' else "⭐"
                st.markdown(f"<div style='font-size:40px;text-align:center;'>{icon}</div>", unsafe_allow_html=True)
        
        st.divider()
    
    # ========================================================================
    # GRÁFICO 4: CORRELACIÓN TEMÁTICA (Drill-Down por Semana)
    # ========================================================================
    st.header("📊 Gráfico 4: Análisis Temático Detallado - Drill-Down")
    st.markdown("""
    **📊 Qué estamos viendo:**
    Selecciona una semana anómala para ver la DISTRIBUCIÓN COMPLETA de tópicos durante ese período.
    Esto aisla la causa primaria: ¿qué temas NO fueron noticia, pero el anómalo sí dominó?
    
    **🔍 Cómo se midió:**
    - Se extraen todos los comentarios de la semana seleccionada
    - Se agregan por tópico
    - Se muestra la distribución de tópicos SOLO para esa semana
    
    **💡 Para qué se usa:**
    Profundizar en "por qué pasó esto".
    Si "Problema de Calidad" fue 65% de la conversación, los otros 35% fueron qué?
    
    **📌 Tips:**
    - Compara la distribución de una semana anómala vs normal
    - Identifica tópicos secundarios que contribuyeron
    - Prepara comunicación que aborde los tópicos secundarios también
    """)
    
    # Selector for anomalous week
    anomaly_weeks = [a['fecha'] for a in anomalias]
    selected_week = st.selectbox(
        "Selecciona una semana anómala para drill-down temático:",
        anomaly_weeks,
        key="week_selector_q8"
    )
    
    if selected_week in distribucion_topicos:
        topicos_dist = distribucion_topicos[selected_week]
        
        # Create bar chart for topic distribution
        temas = list(topicos_dist.keys())
        porcentajes = [v * 100 for v in topicos_dist.values()]
        
        fig_topics = go.Figure([go.Bar(
            x=temas,
            y=porcentajes,
            marker_color=['#e74c3c', '#f39c12', '#95a5a6'],
            text=[f"{p:.0f}%" for p in porcentajes],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>%{y:.0f}%<extra></extra>'
        )])
        
        fig_topics.update_layout(
            title=f"Distribución de Tópicos - Semana {selected_week}",
            xaxis_title="Tópico",
            yaxis_title="% de Conversación",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_topics, use_container_width=True)
        
        # Show context
        st.info(f"""
        **Contexto de la Semana {selected_week}:**
        
        Durante esta semana, la conversación estuvo dominada por los tópicos mostrados arriba.
        El tópico principal representó el mayor porcentaje de la discusión.
        Los secundarios contribuyeron a la complejidad del evento anómalo.
        """)
    
    # ========================================================================
    # RESUMEN ESTRATÉGICO
    # ========================================================================
    st.markdown("---")
    st.markdown("**📈 Resumen Estratégico Global:**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Semanas Analizadas",
            resumen.get('total_semanas_analizadas', 0)
        )
    
    with col2:
        st.metric(
            "Anomalías Detectadas",
            resumen.get('anomalias_totales', 0),
            delta=f"{resumen.get('anomalias_totales', 0) / resumen.get('total_semanas_analizadas', 1) * 100:.0f}% del período"
        )
    
    with col3:
        st.metric(
            "Sentimiento Positivo Promedio",
            f"{resumen.get('promedio_sentimiento_positivo', 0) * 100:.0f}%"
        )
    
    with col4:
        st.metric(
            "Sentimiento Negativo Promedio",
            f"{resumen.get('promedio_sentimiento_negativo', 0) * 100:.0f}%"
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Mejor Semana",
            resumen.get('semana_mejor_desempen', '—')
        )
    
    with col2:
        st.metric(
            "Peor Semana",
            resumen.get('semana_peor_desempen', '—')
        )
    
    with col3:
        st.metric(
            "Tendencia General",
            resumen.get('tendencia_general', '—')
        )

