"""Q9 View: Recommendations Analysis with Strategic Prioritization"""
import streamlit as st # type: ignore
import pandas as pd
import plotly.graph_objects as go  # type: ignore
from view_components.data_loader import load_q9_data as api_load_q9
from view_components.compat_loader import load_from_api_or_file

def load_q9_data():
    """Load Q9 data from API or local file (backward compatibility)."""
    return load_from_api_or_file(api_load_q9, "q9_recomendaciones.json", "Q9")

def get_area_color(area):
    """Map area estratégica to color"""
    color_map = {
        'Comunicación y Transparencia': '#3498db',
        'Contenido y Educación': '#2ecc71',
        'Influenciadores y Advocacy': '#f39c12',
        'Engagement y Comunidad': '#e74c3c',
        'Tono y Narrativa': '#9b59b6',
        'Innovación de Producto': '#1abc9c',
        'Oportunidades de Mercado': '#e67e22'
    }
    return color_map.get(area, '#34495e')

def get_urgencia_color(urgencia):
    """Map urgencia to color"""
    color_map = {
        'CRÍTICA': '#e74c3c',
        'ALTA': '#f39c12',
        'MEDIA-ALTA': '#f1c40f',
        'MEDIA': '#2ecc71',
        'BAJA': '#95a5a6'
    }
    return color_map.get(urgencia, '#34495e')

