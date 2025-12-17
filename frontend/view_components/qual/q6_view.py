"""Q6 View: Opportunities Analysis"""
import streamlit as st # type: ignore
import pandas as pd
import json
import os
import logging
import plotly.graph_objects as go  # type: ignore
from view_components.data_loader import load_q6_data as api_load_q6
from view_components.compat_loader import load_from_api_or_file

logger = logging.getLogger(__name__)

def load_q6_data():
    """Load Q6 data from API or local file (backward compatibility)."""
    return load_from_api_or_file(api_load_q6, "q6_oportunidades.json", "Q6")

def get_priority_color(gap_score, actividad_competitiva):
    """
    Determine color based on position in matrix:
    - Verde (Alta Urgencia / Baja Competencia): #2ecc71
    - Amarillo (Media Urgencia / Media Competencia): #f39c12
    - Rojo (Baja Urgencia / Alta Competencia): #e74c3c
    """
    if gap_score >= 80 and actividad_competitiva == "Baja":
        return "#2ecc71"  # Verde - Alta Prioridad
    elif gap_score >= 70 and actividad_competitiva == "Media":
        return "#f39c12"  # Amarillo - Media Prioridad
    elif actividad_competitiva == "Alta":
        return "#e74c3c"  # Rojo - Baja Prioridad
    else:
        return "#3498db"  # Azul - Otras

def get_actividad_numeric(actividad):
    """Convert actividad_competitiva string to numeric value for plotting"""
    mapping = {"Baja": 1, "Media": 2, "Alta": 3}
    return mapping.get(actividad, 2)

