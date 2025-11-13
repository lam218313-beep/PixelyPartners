import streamlit as st # pyright: ignore[reportMissingImports]
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from frontend.view_components._outputs import get_outputs_dir

def load_q8_data():
    """Carga los datos del análisis Q8 desde el archivo JSON."""
    outputs_dir = get_outputs_dir()

    json_path = os.path.join(outputs_dir, 'q8_temporal.json')
    if not os.path.exists(json_path):
        st.warning(f"Aún no se ha generado el análisis temporal (Q8). Path: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error al cargar Q8: {str(e)}")
        return None

def display_q8_temporal():
    """
    Muestra los resultados del análisis temporal (Q8).
    """
    st.header("Q8: Análisis Temporal")
    
    data = load_q8_data()
    if data is None:
        return
    # 1. Gráfico Principal: Tendencia de Sentimiento + Anomalías
    st.subheader("Tendencia General de Sentimiento (con Anomalías)")

    # Preferimos la serie semanal y las anomalías según el esquema esperado
    serie_semanal = data.get('serie_temporal_semanal') or data.get('serie_temporal') or data.get('tendencia_semanal') or data.get('tendencia_general')
    anomalias = data.get('anomalias_detectadas') or data.get('anomalias') or data.get('anomalies') or []

    if not serie_semanal:
        st.warning("No se encontró una serie temporal semanal en los resultados. Ejecuta el pipeline Q8 para generar 'serie_temporal_semanal'.")
    else:
        df_week = pd.DataFrame(serie_semanal)

        # Normalizar nombres de columnas esperadas
        # Fecha
        if 'fecha_semana' in df_week.columns:
            df_week['date'] = pd.to_datetime(df_week['fecha_semana'], errors='coerce')
        elif 'fecha' in df_week.columns:
            df_week['date'] = pd.to_datetime(df_week['fecha'], errors='coerce')
        elif 'date' in df_week.columns:
            df_week['date'] = pd.to_datetime(df_week['date'], errors='coerce')
        else:
            # try first column
            cols = list(df_week.columns)
            df_week['date'] = pd.to_datetime(df_week[cols[0]], errors='coerce')

        # Sentimiento columns
        if 'porcentaje_positivo' in df_week.columns:
            df_week['positivo'] = pd.to_numeric(df_week['porcentaje_positivo'], errors='coerce')
        elif 'positivo' in df_week.columns:
            df_week['positivo'] = pd.to_numeric(df_week['positivo'], errors='coerce')
        if 'porcentaje_negativo' in df_week.columns:
            df_week['negativo'] = pd.to_numeric(df_week['porcentaje_negativo'], errors='coerce')
        elif 'negativo' in df_week.columns:
            df_week['negativo'] = pd.to_numeric(df_week['negativo'], errors='coerce')

        # Topico dominante
        if 'topico_dominante' not in df_week.columns:
            df_week['topico_dominante'] = df_week.get('topico') if 'topico' in df_week.columns else None

        # Construir figura combinada: líneas para positivo/negativo
        fig = go.Figure()

        if 'positivo' in df_week.columns:
            fig.add_trace(go.Scatter(x=df_week['date'], y=df_week['positivo'], mode='lines+markers', name='Positivo', line=dict(color='green')))
        if 'negativo' in df_week.columns:
            fig.add_trace(go.Scatter(x=df_week['date'], y=df_week['negativo'], mode='lines+markers', name='Negativo', line=dict(color='red')))

        # Preparar dataframe de anomalías para overlay (si existe)
        df_anom = pd.DataFrame(anomalias) if anomalias else pd.DataFrame()
        if not df_anom.empty:
            # Normalizar fecha
            if 'fecha' in df_anom.columns:
                df_anom['date'] = pd.to_datetime(df_anom['fecha'], errors='coerce')
            elif 'date' in df_anom.columns:
                df_anom['date'] = pd.to_datetime(df_anom['date'], errors='coerce')
            else:
                # try to match by index/position to df_week
                df_anom['date'] = None

            # ensure topic and post_url fields exist
            if 'topico_dominante' not in df_anom.columns:
                df_anom['topico_dominante'] = df_anom.get('topico') if 'topico' in df_anom.columns else None
            if 'post_url_viral' not in df_anom.columns:
                df_anom['post_url_viral'] = df_anom.get('post_url') if 'post_url' in df_anom.columns else df_anom.get('post_url_viral') if 'post_url_viral' in df_anom.columns else None
            if 'sentimiento_dominante' not in df_anom.columns:
                df_anom['sentimiento_dominante'] = df_anom.get('sentimiento') if 'sentimiento' in df_anom.columns else None

            # Merge topic from weekly if missing and dates match
            if 'date' in df_anom.columns and 'date' in df_week.columns:
                merged = pd.merge(df_anom, df_week[['date','topico_dominante']], on='date', how='left', suffixes=('','_week'))
                if 'topico_dominante_week' in merged.columns:
                    merged['topico_dominante'] = merged['topico_dominante'].fillna(merged.get('topico_dominante_week'))
                df_anom = merged

            # Color según sentimiento dominante
            def anom_color(s):
                if isinstance(s, str) and s.lower().startswith('pos'):
                    return 'green'
                if isinstance(s, str) and s.lower().startswith('neg'):
                    return 'red'
                return 'blue'

            colors = [anom_color(x) for x in df_anom['sentimiento_dominante']]

            # Hover info: topic and post_url
            hovertext = []
            for i, row in df_anom.iterrows():
                t = row.get('topico_dominante') or ''
                p = row.get('post_url_viral') or ''
                hovertext.append(f"Topico: {t}<br>Viral: {p}")

            fig.add_trace(go.Scatter(x=df_anom['date'], y=[None]*len(df_anom), mode='markers', name='Anomalías', marker=dict(size=12, color=colors, symbol='x'), hovertext=hovertext, hoverinfo='text'))

        fig.update_layout(title='Tendencia semanal de Sentimiento (Positivo vs Negativo) con Anomalías', xaxis_title='Semana', yaxis_title='Porcentaje')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            """
            **Qué significa:** Tendencia temporal del sentimiento (positivo vs negativo) con marcadores de anomalías.

            **Qué mide:** Cambios en la proporción de sentimiento a lo largo del tiempo y eventos anómalos que causan picos.

            **Cómo se calcula:** Series temporales agregadas por periodo (semana/día), con detección de anomalías sobre la métrica de sentimiento.

            **Cómo usarlo:** Detectar picos y correlacionarlos con publicaciones/campañas; priorizar drill-down en anomalías para diagnóstico.
            """
        )

        # 3) Panel de Diagnóstico: Top 3 anomalías
        if not df_anom.empty:
            st.markdown("---")
            st.subheader('Top 3 Anomalías (Diagnóstico)')
            # if anomaly severity exists, sort by it; else keep original order
            if 'severidad' in df_anom.columns:
                df_top = df_anom.sort_values('severidad', ascending=False).head(3)
            else:
                df_top = df_anom.head(3)

            for idx, a in df_top.iterrows():
                with st.expander(f"{a.get('date') or a.get('fecha')}: {a.get('sentimiento_dominante') or ''}"):
                    st.markdown(f"**Tópico dominante:** {a.get('topico_dominante')}")
                    st.markdown(f"**Post viral:** {a.get('post_url_viral')}")
                    st.markdown(f"**Detalle:** {a.get('descripcion') or a.get('detalle') or ''}")

            # 4) Drill-down: escoger una anomalía para mostrar distribución de tópicos en esa semana
            anomaly_options = []
            for i, row in df_anom.iterrows():
                label = str(row.get('date') or row.get('fecha') or f"anom_{i}")
                anomaly_options.append(label)

            selected_label = st.selectbox('Selecciona una anomalía para drill-down en distribución de tópicos:', anomaly_options)
            if selected_label:
                # find row
                selected_row = None
                for i, row in df_anom.iterrows():
                    lbl = str(row.get('date') or row.get('fecha') or f"anom_{i}")
                    if lbl == selected_label:
                        selected_row = row
                        break

                # attempt to get topic distribution from anomaly or from weekly series
                topic_dist = None
                if selected_row is not None:
                    if isinstance(selected_row.get('topicos_distribucion') , dict):
                        topic_dist = selected_row.get('topicos_distribucion')
                    elif isinstance(selected_row.get('topic_distribution'), dict):
                        topic_dist = selected_row.get('topic_distribution')
                    else:
                        # try to find in weekly series by date
                        sel_date = selected_row.get('date') or selected_row.get('fecha')
                        match = None
                        try:
                            match = df_week[df_week['date'] == sel_date]
                        except Exception:
                            match = None
                        if match is not None and not match.empty:
                            roww = match.iloc[0]
                            # check possible keys
                            for k in ['topicos_distribucion','topic_distribution','distribucion_topicos','topics']:
                                if k in roww and isinstance(roww[k], dict):
                                    topic_dist = roww[k]
                                    break

                if topic_dist:
                    df_td = pd.DataFrame(list(topic_dist.items()), columns=['topic','value'])
                    fig_td = px.bar(df_td, x='topic', y='value', title=f'Distribución de tópicos para {selected_label}')
                    st.plotly_chart(fig_td, use_container_width=True)
                else:
                    st.info('No se encontró distribución de tópicos para la anomalía seleccionada.')

        # 2. Patrones por Día de la Semana (descripción breve)
        st.subheader("Patrones por Día de la Semana")
        st.markdown(
            """
            **Descripción:** Promedios de interacciones por día de la semana para identificar días con mayor alcance.

            **Cómo se calcula:** Se agrupan las interacciones por día y se calcula el promedio o mediana.

            **Cómo se emplearía:** Programar contenidos en días con rendimiento histórico superior.
            """
        )

    horas = data.get("horas_pico", [])
    if not horas:
        st.info("No hay datos de 'horas_pico' disponibles.")
    else:
        df_horas = pd.DataFrame(horas)
        if 'hora' in df_horas.columns and 'promedio_actividad' in df_horas.columns:
            fig_horas = px.line(
                df_horas,
                x='hora',
                y='promedio_actividad',
                title="Actividad Promedio por Hora del Día"
            )
            fig_horas.update_layout(
                xaxis_title="Hora del Día",
                yaxis_title="Nivel de Actividad Promedio"
            )
            st.plotly_chart(fig_horas, use_container_width=True)
            st.markdown(
                """
                **Qué significa:** Actividad promedio por hora del día.

                **Qué mide:** Nivel de interacción promedio en cada hora (p. ej., comentarios, menciones).

                **Cómo se calcula:** Promedio o mediana de interacciones por hora en el periodo analizado.

                **Cómo usarlo:** Programar contenidos en horas con mayor actividad para maximizar alcance.
                """
            )
        else:
            st.info("Los datos de horas pico no tienen las columnas esperadas ('hora','promedio_actividad').")

    # 4. Momentos Destacados
    st.subheader("Momentos Destacados")
    st.markdown(
        """
        **Descripción:** Resumen de eventos o publicaciones que generaron picos de interacción, con contexto y métricas.

        **Cómo se calcula:** Se identifican periodos con valores extremos en la serie temporal y se extraen metadatos asociados (título, descripción, interacciones).

        **Cómo se emplearía:** Revisar campañas exitosas o incidentes para replicar buenas prácticas o corregir problemas.

        **Tips para interpretar:** Prioriza momentos con alto alcance y alta conversión (si aplica); documenta acciones relacionadas a esos momentos.
        """
    )
    
    momentos = data.get("momentos_destacados", [])
    if not momentos:
        st.info("No hay 'momentos_destacados' para mostrar.")
    else:
        for momento in momentos:
            fecha = momento.get('fecha', 'sin fecha')
            titulo = momento.get('titulo', 'Sin título')
            with st.expander(f"📅 {fecha} - {titulo}", expanded=False):
                inter = momento.get('interacciones')
                try:
                    inter_display = f"{int(inter):,}" if inter is not None else "N/A"
                except Exception:
                    inter_display = str(inter)
                st.write(f"**Interacciones:** {inter_display}")
                st.write(f"**Descripción:** {momento.get('descripcion', '')}")
                if 'tendencia' in momento:
                    st.write(f"**Tendencia:** {momento['tendencia']}")