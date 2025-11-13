import streamlit as st # type: ignore
import pandas as pd
import json
import os
import importlib


# Helper: attempt to load a display function from multiple possible module paths
def _load_display_func(module_path_candidates, func_name):
    for mp in module_path_candidates:
        try:
            mod = importlib.import_module(mp)
            fn = getattr(mod, func_name, None)
            if fn:
                return fn
        except Exception:
            continue
    return None


def main():
    st.set_page_config(layout="wide", page_title="Pixely Dashboard")

    # Sidebar for navigation
    st.sidebar.title("Menú Principal")
    page = st.sidebar.radio("Selecciona una página", [
        "🏠 Pixely Partners",
        "📚 Wiki",
        "📊 Dashboard",
        "🧠 Análisis Cualitativo",
        "� Análisis numérico",
        "�📈 Análisis Cuantitativo",
        "🛠️ Hilos de Trabajo"
    ])

    # Main content area
    if page == "🏠 Pixely Partners":
        st.title("Bob el constructor está trabajando 👷")
        st.write("Pronto habrá novedades aquí.")
    elif page == "📊 Dashboard":
        st.title("Dashboard de Pixely")
        # Show where the frontend expects outputs to be (helps debugging mounts)
        try:
            from pipelines.social_media.view_components._outputs import get_outputs_dir
            od = get_outputs_dir()
            st.caption(f"Orchestrator outputs dir (resolved): {od}")
            # list q*.json files present
            try:
                files = sorted([f for f in os.listdir(od) if f.startswith('q') and f.endswith('.json')])
                st.write('Resultados detectados:', files)
            except Exception:
                st.write('No se pudo listar archivos en el directorio de outputs (posible permisos o rutas montadas).')

        except Exception:
            st.caption('No se pudo resolver outputs_dir (get_outputs_dir)')

        # Render the main dashboard which internally calls the individual modules
        try:
            draw_fn = _load_display_func([
                'pipelines.social_media.view',
                'frontend.pipelines.social_media.view',
                'pipelines.social_media.view',
                'view'
            ], 'draw_dashboard')
            if draw_fn:
                draw_fn({})
            else:
                st.error('No se encontró la función draw_dashboard para renderizar el dashboard')
        except Exception as e:
            st.error(f"No se pudo renderizar el dashboard: {e}")

    elif page == "📚 Wiki":
        st.title("Bob el constructor está trabajando 👷")
        st.write("Pronto habrá novedades aquí.")
    elif page == "🧠 Análisis Cualitativo":
        st.title("Análisis Cualitativo")
        # Tabs for Q1-Q10
        qual_tabs = st.tabs([
            "😢 Emociones", 
            "👤 Personalidad", 
            "💬 Tópicos", 
            "📜 Marcos Narrativos", 
            "🌟 Influenciadores", 
            "🚀 Oportunidades", 
            "🔍 Sentimiento Detallado", 
            "⏰ Temporal", 
            "📝 Recomendaciones", 
            "📝 Resumen Ejecutivo",
            "🔢 Datos numéricos"
        ])
        
        with qual_tabs[0]: # Q1 Emociones

            # Load Q1 data and display (lazy-import to avoid module path issues)
            st.header("🎭 Análisis dimensional de Plutchik")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q1_view',
                'frontend.pipelines.social_media.view_components.qual.q1_view',
                'view_components.qual.q1_view'
            ], 'display_q1_emotions')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q1 fallo al renderizar: {e}")
            else:
                st.info('Q1 no disponible')

        with qual_tabs[1]: # Q2 Personalidad
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q2_view',
                'frontend.pipelines.social_media.view_components.qual.q2_view',
                'view_components.qual.q2_view'
            ], 'display_q2_personality')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q2 fallo al renderizar: {e}")
            else:
                st.info('Q2 no disponible')
        
        with qual_tabs[2]: # Q3 Temas
            st.header("💬 Análisis de Tópicos Principales")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q3_topicos_view',
                'frontend.pipelines.social_media.view_components.qual.q3_topicos_view',
                'view_components.qual.q3_topicos_view'
            ], 'display_q3_topicos')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q3 fallo al renderizar: {e}")
            else:
                st.info('Q3 no disponible')

        with qual_tabs[3]: # Q4 Marcos Narrativos
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q4_marcos_narrativos_view',
                'frontend.pipelines.social_media.view_components.qual.q4_marcos_narrativos_view',
                'view_components.qual.q4_marcos_narrativos_view'
            ], 'display_q4_marcos_narrativos')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q4 fallo al renderizar: {e}")
            else:
                st.info('Q4 no disponible')

        with qual_tabs[4]: # Q5 Influenciadores
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q5_influenciadores_view',
                'frontend.pipelines.social_media.view_components.qual.q5_influenciadores_view',
                'view_components.qual.q5_influenciadores_view'
            ], 'display_q5_influenciadores')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q5 fallo al renderizar: {e}")
            else:
                st.info('Q5 no disponible')

        with qual_tabs[5]: # Q6 Oportunidades
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q6_oportunidades_view',
                'frontend.pipelines.social_media.view_components.qual.q6_oportunidades_view',
                'view_components.qual.q6_oportunidades_view'
            ], 'display_q6_oportunidades')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q6 fallo al renderizar: {e}")
            else:
                st.info('Q6 no disponible')
        with qual_tabs[6]: # Q7 Sentimiento Detallado
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q7_sentimiento_detallado_view',
                'frontend.pipelines.social_media.view_components.qual.q7_sentimiento_detallado_view',
                'view_components.qual.q7_sentimiento_detallado_view'
            ], 'display_q7_sentimiento_detallado')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q7 fallo al renderizar: {e}")
            else:
                st.info('Q7 no disponible')
        with qual_tabs[7]: # Q8 Temporal
            st.header("⏰ Análisis Temporal")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q8_temporal_view',
                'frontend.pipelines.social_media.view_components.qual.q8_temporal_view',
                'view_components.qual.q8_temporal_view'
            ], 'display_q8_temporal')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q8 fallo al renderizar: {e}")
            else:
                st.info('Q8 no disponible')
        with qual_tabs[8]: # Q9 Recomendaciones
            st.header("📝 Recomendaciones Creativas")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q9_recomendaciones_view',
                'frontend.pipelines.social_media.view_components.qual.q9_recomendaciones_view',
                'view_components.qual.q9_recomendaciones_view'
            ], 'display_q9_recomendaciones')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q9 fallo al renderizar: {e}")
            else:
                st.info('Q9 no disponible')
        with qual_tabs[9]: # Q10 Resumen Ejecutivo
            st.header("📝 Resumen Ejecutivo")
            fn = _load_display_func([
                'pipelines.social_media.view_components.qual.q10_resumen_ejecutivo_view',
                'frontend.pipelines.social_media.view_components.qual.q10_resumen_ejecutivo_view',
                'view_components.qual.q10_resumen_ejecutivo_view'
            ], 'display_q10_resumen_ejecutivo')
            if fn:
                try:
                    fn()
                except Exception as e:
                    st.info(f"Q10 fallo al renderizar: {e}")
            else:
                st.info('Q10 no disponible')
        with qual_tabs[10]:
            st.header("🔢 Datos numéricos")
            st.markdown("""
            Aquí puedes visualizar individualmente gráficos cuantitativos relevantes (unidad por unidad).
            Selecciona el módulo cuantitativo que quieras ver y el sistema intentará renderizar su vista principal.
            """)

            # Mapping of friendly names to module path candidates and function name
            quant_catalog = [
                ("Q11 — Engagement", [
                    'pipelines.social_media.view_components.quant.q11_view',
                    'frontend.pipelines.social_media.view_components.quant.q11_view',
                    'view_components.quant.q11_view',
                    'pipelines.social_media.view_components.qual.q11_engagement_view'
                ], 'display_q11_engagement'),
                ("Q12 — Comunidad", [
                    'pipelines.social_media.view_components.quant.q12_view',
                    'frontend.pipelines.social_media.view_components.quant.q12_view',
                    'view_components.quant.q12_view'
                ], 'display_q12_comunidad'),
                ("Q13 — Frecuencia", [
                    'pipelines.social_media.view_components.quant.q13_view',
                    'frontend.pipelines.social_media.view_components.quant.q13_view',
                    'view_components.quant.q13_view'
                ], 'display_q13_frecuencia'),
                ("Q14 — Formatos", [
                    'pipelines.social_media.view_components.quant.q14_view',
                    'frontend.pipelines.social_media.view_components.quant.q14_view',
                    'view_components.quant.q14_view'
                ], 'display_q14_formatos'),
                ("Q15 — Hashtags", [
                    'pipelines.social_media.view_components.quant.q15_view',
                    'frontend.pipelines.social_media.view_components.quant.q15_view',
                    'view_components.quant.q15_view'
                ], 'display_q15_hashtags'),
                ("Q17 — Sentimiento Agrupado", [
                    'pipelines.social_media.view_components.quant.q17_view',
                    'frontend.pipelines.social_media.view_components.quant.q17_view',
                    'view_components.quant.q17_view',
                    'pipelines.social_media.view_components.qual.q17_view'
                ], 'display_q17_sentimiento_agrupado'),
                ("Q18 — Anomalías", [
                    'pipelines.social_media.view_components.quant.q18_view',
                    'frontend.pipelines.social_media.view_components.quant.q18_view',
                    'view_components.quant.q18_view'
                ], 'display_q18_anomalias'),
                ("Q19 — Correlación", [
                    'pipelines.social_media.view_components.quant.q19_view',
                    'frontend.pipelines.social_media.view_components.quant.q19_view',
                    'view_components.quant.q19_view'
                ], 'display_q19_correlacion'),
                ("Q20 — KPI Global", [
                    'pipelines.social_media.view_components.quant.q20_view',
                    'frontend.pipelines.social_media.view_components.quant.q20_view',
                    'view_components.quant.q20_view'
                ], 'display_q20_kpi_global')
            ]

            options = [c[0] for c in quant_catalog]
            choice = st.selectbox('Selecciona gráfico cuantitativo para ver (unitario):', options)
            if choice:
                # find entry
                entry = next((e for e in quant_catalog if e[0] == choice), None)
                if entry:
                    _, modules, func_name = entry
                    fn = _load_display_func(modules, func_name)
                    if fn:
                        try:
                            fn()
                        except Exception as e:
                            st.error(f"Error al renderizar {choice}: {e}")
                    else:
                        st.info(f"La vista para {choice} no está disponible en esta instalación.")
        # ... and so on for Q4-Q10
    elif page == "📈 Análisis Cuantitativo":
        st.title("Análisis Cuantitativo — desplazado")
        st.info(
            """
La página de análisis cuantitativo fue desplazada: ahora puedes ver gráficos unitarios desde 'Análisis Cualitativo' → '🔢 Datos numéricos'.

Para mantener el enfoque single-client, los panels completos Q11–Q20 han sido deshabilitados en la navegación principal.
            """
        )
    elif page == "📊 Análisis numérico":
        st.title("Análisis numérico (Q21)")
        fn = _load_display_func([
            'pipelines.social_media.view_components.qual.q21_datos_numericos',
            'frontend.pipelines.social_media.view_components.qual.q21_datos_numericos',
            'view_components.qual.q21_datos_numericos'
        ], 'display_q21_datos_numericos')
        if fn:
            try:
                fn()
            except Exception as e:
                st.error(f"Error ejecutando Q21: {e}")
        else:
            st.info('Q21 no disponible — revisa que exista `q21_datos_numericos.py` en view_components.')
    elif page == "🛠️ Hilos de Trabajo":
        st.title("Bob el constructor está trabajando 👷")
        st.write("Pronto habrá novedades aquí.")

if __name__ == "__main__":
    main()