def display_q9_recomendaciones():
    st.title("📝 Q9: Recomendaciones Estratégicas Priorizadas")
    
    st.markdown("""
    ### ¿Qué es este análisis?
    El **Análisis de Recomendaciones** traduce TODO lo anterior (Q1-Q8) en ACCIONES CONCRETAS. No son sugerencias genéricas, sino **recomendaciones priorizadas** con:
    - Score de impacto esperado (0-100)
    - Urgencia (crítica, alta, media, baja)
    - Frameworks que las justifican (traceable a Q1-Q8)
    - Acciones concretas paso-a-paso
    
    ### ¿Por qué es relevante para tu negocio?
    Insights sin acción son solo entretenimiento. Este análisis cierra el loop: aquí vives QUÉ HACER y CUÁNDO. Te permite:
    - **Priorización objetiva:** No debates infinitos "qué es más importante", datos dirimen
    - **Justificación ejecutiva:** "Hacer X porque Q6 muestra oportunidad en [específico]" beats "siento que..."
    - **Ejecución alineada:** Tu equipo sabe qué hacer, por qué hacerlo, y el impacto esperado
    - **ROI tracking:** Cada recomendación tiene un score_impacto esperado, puedes medir si se logró
    - **Roadmap trimestral:** Las recomendaciones urgentes = tu sprint roadmap
    - **Comunicación interna:** Convence a stakeholders mostrando la cadena de evidence Q1→Q9
    
    ### El dato de fondo
    Las 5-7 recomendaciones principales se rankean por urgencia (CRÍTICA/ALTA/MEDIA/BAJA) y cada una está vinculada a 2-3 frameworks previos que la justifican. Si dices "hacer X", el documento dice "por eso": porque Q6 mostró demanda insatisfecha, Q8 mostró oportunidad, Q5 mostró quién lo quiere más.
    """)
    
    data = load_q9_data()
    if data is None:
        return
    
    results = data.get("results", {})
    recs_list = results.get("lista_recomendaciones", [])
    resumen = results.get("resumen_global", {})
    
    if not recs_list:
        st.info("No recommendations available")
        return
    
    df_recs = pd.DataFrame(recs_list)
    
    # ========================================================================
    # GRÁFICO 1: MATRIZ DE PRIORIZACIÓN ESTRATÉGICA (Scatter/Bubbles)
    # ========================================================================
    st.header("📊 Gráfico 1: Matriz de Priorización Estratégica")
    st.markdown("""
    **📊 Qué estamos viendo:**
    Una matriz bidimensional donde:
    - **Eje X (Horizontal):** Área Estratégica (7 dimensiones: Comunicación, Contenido, Influenciadores, etc.)
    - **Eje Y (Vertical):** Score de Impacto (0-100, más alto = mayor impacto potencial)
    - **Tamaño de Burbuja:** Urgencia (burbujas grandes = CRÍTICA/ALTA)
    - **Color:** Área estratégica para fácil identificación
    
    **🔍 Cómo se midió:**
    - Score de Impacto: Combinación de validación en múltiples Q + potencial de ROI
    - Urgencia: Basada en cambios detectados en Q8 (anomalías temporales)
    - Área: Clasificación por dimensión estratégica de marketing
    
    **💡 Para qué se usa:**
    Identificar QUÉ hacer y en QUÉ ORDEN.
    - Cuadrante superior derecho = DO FIRST (Alto impacto, urgente)
    - Cuadrante inferior = Roadmap futuro
    
    **📌 Tips:**
    - Prioriza por impacto × urgencia (arriba a la derecha)
    - Lee el nombre de la recomendación al pasar cursor
    - Agrupa por área para ejecutar conjuntamente
    """)
    
    # Create scatter plot with bubble sizes based on urgencia
    urgencia_order = {'CRÍTICA': 4, 'ALTA': 3, 'MEDIA-ALTA': 2.5, 'MEDIA': 2, 'BAJA': 1}
    df_recs['urgencia_size'] = df_recs['urgencia'].map(urgencia_order) * 20
    
    # Map area to numeric x-axis
    areas_unique = df_recs['area_estrategica'].unique()
    area_to_x = {area: i for i, area in enumerate(sorted(areas_unique))}
    df_recs['x_pos'] = df_recs['area_estrategica'].map(area_to_x)
    
    fig_matrix = go.Figure()
    
    for idx, row in df_recs.iterrows():
        fig_matrix.add_trace(
            go.Scatter(
                x=[row['x_pos']],
                y=[row['score_impacto']],
                mode='markers',
                marker=dict(
                    size=row['urgencia_size'],
                    color=get_area_color(row['area_estrategica']),
                    line=dict(width=2, color=get_urgencia_color(row['urgencia'])),
                    opacity=0.7
                ),
                text=f"<b>{row['recomendacion']}</b><br>Impacto: {row['score_impacto']}<br>Urgencia: {row['urgencia']}<br>Área: {row['area_estrategica']}",
                hovertemplate='%{text}<extra></extra>',
                showlegend=False
            )
        )
    
    fig_matrix.update_xaxes(
        ticktext=sorted(areas_unique),
        tickvals=list(range(len(areas_unique))),
        title_text="Área Estratégica",
        showgrid=True
    )
    fig_matrix.update_yaxes(
        title_text="Score de Impacto (0-100)",
        showgrid=True,
        zeroline=False
    )
    
    fig_matrix.update_layout(
        title="Matriz de Priorización: Área × Impacto × Urgencia",
        height=500,
        hovermode='closest',
        xaxis={'showticklabels': True, 'tickangle': -45}
    )
    
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    # ========================================================================
    # GRÁFICO 2: PANEL DE EVIDENCIA (Trazabilidad)
    # ========================================================================
    st.header("📊 Gráfico 2: Panel de Evidencia & Trazabilidad")
    st.markdown("""
    **📊 Qué estamos viendo:**
    Detalle de cada recomendación con:
    - Descripción de la acción específica
    - Framework (Q) que la justifica (trazabilidad)
    - Acciones concretas y próximos pasos
    
    **🔍 Cómo se midió:**
    Cada recomendación está vinculada a 1 o múltiples análisis (Q1-Q8):
    - Q1: Emociones → Detecta sentimientos clave
    - Q3: Tópicos → Identifica temas dominantes
    - Q4: Marcos → Define narrativas
    - Q5: Influenciadores → Valida voces clave
    - Q7: Sentimiento detallado → Detecta ambivalencias
    - Q8: Temporal → Identifica anomalías y urgencias
    - Q6: Oportunidades → Sugiere gaps a llenar
    
    **💡 Para qué se usa:**
    Responder "¿por qué?" a cada recomendación.
    La trazabilidad permite validar y reproducir el razonamiento.
    
    **📌 Tips:**
    - Lee el Marco de Referencia para entender la evidencia
    - Haz clic en las Acciones Concretas para planificar sprints
    - Agrupa recomendaciones con mismo Q para ejecutar coordinadamente
    """)
    
    # Display each recommendation as a detail card
    for idx, row in df_recs.sort_values('score_impacto', ascending=False).iterrows():
        
        # Color badge for urgencia
        urgencia_color = get_urgencia_color(row['urgencia'])
        
        with st.container():
            col1, col2 = st.columns([1, 5])
            
            with col1:
                st.markdown(
                    f"""
                    <div style='
                        background-color:{urgencia_color};
                        color:white;
                        padding:20px;
                        border-radius:8px;
                        text-align:center;
                        font-size:14px;
                        font-weight:bold;
                        min-height:100px;
                        display:flex;
                        flex-direction:column;
                        justify-content:center;
                    '>
                    {row['urgencia']}<br>
                    Score: {row['score_impacto']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(f"""
                #### #{row['id']}: {row['recomendacion']}
                
                **📌 Área:** {row['area_estrategica']}
                
                **📝 Descripción:**
                {row['descripcion']}
                
                **🔗 Frameworks de Referencia:** 
                {' | '.join([f'**Q{q}**' for q in row['justificacion_framework']])}
                
                **✅ Acciones Concretas:**
                """)
                
                for accion in row['acciones_concretas']:
                    st.markdown(f"- {accion}")
        
        st.divider()
    
    # ========================================================================
    # RESUMEN EJECUTIVO
    # ========================================================================
    st.markdown("---")
    st.markdown("**📈 Resumen Ejecutivo Global:**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Recomendaciones",
            resumen.get('total_recomendaciones', 0)
        )
    
    with col2:
        st.metric(
            "Recomendaciones CRÍTICAS",
            resumen.get('recomendaciones_criticas', 0),
            delta="Atender ahora"
        )
    
    with col3:
        st.metric(
            "Recomendaciones ALTAS",
            resumen.get('recomendaciones_altas', 0),
            delta="Próximas 2 semanas"
        )
    
    with col4:
        st.metric(
            "Score Impacto Promedio",
            f"{resumen.get('score_impacto_promedio', 0):.0f}/100"
        )
    
    # Urgencia distribution
    st.markdown("**Distribución de Urgencias:**")
    urgencia_dist = resumen.get('urgencia_distribucion', {})
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🔴 CRÍTICA", urgencia_dist.get('CRÍTICA', 0))
    with col2:
        st.metric("🟠 ALTA", urgencia_dist.get('ALTA', 0))
    with col3:
        st.metric("🟡 MEDIA-ALTA", urgencia_dist.get('MEDIA-ALTA', 0))
    with col4:
        st.metric("🟢 MEDIA", urgencia_dist.get('MEDIA', 0))
    with col5:
        st.metric("⚪ BAJA", urgencia_dist.get('BAJA', 0))
    
    # Recommendations by area
    st.markdown("**Recomendaciones por Área Estratégica:**")
    area_dist = df_recs['area_estrategica'].value_counts()
    
    fig_areas = go.Figure([go.Bar(
        x=area_dist.index,
        y=area_dist.values,
        marker_color='#3498db',
        text=area_dist.values,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y} recomendaciones<extra></extra>'
    )])
    
    fig_areas.update_layout(
        title="Distribución de Recomendaciones por Área",
        xaxis_title="Área Estratégica",
        yaxis_title="Cantidad",
        height=400,
        showlegend=False,
        xaxis={'showticklabels': True, 'tickangle': -45}
    )
    
    st.plotly_chart(fig_areas, use_container_width=True)
    
    # Strategic roadmap
    st.markdown("---")
    st.markdown("**🗓️ Roadmap Sugerido (por Urgencia):**")
    
    st.info("""
    **AHORA (Próximos 3 días):** Recomendaciones CRÍTICAS
    - Revisar con liderazgo
    - Asignar propietarios
    - Iniciar acciones inmediatas
    
    **PRÓXIMA SEMANA:** Recomendaciones ALTAS
    - Planificar sprints
    - Alinear recursos
    - Comunicar a equipos
    
    **MES ACTUAL:** Recomendaciones MEDIA-ALTA y MEDIA
    - Incluir en roadmap trimestral
    - Validar capacidad de recursos
    - Scheduling en calendario
    
    **ROADMAP FUTURO:** Recomendaciones BAJA
    - Evaluar mensualmente
    - Incluir si hay cambios en prioridades
    - Preparar para próximo ciclo
    """)