def display_q6_oportunidades():
    st.title("🚀 Q6: Análisis de Oportunidades Estratégicas")
    
    st.markdown("""
    ### ¿Qué es este análisis?
    El **Análisis de Oportunidades** busca BRECHAS en el mercado: diferencias entre lo que la audiencia PIDE y lo que se OFRECE. Una oportunidad existe cuando hay DEMANDA (audiencia lo quiere) + BAJA COMPETENCIA (pocos lo ofrecen) = Oro puro.
    
    ### ¿Por qué es relevante para tu negocio?
    La mayoría de negocios compiten en espacios saturados. Este análisis te permite encontrar "océanos azules" (espacios sin competencia) dentro de tu industria. Te permite:
    - **Priorizar desarrollo de producto:** ¿Qué característica agregamos primero?
    - **Diferenciar:** Competir en una dimensión donde nadie más está = ganar
    - **Minimizar riesgo:** Invertir en oportunidades validadas por mercado, no en intuiciones
    - **Asignación de presupuesto:** Marketing de oportunidades tiene ROI 5x mejor que defensa
    - **Entrada a nuevos segmentos:** Estas brechas a menudo revelan customer segments desatendidos
    - **Timing de innovación:** Saber CUÁNDO lanzar (cuando demanda crece + competencia es baja)
    
    ### El dato de fondo
    Comparamos lo que la audiencia PIDE (menciones, requests, frustrations) vs lo que existe en el mercado (análisis competitivo). El gap = oportunidad. El tamaño del gap × inversión competitiva baja = prioridad.
    """)
    
    data = load_q6_data()
    if data is None:
        return
    
    results = data.get("results", {})
    oportunidades = results.get("lista_oportunidades", [])
    
    if oportunidades:
        df_opp = pd.DataFrame(oportunidades)
        
        # Validate required columns
        required_cols = ['gap_score', 'actividad_competitiva', 'tema']
        missing = [c for c in required_cols if c not in df_opp.columns]
        if missing:
            st.error(f"❌ Columnas faltantes: {missing}")
            st.stop()
        
        # Ensure numeric columns
        df_opp['gap_score'] = pd.to_numeric(df_opp['gap_score'], errors='coerce')
        df_opp['competencia_score'] = pd.to_numeric(df_opp['competencia_score'], errors='coerce')
        
        # ========================================================================
        # GRÁFICO 1: MATRIZ DE PRIORIZACIÓN ESTRATÉGICA (SCATTER PLOT)
        # ========================================================================
        st.header("📊 Gráfico 1: Matriz de Priorización Estratégica")
        st.markdown("""
        **📊 Qué estamos viendo:**
        Una matriz bidimensional que posiciona cada oportunidad según dos factores críticos:
        - **Eje X (Horizontal):** Barrera de Entrada = Actividad Competitiva (1=Baja, 2=Media, 3=Alta)
        - **Eje Y (Vertical):** Urgencia Estratégica = Gap Score (0-100)
        
        **🔍 Cómo se midió:**
        - Gap Score: Mide la brecha entre demanda de mercado y oferta actual (0-100)
        - Actividad Competitiva: Nivel de competencia en esa oportunidad (Baja/Media/Alta)
        
        **💡 Para qué se usa:**
        Identificar dónde invertir recursos primero: Alta urgencia + Baja competencia = oro puro.
        
        **📌 Tips:**
        - Verde (Arriba-Izquierda): Alta Urgencia + Baja Competencia = MÁXIMA PRIORIDAD
        - Amarillo (Centro): Media Urgencia + Media Competencia = Seguimiento
        - Rojo (Abajo-Derecha): Baja Urgencia + Alta Competencia = Baja Prioridad
        """)
        
        # Prepare data for scatter plot
        df_opp['actividad_numeric'] = df_opp['actividad_competitiva'].apply(get_actividad_numeric)
        df_opp['color'] = df_opp.apply(
            lambda row: get_priority_color(row['gap_score'], row['actividad_competitiva']), 
            axis=1
        )
        
        # Create scatter plot - ensure all rows are added
        fig_matriz = go.Figure()
        
        import numpy as np
        added_count = 0
        for idx, row in df_opp.iterrows():
            try:
                if pd.isna(row['gap_score']) or pd.isna(row['actividad_numeric']):
                    continue
                
                # Add jitter to x-axis to prevent overlapping when multiple opportunities 
                # have the same actividad_numeric and gap_score values
                jitter = np.random.normal(0, 0.08)  # Small random offset
                x_jittered = row['actividad_numeric'] + jitter
                    
                fig_matriz.add_trace(go.Scatter(
                    x=[x_jittered],
                    y=[row['gap_score']],
                    mode='markers',
                    marker=dict(
                        size=15,
                        color=row['color'],
                        line=dict(width=2, color='white')
                    ),
                    text=row['tema'],
                    hovertemplate=(
                        f"<b>{row['tema']}</b><br>"
                        f"Gap Score: {row['gap_score']}<br>"
                        f"Actividad Competitiva: {row['actividad_competitiva']}<br>"
                        f"<extra></extra>"
                    ),
                    showlegend=False,
                    name=row['tema']  # Add name for debugging
                ))
                added_count += 1
            except Exception as e:
                logger.error(f"Error agregando fila {idx}: {e}")
        
        # Add layout
        fig_matriz.add_hline(y=80, line_dash="dash", line_color="rgba(0,0,0,0.2)")
        fig_matriz.add_vline(x=2, line_dash="dash", line_color="rgba(0,0,0,0.2)")
        
        st.plotly_chart(fig_matriz, use_container_width=True)
        
        # ========================================================================
        # GRÁFICO 2: ZONAS DE ACCIÓN (COLORACIÓN CONDICIONAL CON CUADRANTES)
        # ========================================================================
        st.header("📊 Gráfico 2: Zonas de Acción Estratégica")
        st.markdown("""
        **📊 Qué estamos viendo:**
        Una matriz dividida en 4 cuadrantes que indican el tipo de acción recomendada:
        
        | Zona | Características | Acción |
        |------|-----------------|--------|
        | 🟢 **VERDE (Arriba-Izquierda)** | Alta Urgencia + Baja Competencia | **INVERSA AGRESIVAMENTE** - Quick wins |
        | 🟡 **AMARILLO (Centro)** | Media Urgencia + Media Competencia | **PLANIFICAR** - Seguimiento cercano |
        | 🔴 **ROJO (Abajo-Derecha)** | Baja Urgencia + Alta Competencia | **MONITOREAR** - Diferenciación |
        | ⚪ **AZUL (Otras)** | Combinaciones mixtas | **EVALUAR** - Caso por caso |
        
        **🔍 Cómo se interpreta:**
        Cada zona corresponde a una estrategia diferente. Verde = Oportunidades que debes aprovechar YA.
        """)
        
        # Create heatmap-style visualization
        fig_zonas = go.Figure()
        
        # Add background rectangles for zones
        fig_zonas.add_shape(type="rect", x0=0.5, y0=80, x1=2, y1=100,
                           fillcolor="#2ecc71", opacity=0.2, line_width=0)
        fig_zonas.add_shape(type="rect", x0=1.5, y0=60, x1=3, y1=80,
                           fillcolor="#f39c12", opacity=0.2, line_width=0)
        fig_zonas.add_shape(type="rect", x0=2, y0=0, x1=3.5, y1=60,
                           fillcolor="#e74c3c", opacity=0.2, line_width=0)
        
        # Add zone labels
        fig_zonas.add_annotation(text="🟢 MÁXIMA PRIORIDAD", x=1.2, y=95, 
                                font=dict(size=12, color="green"), showarrow=False)
        fig_zonas.add_annotation(text="🟡 SEGUIMIENTO", x=2.3, y=75, 
                                font=dict(size=12, color="orange"), showarrow=False)
        fig_zonas.add_annotation(text="🔴 BAJA PRIORIDAD", x=2.8, y=25, 
                                font=dict(size=12, color="red"), showarrow=False)
        
        # Add data points
        added_count_g2 = 0
        for idx, row in df_opp.iterrows():
            try:
                if pd.isna(row['gap_score']) or pd.isna(row['actividad_numeric']):
                    continue
                
                # Add jitter to prevent overlapping markers with same coordinates
                jitter = np.random.normal(0, 0.08)
                x_jittered = row['actividad_numeric'] + jitter
                    
                fig_zonas.add_trace(go.Scatter(
                    x=[x_jittered],
                    y=[row['gap_score']],
                    mode='markers+text',
                    marker=dict(size=20, color=row['color'], line=dict(width=2, color='white')),
                    text=row['tema'].split()[0] if len(row['tema']) > 0 else "?",  # First word for compact label
                    textposition='top center',
                    hovertemplate=f"<b>{row['tema']}</b><br>Gap: {row['gap_score']}<br>Competencia: {row['actividad_competitiva']}<extra></extra>",
                    showlegend=False,
                    name=row['tema']
                ))
                added_count_g2 += 1
            except Exception as e:
                logger.error(f"Error en Gráfico 2, fila {idx}: {e}")
        
        fig_zonas.update_layout(
            title="Zonas de Acción Estratégica",
            xaxis_title="Barrera de Entrada",
            yaxis_title="Urgencia Estratégica",
            xaxis=dict(
                tickvals=[1, 2, 3],
                ticktext=['Baja', 'Media', 'Alta'],
                range=[0.5, 3.5]
            ),
            yaxis=dict(range=[0, 100]),
            height=500,
            hovermode='closest',
            plot_bgcolor='rgba(255, 255, 255, 0.9)',
            showlegend=False
        )
        
        st.plotly_chart(fig_zonas, use_container_width=True)
        
        # ========================================================================
        # GRÁFICO 3: DETALLE DE OPORTUNIDAD (CARDS INTERACTIVAS CON TOOLTIPS)
        # ========================================================================
        st.header("📊 Gráfico 3: Detalle de Oportunidad (Deep Dive)")
        st.markdown("""
        **📊 Qué estamos viendo:**
        Información detallada de cada oportunidad con contexto estratégico completo.
        
        **🔍 Cómo usarlo:**
        Selecciona una oportunidad para ver:
        - Descripción completa del gap/brecha
        - Justificación basada en datos
        - Recomendación de acción específica
        - Matriz de impacto
        """)
        
        # Selector for opportunity
        selected_opp = st.selectbox(
            "Selecciona una oportunidad para ver detalles:",
            df_opp['tema'].tolist(),
            key="opportunity_selector"
        )
        
        opp_data = df_opp[df_opp['tema'] == selected_opp].iloc[0]
        
        # Display cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gap Score (Urgencia)", opp_data['gap_score'])
        with col2:
            st.metric("Actividad Competitiva", opp_data['actividad_competitiva'])
        with col3:
            prioridad_map = {
                'Baja': '🔴 Baja',
                'Media': '🟡 Media',
                'Alta': '🟢 Alta'
            }
            actividad = opp_data['actividad_competitiva']
            st.metric("Nivel de Prioridad", 
                     "🟢 MÁXIMA" if opp_data['gap_score'] >= 80 and actividad == 'Baja' 
                     else "🟡 MEDIA" if opp_data['gap_score'] >= 70 and actividad == 'Media'
                     else "🔴 BAJA")
        
        # Display justification
        st.markdown("**Justificación (Evidencia de Oportunidad):**")
        with st.expander("📋 Leer completo", expanded=True):
            st.write(opp_data['justificacion'])
        
        # Display recommendation
        st.markdown("**Recomendación de Acción:**")
        with st.expander("💡 Plan de Acción", expanded=True):
            st.write(opp_data['recomendacion_accion'])
        
        # Show comparison table
        st.markdown("**Comparativa de Todas las Oportunidades:**")
        comparison_df = df_opp[['tema', 'gap_score', 'actividad_competitiva']].copy()
        comparison_df = comparison_df.sort_values('gap_score', ascending=False)
        
        # Add priority ranking
        comparison_df['🎯 Prioridad'] = comparison_df.apply(
            lambda row: '🟢 MÁXIMA' if row['gap_score'] >= 80 and row['actividad_competitiva'] == 'Baja'
                       else '� MEDIA' if row['gap_score'] >= 70 and row['actividad_competitiva'] == 'Media'
                       else '🔴 BAJA',
            axis=1
        )
        
        st.dataframe(
            comparison_df[['tema', 'gap_score', 'actividad_competitiva', '🎯 Prioridad']],
            use_container_width=True
        )
        
        # Summary statistics
        st.markdown("---")
        st.markdown("**📈 Resumen Estratégico:**")
        resumen = results.get("resumen_global", {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Oportunidades", len(df_opp))
        with col2:
            st.metric("Gap Score Promedio", f"{resumen.get('promedio_gap_score', 0):.0f}")
        with col3:
            opp_max_gap = df_opp.loc[df_opp['gap_score'].idxmax()]
            st.metric("Máxima Urgencia", f"{opp_max_gap['gap_score']}")
        with col4:
            st.metric("Oportunidades Críticas", resumen.get('oportunidades_criticas', 0))
    
    else:
        st.info("No opportunities data available")

