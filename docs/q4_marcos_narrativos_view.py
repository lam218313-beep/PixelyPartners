import streamlit as st
import json
import os
from frontend.view_components._outputs import get_outputs_dir

try:
    import pandas as pd
    import plotly.express as px
except Exception:
    pd = None
    px = None


def load_q4_data():
    """Carga los datos del análisis Q4 desde el archivo JSON."""
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, 'q4_marcos_narrativos.json')

    if not os.path.exists(json_path):
        st.error(f"No se encontró el archivo de resultados en la ruta: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        st.error(f"Error al decodificar el archivo JSON: {json_path}")
        return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al cargar Q4: {e}")
        return None


def display_q4_marcos_narrativos():
    st.title("📜 Marcos Narrativos")
    st.write("Este análisis identifica los marcos narrativos utilizados en la comunicación de la marca. Ayuda a comprender cómo se cuenta la historia de la marca y qué arquetipos se están empleando.")
    st.header("Q4: Marcos Narrativos")

    data = load_q4_data()
    if data is None:
        return

    # Expected keys (preferidos por el orquestador/arquitectura)
    analisis_agregado = data.get('analisis_agregado') or data.get('marcos_agregados')
    analisis_por_publicacion = data.get('analisis_por_publicacion') or data.get('por_publicacion') or []
    serie_temporal = data.get('serie_temporal') or data.get('evolucion')

    # 1) Distribución Global (Barras apiladas o Pie)
    st.subheader("1. Distribución Global")
    st.markdown(
        """
        **Descripción:** Muestra la participación porcentual de cada marco narrativo (Positivo / Negativo / Aspiracional) en el conjunto de comentarios.

        **Cómo se calcula:** Se agregan las etiquetas de marco por comentario y se normaliza el conteo a porcentajes sobre el total de comentarios analizados.

        **Cómo se emplearía:** Úsalo para obtener una foto rápida del tono dominante de la conversación y detectar si hay un sesgo sostenido hacia marcos negativos o aspiracionales.

        **Tips para interpretar:** Presta atención a cambios grandes respecto a periodos anteriores (usar con la sección 4). Un porcentaje alto de "Aspiracional" puede indicar oportunidades de producto; un pico en "Negativo" requiere análisis por publicación para localizar la causa.
        """
    )
    if analisis_agregado:
        # analisis_agregado puede ser dict {'Positivo':0.6, ...} o list of dicts
        if isinstance(analisis_agregado, dict):
            labels = list(analisis_agregado.keys())
            values = [analisis_agregado[k] for k in labels]
            df_global = None
            try:
                df_global = pd.DataFrame({'marco': labels, 'porcentaje': values}) if pd is not None else None
            except Exception:
                df_global = None

            if px is not None and df_global is not None:
                fig = px.pie(df_global, names='marco', values='porcentaje', title='Distribución de Marcos Narrativos (Global)')
                st.plotly_chart(fig)
                st.markdown(
                    """
                    **Qué significa:** Participación porcentual de cada marco narrativo en el corpus analizado.

                    **Qué mide:** La proporción de menciones asociadas a cada marco (p. ej., Positivo, Negativo, Aspiracional).

                    **Cómo se calcula:** Agregando etiquetas de marco por comentario y normalizando por el total de comentarios.

                    **Cómo usarlo:** Detecta sesgos en el relato de marca; útil para auditoría de tono y priorizar intervenciones.
                    """
                )
            else:
                for m, v in zip(labels, values):
                    st.write(f"- {m}: {v}")
        else:
            st.info("Formato inesperado de 'analisis_agregado' — mostrando contenido crudo.")
            st.write(analisis_agregado)
    else:
        st.info("No hay datos agregados de marcos narrativos.")

    st.markdown("---")

    # 2) Posts con Mayor Impacto de Framing
    st.subheader("2. Posts con Mayor Impacto de Framing")
    st.markdown(
        """
        **Descripción:** Lista y compara las publicaciones que concentran mayor proporción de un marco narrativo seleccionado (ej. Negativo o Aspiracional).

        **Cómo se calcula:** Para cada publicación se extrae la proporción del marco seleccionado dentro de su distribución de marcos; se ordenan y seleccionan las 5 con mayor valor.

        **Cómo se emplearía:** Permite priorizar revisiones de contenido o intervenciones (respuestas, aclaraciones, campañas) sobre las publicaciones que más impactan el sentimiento/relato.

        **Tips para interpretar:** Verifica el contenido y los comentarios asociados en esas publicaciones antes de actuar; una alta proporción no siempre implica volumen absoluto (combínalo con métricas de alcance/engagement).
        """
    )
    if analisis_por_publicacion:
        # crear dataframe
        try:
            df_posts = pd.DataFrame(analisis_por_publicacion) if pd is not None else None
        except Exception:
            df_posts = None

        # Ask which marco to rank
        possible_marcos = []
        # infer marcos desde la primera fila
        if df_posts is not None and not df_posts.empty:
            first = df_posts.iloc[0].to_dict()
            # buscar key 'distribucion_marcos' o similar
            distrib_key = None
            for k in ['distribucion_marcos', 'distribucion', 'marcos_porcentajes', 'distribucion_marco']:
                if k in first:
                    distrib_key = k
                    break

            if distrib_key is None:
                # try if temas are directly keys inside items
                sample = first
            else:
                sample = first[distrib_key]

            if isinstance(sample, dict):
                possible_marcos = list(sample.keys())

        if possible_marcos:
            selected_marco = st.selectbox("Selecciona un marco para rankear posts:", possible_marcos)
            # compute percentage per post
            if df_posts is not None:
                df_posts['_selected_pct'] = df_posts.apply(lambda r: (r.get('distribucion_marcos') or r.get('distribucion') or {}).get(selected_marco, 0) if isinstance(r, dict) or hasattr(r, 'get') else 0, axis=1)
                top5 = df_posts.nlargest(5, '_selected_pct')
                if px is not None and not top5.empty:
                    fig = px.bar(top5, x='_selected_pct', y='post_url', orientation='h', title=f'Top 5 publicaciones con mayor proporción de {selected_marco}')
                    st.plotly_chart(fig)
                    st.markdown(
                        """
                        **Qué significa:** Ranking de publicaciones con mayor proporción del marco seleccionado.

                        **Qué mide:** La proporción del marco (porcentaje) en cada publicación seleccionada.

                        **Cómo se calcula:** Para cada publicación se calcula la fracción del marco dentro de su distribución.

                        **Cómo usarlo:** Prioriza revisiones o respuestas sobre las publicaciones que concentran el marco problemático.
                        """
                    )
                else:
                    st.write(top5[['post_url', '_selected_pct']])
        else:
            st.info("No se pudieron inferir los marcos desde los datos por publicación.")
    else:
        st.info("No hay datos por publicación para ranking de marcos.")

    st.markdown("---")

    # 3) Análisis Narrativo por Publicación (Selector + Cards de evidencia)
    st.subheader("3. Análisis Narrativo por Publicación")
    st.markdown(
        """
        **Descripción:** Desagrega la distribución de marcos para una publicación específica y presenta ejemplos textuales (evidencia) que justifican cada marco.

        **Cómo se calcula:** Para la publicación seleccionada se cuentan las etiquetas de marco por comentario y se normalizan a porcentajes; también se extraen los comentarios más representativos por marco (según score o heurística del orquestador).

        **Cómo se emplearía:** Fundamental para auditoría y trazabilidad: permite identificar qué comentarios concretos explican un marco negativo o aspiracional en una publicación concreta.

        **Tips para interpretar:** Revisa los ejemplos narrativos antes de tomar acciones públicas; prioriza ejemplos con contexto (más de 10 palabras) y valida si son repetidos o aislados.
        """
    )
    if analisis_por_publicacion:
        try:
            df_posts = pd.DataFrame(analisis_por_publicacion) if pd is not None else None
        except Exception:
            df_posts = None

        post_urls = [p.get('post_url') for p in analisis_por_publicacion if p.get('post_url')]
        selected = st.selectbox("Selecciona una publicación:", post_urls)
        if selected:
            post_obj = next((p for p in analisis_por_publicacion if p.get('post_url') == selected), None)
            if post_obj:
                distrib = post_obj.get('distribucion_marcos') or post_obj.get('distribucion') or {}
                # mostrar barras por marco
                if distrib and px is not None:
                    df_post = pd.DataFrame({'marco': list(distrib.keys()), 'porcentaje': list(distrib.values())})
                    fig = px.bar(df_post, x='marco', y='porcentaje', title=f'Distribución de marcos para {selected}')
                    st.plotly_chart(fig)
                else:
                    st.write(distrib)

                # mostrar ejemplos_narrativos
                ejemplos = post_obj.get('ejemplos_narrativos') or post_obj.get('ejemplos') or {}
                if ejemplos:
                    st.markdown("**Ejemplos narrativos (evidencia por marco):**")
                    # ejemplos puede ser dict marco->[texts] o marco->text
                    if isinstance(ejemplos, dict):
                        for m, val in ejemplos.items():
                            st.markdown(f"**{m}**")
                            if isinstance(val, list):
                                for ev in val:
                                    st.write(f"> {ev}")
                            else:
                                st.write(f"> {val}")
                    else:
                        st.write(ejemplos)
                else:
                    st.info("No hay ejemplos narrativos para esta publicación.")
            else:
                st.warning("No se encontró la publicación seleccionada en los datos.")
    else:
        st.info("No hay datos por publicación para mostrar.")

    st.markdown("---")

    # 4) Evolución del Discurso (serie temporal)
    st.subheader("4. Evolución del Discurso (Temporal)")
    st.markdown(
        """
        **Descripción:** Serie temporal que muestra cómo evolucionan los porcentajes de cada marco (Positivo/Negativo/Aspiracional) a lo largo del tiempo.

        **Cómo se calcula:** Agregando las etiquetas de marco por intervalo temporal (día/semana) y calculando porcentajes por periodo para cada marco.

        **Cómo se emplearía:** Úsalo para detectar tendencias, picos ligados a campañas o eventos y para validar si medidas correctivas reducen el marco negativo con el tiempo.

        **Tips para interpretar:** Correlaciona picos con calendario de publicaciones o eventos; controla ventanas de comparación (p. ej., 2 vs 4 semanas) y combina con métricas de alcance para ponderar relevancia.
        """
    )
    if serie_temporal:
        # serie_temporal esperado: list of {date: 'YYYY-MM-DD', 'Positivo':0.2, ...}
        try:
            df_time = pd.DataFrame(serie_temporal) if pd is not None else None
        except Exception:
            df_time = None

        if df_time is not None and not df_time.empty and px is not None:
            # melt and plot area
            if 'date' in df_time.columns:
                df_time['date'] = pd.to_datetime(df_time['date'])
            else:
                # attempt to infer first column as date
                pass
            df_melt = df_time.melt(id_vars=['date'], var_name='marco', value_name='porcentaje')
            fig = px.area(df_melt, x='date', y='porcentaje', color='marco', title='Evolución temporal de marcos narrativos')
            st.plotly_chart(fig)
        else:
            st.info("No hay una serie temporal adecuada en los datos para graficar la evolución.")

    # (debug dump removed to avoid showing raw JSON in the UI)