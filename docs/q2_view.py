import streamlit as st # type: ignore
import pandas as pd
import json
import os
from frontend.view_components._outputs import get_outputs_dir
import plotly.graph_objects as go # type: ignore

def load_q2_data():
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q2_personalidad.json')

    if not os.path.exists(json_path):
        st.error(f"Error: No se encontró el archivo de análisis de personalidad Q2 en {json_path}")
        return None

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def display_q2_personality():
    st.title("👤Análisis modelo Aaker")
    st.write("""
        Este análisis determina la percepción de la personalidad de la marca por parte de la audiencia, utilizando el **Modelo de Aaker**.
        Clasifica la percepción en cinco rasgos: **Sinceridad, Emoción, Competencia, Sofisticación y Robustez**.
        El análisis se desglosa por publicación para identificar qué contenido refuerza o debilita la personalidad deseada.
    """)

    st.header("Análisis de Personalidad de Marca")

    q2_data = load_q2_data()

    if q2_data is None:
        return

    # Perfil Global de Personalidad
    st.subheader("Perfil Global de Personalidad de Marca")
    st.write("""
        Este gráfico muestra la distribución porcentual de los 5 rasgos de Aaker a nivel global, 
        calculada a partir de todos los comentarios analizados. Ofrece una visión general de cómo 
        la audiencia percibe la personalidad de la marca.
    """)
    analisis_agregado = q2_data.get("analisis_agregado", {})

    if analisis_agregado:
        traits = list(analisis_agregado.keys())
        values = list(analisis_agregado.values())

        fig_global = go.Figure(data=[go.Bar(x=traits, y=values, marker_color='indianred')])
        fig_global.update_layout(title="Distribución Global de Rasgos de Personalidad (Aaker)",
                                 xaxis_title="Rasgo de Personalidad",
                                 yaxis_title="Distribución Porcentual (%)")
        st.plotly_chart(fig_global)
        st.markdown(
            """
            **Qué significa:** Distribución porcentual de los rasgos de personalidad según el modelo de Aaker.

            **Qué mide:** La proporción relativa de menciones asociadas a cada rasgo en el conjunto de comentarios.

            **Cómo se calcula:** Se agregan etiquetas de rasgo por comentario y se normaliza por el total de comentarios.

            **Cómo usarlo:** Identifica rasgos dominantes y brechas frente a la personalidad deseada; prioriza publicaciones que refuercen rasgos estratégicos.
            """
        )
    else:
        st.info("No hay datos del perfil global de personalidad disponibles para graficar.")

    # Análisis por Publicación
    analisis_por_publicacion = q2_data.get("analisis_por_publicacion", [])
    if not analisis_por_publicacion:
        st.info("No hay datos de personalidad por publicación para mostrar.")
        return

    df_personalidad = pd.DataFrame(analisis_por_publicacion)

    st.subheader("Análisis Detallado por Publicación")
    st.write("""
        Explore el perfil de personalidad específico de cada publicación. Seleccione una URL para ver 
        un gráfico de radar que muestra la distribución de los 5 rasgos de Aaker para los comentarios 
        asociados a esa publicación. Esto permite diagnosticar la percepción generada por contenido específico.
    """)

    # Selector de Publicaciones
    post_urls = df_personalidad["post_url"].tolist()
    selected_post_url = st.selectbox("Selecciona una publicación para ver su análisis de personalidad:", post_urls, key='q2_post_selector')

    if selected_post_url:
        selected_post = df_personalidad[df_personalidad["post_url"] == selected_post_url].iloc[0]
        
        st.write(f"**URL de la Publicación:** {selected_post['post_url']}")
        
        rasgos_distribuidos = selected_post.get("rasgos_distribuidos", {})
        if rasgos_distribuidos:
            traits = list(rasgos_distribuidos.keys())
            values = list(rasgos_distribuidos.values())

            fig = go.Figure(data=go.Scatterpolar(r=values, theta=traits, fill='toself', name='Distribución'))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                showlegend=False,
                title=f"Perfil de Personalidad para: {selected_post_url}"
            )
            st.plotly_chart(fig)
        else:
            st.warning("No hay datos de distribución de rasgos para esta publicación.")

    # Top 5 Publicaciones por Rasgo de Personalidad
    st.subheader("Top 5 Publicaciones por Rasgo de Personalidad")
    st.write("""
        Identifique las 5 publicaciones que más contribuyeron a la percepción de un rasgo de personalidad específico.
        Esta herramienta es útil para entender qué contenido resuena con la personalidad de marca deseada.
    """)
    
    if not df_personalidad.empty and 'rasgos_distribuidos' in df_personalidad.columns:
        # Extraer el primer diccionario de rasgos para obtener los nombres de los rasgos
        # Asegurarse de que haya al menos una fila con datos válidos
        valid_traits_series = df_personalidad['rasgos_distribuidos'].apply(lambda x: x if isinstance(x, dict) and x else None).dropna()
        
        if not valid_traits_series.empty:
            first_valid_traits = valid_traits_series.iloc[0]
            available_traits = list(first_valid_traits.keys())
        else:
            available_traits = []
        
        if available_traits:
            selected_trait_for_ranking = st.selectbox("Selecciona un rasgo para ver el Top 5:", available_traits, key='q2_trait_selector')

            if selected_trait_for_ranking:
                # Crear columna temporal para el rasgo seleccionado
                df_personalidad[selected_trait_for_ranking] = df_personalidad["rasgos_distribuidos"].apply(lambda x: x.get(selected_trait_for_ranking, 0) if isinstance(x, dict) else 0)
                
                top_5_posts = df_personalidad.nlargest(5, selected_trait_for_ranking)

                if not top_5_posts.empty:
                    display_df = top_5_posts[["post_url", selected_trait_for_ranking]].copy()
                    display_df.rename(columns={
                        "post_url": "URL de Publicación",
                        selected_trait_for_ranking: f"Puntuación de {selected_trait_for_ranking.capitalize()}"
                    }, inplace=True)
                    
                    st.dataframe(display_df.style.background_gradient(
                        cmap='Reds',
                        subset=[f"Puntuación de {selected_trait_for_ranking.capitalize()}"]
                    ), hide_index=True)
                else:
                    st.info(f"No se encontraron publicaciones con el rasgo '{selected_trait_for_ranking}'.")
        else:
            st.info("No hay rasgos de personalidad disponibles en los datos para generar el ranking.")
    else:
        st.info("No hay datos de rasgos distribuidos disponibles para generar el ranking.")

    st.markdown("--- ")