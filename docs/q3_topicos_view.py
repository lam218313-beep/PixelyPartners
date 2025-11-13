import streamlit as st # type: ignore
import pandas as pd
import json
import os
from frontend.view_components._outputs import get_outputs_dir
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore

def load_q3_data():
    """Carga los datos del análisis Q3 desde el archivo JSON."""
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q3_topicos.json')

    if not os.path.exists(json_path):
        st.error(f"Error: No se encontró el archivo de análisis de tópicos Q3 en {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        st.error(f"Error al decodificar el archivo JSON: {json_path}")
        return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al cargar Q3: {e}")
        return None

def display_q3_topicos():

    st.write("""
        Este análisis identifica los temas clave tratados por la audiencia de la marca, mostrando la distribución de tópicos
        y el sentimiento asociado tanto a nivel global como para cada publicación individual. Permite comprender qué temas
        generan mayor conversación y cómo se perciben emocionalmente.
    """)

    st.header("Análisis de Tópicos Principales")

    q3_data = load_q3_data()

    if q3_data is None:
        return

    # Resumen Global de Tópicos (Graph 1)
    st.subheader("Resumen Global de Tópicos")
    st.write("""
        Este gráfico muestra los tópicos más relevantes a nivel global, donde el tamaño de la burbuja representa
        la frecuencia porcentual del tópico y el color indica el sentimiento promedio asociado (verde para positivo,
        rojo para negativo, gris para neutral).
    """)
    analisis_agregado = q3_data.get("analisis_agregado", [])

    if analisis_agregado:
        df_agregado = pd.DataFrame(analisis_agregado)
        
        # Map sentiment to color
        df_agregado['color_sentimiento'] = df_agregado['sentimiento_promedio'].apply(
            lambda x: 'Positivo' if x > 0.1 else ('Negativo' if x < -0.1 else 'Neutral')
        )
        df_agregado['color_code'] = df_agregado['sentimiento_promedio'].apply(
            lambda x: 'green' if x > 0.1 else ('red' if x < -0.1 else 'gray')
        )

        fig_global = px.scatter(
            df_agregado,
            x="frecuencia_porcentaje",
            y="tema",
            size="frecuencia_porcentaje",
            color="color_sentimiento",
            color_discrete_map={'Positivo': 'green', 'Negativo': 'red', 'Neutral': 'gray'},
            hover_name="tema",
            hover_data={'frecuencia_porcentaje': ':.2f%', 'sentimiento_promedio': ':.2f', 'color_sentimiento': False},
            title="Tópicos Globales por Frecuencia y Sentimiento"
        )
        fig_global.update_layout(xaxis_title="Frecuencia Porcentual", yaxis_title="Tópico")
        st.plotly_chart(fig_global)
        st.markdown(
            """
            **Qué significa:** Mapa de tópicos globales donde el tamaño muestra frecuencia y el color indica sentimiento promedio.

            **Qué mide:** Frecuencia relativa de cada tópico y su polaridad emocional agregada.

            **Cómo se calcula:** Se cuentan menciones por tópico y se calcula promedio de score de sentimiento por tópico.

            **Cómo usarlo:** Detecta temas dominantes y prioriza análisis/acciones para tópicos con sentimiento negativo o alta frecuencia.
            """
        )
    else:
        st.info("No hay datos de tópicos globales disponibles para graficar.")

    # Análisis por Publicación (Graph 3)
    analisis_por_publicacion = q3_data.get("analisis_por_publicacion", [])
    if not analisis_por_publicacion:
        st.info("No hay datos de tópicos por publicación para mostrar.")
        return

    df_publicacion = pd.DataFrame(analisis_por_publicacion)

    st.subheader("Análisis Detallado por Publicación")
    st.write("""
        Selecciona una publicación para visualizar la distribución de tópicos y el sentimiento asociado
        específicamente para los comentarios de esa publicación. Esto permite una comprensión granular
        de las conversaciones temáticas en torno a contenidos específicos.
    """)

    post_urls = df_publicacion["post_url"].tolist()
    selected_post_url = st.selectbox("Selecciona una publicación para ver su análisis detallado de tópicos:", post_urls)

    if selected_post_url:
        selected_post_data = df_publicacion[df_publicacion["post_url"] == selected_post_url].iloc[0]
        
        temas_distribucion = selected_post_data["temas_distribucion"]
        sentimiento_por_tema = selected_post_data["sentimiento_promedio_por_tema"]

        if temas_distribucion:
            df_post_temas = pd.DataFrame({
                'tema': list(temas_distribucion.keys()),
                'frecuencia_porcentaje': list(temas_distribucion.values()),
                'sentimiento_promedio': [sentimiento_por_tema.get(t, 0) for t in temas_distribucion.keys()]
            })

            df_post_temas['color_sentimiento'] = df_post_temas['sentimiento_promedio'].apply(
                lambda x: 'Positivo' if x > 0.1 else ('Negativo' if x < -0.1 else 'Neutral')
            )
            
            fig_post = px.scatter(
                df_post_temas,
                x="frecuencia_porcentaje",
                y="tema",
                size="frecuencia_porcentaje",
                color="color_sentimiento",
                color_discrete_map={'Positivo': 'green', 'Negativo': 'red', 'Neutral': 'gray'},
                hover_name="tema",
                hover_data={'frecuencia_porcentaje': ':.2f%', 'sentimiento_promedio': ':.2f', 'color_sentimiento': False},
                title=f"Tópicos para la Publicación: {selected_post_url}"
            )
            fig_post.update_layout(xaxis_title="Frecuencia Porcentual", yaxis_title="Tópico")
            st.plotly_chart(fig_post)
            st.markdown(
                """
                **Qué significa:** Distribución de tópicos para la publicación seleccionada.

                **Qué mide:** Qué proporción de comentarios de esa publicación corresponde a cada tópico y el sentimiento asociado.

                **Cómo se calcula:** Se extraen y normalizan las etiquetas de tópico por comentario para esa publicación.

                **Cómo usarlo:** Analiza la conversación alrededor de una publicación específica para entender qué temas impulsan interacción o controversia.
                """
            )
        else:
            st.info(f"No hay datos de tópicos para la publicación {selected_post_url}.")

    # Top 5 Publicaciones por Tópico (Graph 2)
    st.subheader("Top 5 Publicaciones por Tópico")
    st.write("""
        Identifica las 5 publicaciones con la mayor concentración de un tópico específico seleccionado.
        Esta herramienta es útil para entender qué contenidos impulsan conversaciones sobre temas particulares.
    """)
    
    all_topics = []
    for item in analisis_agregado:
        all_topics.append(item['tema'])
    
    if not all_topics:
        st.info("No hay tópicos disponibles para generar el ranking.")
    else:
        selected_topic_for_ranking = st.selectbox("Selecciona un tópico para ver el Top 5 de publicaciones:", all_topics)

        if selected_topic_for_ranking:
            # Create a temporary column for the selected topic's distribution percentage
            # This requires iterating through the temas_distribucion dict for each post
            df_publicacion['selected_topic_percentage'] = df_publicacion['temas_distribucion'].apply(
                lambda x: x.get(selected_topic_for_ranking, 0)
            )
            
            top_5_posts = df_publicacion.nlargest(5, 'selected_topic_percentage')

            if not top_5_posts.empty:
                display_df = top_5_posts[["post_url", 'selected_topic_percentage']].copy()
                display_df.rename(columns={
                    "post_url": "URL de Publicación",
                    'selected_topic_percentage': f"% de {selected_topic_for_ranking}"
                }, inplace=True)
                
                st.dataframe(display_df.style.background_gradient(
                    cmap='YlGnBu',
                    subset=[f"% de {selected_topic_for_ranking}"]
                ), hide_index=True)
            else:
                st.info(f"No se encontraron publicaciones con el tópico '{selected_topic_for_ranking}' para el ranking.")
    
    st.markdown("--- ")