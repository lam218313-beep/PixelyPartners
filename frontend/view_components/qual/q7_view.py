"""Q7 View: Detailed Sentiment Analysis"""
import streamlit as st # type: ignore
import pandas as pd
import json
import os
import plotly.graph_objects as go  # type: ignore
from .._outputs import get_outputs_dir

def get_sentiment_color(sentiment_type):
    """Map sentiment type to color"""
    color_map = {
        'Positivo': '#2ecc71',    # Green
        'Negativo': '#e74c3c',    # Red
        'Neutral': '#95a5a6',     # Gray
        'Mixto': '#f39c12'        # Orange (ambivalent)
    }
    return color_map.get(sentiment_type, '#3498db')

def display_q7_sentimiento():
    st.title("🔍 Q7: Análisis de Sentimiento Detallado")
    
    st.markdown("""
    ### ¿Qué es este análisis?
    El **Análisis de Sentimiento Detallado** profundiza DENTRO del sentimiento: no solo "positivo" vs "negativo", sino MATICES. Incluso dentro de lo positivo, ¿hay ambivalencia? (ej: "Amo el producto pero odio el servicio al cliente"). Este análisis identifica sentimientos MIXTOS y subjetividad.
    
    ### ¿Por qué es relevante para tu negocio?
    Sentimientos puros son raros. La mayoría de clientes tienen opiniones COMPLEJAS: pueden amar tu producto pero estar enojados con tu servicio. Si tu métrica es solo "% positivo", te estás perdiendo la COMPLEJIDAD. Este análisis te permite:
    - **Detectar clientes "en riesgo":** Los ambivalentes son los primeros en cambiar a competidor
    - **Priorizar problemas:** Si muchos dicen "buen producto, mal servicio", el fix es obvio
    - **Entender clientes emocionales:** Cuánta subjetividad hay (son rationalists o emotionals?)
    - **Diseñar respuestas segmentadas:** No todos los "positivos" merecen la misma respuesta
    - **Predecir churn:** Ambivalencia es predictor fuerte de abandono
    
    ### El dato de fondo
    Usamos análisis de oraciones múltiples (no solo agregamos positivo/negativo al comment level) para detectar CONTRADICCIONES dentro de un mismo comentario. También medimos subjetividad (cuánta opinión vs factos). El resultado es un perfil mucho más realista.
    """)
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, "q7_sentimiento_detallado.json")
    if not os.path.exists(json_path):
        st.error(f"Q7 file not found"); return
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = data.get("results", {})
    
    analisis_agregado = results.get("analisis_agregado", {})
    analisis_por_pub = results.get("analisis_por_publicacion", [])
    resumen = results.get("resumen_global", {})
    
    if analisis_agregado and analisis_por_pub:
        
        # ========================================================================
        # GRÁFICO 1: SENTIMIENTO GLOBAL (ANILLO) + TARJETA MÉTRICA
        # ========================================================================
        st.header("📊 Gráfico 1: Sentimiento Global y Subjetividad")
        st.markdown("""
        **📊 Qué estamos viendo:**
        Una vista de 360° del sentimiento en la conversación, destacando qué porcentaje es MIXTO (ambivalente).
        La tarjeta muestra el Score de Subjetividad Global: qué tan basado en opiniones vs hechos es el discurso.
        
        **🔍 Cómo se midió:**
        - Positivo: Comentarios favorables hacia la marca
        - Negativo: Críticas o insatisfacción
        - Neutral: Comentarios informativos sin posición
        - Mixto: Ambivalentes (reconocen aspectos positivos Y negativos)
        - Subjetividad: Ratio de opiniones vs hechos (0.0-1.0)
        
        **💡 Para qué se usa:**
        El segmento MIXTO es clave: muestra confusión, indecisión o claridad insuficiente en la comunicación.
        Subjetividad alta = Discurso emocional (puede ser bueno o malo según contexto).
        
        **📌 Tips:**
        - Si Mixto > 30% → La marca no comunica claramente (hay ambigüedad)
        - Si Subjetividad > 75% → Discurso muy emocional (target específico)
        - Cruce: Mixto alto + Subjetividad alta = Confusión emocional
        """)
        
        # Extract sentiment distribution
        sentimientos = ['Positivo', 'Negativo', 'Neutral', 'Mixto']
        valores = [analisis_agregado.get(s, 0) for s in sentimientos]
        colores = [get_sentiment_color(s) for s in sentimientos]
        
        # Convert to percentages
        porcentajes = [v * 100 for v in valores]
        
        # Create donut chart
        fig_donut = go.Figure(data=[go.Pie(
            labels=sentimientos,
            values=porcentajes,
            marker=dict(colors=colores),
            hole=0.4,
            textposition='inside',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'
        )])
        
        fig_donut.update_layout(
            title="Distribución de Sentimientos (P/N/N/M)",
            height=400,
            showlegend=True
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.plotly_chart(fig_donut, use_container_width=True)
        with col2:
            subjetividad = analisis_agregado.get('subjetividad_promedio_global', 0)
            st.metric(
                "Subjetividad Global",
                f"{subjetividad * 100:.0f}%",
                delta=f"{'Muy Alta' if subjetividad > 0.75 else 'Alta' if subjetividad > 0.60 else 'Moderada'}"
            )
            
            # Show mixto percentage
            mixto_pct = analisis_agregado.get('Mixto', 0) * 100
            st.metric(
                "Ambivalencia",
                f"{mixto_pct:.0f}%",
                delta=f"{'Alerta!' if mixto_pct > 30 else 'Normal' if mixto_pct > 20 else 'Baja'}"
            )
        
        # ========================================================================
        # GRÁFICO 2: TOP 5 AMBIVALENCIA (BARRAS)
        # ========================================================================
        st.header("📊 Gráfico 2: Top 5 Publicaciones con Mayor Ambivalencia")
        st.markdown("""
        **📊 Qué estamos viendo:**
        Las 5 publicaciones donde el sentimiento MIXTO es más prevalente.
        Esto señala dónde hay MAYOR CONFUSIÓN en la conversación sobre tu marca.
        
        **🔍 Cómo se midió:**
        Se calcula el porcentaje de comentarios Mixtos para cada post_url.
        Se rankean las 5 con mayor % de Mixto (ambivalencia).
        
        **💡 Para qué se usa:**
        Identificar publicaciones que necesitan CLARIFICACIÓN.
        Estas son oportunidades para:
        - Responder preguntas frecuentes
        - Aclarar posiciones ambiguas
        - Reunir más contexto sobre confusiones
        
        **📌 Tips:**
        - Publica contenido aclaratorio sobre los top posts ambigüos
        - Monitorea si Mixto baja después de tu acción
        """)
        
        # Get top 5 by mixto
        df_pubs = pd.DataFrame(analisis_por_pub)
        df_pubs['post_corto'] = df_pubs['post_url'].str.extract(r'/p/([^/]+)')[0].fillna(df_pubs['post_url'])
        df_top_mixto = df_pubs.nlargest(5, 'porcentaje_mixto')
        
        fig_bars = go.Figure([go.Bar(
            y=df_top_mixto['post_corto'],
            x=df_top_mixto['porcentaje_mixto'],
            orientation='h',
            marker_color='#f39c12',
            text=df_top_mixto['porcentaje_mixto'].apply(lambda x: f"{x:.0f}%"),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Ambivalencia: %{x:.0f}%<extra></extra>'
        )])
        
        fig_bars.update_layout(
            title="5 Posts con Mayor % de Sentimiento Mixto",
            xaxis_title="Porcentaje de Comentarios Mixtos",
            yaxis_title="Publicación",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_bars, use_container_width=True)
        
        # ========================================================================
        # GRÁFICO 3: ANÁLISIS DETALLADO POR PUBLICACIÓN (SELECTOR + PANEL)
        # ========================================================================
        st.header("📊 Gráfico 3: Análisis de Evidencia Mixta")
        st.markdown("""
        **📊 Qué estamos viendo:**
        Una profundización en una publicación específica:
        - Distribución completa de sentimientos (P/N/N/M)
        - Score de Subjetividad específico del post
        - Comentario REAL más representativo del sentimiento Mixto
        
        **🔍 Cómo se midió:**
        Se extrae el comentario más representativo del segmento Mixto para cada post.
        Este ejemplo vincula la métrica con la realidad cualitativa.
        
        **💡 Para qué se usa:**
        Entender QUÉ ESPECÍFICAMENTE genera ambivalencia.
        Leer el comentario real es más valioso que solo ver %s.
        
        **📌 Tips:**
        - Lee el comentario Mixto para cada post top
        - Busca patrones: ¿por qué hay ambivalencia?
        - Responde directamente a esos comentarios
        """)
        
        # Selector for publication
        selected_post_corto = st.selectbox(
            "Selecciona una publicación para ver detalles:",
            df_pubs['post_corto'].tolist(),
            key="pub_selector_q7"
        )
        
        # Get full URL from corto
        selected_pub = df_pubs[df_pubs['post_corto'] == selected_post_corto].iloc[0]
        
        # Display sentiment distribution for this post
        st.markdown(f"**Publicación:** `{selected_pub['post_url']}`")
        
        # Show distribution as bars
        sentimientos_post = selected_pub['distribucion_sentimiento']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            positivo = sentimientos_post.get('Positivo', 0) * 100
            st.metric("Positivo", f"{positivo:.0f}%")
        with col2:
            negativo = sentimientos_post.get('Negativo', 0) * 100
            st.metric("Negativo", f"{negativo:.0f}%")
        with col3:
            neutral = sentimientos_post.get('Neutral', 0) * 100
            st.metric("Neutral", f"{neutral:.0f}%")
        with col4:
            mixto = sentimientos_post.get('Mixto', 0) * 100
            st.metric("Mixto", f"{mixto:.0f}%")
        
        # Show subjectivity
        subj = selected_pub.get('subjetividad_promedio', 0)
        st.metric(
            "Subjetividad de Este Post",
            f"{subj * 100:.0f}%",
            delta="Muy Subjetivo" if subj > 0.75 else "Moderadamente Subjetivo" if subj > 0.60 else "Relativamente Objetivo"
        )
        
        # Show example of Mixto sentiment
        st.markdown("**💬 Comentario Representativo del Sentimiento Mixto:**")
        with st.expander("Leer comentario completo", expanded=True):
            ejemplo = selected_pub.get('ejemplo_mixto', 'Sin ejemplo disponible')
            st.write(f"> *{ejemplo}*")
        
        # Show all publications summary table
        st.markdown("---")
        st.markdown("**📋 Comparativa de Todas las Publicaciones:**")
        
        # Create summary table
        table_df = df_pubs[['post_corto', 'porcentaje_mixto', 'subjetividad_promedio']].copy()
        table_df.columns = ['Publicación', 'Ambivalencia (%)', 'Subjetividad']
        table_df['Ambivalencia (%)'] = table_df['Ambivalencia (%)'].round(0).astype(int)
        table_df['Subjetividad'] = (table_df['Subjetividad'] * 100).round(0).astype(int)
        table_df = table_df.sort_values('Ambivalencia (%)', ascending=False)
        
        st.dataframe(table_df, use_container_width=True)
        
        # Summary statistics
        st.markdown("---")
        st.markdown("**📈 Resumen Estratégico:**")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Publicaciones", resumen.get('total_publicaciones_analizadas', 0))
        with col2:
            st.metric("Promedio Ambivalencia", f"{resumen.get('promedio_porcentaje_mixto', 0):.1f}%")
        with col3:
            st.metric("Promedio Subjetividad", f"{resumen.get('promedio_subjetividad', 0) * 100:.0f}%")
        with col4:
            st.metric(
                "Claridad de Mensaje",
                "BAJA" if resumen.get('promedio_porcentaje_mixto', 0) > 25 else "MEDIA" if resumen.get('promedio_porcentaje_mixto', 0) > 15 else "ALTA"
            )
        
    else:
        st.info("No sentiment data available")
