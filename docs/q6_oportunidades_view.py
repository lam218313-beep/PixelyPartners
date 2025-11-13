import streamlit as st # pyright: ignore[reportMissingImports]
import pandas as pd
import plotly.express as px
import json
import os
from frontend.view_components._outputs import get_outputs_dir

def load_q6_data():
    """Carga los datos del análisis Q6 desde el archivo JSON."""
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q6_oportunidades.json')

    if not os.path.exists(json_path):
        st.warning(f"Aún no se ha generado el análisis de oportunidades (Q6). Ejecuta el pipeline correspondiente. Path: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Eliminar cualquier carácter BOM si existe
            if content.startswith('\ufeff'):
                content = content[1:]
            # Intentar decodificar el JSON
            data = json.loads(content)
            
            # Verificar la estructura esperada
            if "lista_oportunidades" not in data:
                st.error("El archivo JSON no tiene la estructura esperada (falta 'lista_oportunidades')")
                return None
                
            return data
    except json.JSONDecodeError as e:
        st.error(f"Error al decodificar el JSON de Q6: {str(e)}\nPath: {json_path}")
        with st.expander("Contenido del archivo con error"):
            st.code(content[:500] + "..." if len(content) > 500 else content)
        return None
    except Exception as e:
        st.error(f"Error al cargar Q6: {str(e)}")
        return None

def display_q6_oportunidades():
    """
    Muestra los resultados del análisis de oportunidades (Q6) usando una matriz de priorización estratégica.
    """
    st.header("Q6: Análisis de Oportunidades de Mercado")
    st.markdown(
        """
        **Descripción:** Identifica y prioriza oportunidades de producto/mercado usando una matriz (actividad competitiva vs urgencia estratégica).

        **Cómo se calcula:** Cada oportunidad recibe un "gap_score" (urgencia) y una etiqueta de actividad competitiva; se plotean en una matriz donde el eje X refleja la barrera/actividad competitiva y el eje Y la urgencia.

        **Cómo se emplearía:** Usar para priorizar iniciativas de producto, asignar recursos y definir quick-wins con baja competencia y alto impacto.

        **Tips para interpretar:** Busca oportunidades en la zona de alta urgencia y baja competencia; valida con datos cuantitativos (volumen, crecimiento) antes de invertir.
        """
    )

    data = load_q6_data()
    if data is None:
        return

    oportunidades = data.get("lista_oportunidades", [])
    metadata = data.get("metadata", {})

    if not oportunidades:
        st.info("No se encontraron oportunidades para mostrar.")
        return

    # Crear DataFrame para la visualización
    df = pd.DataFrame(oportunidades)
    
    # Convertir actividad_competitiva a valores numéricos para el eje X
    actividad_map = {"Baja": 1, "Media": 2, "Alta": 3}
    df["actividad_valor"] = df["actividad_competitiva"].map(actividad_map)

    # Crear gráfico de dispersión (Matriz de Priorización)
    # Añadir columna de prioridad/zone para coloración condicional
    def compute_zone(row):
        # Alta prioridad: gap_score alto y actividad competitiva baja
        try:
            gap = float(row.get('gap_score') or 0)
        except Exception:
            gap = 0
        act = row.get('actividad_competitiva')
        act_val = row.get('actividad_valor')
        if act_val is None:
            return 'Normal'
        if gap >= 70 and act_val <= 1.5:
            return 'Alta Prioridad'
        if gap < 30 and act_val >= 2.5:
            return 'Baja Prioridad'
        return 'Medio'

    df['prioridad_zona'] = df.apply(compute_zone, axis=1)

    # Crear scatter con hover detallado (tooltip con justificacion y recomendacion)
    hover_cols = ['tema', 'justificacion', 'recomendacion_accion', 'gap_score', 'actividad_competitiva']
    for c in hover_cols:
        if c not in df.columns:
            df[c] = None

    fig = px.scatter(
        df,
        x="actividad_valor",
        y="gap_score",
        text="tema",
        color='prioridad_zona',
        size='gap_score',
        hover_name='tema',
        hover_data=hover_cols,
        title="Matriz de Priorización Estratégica",
        labels={
            "actividad_valor": "Barrera de Entrada (Actividad Competitiva)",
            "gap_score": "Urgencia Estratégica (Gap Score)",
            "tema": "Oportunidad"
        },
        height=600
    )

    # Personalizar el gráfico: marker y texto
    fig.update_traces(
        marker=dict(opacity=0.8),
        textposition="top center"
    )

    # Mapear colores para las zonas (verde para alta prioridad, rojo para baja)
    color_map = {'Alta Prioridad': 'green', 'Medio': 'orange', 'Baja Prioridad': 'red', 'Normal': 'gray'}
    try:
        fig.update_traces(marker=dict(sizemode='area'))
        fig.update_layout(legend_title_text='Zona de Prioridad')
        # apply discrete color mapping
        fig.for_each_trace(lambda t: t.update(marker=dict(color=color_map.get(t.name, '#636EFA'))))
    except Exception:
        pass
    fig.update_xaxes(
        ticktext=["Baja", "Media", "Alta"],
        tickvals=[1, 2, 3],
        range=[0.5, 3.5]
    )
    fig.update_yaxes(range=[0, 100])

    # Agregar zonas de prioridad
    fig.add_shape(
        type="rect",
        x0=0.5, y0=70,
        x1=1.5, y1=100,
        fillcolor="rgba(0,255,0,0.1)",
        line_width=0,
        name="Alta Prioridad"
    )
    fig.add_shape(
        type="rect",
        x0=2.5, y0=0,
        x1=3.5, y1=30,
        fillcolor="rgba(255,0,0,0.1)",
        line_width=0,
        name="Baja Prioridad"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        **Qué significa:** Matriz de priorización que muestra oportunidades posicionadas por urgencia (Gap Score) y nivel de actividad competitiva.

        **Qué mide:** Urgencia estratégica (Y) frente a barreras/actividad competitiva (X) para cada oportunidad.

        **Cómo se calcula:** Cada oportunidad recibe un gap_score y una etiqueta de actividad; se plotean como puntos con tamaño proporcional al gap_score.

        **Cómo usarlo:** Prioriza iniciativas en la zona de alta urgencia y baja competencia; usa los detalles para diseñar pilotos / experiments.
        """
    )

    # Mostrar métricas agregadas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Promedio Gap Score", f"{metadata.get('promedio_gap', 0):.1f}")
    with col2:
        dist = metadata.get("distribucion_actividad", {})
        st.metric("Oportunidades Alta Prioridad", 
                 sum(1 for op in oportunidades if op["gap_score"] >= 70 and op["actividad_competitiva"] == "Baja"))
    with col3:
        st.metric("Total Oportunidades", metadata.get("total_oportunidades", 0))

    # Detalles de las oportunidades
    st.subheader("Detalles de Oportunidades")
    st.markdown(
        """
        **Descripción:** Listado detallado de cada oportunidad con justificación, recomendación y métricas asociadas (Gap Score, actividad competitiva).

        **Cómo se calcula:** Se presentan las oportunidades ordenadas por Gap Score (o la métrica de prioridad definida en el pipeline).

        **Cómo se emplearía:** Utilizar como base para planes de acción, definiciones de pilotos y para comunicar prioridades a stakeholders.

        **Tips para interpretar:** Revisa la justificación y la recomendación; prioriza oportunidades que ofrezcan ROI rápido y que requieran cambios tácticos en lugar de estratégicos complejos.
        """
    )
    for oportunidad in sorted(oportunidades, key=lambda x: x["gap_score"], reverse=True):
        with st.expander(f"{oportunidad['tema']} (Gap Score: {oportunidad['gap_score']})"):
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f"**Justificación:** {oportunidad['justificacion']}")
                st.markdown(f"**Recomendación:** {oportunidad['recomendacion_accion']}")
            with col2:
                st.metric("Gap Score", oportunidad["gap_score"])
                st.markdown(f"**Actividad Competitiva:** {oportunidad['actividad_competitiva']}")