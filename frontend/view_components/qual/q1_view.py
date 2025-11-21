import streamlit as st  # type: ignore
import pandas as pd
from view_components.data_loader import load_q1_data as api_load_q1
from view_components.compat_loader import load_from_api_or_file
import plotly.graph_objects as go  # type: ignore


def load_q1_data():
    """Load Q1 data from API or local file (backward compatibility)."""
    return load_from_api_or_file(api_load_q1, "q1_emociones.json", "Q1")


def display_q1_emotions():
    """Main Q1 view: global emotion distribution + per-post radar + top-5 ranking."""
    st.title("😢 Q1 — Análisis de Emociones (Plutchik)")
    
    st.markdown("""
    ### ¿Qué es este análisis?
    El **Análisis de Emociones** utiliza el Modelo Dimensional de Plutchik para descomponer la respuesta emocional de tu audiencia en 8 emociones primarias: alegría, confianza, sorpresa, tristeza, enojo, miedo, disgusto y anticipación. No es solo sentimiento (positivo/negativo), sino las EMOCIONES REALES que genera tu contenido.
    
    ### ¿Por qué es relevante para tu negocio?
    Las emociones son los drivers de decisión más poderosos en redes sociales. Un cliente que siente **confianza** es 10x más probable que realice una compra que uno que solo siente algo "positivo" genérico. Este análisis te permite:
    - **Optimizar contenido:** Saber qué tipo de posts generan alegría vs. anticipación
    - **Identificar fricción:** Detectar cuándo tu marca genera miedo o disgusto en lugar de inspiración
    - **Diseñar campañas emocionalmente:** Crear mensajes que resonan a nivel emocional profundo
    - **Predecir comportamiento:** Las emociones son predictores de loyalty, advocacy y repeat purchase
    - **Segmentar audiencia:** Diferentes segmentos responden a diferentes emociones
    
    ### El dato de fondo
    A diferencia de análisis de sentimiento binarios (positivo/negativo), Plutchik captura el **espectro emocional completo** de tu audiencia. Esto es critical porque una audiencia que siente mucha "sorpresa" puede actuar diferente a una que siente "anticipación", aunque ambas sean emociones positivas.
    """)

    data = load_q1_data()
    if data is None:
        return

    results = data.get("results", {})

    # Global emotions
    st.header("Resumen Global de Emociones")
    global_emotions = results.get("resumen_global_emociones", {})
    if global_emotions:
        # Remove sentiment aggregates if present
        emotion_scores = {k: v for k, v in global_emotions.items() if k.lower().startswith(("alegr", "conf", "sorp", "triste", "enojo", "mied", "disgust", "antic")) or len(k) < 30}
        if emotion_scores:
            fig = go.Figure([go.Bar(x=list(emotion_scores.keys()), y=list(emotion_scores.values()))])
            fig.update_layout(xaxis_title="Emoción", yaxis_title="Puntuación promedio")
            st.plotly_chart(fig)
            
            # Descripción del gráfico
            st.markdown("""
            **📊 Qué estamos viendo:**
            Este gráfico muestra la distribución de las 8 emociones primarias del Modelo de Plutchik (alegría, confianza, sorpresa, tristeza, enojo, miedo, disgusto, anticipación) en toda la audiencia.

            **🔍 Cómo se midió:**
            Utilizamos procesamiento de lenguaje natural (NLP) y análisis de sentimientos avanzado para clasificar cada comentario de la audiencia en una o más categorías emocionales del Modelo Dimensional de Plutchik. Se asignó una puntuación de intensidad (0-1) a cada emoción detectada en los comentarios, y luego se promedió en toda la base de datos.

            **💡 Para qué se usa:**
            Entender el perfil emocional global de tu audiencia es fundamental para:
            - Identificar qué sentimientos dominan en tu comunidad.
            - Detectar oportunidades de contenido que resuene mejor.
            - Anticipar cómo reaccionará la audiencia a nuevas iniciativas.
            - Alinear la estrategia de marca con las emociones que generan engagement.

            **📌 Tips para interpretarlo:**
            - Las emociones positivas (alegría, confianza) generalmente correlacionan con mayor engagement.
            - El miedo y disgusto pueden indicar puntos de fricción que requieren atención.
            - La anticipación sugiere que tu audiencia espera activamente nuevo contenido.
            - Un balance equilibrado de emociones indica una comunidad saludable y diversa.
            """)
        else:
            st.info("No hay emociones globales para graficar.")

        # Optional sentiment display
        for key in ("Sentimiento Positivo", "Sentimiento Negativo", "Sentimiento Neutral"):
            if key in global_emotions:
                st.write(f"**{key}:** {global_emotions[key]}")
    else:
        st.info("No se encontró resumen global de emociones en los resultados.")

    # Per-post analysis
    per_posts = results.get("analisis_por_publicacion", [])
    if not per_posts:
        st.info("No hay datos por publicación para mostrar.")
        return

    df = pd.DataFrame(per_posts)
    st.header("Análisis por Publicación")
    post = st.selectbox("Selecciona publicación", df["post_link"].tolist())
    selected = df[df["post_link"] == post].iloc[0]

    st.write(f"**Resumen:** {selected.get('resumen_emocional', 'N/A')}")
    emociones = selected.get("emociones", {})
    if emociones:
        names = list(emociones.keys())
        vals = list(emociones.values())
        fig = go.Figure(data=go.Scatterpolar(r=vals, theta=names, fill="toself"))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 1])), showlegend=False)
        st.plotly_chart(fig)
        
        # Descripción del gráfico radar
        st.markdown("""
        **📊 Qué estamos viendo:**
        Un gráfico de radar (o "rueda de Plutchik") que muestra el perfil emocional específico de esta publicación. Cada eje representa una emoción primaria, y la distancia del centro indica la intensidad de esa emoción en los comentarios de esta publicación en particular.

        **🔍 Cómo se midió:**
        Se extrajeron todos los comentarios asociados a esta publicación específica y se analizó su contenido emocional usando el mismo modelo de Plutchik. La intensidad de cada emoción se calcula como el promedio de todas las puntuaciones de esa emoción en los comentarios de la publicación.

        **💡 Para qué se usa:**
        Este análisis granular te permite:
        - Diagnosticar qué emociones dispara cada publicación específica.
        - Comparar el impacto emocional de diferentes contenidos.
        - Optimizar futuras publicaciones basándote en las respuestas emocionales.
        - Identificar publicaciones que generan un rango emocional más amplio (radar más "lleno") versus las que generan emociones muy específicas.

        **📌 Tips para interpretarlo:**
        - Un radar "redondeado" indica contenido que genera múltiples emociones (generalmente más viral y memorable).
        - Un radar "puntiagudo" (con solo algunos picos) indica contenido que dispara emociones muy específicas.
        - Emociones como "anticipación" o "sorpresa" en publicaciones de anuncios son muy positivas.
        - "Miedo" o "disgusto" altos pueden indicar contenido controvertido o alarmista.
        """)

    # Top-5 by selected emotion
    st.header("Top 5 publicaciones por emoción")
    available = list(per_posts[0].get("emociones", {}).keys())
    emotion = st.selectbox("Elige emoción", available)
    df[emotion] = df["emociones"].apply(lambda d: d.get(emotion, 0))
    top5 = df.nlargest(5, emotion)[["post_link", emotion, "resumen_emocional"]]
    st.dataframe(top5.rename(columns={emotion: f"Puntuación ({emotion})", "post_link": "URL"}))
    
    # Descripción del ranking
    st.markdown("""
    **📊 Qué estamos viendo:**
    Un ranking de las 5 publicaciones que generaron la mayor intensidad de la emoción seleccionada. Cada fila muestra la URL de la publicación, la puntuación promedio de esa emoción específica, y un breve resumen del sentimiento general.

    **🔍 Cómo se midió:**
    Se calculó la puntuación promedio de la emoción seleccionada para cada publicación (basada en el análisis de todos sus comentarios) y se ordenaron las publicaciones de mayor a menor intensidad.

    **💡 Para qué se usa:**
    Este ranking es instrumental para:
    - Identificar qué contenido es más "alegre", "sorprendente", "aterrador", etc.
    - Replicar patrones de contenido exitoso que generan emociones deseadas.
    - Detectar contenido problemático (p. ej., publicaciones con alto "disgusto" que podrían dañar la marca).
    - Informar la estrategia de redes sociales con datos concretos sobre qué funciona.

    **📌 Tips para interpretarlo:**
    - Las puntuaciones más altas en emociones positivas indican "éxitos emocionales" que deberías replicar.
    - Publicaciones con altas puntuaciones en "sorpresa" o "anticipación" suelen tener mejor alcance.
    - Si encuentras muchas publicaciones con "miedo" o "enojo" altos, considera si eso alinea con tu marca.
    - Compara este ranking entre diferentes emociones para encontrar patrones en tu estrategia de contenido.
    """)


def display_q1_emociones():
    """Spanish compatibility wrapper used elsewhere in the app and tests."""
    display_q1_emotions()
