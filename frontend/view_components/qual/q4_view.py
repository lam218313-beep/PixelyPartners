"""Q4 View: Narrative Framing Analysis - 4 Gráficos Según Especificación"""
import streamlit as st # type: ignore
import pandas as pd
import plotly.graph_objects as go  # type: ignore
from view_components.data_loader import load_q4_data as api_load_q4
from view_components.compat_loader import load_from_api_or_file

def load_q4_data():
    """Load Q4 data from API or local file (backward compatibility)."""
    return load_from_api_or_file(api_load_q4, "q4_marcos_narrativos.json", "Q4")

# Mapeo de marcos a colores
MARCO_COLORS = {
    'Positivo': '#2ecc71',      # Verde
    'Negativo': '#e74c3c',      # Rojo
    'Aspiracional': '#3498db',  # Azul
    'Positiva': '#2ecc71',
    'Negativa': '#e74c3c',
}

def get_marco_color(marco):
    """Retorna color CSS para un marco dado."""
    if marco in MARCO_COLORS:
        return MARCO_COLORS[marco]
    # Mapeo automático por palabra clave
    marco_lower = str(marco).lower()
    if 'positiv' in marco_lower:
        return '#2ecc71'
    elif 'negativ' in marco_lower:
        return '#e74c3c'
    elif 'aspir' in marco_lower:
        return '#3498db'
    else:
        return '#95a5a6'

