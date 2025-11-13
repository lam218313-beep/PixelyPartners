import streamlit as st  # pyright: ignore[reportMissingImports]
import pandas as pd
import plotly.express as px
import json
import os


def load_q9_data():
    from frontend.view_components._outputs import get_outputs_dir
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q9_recomendaciones.json')
    if not os.path.exists(json_path):
        st.warning(f"Aún no se ha generado Q9 (Recomendaciones). Path: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error al cargar Q9: {e}")
        return None


def display_q9_recomendaciones():
    st.header("Q9: Recomendaciones Creativas (Prioritizadas)")

    data = load_q9_data()
    if data is None:
        return

    lista = data.get('lista_recomendaciones', [])
    metadata = data.get('metadata', {})

    # Convertir a DataFrame temprano para poder calcular métricas
    try:
        df = pd.DataFrame(lista) if lista else pd.DataFrame()
    except Exception:
        df = pd.DataFrame()

    st.subheader("Resumen")
    st.markdown(
        """
        **Descripción:** Resumen de las recomendaciones creativas y priorizadas derivadas del análisis, con métricas de impacto.

        **Cómo se calcula:** Las recomendaciones se generan y se puntúan (score_impacto) en el pipeline del orquestador y se priorizan por área estratégica.

        **Cómo se emplearía:** Servir como hoja de ruta para equipos de contenido y producto; priorizar actividades con mayor score de impacto.

        **Tips para interpretar:** Revisa la justificación (framework) y evidencia asociada antes de ejecutar. Usa el promedio de scores para evaluar esfuerzos globales.
        """
    )
    # Present metadata as readable metrics
    fecha = metadata.get('fecha_analisis') or metadata.get('date') or metadata.get('fecha')
    total = metadata.get('total_recomendaciones') or len(lista)
    promedio = metadata.get('promedio_score')
    if promedio is None and not df.empty and 'score_impacto' in df.columns:
        try:
            promedio_val = pd.to_numeric(df['score_impacto'], errors='coerce')
            if not promedio_val.dropna().empty:
                promedio = float(promedio_val.mean())
        except Exception:
            promedio = None

    cols = st.columns([2, 1, 1])
    with cols[0]:
        if fecha:
            st.write(f"**Fecha de análisis:** {fecha}")
    with cols[1]:
        st.metric(label="Total recomendaciones", value=str(total))
    with cols[2]:
        if promedio is not None:
            st.metric(label="Promedio score", value=f"{promedio}")

    if not lista:
        st.info("No hay recomendaciones disponibles en este momento.")
        return

    # Convertir a DataFrame
    df = pd.DataFrame(lista)
    if 'score_impacto' not in df.columns:
        st.warning("Las recomendaciones no contienen 'score_impacto'. Mostrando lista simple.")
        for rec in lista:
            with st.expander(rec.get('area_estrategica', 'Sin área')):
                st.write(rec.get('recomendacion'))
                st.write(rec.get('justificacion_framework', []))
        return

    # Plot: bar chart of scores grouped by area
    try:
        df_plot = df.copy()
        df_plot['score_impacto'] = pd.to_numeric(df_plot['score_impacto'], errors='coerce').fillna(0)
        fig = px.bar(df_plot, x='area_estrategica', y='score_impacto', color='area_estrategica', title='Score de Impacto por Área Estratégica')
        fig.update_layout(xaxis_title='Área Estratégica', yaxis_title='Score de Impacto (0-100)', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            """
            **Qué significa:** Priorización de recomendaciones por área estratégica según su score de impacto.

            **Qué mide:** El impacto estimado de cada recomendación, normalizado para comparación entre áreas.

            **Cómo se calcula:** Cada recomendación incluye un score de impacto calculado en el pipeline (p. ej., potencial de mejora, evidencia).

            **Cómo usarlo:** Prioriza acciones con mayor score y valida con evidencia antes de implementación.
            """
        )
    except Exception:
        st.info('No se pudo generar el gráfico de priorización. Se mostrará la lista de recomendaciones.')

    st.subheader("Detalle de Recomendaciones")
    st.markdown(
        """
        **Descripción:** Vista detallada de cada recomendación, su score de impacto, justificación y evidencia asociada.

        **Cómo se calcula:** Cada recomendación incluye un score calculado por el orquestador (p. ej., impacto estimado) y una lista de evidencias que sustentan la recomendación.

        **Cómo se emplearía:** Usar las expander para revisar, asignar responsables y convertir recomendaciones en acciones con KPIs asociados.

        **Tips para interpretar:** Prioriza recomendaciones con alto score y evidencia consistente; transforma recomendaciones en experimentos medibles.
        """
    )
    for idx, rec in enumerate(lista):
        title = f"{idx+1}. [{rec.get('score_impacto')}] {rec.get('area_estrategica')}"
        with st.expander(title, expanded=False):
            st.markdown(f"**Recomendación:** {rec.get('recomendacion')}")
            st.markdown(f"**Score impacto:** {rec.get('score_impacto')}")
            # show justification list nicely
            jfs = rec.get('justificacion_framework') or []
            if jfs:
                st.markdown("**Justificación (Frameworks):**")
                for jf in jfs:
                    st.write(f"- {jf}")

            st.markdown(f"**Evidencia (resumen):** {rec.get('evidencia')}" )
            evidencias = rec.get('evidencia_detallada') or []
            if evidencias:
                st.markdown("**Evidencia detallada:**")
                for ev in evidencias:
                    st.write(f"- {ev}")

            # Show reference path resolved from outputs resolver
            from .._outputs import get_outputs_dir
            outputs_dir = get_outputs_dir()
            st.markdown(f"**Referencia (outputs dir):** `{outputs_dir}`")
