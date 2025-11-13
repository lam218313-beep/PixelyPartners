"""Q2 View: Personality Analysis Display - 3 Gráficos Según Especificación Aaker"""
import streamlit as st # type: ignore
import pandas as pd
import json
import os
import plotly.graph_objects as go  # type: ignore
from .._outputs import get_outputs_dir

def display_q2_personalidad():
    st.title("👤 Q2: Análisis de Personalidad de Marca (Aaker)")
    
    st.markdown("""
    ### ¿Qué es este análisis?
    El **Análisis de Personalidad de Marca** basado en el Framework Aaker clasifica cómo es PERCIBIDA tu marca en cinco dimensiones: Sinceridad (confiable, honesto), Emoción (energético, apasionado), Competencia (líder, confiable), Sofisticación (elegante, refinado) y Rudeza (resistente, aventurero). Es como un "psicoanálisis de marca" basado en cómo la ven tus clientes.
    
    ### ¿Por qué es relevante para tu negocio?
    Tu marca tiene una personalidad percibida, te des cuenta o no. El problema es que **esa personalidad puede ser diferente a la que QUIERES proyectar**. Este análisis te permite:
    - **Validar consistencia:** ¿Se ve tu marca como la diseñaste?
    - **Identificar brechas:** Si quieres ser "Sofisticación" pero te ven como "Rudeza", hay un gap
    - **Guiar contenido:** Cada tipo de contenido refuerza ciertas dimensiones
    - **Diferenciarse:** Personalidades claras se recuerdan; las borrosas se olvidan
    - **Atraer talento:** Marcas con personalidad fuerte atraen empleados más comprometidos
    
    ### El dato de fondo
    Las 5 dimensiones de Aaker se basan en investigación exhaustiva con miles de marcas. La mayoría de marcas exitosas tienen una dimensión FUERTE (no tratan de ser todo para todos). Apple = Sofisticación. Nike = Competencia. Esto es lo que verás aquí.
    """)
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, "q2_personalidad.json")
    if not os.path.exists(json_path):
        st.error(f"Q2 file not found at {json_path}")
        return
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = data.get("results", {})
    
    # ============================================================================
    # GRÁFICO 1: PERFIL GLOBAL DE PERSONALIDAD DE MARCA
    # ============================================================================
    st.header("📊 Gráfico 1: Perfil Global de Personalidad")
    global_personality = results.get("resumen_global_personalidad", {})
    if global_personality:
        # Create bar chart for personality dimensions
        dims = {k: v for k, v in global_personality.items() if isinstance(v, (int, float))}
        if dims:
            fig = go.Figure([go.Bar(x=list(dims.keys()), y=list(dims.values()), marker_color='steelblue')])
            fig.update_layout(
                title="Distribución Global de Rasgos Aaker",
                xaxis_title="Rasgo de Personalidad",
                yaxis_title="Intensidad Promedio",
                showlegend=False,
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Descripción Gráfico 1
            st.markdown("""
            **📊 Qué estamos viendo:**
            Este gráfico de barras muestra el perfil global de personalidad de tu marca según la percepción de la audiencia. Los cinco rasgos de Aaker son: Sinceridad (confiable, honesto), Emoción (energético, apasionado), Competencia (confiable, líder), Sofisticación (elegante, refinado) y Rudeza (resistente, aventurero). Cada barra representa la intensidad con la que la audiencia asocia tu marca con ese rasgo.

            **🔍 Cómo se midió:**
            Se analizaron todos los comentarios de la audiencia utilizando el Framework de Personalidad de Marca de Jennifer Aaker. Para cada comentario, se identificaron palabras clave, tono de voz y contexto que indicaban asociación con cada uno de los cinco rasgos. Luego se calculó una puntuación promedio por rasgo a nivel global.

            **💡 Para qué se usa:**
            Este perfil global te permite:
            - Validar si tu marca se percibe como pretendías (¿Eres visto como "Sincero" o como "Sofisticado"?).
            - Identificar inconsistencias entre tu identidad de marca deseada y la percibida.
            - Desarrollar estrategias de contenido que refuercen dimensiones fuertes.
            - Corregir deficiencias en dimensiones importantes para tu marca.
            - Crear mensajes más resonantes con la audiencia.

            **📌 Tips para interpretarlo:**
            - Los rasgos con barras altas son tus fortalezas; refuérzalos en futuro contenido.
            - Los rasgos con barras bajas podrían ser oportunidades (si deseas desarrollarlos) o puntos seguros de tu identidad.
            - Las marcas líderes tienen perfiles de personalidad únicos y consistentes.
            - Un perfil "equilibrado" puede indicar confusión; considera fortalecer 2-3 rasgos principales.
            """)
    else:
        st.info("No global personality data available")
    
    # ============================================================================
    # GRÁFICO 2: TOP 5 POSTS POR RASGO SELECCIONADO
    # ============================================================================
    st.header("📊 Gráfico 2: Top 5 Publicaciones por Rasgo")
    per_post = results.get("analisis_por_publicacion", [])
    if per_post:
        df_posts = pd.DataFrame(per_post)
        
        # Extract all available traits from first post
        first_post_traits = df_posts.iloc[0].get("rasgos_aaker", {})
        available_traits = list(first_post_traits.keys()) if isinstance(first_post_traits, dict) else []
        
        if available_traits:
            selected_trait = st.selectbox(
                "Selecciona un rasgo de Aaker para ver los Top 5 posts que lo generaron:",
                available_traits,
                key="trait_selector"
            )
            
            # Extract trait scores for all posts
            df_posts['trait_score'] = df_posts['rasgos_aaker'].apply(
                lambda x: x.get(selected_trait, 0) if isinstance(x, dict) else 0
            )
            
            # Get top 5
            top_5 = df_posts.nlargest(5, 'trait_score')[['post_url', 'trait_score']]
            
            # Create horizontal bar chart
            fig = go.Figure([go.Bar(
                y=top_5['post_url'].str[:50],
                x=top_5['trait_score'],
                orientation='h',
                marker_color='coral'
            )])
            fig.update_layout(
                title=f"Top 5 Publicaciones por Rasgo: {selected_trait}",
                xaxis_title=f"Intensidad de {selected_trait}",
                yaxis_title="Publicación (URL acortada)",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            st.write("**Detalle de Top 5:**")
            display_df = top_5.copy()
            display_df['post_url'] = display_df['post_url'].str[:60] + "..."
            display_df = display_df.rename(columns={
                'post_url': 'URL',
                'trait_score': f'{selected_trait} (Intensidad)'
            })
            st.dataframe(display_df, use_container_width=True)
            
            # Descripción Gráfico 2
            st.markdown(f"""
            **📊 Qué estamos viendo:**
            Un ranking de las 5 publicaciones que generaron la mayor intensidad del rasgo "{selected_trait}" que seleccionaste. Cada barra representa qué tan fuerte fue ese rasgo de personalidad en los comentarios de esa publicación específica.

            **🔍 Cómo se midió:**
            Para cada publicación, se analizaron todos sus comentarios y se calculó la puntuación promedio del rasgo "{selected_trait}". Luego se ordenaron todas las publicaciones de mayor a menor intensidad y se seleccionaron las top 5.

            **💡 Para qué se usa:**
            Este ranking te permite:
            - Identificar qué contenido refuerza mejor cada rasgo de personalidad deseado.
            - Replicar patrones de éxito: ¿Qué hace que ciertas publicaciones generen más "Sinceridad" o "Sofisticación"?
            - Ajustar tu estrategia de contenido para fortalecer rasgos específicos.
            - Comparar el desempeño emocional de diferentes tipos de posts.

            **📌 Tips para interpretarlo:**
            - Las publicaciones en la parte superior son "modelos a replicar" para ese rasgo.
            - Si buscas fortalecer "Competencia", analiza qué tienen en común las top 5 posts de competencia.
            - Considera el tipo de contenido (video, texto, imagen) que mejor activa cada rasgo.
            - Un rasgo muy concentrado en pocas publicaciones indica inconsistencia de marca.
            """)
        else:
            st.info("No trait data available for analysis")
    else:
        st.info("No per-publication data available")
    
    # ============================================================================
    # GRÁFICO 3: PERFIL AAKER POR PUBLICACIÓN SELECCIONADA
    # ============================================================================
    st.header("📊 Gráfico 3: Perfil Aaker por Publicación")
    if per_post:
        df_posts = pd.DataFrame(per_post)
        selected_url = st.selectbox(
            "Selecciona una publicación para ver su perfil de personalidad completo:",
            df_posts["post_url"].tolist(),
            key="post_selector"
        )
        selected_post = df_posts[df_posts["post_url"] == selected_url].iloc[0]
        
        traits = selected_post.get("rasgos_aaker", {})
        if traits and isinstance(traits, dict):
            names = list(traits.keys())
            vals = list(traits.values())
            
            # Create radar chart for more visual impact
            fig = go.Figure(data=go.Scatterpolar(
                r=vals,
                theta=names,
                fill='toself',
                marker_color='mediumseagreen'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0, max(vals) * 1.1 if vals else 1])),
                title=f"Perfil Aaker: {selected_url[:60]}...",
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tono Percibido", selected_post.get('tono_percibido', 'N/A'))
            with col2:
                st.metric("Rasgo Máximo", f"{max(names, key=lambda x: traits[x]) if traits else 'N/A'}")
            with col3:
                st.metric("Intensidad Promedio", f"{sum(vals) / len(vals):.2f}" if vals else "N/A")
            
            # Descripción Gráfico 3
            st.markdown(f"""
            **📊 Qué estamos viendo:**
            Un gráfico de radar (también llamado "rueda de Aaker") que muestra el perfil completo de personalidad de esta publicación específica. Cada eje representa un rasgo de Aaker, y la distancia del centro indica la intensidad de ese rasgo en los comentarios de la publicación.

            **🔍 Cómo se midió:**
            Se extrajeron todos los comentarios asociados a esta publicación y se analizó su contenido para determinar qué dimensiones de personalidad fueron activadas o reforzadas. Se calculó un promedio para cada rasgo basado en los comentarios de la publicación.

            **💡 Para qué se usa:**
            Este análisis granular por publicación te permite:
            - Diagnosticar exactamente qué personalidad de marca proyecta cada contenido.
            - Comparar diferentes tipos de posts: ¿El post A enfatiza Sinceridad mientras que el post B enfatiza Sofisticación?
            - Optimizar futuras publicaciones basándote en respuestas emocionales específicas.
            - Identificar si un post es coherente con tu identidad de marca deseada.
            - Detectar posts que generan "ruido de personalidad" (muchos rasgos débiles en lugar de pocos fuertes).

            **📌 Tips para interpretarlo:**
            - Un radar "redondeado" (todos los ejes expandidos) indica contenido que activa múltiples rasgos (generalmente más viral).
            - Un radar "puntiagudo" (con solo 1-2 picos) indica contenido muy específico en tono (claridad de mensaje).
            - La "personalidad dominante" es el rasgo más fuerte; verifica si alinea con tu identidad deseada.
            - Compara radares de posts exitosos vs posts con bajo engagement para detectar patrones.
            """)
        else:
            st.info("No personality traits available for this post.")
    else:
        st.info("No per-publication data available")