def display_q4_marcos_narrativos():
    st.title("📜 Q4: Análisis de Marcos Narrativos (Entman)")
    
    st.markdown("""
    ### ¿Qué es este análisis?
    El **Análisis de Marcos Narrativos** basado en Entman identifica **CÓMO se cuenta la historia** sobre tu marca: ¿De forma positiva (oportunidad, progreso)? ¿Negativa (crisis, problema)? ¿Aspiracional (futuro deseado)? Los marcos NO cambian los HECHOS, pero cambian cómo se INTERPRETAN.
    
    ### ¿Por qué es relevante para tu negocio?
    Dos comentarios pueden describir el MISMO HECHO pero con marcos diferentes:
    - "Tu producto es caro" (Marco Negativo = Precio es un problema)
    - "Tu producto es premium" (Marco Positivo = Precio refleja calidad)
    
    Este análisis te permite:
    - **Detectar narrativas dominantes:** ¿Cómo cuenta la gente tu historia?
    - **Reframing estratégico:** Si tu marca es vista como "problema", necesitas cambiar cómo se cuenta
    - **Anticipar crisis:** Los marcos negativos son predictores de PR crisis
    - **Aprovechar oportunidades:** Los marcos aspiracionales son donde viven los brand advocates
    - **Comunicar efectivamente:** Tu mensaje debe ALINEAR con el marco que quieres dominar
    
    ### El dato de fondo
    Este es el análisis que usa Hollywood para editar películas, que usan políticos para ganar elecciones, y que líderes de marca usan para controlar narrativas. Un marco positivo hace que los clientes CREAN en tu valor; un marco negativo los hace sentir estafados por el mismo producto.
    """)
    
    data = load_q4_data()
    if data is None:
        return
    
    results = data.get("results", {})
    
    # ============================================================================
    # GRÁFICO 1: DISTRIBUCIÓN GLOBAL DE MARCOS NARRATIVOS
    # ============================================================================
    st.header("📊 Gráfico 1: Distribución Global de Marcos Narrativos")
    
    marcos_agregado = results.get("analisis_agregado", {}) or results.get("resumen_marcos", {})
    
    if marcos_agregado:
        if isinstance(marcos_agregado, dict):
            marcos_list = list(marcos_agregado.keys())
            marcos_valores = list(marcos_agregado.values())
        elif isinstance(marcos_agregado, list):
            marcos_list = [m.get('marco', 'Unknown') for m in marcos_agregado]
            marcos_valores = [m.get('frecuencia', 0) for m in marcos_agregado]
        else:
            marcos_list = []
            marcos_valores = []
        
        if marcos_list:
            # Create stacked bar or pie chart
            colors = [get_marco_color(m) for m in marcos_list]
            
            fig = go.Figure([go.Bar(
                x=marcos_list,
                y=marcos_valores,
                marker_color=colors
            )])
            fig.update_layout(
                title="Distribución Global de Marcos Narrativos",
                xaxis_title="Marco Narrativo",
                yaxis_title="Distribución (%)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **📊 Qué estamos viendo:**
            La distribución global de los tres marcos narrativos principales: Positivo (afirmaciones, satisfacción), Negativo (quejas, reclamos) y Aspiracional (sugerencias de mejora, deseos de futuro). Esto muestra el "tono narrativo" dominante en toda tu audiencia.

            **🔍 Cómo se midió:**
            Se analizaron todos los comentarios usando la Teoría del Framing de Entman. Cada comentario fue clasificado en uno de los tres marcos narrativos según su intención dominante, y luego se calculó el porcentaje global de cada marco.

            **💡 Para qué se usa:**
            - Entender si tu audiencia es generalmente positiva, crítica o aspiracional.
            - Identificar oportunidades: audiencia aspiracional busca mejora (engagement alto).
            - Detectar riesgos: alto porcentaje negativo requiere estrategia de mitigación.
            - Alinear tu contenido futuro con el marco dominante.

            **� Tips para interpretarlo:**
            - 60%+ Positivo = marca bien recibida, mantén consistencia.
            - 20%+ Negativo = pain points existentes, necesitan solución.
            - 30%+ Aspiracional = audiencia activa, oportunidad de co-creación.
            - Balance (todos ~33%) = audiencia reflexiva y crítica.
            """)
    else:
        st.info("No global narrative framing data available")
    
    # ============================================================================
    # GRÁFICO 2: TOP 5 POSTS POR MARCO NARRATIVO SELECCIONADO
    # ============================================================================
    st.header("📊 Gráfico 2: Top 5 Publicaciones por Marco Narrativo")
    
    per_post = results.get("analisis_por_publicacion", [])
    
    if per_post:
        df_posts = pd.DataFrame(per_post)
        
        # Extract available marcos from first post - try multiple column names
        first_post_dist = {}
        if 'marcos_narrativos' in df_posts.columns:
            first_post_dist = df_posts.iloc[0].get("marcos_narrativos", {}) if isinstance(df_posts.iloc[0].get("marcos_narrativos"), dict) else {}
        elif 'distribucion_marcos' in df_posts.columns:
            first_post_dist = df_posts.iloc[0].get("distribucion_marcos", {}) if isinstance(df_posts.iloc[0].get("distribucion_marcos"), dict) else {}
        
        available_marcos = list(first_post_dist.keys()) if first_post_dist else []
        
        if not available_marcos:
            # Try alternative structures
            for col in ['marcos', 'narrativos', 'framing']:
                if col in df_posts.columns:
                    first_val = df_posts.iloc[0][col]
                    if isinstance(first_val, dict):
                        available_marcos = list(first_val.keys())
                        break
        
        if available_marcos:
            selected_marco = st.selectbox(
                "Selecciona un marco narrativo para ver los Top 5 posts que lo generaron:",
                available_marcos,
                key="marco_selector"
            )
            
            # Extract marco concentration for all posts - handle both column names
            def get_marco_value(row):
                if isinstance(row.get('marcos_narrativos'), dict):
                    return row.get('marcos_narrativos', {}).get(selected_marco, 0)
                elif isinstance(row.get('distribucion_marcos'), dict):
                    return row.get('distribucion_marcos', {}).get(selected_marco, 0)
                return 0
            
            df_posts['marco_concentration'] = df_posts.apply(get_marco_value, axis=1)
            
            # Get top 5
            top_5_posts = df_posts.nlargest(5, 'marco_concentration')[['link', 'marco_concentration']]
            
            # Create horizontal bar chart with marco color
            marco_color = get_marco_color(selected_marco)
            fig = go.Figure([go.Bar(
                y=top_5_posts['link'].str[:50],
                x=top_5_posts['marco_concentration'],
                orientation='h',
                marker_color=marco_color
            )])
            fig.update_layout(
                title=f"Top 5 Publicaciones con Mayor Concentración: {selected_marco}",
                xaxis_title=f"Concentración de {selected_marco} (%)",
                yaxis_title="Publicación (URL acortada)",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            st.write("**Detalle de Top 5:**")
            display_df = top_5_posts.copy()
            display_df['link'] = display_df['link'].str[:60] + "..."
            display_df = display_df.rename(columns={
                'link': 'URL',
                'marco_concentration': f'{selected_marco} (%)'
            })
            st.dataframe(display_df, use_container_width=True)
            
            st.markdown(f"""
            **📊 Qué estamos viendo:**
            Un ranking de las 5 publicaciones que generaron la mayor proporción del marco narrativo "{selected_marco}". Esto te muestra qué contenido específico "activó" este tipo de narrativa en tu audiencia.

            **🔍 Cómo se midió:**
            Para cada publicación, se analizó todos sus comentarios y se calculó qué porcentaje corresponden al marco "{selected_marco}".

            **💡 Para qué se usa:**
            - Si buscas narrativa Positiva: replica los elementos de estos top 5 posts.
            - Si buscas reducir narrativa Negativa: analiza qué tienen en común para evitarlo.
            - Si buscas estimular Aspiracional: usa estos posts como modelo para futuro contenido.

            **📌 Tips para interpretarlo:**
            - Los posts con concentración alta son "activadores" de ese marco.
            - Si un marco está disperso (sin posts con alta concentración), es un patrón consistente general.
            - Si está concentrado en pocos posts, esos posts específicos causaron esa narrativa.
            """)
        else:
            st.info("No marco distribution data available per post")
    else:
        st.info("No per-publication data available")
    
    # ============================================================================
    # GRÁFICO 3: ANÁLISIS NARRATIVO POR PUBLICACIÓN + EVIDENCIA TEXTUAL
    # ============================================================================
    st.header("📊 Gráfico 3: Análisis Narrativo por Publicación (con Evidencia)")
    
    if per_post:
        df_posts = pd.DataFrame(per_post)
        selected_url = st.selectbox(
            "Selecciona una publicación para ver su perfil narrativo y ejemplos:",
            df_posts["link"].tolist(),
            key="post_marco_selector"
        )
        selected_post = df_posts[df_posts["link"] == selected_url].iloc[0]
        
        # Extract marcos distribution - try both column names
        marcos_dist = selected_post.get("marcos_narrativos", {})
        if not marcos_dist or not isinstance(marcos_dist, dict):
            marcos_dist = selected_post.get("distribucion_marcos", {})
        if not marcos_dist or not isinstance(marcos_dist, dict):
            marcos_dist = selected_post.get('marcos', {})
        
        if marcos_dist and isinstance(marcos_dist, dict):
            marcos_names = list(marcos_dist.keys())
            marcos_values = list(marcos_dist.values())
            colors = [get_marco_color(m) for m in marcos_names]
            
            # Create bar chart
            fig = go.Figure([go.Bar(
                x=marcos_names,
                y=marcos_values,
                marker_color=colors
            )])
            fig.update_layout(
                title=f"Distribución de Marcos: {selected_url[:60]}...",
                xaxis_title="Marco Narrativo",
                yaxis_title="Distribución (%)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"""
            **📊 Qué estamos viendo:**
            La distribución de los tres marcos narrativos en los comentarios de esta publicación específica. Muestra qué tipo de narrativas generó tu contenido.

            **🔍 Cómo se midió:**
            Se extrajeron todos los comentarios de esta publicación y se clasificaron según su marco narrativo.

            **💡 Para qué se usa:**
            - Validar si generaste la narrativa que esperabas.
            - Ajustar el tono de futuras publicaciones basándote en lo que generaste.

            **📌 Tips para interpretarlo:**
            - Un marco dominante (>60%) indica mensaje claro.
            - Un perfil equilibrado indica audiencia reflexiva o contenido ambiguo.
            """)
            
            # Show representative examples (if available)
            st.markdown("---")
            st.markdown("#### 💬 Ejemplos Narrativos (Evidencia Textual)")
            
            ejemplos = selected_post.get("ejemplos_narrativos", {})
            if ejemplos and isinstance(ejemplos, dict):
                for marco, ejemplo_text in ejemplos.items():
                    if ejemplo_text:
                        with st.expander(f"Ejemplo {marco}"):
                            st.write(f"**{ejemplo_text}**")
            elif ejemplos and isinstance(ejemplos, list):
                for i, ejemplo_text in enumerate(ejemplos, 1):
                    if ejemplo_text:
                        with st.expander(f"Ejemplo {i}"):
                            st.write(f"**{ejemplo_text}**")
            else:
                st.info("No narrative examples available for this publication")
        else:
            st.info("No marco distribution available for this publication")
    else:
        st.info("No per-publication data available")
    
    # ============================================================================
    # GRÁFICO 4: EVOLUCIÓN TEMPORAL DEL DISCURSO (OPCIONAL)
    # ============================================================================
    st.header("📊 Gráfico 4: Evolución Temporal del Discurso")
    
    temporal_data = results.get("evolucion_temporal", []) or results.get("analisis_temporal", []) or results.get("evolucion_marcos", [])
    
    if temporal_data and isinstance(temporal_data, list) and len(temporal_data) > 0:
        # Try to create temporal visualization
        try:
            # Extract marcos data from each period
            periods = []
            marcos_data = {}
            
            for item in temporal_data:
                if isinstance(item, dict):
                    period = item.get("semana") or item.get("periodo") or item.get("fecha")
                    period_str = f"Semana {period}" if isinstance(period, int) else str(period)
                    periods.append(period_str)
                    
                    marcos_dist = item.get("marcos_distribucion", {})
                    if isinstance(marcos_dist, dict):
                        for marco, value in marcos_dist.items():
                            if marco not in marcos_data:
                                marcos_data[marco] = []
                            marcos_data[marco].append(value)
            
            if periods and marcos_data:
                fig = go.Figure()
                for marco, values in marcos_data.items():
                    fig.add_trace(go.Scatter(
                        x=periods,
                        y=values,
                        mode='lines+markers',
                        name=marco,
                        line=dict(color=get_marco_color(marco), width=2)
                    ))
                
                fig.update_layout(
                    title="Evolución Temporal de Marcos Narrativos",
                    xaxis_title="Tiempo",
                    yaxis_title="Concentración (%)",
                    hovermode='x unified',
                    height=450
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                **📊 Qué estamos viendo:**
                La evolución de cada marco narrativo a lo largo del tiempo. Permite identificar si la audiencia está siendo más positiva, más negativa, o más aspiracional con el tiempo.

                **🔍 Cómo se midió:**
                Se agruparon los comentarios por período (día, semana, etc.) y se calculó la distribución de marcos para cada período.

                **💡 Para qué se usa:**
                - Correlacionar cambios narrativos con eventos de marketing específicos.
                - Detectar si una crisis (aumento de negatividad) está siendo resuelta.
                - Validar si tu estrategia de contenido está cambiando la narrativa.

                **📌 Tips para interpretarlo:**
                - Línea positiva subiendo = estrategia funcionando.
                - Línea negativa subiendo = crisis en curso.
                - Línea aspiracional subiendo = audiencia comprometida y optimista.
                """)
            else:
                st.info("Temporal data available but structure not compatible")
        except Exception as e:
            st.info(f"Temporal analysis data available but unable to visualize: {str(e)}")
    else:
        st.info("No temporal evolution data available (optional feature)")
