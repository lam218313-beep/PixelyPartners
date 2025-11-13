import streamlit as st # pyright: ignore[reportMissingImports]
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px


def load_q10_data():
    from frontend.view_components._outputs import get_outputs_dir
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q10_resumen_ejecutivo.json')

    if not os.path.exists(json_path):
        st.warning(f"Aún no se ha generado Q10 (Resumen Ejecutivo). Path: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar Q10: {e}")
        return None


def display_q10_resumen_ejecutivo():
    st.header("Q10: Resumen Ejecutivo")

    data = load_q10_data()
    if data is None:
        return
    # Fecha
    fecha = data.get('fecha_analisis') or data.get('metadata', {}).get('fecha_analisis') or data.get('metadata', {}).get('date')
    if fecha:
        st.markdown(f"**Fecha de Análisis:** {fecha}")

    # ALERTA prioritaria
    alerta = data.get('alerta_prioritaria') or data.get('alerta')
    alerta_obj = data.get('alerta_obj', {}) or {}
    if alerta:
        sev = int(alerta_obj.get('severidad', 0) or 0)
        if sev >= 80:
            st.error(f"**ALERTA PRIORITARIA:** {alerta}")
        else:
            st.warning(f"**ALERTA PRIORITARIA:** {alerta}")

    # Hallazgos clave
    hallazgos = data.get('hallazgos_clave') or data.get('puntos_clave') or []
    if hallazgos:
        st.subheader('Hallazgos Clave')
        for h in hallazgos:
            st.markdown(f"- {h}")

    # Resumen general en expander
    resumen_general = data.get('resumen_general') or data.get('resumen')
    with st.expander('Leer Resumen Detallado', expanded=False):
        if not resumen_general:
            st.info('No hay resumen general disponible.')
        else:
            if isinstance(resumen_general, str):
                st.write(resumen_general)
            elif isinstance(resumen_general, (list, tuple)):
                for p in resumen_general:
                    st.write(p)
            else:
                st.write(str(resumen_general))

    # Implicaciones estratégicas
    implicaciones = data.get('implicaciones_estrategicas') or []
    if implicaciones:
        st.info('\n'.join([f"- {i}" for i in implicaciones]))

    # Visualizaciones: prioridades (barra) y fuentes de contribución (torta)
    st.subheader('Visualizaciones')
    prioridades = data.get('prioridades') or data.get('priorities') or []
    try:
        dfp = pd.DataFrame(prioridades) if prioridades else pd.DataFrame()
        if not dfp.empty:
            # detectar columna de impacto
            ycol = None
            for c in ['impacto_score','impacto','impacto_score','impacto_score','impacto_score','impacto_score','impacto_score','impacto_score','impacto_score','impacto_score','impacto_score','impacto_score']:
                if c in dfp.columns:
                    ycol = c
                    break
            # fallback common name
            if ycol is None:
                for c in ['impacto_score','impacto_score','impacto_score','impacto_score','impacto_score']:
                    if c in dfp.columns:
                        ycol = c
                        break
            # try 'impacto_score' or 'impacto_score' or 'impacto'
            if ycol is None:
                # pick any numeric column
                numeric_cols = dfp.select_dtypes(include='number').columns.tolist()
                ycol = numeric_cols[0] if numeric_cols else None

            xcol = None
            for c in ['accion','title','name']:
                if c in dfp.columns:
                    xcol = c
                    break
            if xcol is None:
                xcol = dfp.columns[0]

            if ycol is not None:
                dfp[ycol] = pd.to_numeric(dfp[ycol], errors='coerce').fillna(0)
                figp = px.bar(dfp, x=xcol, y=ycol, color=ycol, title='Impacto estimado por Prioridad')
                figp.update_layout(xaxis_title='Acción', yaxis_title='Impacto estimado')
                st.plotly_chart(figp, use_container_width=True)
                st.markdown(
                    """
                    **Qué significa:** Estimación visual del impacto por prioridad/acción.

                    **Qué mide:** El score de impacto estimado asociado a cada prioridad o acción.

                    **Cómo se calcula:** El orquestador genera un score (p. ej., impacto potencial) para cada recomendación/acción; aquí se agrupa por prioridad.

                    **Cómo usarlo:** Priorizar acciones con mayor impacto estimado y contrastar con recursos disponibles.
                    """
                )
    except Exception:
        st.info('No se pudo generar la visualización de prioridades.')

    fuentes = data.get('fuentes_contribucion') or {}
    try:
        if isinstance(fuentes, dict) and fuentes:
            dff = pd.DataFrame(list(fuentes.items()), columns=['fuente','valor'])
            figf = px.pie(dff, names='fuente', values='valor', title='Contribución por módulo (Q)')
            st.plotly_chart(figf, use_container_width=True)
            st.markdown(
                """
                **Qué significa:** Porcentaje de contribución de cada módulo Q al resultado global.

                **Qué mide:** La proporción de impacto / contribución atribuida a cada módulo de análisis.

                **Cómo se calcula:** Suma de contribuciones normalizadas por módulo según el pipeline.

                **Cómo usarlo:** Identifica qué módulos aportan más a las conclusiones y dónde invertir esfuerzos de mejora.
                """
            )
    except Exception:
        st.info('No se pudo generar la visualización de fuentes de contribución.')
