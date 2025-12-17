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
    st.header("📊 Gráfico 2: Marcadores Contextuales & Anomalías Detectadas")
    st.markdown("""
    **📊 Qué estamos viendo:**
    Amplificación de las anomalías: cada marcador representa una semana anómala.
    El COLOR indica si fue MEJORA (verde) o DETERIORO (roja).
    
    **🔍 Cómo se midió:**
    - Se detectaron semanas con cambio > 25% en sentimiento
    - Se extrajeron los tópicos principales de cada semana
    
    **💡 Para qué se usa:**
    Entender QUÉ SEMANA y POR QUÉ cambió la conversación abruptamente.
    """)
    
    # Create contextual markers chart
    fig_markers = go.Figure()
    
    if anomalias:
        for i, anomalia in enumerate(anomalias):
            fecha = pd.to_datetime(anomalia.get('fecha_semana', anomalia.get('fecha', '2024-01-01')))
            es_mejora = 'Mejora' in anomalia.get('tipo_anomalia', '')
            color = '#2ecc71' if es_mejora else '#e74c3c'
            cambio = anomalia.get('cambio_porcentaje', anomalia.get('porcentaje_cambio', 0))
            topico = anomalia.get('topico_dominante', 'Desconocido')
            
            fig_markers.add_trace(
                go.Scatter(
                    x=[fecha],
                    y=[cambio],
                    mode='markers+text',
                    marker=dict(size=25, color=color, symbol='diamond', line=dict(color='gold', width=2)),
                    text=[topico],
                    textposition='top center',
                    textfont=dict(size=10, color='black'),
                    name=topico,
                    hovertemplate=(
                        f"<b>{topico}</b><br>"
                        f"Cambio: {cambio:+.1f}%<br>"
                        f"Tipo: {anomalia.get('tipo_anomalia', 'N/A')}<extra></extra>"
                    )
                )
            )
        
        fig_markers.update_layout(
            title="Anomalías Detectadas: Cambios Significativos en Sentimiento",
            xaxis_title="Fecha",
            yaxis_title="Cambio en Sentimiento (%)",
            height=400,
            hovermode='closest',
            showlegend=False
        )
        
        st.plotly_chart(fig_markers, use_container_width=True)
    else:
        st.info("No anomalías detectadas en el período analizado")
    
    # ========================================================================
    # GRÁFICO 3: PANEL DE DIAGNÓSTICO (Cards de Alerta)
    # ========================================================================
    st.header("📊 Gráfico 3: Panel de Diagnóstico - Anomalías por Semana")
    st.markdown("""
    **📊 Qué estamos viendo:**
    Resumen de las anomalías detectadas presentadas de forma clara.
    Cada anomalía muestra: Cambio de Sentimiento → Tópico Dominante → Tipo.
    
    **💡 Para qué se usa:**
    Toma de decisiones inmediata sobre eventos críticos.
    """)
    
    # Display anomaly cards
    if anomalias:
        for i, anomalia in enumerate(anomalias, 1):
            with st.container():
                col1, col2, col3 = st.columns([1, 4, 1])
                
                with col1:
                    es_mejora = 'Mejora' in anomalia.get('tipo_anomalia', '')
                    color = '#2ecc71' if es_mejora else '#e74c3c'
                    st.markdown(f"<div style='background-color:{color};color:white;padding:15px;border-radius:8px;text-align:center;font-size:20px;font-weight:bold;'>#{i}</div>", unsafe_allow_html=True)
                
                with col2:
                    cambio = anomalia.get('cambio_porcentaje', 0)
                    tipoanomalia = anomalia.get('tipo_anomalia', 'N/A')
                    topico = anomalia.get('topico_dominante', 'Desconocido')
                    fecha = anomalia.get('fecha_semana', 'N/A')
                    st.markdown(f"""
                    **📊 Tópico Dominante:** {topico}
                    
                    **📈 Tipo:** {tipoanomalia}
                    
                    **🔢 Cambio:** {cambio:+.1f}% (Sentimiento: {anomalia.get('sentimiento_anterior', 0):.0f}% → {anomalia.get('sentimiento_actual', 0):.0f}%)
                    
                    **📅 Semana:** {fecha}
                    """)
                
                with col3:
                    icon = "📈" if 'Mejora' in tipoanomalia else "📉"
                    st.markdown(f"<div style='font-size:40px;text-align:center;'>{icon}</div>", unsafe_allow_html=True)
            
            st.divider()
    else:
        st.info("No anomalías detectadas para mostrar")
    
    # ========================================================================
    # GRÁFICO 4: CORRELACIÓN TEMÁTICA (Drill-Down por Semana)
    # ========================================================================
    st.header("📊 Gráfico 4: Análisis Temático Detallado - Drill-Down")
    st.markdown("""
    **📊 Qué estamos viendo:**
    Selecciona una semana para ver la EVOLUCIÓN de tópicos durante ese período.
    
    **💡 Para qué se usa:**
    Profundizar en los cambios de tema semana a semana.
    """)
    
    # Get unique weeks from temporal series
    if serie_temporal and len(serie_temporal) > 0:
        semanas_disponibles = [s.get('fecha_semana', f"Week {s.get('semana_numero', i)}") for i, s in enumerate(serie_temporal)]
        
        # Remove duplicates while maintaining order
        semanas_unicas = []
        for s in semanas_disponibles:
            if s not in semanas_unicas:
                semanas_unicas.append(s)
        
        if semanas_unicas:
            selected_week = st.selectbox(
                "Selecciona una semana para análisis detallado:",
                semanas_unicas,
                key="week_selector_q8"
            )
            
            # Find the selected week data
            week_data = None
            for week in serie_temporal:
                if week.get('fecha_semana') == selected_week or str(week.get('fecha_semana')) == selected_week:
                    week_data = week
                    break
            
            if week_data:
                st.success(f"📊 Datos de la semana: {selected_week}")
                
                # Display week metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Comentarios", week_data.get('num_comentarios', 0))
                with col2:
                    st.metric("Sentimiento +", f"{week_data.get('porcentaje_positivo', 0)*100:.0f}%")
                with col3:
                    st.metric("Sentimiento -", f"{week_data.get('porcentaje_negativo', 0)*100:.0f}%")
                with col4:
                    st.metric("Tópico Principal", week_data.get('topico_principal', 'N/A'))
                
                # Show topic distribution if available
                if selected_week in distribucion_topicos:
                    topicos_dist = distribucion_topicos[selected_week]
                    temas = list(topicos_dist.keys())
                    porcentajes = [v * 100 for v in topicos_dist.values()]
                    
                    fig_topics = go.Figure([go.Bar(
                        x=temas,
                        y=porcentajes,
                        marker_color=['#e74c3c', '#f39c12', '#95a5a6'][:len(temas)],
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
                else:
                    st.info(f"No hay distribución de tópicos detallada para {selected_week}")
            else:
                st.warning("No se encontraron datos para la semana seleccionada")
        else:
            st.info("No hay semanas disponibles para análisis")
    else:
        st.info("No hay datos temporales disponibles")
    
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

