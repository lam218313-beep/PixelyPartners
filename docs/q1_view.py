import streamlit as st # type: ignore
import pandas as pd
import json
import os
from frontend.view_components._outputs import get_outputs_dir
import plotly.graph_objects as go # type: ignore
import ast

def load_q1_data():
    # Resolve orchestrator outputs directory using centralized resolver
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q1_emociones.json')

    if not os.path.exists(json_path):
        st.error(f"Error: No se encontró el archivo de análisis de emociones Q1 en {json_path}")
        return None

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def display_q1_emotions():

    st.write("""
        Este análisis determina el perfil emocional de la audiencia de la marca utilizando el **Modelo Dimensional de Plutchik**.
        Se desagrega el análisis para mostrar el perfil emocional de los comentarios de cada publicación única,
        permitiendo la trazabilidad de emociones a nivel de publicación y cuantificando la intensidad promedio de cada emoción.
        Los datos se obtienen mediante un *prompt* literal dirigido a un modelo de IA (LLM) que clasifica las emociones
        en ocho categorías primarias de Plutchik (alegría, confianza, sorpresa, tristeza, enojo, miedo, disgusto, anticipación)
        y asigna un nivel de intensidad.
    """)

    st.header("Análisis de Emociones")

    q1_data = load_q1_data()

    if q1_data is None:
        return

    # Resumen Global de Emociones
    st.subheader("Resumen Global de Emociones")
    st.write("""
        Este gráfico muestra la distribución general de las 8 emociones primarias de Plutchik (alegría, confianza, sorpresa, tristeza, enojo, miedo, disgusto, anticipación)
        en el conjunto total de comentarios analizados. Permite obtener una visión rápida del panorama emocional global de la audiencia.
    """)
    global_emotions = q1_data.get("resumen_global_emociones", {})

    if global_emotions:
        # Filter out non-emotion keys if any, and prepare data for chart
        emotion_scores = {k: v for k, v in global_emotions.items() if k not in ["Sentimiento Positivo", "Sentimiento Negativo", "Sentimiento Neutral"]}
        
        if emotion_scores:
            emotions_names = list(emotion_scores.keys())
            emotions_values = list(emotion_scores.values())

            fig_global = go.Figure(data=[go.Bar(x=emotions_names, y=emotions_values)])
            fig_global.update_layout(title="Distribución Global de Emociones",
                                     xaxis_title="Emoción",
                                     yaxis_title="Puntuación Promedio")
            st.plotly_chart(fig_global)
        else:
            st.info("No hay datos de emociones globales disponibles para graficar.")
        
        # Display sentiment if available
        sentiment_info = {k: v for k, v in global_emotions.items() if k in ["Sentimiento Positivo", "Sentimiento Negativo", "Sentimiento Neutral"]}
        if sentiment_info:
            st.write("**Sentimiento General:**")
            for sentiment, value in sentiment_info.items():
                st.write(f"- {sentiment}: {value:.2f}")
    else:
        st.write("No hay resumen global disponible.")

    # Análisis por Publicación
    analisis_por_publicacion = q1_data.get("analisis_por_publicacion", [])
    if not analisis_por_publicacion:
        st.info("No hay datos de emociones por publicación para mostrar.")
        return

    df_emociones = pd.DataFrame(analisis_por_publicacion)

    st.subheader("Análisis Detallado por Publicación")
    st.write("""
        Esta sección permite explorar el perfil emocional específico de cada publicación individual.
        Al seleccionar una URL de publicación, se visualiza un gráfico de radar (Rueda de Plutchik)
        que muestra la distribución de las 8 emociones primarias para los comentarios asociados a esa publicación.
        Esto es crucial para comprender la granularidad del análisis de IA y diagnosticar reacciones emocionales a contenido específico.
    """)

    # Selector de Publicaciones
    post_urls = df_emociones["post_url"].tolist()
    selected_post_url = st.selectbox("Selecciona una publicación para ver su análisis detallado:", post_urls)

    if selected_post_url:
        selected_post = df_emociones[df_emociones["post_url"] == selected_post_url].iloc[0]
        
        st.write(f"**URL de la Publicación:** {selected_post['post_url']}")
        st.write(f"**Resumen Emocional:** {selected_post['resumen_emocional']}")

        # Mostrar emociones como un gráfico de radar
        emociones_scores = selected_post["emociones"]
        emociones_names = list(emociones_scores.keys())
        emociones_values = list(emociones_scores.values())

        fig = go.Figure(data=go.Scatterpolar(r=emociones_values, theta=emociones_names, fill='toself'))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=False,
            title=f"Emociones para la Publicación: {selected_post_url}"
        )
        st.plotly_chart(fig)

    # Top 5 Publicaciones por Emoción
    st.subheader("Top 5 Publicaciones por Emoción")
    st.write("""
        Este ranking interactivo permite identificar las 5 publicaciones que generaron la mayor intensidad
        para una emoción específica seleccionada. Es una herramienta valiosa para entender qué tipo de contenido
        desencadena reacciones emocionales particulares en la audiencia y optimizar estrategias de contenido.
    """)
    
    # Obtener la lista de emociones disponibles de la primera publicación
    # Asegurarse de que analisis_por_publicacion no esté vacío antes de intentar acceder a sus elementos
    if analisis_por_publicacion and "emociones" in analisis_por_publicacion[0]:
        available_emotions = list(analisis_por_publicacion[0]["emociones"].keys())
        
        if not available_emotions:
            st.info("No hay emociones disponibles en los datos para generar el ranking.")
        else:
            selected_emotion_for_ranking = st.selectbox("Selecciona una emoción para ver el Top 5 de publicaciones:", available_emotions)

            if selected_emotion_for_ranking:
                # Crear una columna temporal para la emoción seleccionada
                df_emociones[selected_emotion_for_ranking] = df_emociones["emociones"].apply(lambda x: x.get(selected_emotion_for_ranking, 0))
                
                # Ordenar por la emoción seleccionada y obtener el top 5
                top_5_posts = df_emociones.nlargest(5, selected_emotion_for_ranking)

                if not top_5_posts.empty:
                    display_df = top_5_posts[["post_url", selected_emotion_for_ranking, "resumen_emocional"]].copy()
                    display_df.rename(columns={
                        "post_url": "URL de Publicación",
                        selected_emotion_for_ranking: f"Puntuación de {selected_emotion_for_ranking.capitalize()}",
                        "resumen_emocional": "Resumen Emocional"
                    }, inplace=True)
                    
                    # Apply conditional formatting
                    st.dataframe(display_df.style.background_gradient(
                        cmap='YlGnBu',
                        subset=[f"Puntuación de {selected_emotion_for_ranking.capitalize()}"]
                    ), hide_index=True)
                else:
                    st.info(f"No se encontraron publicaciones con la emoción '{selected_emotion_for_ranking}' para el ranking.")
    else:
        st.info("No hay datos de emociones disponibles para generar el ranking.")

    st.markdown("--- ")
