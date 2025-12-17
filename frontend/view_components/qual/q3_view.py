"""Q3 View: Topic Modeling Display - 3 Gráficos Según Especificación"""
import streamlit as st # type: ignore
import pandas as pd
import plotly.graph_objects as go  # type: ignore
from view_components.data_loader import load_q3_data as api_load_q3
from view_components.compat_loader import load_from_api_or_file

def load_q3_data():
    """Load Q3 data from API or local file (backward compatibility)."""
    return load_from_api_or_file(api_load_q3, "q3_topicos.json", "Q3")

def display_q3_topicos():
    st.title("💬 Q3: Análisis de Tópicos Principales")
    
    st.markdown("""
    ### ¿Qué es este análisis?
    El **Análisis de Tópicos** identifica los TEMAS principales sobre los que habla tu audiencia. No es sentimiento (positivo/negativo), sino el QUÉ: ¿Hablan de precio? ¿Calidad? ¿Sostenibilidad? ¿Servicio al cliente? Este análisis segmenta toda la conversación en clusters temáticos.
    
    ### ¿Por qué es relevante para tu negocio?
    Tu audiencia solo habla de lo que les importa (y a veces, de lo que va mal). Si el 60% de la conversación es sobre "Precio" pero tu estrategia se enfoca en "Innovación", estás hablando en otro idioma. Este análisis te permite:
    - **Alinear inversión:** Dónde va el dinero de marketing debe reflejar dónde está el ruido
    - **Identificar crisis temprano:** Si "Problema de Calidad" crece 40% MoM, es alerta roja
    - **Detectar oportunidades:** Si nadie habla de Sostenibilidad pero es una tendencia emergente, hay espacio
    - **Segmentar estrategia:** Diferentes tópicos requieren diferentes mensajes
    - **Medir influencia de cambios:** Después de un cambio de producto, ¿qué tópicos subieron/bajaron?
    
    ### El dato de fondo
    Este análisis usa Topic Modeling (LDA/BERTopic) para identificar clusters de palabras que frecuentemente aparecen juntas. No es buscar keywords, sino descubrir TEMAS emergentes que tu equipo podría no haber anticipado.
    """)
    
    data = load_q3_data()
    if data is None:
        return
    
    results = data.get("results", {})
    
    # ============================================================================
    # GRÁFICO 1: TÓPICOS GLOBALES (BURBUJAS)
    # ============================================================================
    st.header("📊 Gráfico 1: Tópicos Globales")
    
    # Try to get topics from analisis_agregado first (new format), then topicos_principales (fallback)
    analisis_agregado = results.get("analisis_agregado", [])
    topicos_principales = results.get("topicos_principales", [])
    
    topics_list = []
    
    # Parse analisis_agregado (new Q3 format: array of dicts with topic, frecuencia_relativa, sentimiento_promedio)
    if analisis_agregado and isinstance(analisis_agregado, list):
        for item in analisis_agregado:
            if isinstance(item, dict):
                topics_list.append({
                    'topico': item.get('topic', item.get('nombre', '')),
                    'frecuencia': item.get('frecuencia_relativa', item.get('frecuencia', 0)),
                    'sentimiento': item.get('sentimiento_promedio', item.get('sentimiento', 0))
                })
    
    # Fallback: Try topicos_principales
    if not topics_list and topicos_principales:
        if isinstance(topicos_principales, list):
            for i, topic in enumerate(topicos_principales):
                topics_list.append({
                    'topico': topic,
                    'frecuencia': (len(topicos_principales) - i) * 10,  # Default scoring
                    'sentimiento': 0
                })
        elif isinstance(topicos_principales, dict):
            for topic, data_item in topicos_principales.items():
                if isinstance(data_item, dict):
                    topics_list.append({
                        'topico': topic,
                        'frecuencia': data_item.get('frecuencia', 0),
                        'sentimiento': data_item.get('sentimiento', 0)
                    })
    
    if topics_list:
        df_topics = pd.DataFrame(topics_list)
        
        # Normalize column names
        if 'nombre' in df_topics.columns and 'topico' not in df_topics.columns:
            df_topics['topico'] = df_topics['nombre']
        elif 'topico' not in df_topics.columns:
            df_topics['topico'] = df_topics.index.astype(str)
        
        # Ensure numeric columns
        df_topics['frecuencia'] = pd.to_numeric(df_topics['frecuencia'], errors='coerce').fillna(0)
        df_topics['sentimiento'] = pd.to_numeric(df_topics['sentimiento'], errors='coerce').fillna(0)
        
        # Scale frecuencia for bubble visibility
        max_freq = df_topics['frecuencia'].max()
        if max_freq > 0:
            df_topics['size'] = (df_topics['frecuencia'] / max_freq) * 40 + 5  # Scale to 5-45
        else:
            df_topics['size'] = 15
        
        # Create bubble chart
        fig = go.Figure(data=[go.Scatter(
            x=df_topics['topico'],
            y=df_topics['sentimiento'],
            mode='markers',
            marker=dict(
                size=df_topics['size'],
                color=df_topics['sentimiento'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Sentimiento"),
                line=dict(width=1, color='white')
            ),
            text=df_topics['topico'],
            customdata=df_topics['frecuencia'],
            hovertemplate='<b>%{text}</b><br>Frecuencia: %{customdata:.2f}<br>Sentimiento: %{y:.2f}<extra></extra>'
        )])
        fig.update_layout(
            title="Distribución de Tópicos Globales (tamaño=frecuencia, color=sentimiento)",
            xaxis_title="Tópico",
            yaxis_title="Sentimiento Promedio",
            height=500,
            showlegend=False,
            hovermode='closest'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Descripción Gráfico 1
        st.markdown("""
        **📊 Qué estamos viendo:**
        Un gráfico de burbujas que muestra todos los tópicos identificados en los comentarios de tu audiencia. El tamaño de cada burbuja representa la frecuencia (cuántas veces se menciona ese tópico), y el color representa el sentimiento promedio asociado (rojo=negativo, verde=positivo, amarillo=neutral).

        **🔍 Cómo se midió:**
        Se aplicó modelado de tópicos (Topic Modeling) a todos los comentarios para identificar los temas principales. Para cada tópico, se contó su frecuencia de aparición y se calculó el sentimiento promedio de los comentarios que lo mencionan.

        **💡 Para qué se usa:**
        Este gráfico te permite:
        - Identificar rápidamente de qué habla tu audiencia (cuáles son los temas candentes).
        - Ver si los tópicos frecuentes tienen sentimiento positivo o negativo.
        - Detectar oportunidades: tópicos con alta frecuencia pero sentimiento negativo necesitan atención.
        - Priorizar temas para futuro contenido basado en interés de la audiencia.

        **📌 Tips para interpretarlo:**
        - Burbujas grandes en la derecha (verdes) son "golden topics": populares y bien recibidos.
        - Burbujas grandes en la izquierda (rojas) son "pain points": necesitan solución.
        - Burbujas pequeñas pero verdes son oportunidades emergentes de positividad.
        - Compara el tamaño relativo para priorizar temas.
        """)
    else:
        st.info("No topics data available for global analysis")
    
    # ============================================================================
    # GRÁFICO 2: TOP 5 POSTS POR TÓPICO SELECCIONADO
    # ============================================================================
    st.header("📊 Gráfico 2: Top 5 Publicaciones por Tópico")
    
    per_post = results.get("analisis_por_publicacion", [])
    
    if per_post and isinstance(per_post, list) and len(per_post) > 0:
        df_posts = pd.DataFrame(per_post)
        
        # Extract all available topics from all posts (more robust)
        available_topics = set()
        for post in per_post:
            if isinstance(post, dict):
                topicos = post.get("topicos", {})
                if isinstance(topicos, dict):
                    available_topics.update(topicos.keys())
        
        available_topics = sorted(list(available_topics))
        
        if available_topics:
            selected_topic = st.selectbox(
                "Selecciona un tópico para ver los Top 5 posts que lo mencionan:",
                available_topics,
                key="topic_selector"
            )
            
            # Extract topic concentration for all posts
            df_posts['topic_concentration'] = df_posts.apply(
                lambda row: (row.get('topicos', {}).get(selected_topic, 0) 
                            if isinstance(row.get('topicos'), dict) 
                            else 0),
                axis=1
            )
            
            # Get top 5 (filter by non-zero concentration)
            top_5_posts = df_posts[df_posts['topic_concentration'] > 0].nlargest(5, 'topic_concentration')
            
            if len(top_5_posts) == 0:
                st.warning(f"No posts encontrados con el tópico: {selected_topic}")
            else:
                cols_to_select = ['link', 'topic_concentration']
                if 'sentimiento' in df_posts.columns:
                    cols_to_select.append('sentimiento')
                
                display_data = top_5_posts[cols_to_select].copy()
                
                # Create horizontal bar chart
                fig = go.Figure([go.Bar(
                    y=display_data['link'].str[:50],
                    x=display_data['topic_concentration'],
                    orientation='h',
                    marker_color='mediumpurple'
                )])
                fig.update_layout(
                    title=f"Top 5 Publicaciones con Mayor Concentración: {selected_topic}",
                    xaxis_title=f"Concentración de {selected_topic}",
                    yaxis_title="Publicación (URL acortada)",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show detailed table
                st.write("**Detalle de Top 5:**")
                display_df = top_5_posts[['link', 'topic_concentration']].copy()
                display_df['link'] = display_df['link'].str[:60] + "..."
                display_df['topic_concentration'] = display_df['topic_concentration'].round(2)
                
                display_df = display_df.rename(columns={
                    'link': 'URL del Post',
                    'topic_concentration': f'Concentración de "{selected_topic}" (%)'
                })
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Descripción Gráfico 2
            st.markdown(f"""
            **📊 Qué estamos viendo:**
            Un ranking de las 5 publicaciones que tienen la mayor concentración del tópico "{selected_topic}". Cada barra muestra qué porcentaje de los comentarios de esa publicación están dedicados a este tópico específico.

            **🔍 Cómo se midió:**
            Para cada publicación, se identificaron todos los comentarios que mencionan el tópico "{selected_topic}" y se calculó qué porcentaje representan del total de comentarios de esa publicación.

            **💡 Para qué se usa:**
            Este ranking te permite:
            - Identificar qué contenido atrae la conversación sobre "{selected_topic}".
            - Replicar patrones de éxito: si quieres más conversación sobre este tópico, analiza qué tienen en común estos 5 posts.
            - Validar si el tema que esperabas tratar en una publicación fue realmente lo que discutió la audiencia.
            - Detectar si un tópico se dispersa mucho o se concentra en pocos posts (concentración = consistencia de mensaje).

            **📌 Tips para interpretarlo:**
            - Los posts con barras largas "capturaron" la conversación sobre este tópico.
            - Si el top 5 tiene concentraciones similares, indica que el tópico es "sticky" (pegajoso).
            - Si una publicación tiene concentración muy alta en un tópico, es "especialista" en ese tema.
            - Compara diferentes tópicos para identificar cuáles generan conversación concentrada vs dispersa.
            """)
        else:
            st.info("No topic data available per post")
    else:
        st.info("No per-publication data available")
    
    # ============================================================================
    # GRÁFICO 3: TÓPICOS POR PUBLICACIÓN SELECCIONADA
    # ============================================================================
    st.header("📊 Gráfico 3: Tópicos de Una Publicación Específica")
    
    if per_post and isinstance(per_post, list) and len(per_post) > 0:
        df_posts = pd.DataFrame(per_post)
        
        # Ensure 'link' column exists
        if 'link' not in df_posts.columns:
            df_posts['link'] = [f"Post {i}" for i in range(len(df_posts))]
        
        selected_url = st.selectbox(
            "Selecciona una publicación para ver su distribución de tópicos:",
            df_posts["link"].tolist(),
            key="post_topic_selector"
        )
        selected_post = df_posts[df_posts["link"] == selected_url].iloc[0]
        
        # Extract topics for this post
        topics_dict = selected_post.get("topicos", {})
        
        if topics_dict and isinstance(topics_dict, dict) and len(topics_dict) > 0:
            # Prepare data
            topics_names = list(topics_dict.keys())
            topics_values = [topics_dict[t] for t in topics_names]
            
            # Create bubble chart for post-specific topics
            fig = go.Figure(data=[go.Scatter(
                x=topics_names,
                y=[1] * len(topics_names),
                mode='markers',
                marker=dict(
                    size=[max(v * 5, 10) for v in topics_values],
                    color=topics_values,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Concentración"),
                    line=dict(width=1, color='white')
                ),
                text=topics_names,
                customdata=topics_values,
                hovertemplate='<b>%{text}</b><br>Concentración: %{customdata:.2f}<extra></extra>'
            )])
            fig.update_layout(
                title=f"Tópicos en: {selected_url[:60]}...",
                xaxis_title="Tópico",
                yaxis_visible=False,
                height=400,
                showlegend=False,
                hovermode='closest'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show summary
            st.write("**Resumen de Tópicos:**")
            summary_df = pd.DataFrame({
                'Tópico': topics_names,
                'Concentración (%)': topics_values
            }).sort_values('Concentración (%)', ascending=False)
            st.dataframe(summary_df, use_container_width=True)
            
            # Descripción Gráfico 3
            st.markdown(f"""
            **📊 Qué estamos viendo:**
            Un gráfico de burbujas que muestra todos los tópicos identificados en los comentarios de esta publicación específica. El tamaño y color de cada burbuja indican la concentración (qué porcentaje de los comentarios hablan de ese tópico).

            **🔍 Cómo se midió:**
            Se extrajeron todos los comentarios asociados a esta publicación y se aplicó modelado de tópicos para identificar los temas presentes. Se calculó qué porcentaje de los comentarios corresponden a cada tópico.

            **💡 Para qué se usa:**
            Este análisis granular por publicación te permite:
            - Validar si los comentarios trataron el tema que esperabas: ¿Publicaste sobre "Precios" pero la audiencia habló de "Envío"?
            - Detectar "ruido temático": ¿La conversación fue dispersa (muchos tópicos pequeños) o concentrada (1-2 tópicos dominantes)?
            - Evaluar la claridad del mensaje: mensajes claros generan conversaciones concentradas en el tópico deseado.
            - Identificar tópicos emergentes no esperados: ¿Surgió una conversación sobre algo que no mencionaste?

            **📌 Tips para interpretarlo:**
            - Burbujas grandes = tópicos dominantes en la conversación de este post.
            - Un perfil "desequilibrado" (1-2 burbujas grandes) indica mensaje claro y consistente.
            - Un perfil "equilibrado" (muchas burbujas similares) indica conversación dispersa o ambigüedad en el mensaje.
            - Compara con otros posts de tema similar para ver variaciones en distribución tópica.
            """)
        else:
            st.info("No topics available for this publication")
    else:
        st.info("No per-publication data available")
