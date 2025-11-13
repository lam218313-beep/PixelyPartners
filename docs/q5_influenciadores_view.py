
import streamlit as st # pyright: ignore[reportMissingImports]
import pandas as pd
import plotly.express as px # pyright: ignore[reportMissingImports]
import json
import os
from frontend.view_components._outputs import get_outputs_dir

def load_q5_data():
    """Carga los datos del análisis Q5 desde el archivo JSON."""
    script_dir = os.path.dirname(__file__)
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q5_influenciadores.json')

    if not os.path.exists(json_path):
        st.warning(f"Aún no se ha generado el análisis de influenciadores (Q5). Ejecuta el pipeline correspondiente. Path: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        st.error(f"Error al leer o decodificar el archivo de resultados de Q5: {json_path}")
        return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al cargar Q5: {e}")
        return None

def display_q5_influenciadores():
    """
    Muestra los resultados del análisis de influenciadores (Q5).
    """
    st.header("Q5: Análisis de Influenciadores Clave")
    st.markdown(
        """
        **Descripción:** Identifica y prioriza usuarios que ejercen mayor influencia sobre la conversación (centralidad, alcance y polaridad).

        **Cómo se calcula:** Se calculan métricas de centralidad/score (p. ej., grado, PageRank, interacción) y se combina con señales de polaridad y alcance para ordenar a los influenciadores.

        **Cómo se emplearía:** Usar para diseñar estrategias de engagement, outreach y gestión de crisis. Priorizar a promotores para amplificación y monitorear a detractores para mitigación.

        **Tips para interpretar:** Comprueba si los top influenciadores tienen audiencia relevante para tu segmento y combina score con métricas de alcance/engagement antes de tomar acciones.
        """
    )

    data = load_q5_data()
    if data is None:
        return

    if isinstance(data, list):
        # If data is a list, assume it's the list of influencers directly
        influencers = data
        summary = {"Promotor": 0, "Detractor": 0} # Default empty summary
    elif isinstance(data, dict):
        influencers = data.get("top_influenciadores_detallado", [])
        summary = data.get("resumen_polaridad", {"Promotor": 0, "Detractor": 0})
    else:
        st.error("Formato de datos inesperado para Q5.")
        return

    if not influencers:
        st.info("No se encontraron datos de influenciadores para mostrar.")
        return

    df = pd.DataFrame(influencers)

    # --- Resumen General ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Promotores", summary.get("Promotor", 0))
    with col2:
        st.metric("Total Detractores", summary.get("Detractor", 0))

    st.markdown("---")

    # --- Gráfico de Influencia General ---
    st.subheader("Top 10 Influenciadores por Centralidad")
    st.markdown(
        """
        **Descripción:** Gráfico que muestra los principales influenciadores ordenados por su score de influencia.

        **Cómo se calcula:** Se ordenan los usuarios por la métrica de score (centralidad, interacciones o métrica compuesta) y se muestran los 10 primeros.

        **Cómo se emplearía:** Identificar líderes de opinión y micro-influencers relevantes para campañas o respuesta a incidencias.

        **Tips para interpretar:** Revisa la polaridad asociada y los temas principales de cada influencer antes de contactarlos; un alto score con polaridad negativa puede indicar riesgo reputacional.
        """
    )
    
    # Asegurarse que el score es numérico
    df['score'] = pd.to_numeric(df['score'], errors='coerce')

    # Colorear barras según el sentimiento / polaridad (varía según pipeline)
    color_map = {'Positivo': 'green', 'Neutro': 'gray', 'Negativo': 'red', 'Promotor': 'green', 'Detractor': 'red'}

    # Determine which polarity column exists
    polarity_col = None
    for c in ['polaridad_dominante', 'sentiment', 'polaridad']:
        if c in df.columns:
            polarity_col = c
            break

    try:
        if 'score' in df.columns:
            sort_col = 'score'
            x_col = 'influencer_name' if 'influencer_name' in df.columns else ( 'username' if 'username' in df.columns else df.columns[0])
            y_col = sort_col
        elif 'score_centralidad' in df.columns:
            sort_col = 'score_centralidad'
            x_col = 'username' if 'username' in df.columns else df.columns[0]
            y_col = sort_col
        else:
            # Fallback to first numeric column
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                sort_col = numeric_cols[0]
                x_col = df.columns[0]
                y_col = sort_col
            else:
                sort_col = None

        if polarity_col is not None and sort_col is not None:
            # Use the polarity column to color bars if available
            fig = px.bar(
                df.sort_values(sort_col, ascending=False),
                x=x_col,
                y=y_col,
                title="Influencia y Polaridad de Influenciadores",
                labels={x_col: 'Influencer', y_col: 'Score'},
                color=polarity_col,
                color_discrete_map=color_map
            )
        elif sort_col is not None:
            fig = px.bar(
                df.sort_values(sort_col, ascending=False),
                x=x_col,
                y=y_col,
                title="Influencia de Usuarios",
                labels={x_col: 'Usuario', y_col: 'Score'}
            )
        else:
            st.info("No hay columnas numéricas para graficar en Q5.")
            fig = None
    except Exception as e:
        st.warning(f"No fue posible generar el gráfico de influenciadores: {e}")
        fig = None
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        """
        **Qué significa:** Visualiza los principales influenciadores ordenados por su score de influencia y polaridad.

        **Qué mide:** La combinación de centralidad/score y la polaridad asociada a cada cuenta.

        **Cómo se calcula:** Se usan métricas de centralidad (p. ej., interacciones, PageRank) combinadas con señales de polaridad precomputadas.

        **Cómo usarlo:** Identifica líderes para outreach y monitorea detractores; cruza con alcance para priorizar acciones.
        """
    )

    st.markdown("---")

    # --- Filtro y Desglose de Influenciadores ---
    st.subheader("Explorador de Influenciadores")
    st.markdown(
        """
        **Descripción:** Panel interactivo para filtrar y explorar información detallada de cada influenciador (temas, posts analizados, score y polaridad).

        **Cómo se calcula:** Los filtros aplican sobre la tabla de influenciadores y muestran métricas/calculaciones ya precomputadas en el pipeline.

        **Cómo se emplearía:** Usar para preparar listas de outreach, monitorizar cambios en la polaridad por influencer y extraer evidencia de publicaciones clave.

        **Tips para interpretar:** Utiliza el filtro por tipo (Promotores/Detractores) y revisa ejemplos de posts antes de actuar; prioriza influenciadores por relevancia y afinidad temática.
        """
    )
    filter_option = st.selectbox(
        "Filtrar por tipo de influencia:",
        ["Todos", "Promotores", "Detractores"]
    )

    # Filter safely by the detected polarity column (if present)
    if polarity_col is None:
        if filter_option != "Todos":
            st.info("No se encontró columna de polaridad en los datos. El filtro no está disponible.")
            filtered_df = df
        else:
            filtered_df = df
    else:
        if filter_option == "Promotores":
            try:
                filtered_df = df[df[polarity_col].astype(str).str.lower().str.contains('promot')]
            except Exception:
                filtered_df = df[df[polarity_col] == 'Promotor']
        elif filter_option == "Detractores":
            try:
                filtered_df = df[df[polarity_col].astype(str).str.lower().str.contains('detract')]
            except Exception:
                filtered_df = df[df[polarity_col] == 'Detractor']
        else:
            filtered_df = df

    if filtered_df.empty:
        st.info(f"No se encontraron influenciadores del tipo '{filter_option}'.")
    else:
        for index, row in filtered_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Influencer:** `{row.get('influencer_name') or row.get('username')}`")
                    top_topics = row.get('top_topics') or []
                    if isinstance(top_topics, (list, tuple)):
                        st.markdown(f"**Temas Principales:** *{', '.join(top_topics)}*")
                    else:
                        st.markdown(f"**Temas Principales:** *{top_topics}*")
                    st.markdown(f"**Posts Analizados:** {row.get('posts_analyzed', row.get('posts_count', 'N/A'))}")
                with col2:
                    score_val = row.get('score') or row.get('score_centralidad') or 0
                    try:
                        st.metric("Score", f"{float(score_val):.2f}")
                    except Exception:
                        st.metric("Score", str(score_val))
                    # Safe sentiment display
                    sentiment_val = None
                    if polarity_col and polarity_col in row:
                        sentiment_val = row.get(polarity_col)
                    elif 'sentiment' in row:
                        sentiment_val = row.get('sentiment')
                    if sentiment_val:
                        color = color_map.get(sentiment_val, 'black')
                        st.markdown(f"**Sentimiento:** <span style='color:{color};'>{sentiment_val}</span>", unsafe_allow_html=True)
    # Render figure if available (already rendered above)
