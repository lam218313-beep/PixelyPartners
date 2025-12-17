"""
Pixely Partners - Frontend Dashboard

Streamlit-based dashboard for qualitative analysis (Q1-Q10).
Displays results from API with JWT authentication.
"""

import streamlit as st # type: ignore
import streamlit.components.v1 as components # type: ignore
import os
import base64
import plotly.graph_objects as go  # type: ignore
from pathlib import Path
from api_client import APIClient, init_session_state, is_authenticated
from auth_view import display_login, display_user_info
from cookie_manager import CookieManager
from style_loader import load_login_styles, load_dashboard_styles
from view_components.qual import (
    q1_view, q2_view, q3_view, q4_view, q5_view,
    q6_view, q7_view, q8_view, q9_view, q10_view
)

st.set_page_config(
    layout="wide", 
    page_title="Pixely Partners Dashboard", 
    page_icon="frontend/assets/logo.png",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Try to restore session from cookie if not authenticated
if not is_authenticated():
    # Load login page styles
    load_login_styles()
    
    cookie_mgr = CookieManager()
    restored = cookie_mgr.restore_session_from_cookie()
    
    if not restored:
        # No valid cookie, show login
        display_login()
        st.stop()
    else:
        # Session restored from cookie, rerun to show dashboard
        st.rerun()
else:
    # User is authenticated, load dashboard styles
    load_dashboard_styles()

# Display user info
display_user_info()

page = st.sidebar.radio(
    "Navegación",
    [
        "Pixely Partners",
        "Wiki",
        "Dashboard",
        "Análisis de Redes",
        "Hilos de Trabajo",
    ],
)

# Logout button at the bottom of sidebar
from auth_view import display_logout_button
st.sidebar.markdown("---")
display_logout_button()

# Main content
if page == "Pixely Partners":
    st.title("🚀 Programa de Partners Pixely")
    st.markdown("### **Inteligencia de Mercado como Servicio**")
    
    st.write("")
    st.write("""
    Bienvenido al ecosistema de **Pixely Partners**. Si estás aquí, es porque tu empresa ha sido seleccionada 
    para formar parte de una iniciativa exclusiva diseñada para redefinir cómo las marcas entienden y actúan 
    sobre su mercado.
    
    A continuación, te explicamos el origen de este programa, el valor incalculable de la tecnología que tienes 
    en tus manos y cómo convertimos la data compleja en acciones simples.
    """)
    
    st.write("")
    st.markdown("---")
    
    # SECCIÓN 1: EL ORIGEN
    st.markdown("## 📌 1. El Origen: ¿Por qué existe este programa?")
    st.markdown("### **La Transparencia como Estrategia**")
    
    st.write("""
    Pixely nació en un sector saturado de promesas vacías. Como una firma nueva de tecnología de marketing, 
    nos enfrentamos a la barrera clásica: **la confianza se gana con experiencia demostrada**.
    
    Decidimos invertir la ecuación. En lugar de pedir tu confianza para venderte un servicio, decidimos 
    **ganarnos tu confianza entregándote un valor sin precedentes**, sin costo inicial.
    """)
    
    st.info("""
    💡 **El Programa de Partners no es una prueba gratuita; es una alianza estratégica bilateral.**  
    
    Nosotros ponemos a tu disposición nuestro motor de Inteligencia Artificial de vanguardia para realizar 
    un diagnóstico forense continuo de tu marca. A cambio, construimos juntos un caso de éxito innegable 
    que valida nuestra metodología en el mercado real.
    
    **Tú obtienes:** Una ventaja competitiva injusta basada en datos.  
    **Nosotros obtenemos:** La credibilidad de haber impulsado tu liderazgo.
    """)
    
    st.write("")
    st.markdown("---")
    
    # SECCIÓN 2: LA UTILIDAD
    st.markdown("## 🎯 2. La Utilidad: ¿Para qué sirven 10 frameworks de IA?")
    
    st.write("""
    Es válido preguntar: *"¿Por qué necesito análisis de emociones, marcos narrativos o modelos de personalidad? 
    Yo solo quiero vender más."*
    
    La respuesta es simple: **Ya no puedes vender más solo haciendo "buen contenido".**
    
    El mercado actual es ruidoso y la competencia es feroz. Las métricas tradicionales (likes, alcance) te dicen 
    **qué pasó**, pero no **por qué pasó**. Nuestro sistema utiliza 10 lentes teóricas diferentes (psicología, 
    sociología, marketing) para leer miles de comentarios y entender la mente de tu consumidor mejor de lo que 
    ellos mismos la entienden.
    """)
    
    st.markdown("### **Este sistema te sirve para:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎲 Dejar de Adivinar**  
        No lances campañas basadas en intuición. Usa la **Matriz de Oportunidades** (Q6) para saber 
        exactamente qué necesidades de alta demanda y alto impacto no están siendo atendidas en tu sector.
        
        **⚠️ Detectar Crisis Latentes**  
        Un aumento sutil en la emoción de "Disgusto" (Q1) o un cambio en el "Marco Narrativo" (Q4) hacia 
        la negatividad te avisa de un problema semanas antes de que explote en ventas.
        """)
    
    with col2:
        st.markdown("""
        **🎨 Alinear tu Marca**  
        ¿Crees que tu marca es "Sofisticada" pero el mercado la percibe como "Ruda" (Q2)? Esa disonancia 
        te está costando dinero. El sistema la detecta para que puedas corregirla.
        
        **👥 Encontrar a los Verdaderos Líderes**  
        Olvida el número de seguidores. Identifica quiénes están liderando la conversación (Q5) en los 
        tópicos que realmente importan a tu negocio (Q3).
        """)
    
    st.write("")
    st.markdown("---")
    
    # SECCIÓN 3: LA EJECUCIÓN
    st.markdown("## ⚡ 3. La Ejecución: De la Complejidad a la Acción Simple")
    
    st.write("""
    Sabemos que un dashboard con 10 análisis profundos puede ser abrumador. **Si la información no es fácil 
    de usar, es inútil.**
    
    Por eso, hemos diseñado un flujo de trabajo que elimina la parálisis por análisis:
    """)
    
    st.markdown("### **El Puente: Recomendaciones e Hilos de Trabajo**")
    
    st.success("""
    **📋 Síntesis Automática (Q9)**  
    Nuestro sistema de inteligencia de redes no solo te da gráficos; al final de cada ciclo, actúa como un consultor estratégico senior. 
    Sintetiza los 10 análisis y te entrega una lista priorizada de **Recomendaciones Tácticas** concretas.
    """)
    
    st.success("""
    **🔗 Activación de Hilos de Trabajo**  
    Estas recomendaciones no se quedan en un PDF. Se transforman automáticamente en **"Hilos de Trabajo"** 
    dentro de este dashboard. Un Hilo es una tarea estratégica específica (ej. "Ajustar el tono de comunicación 
    en Instagram para aumentar la percepción de 'Sinceridad'").
    """)
    
    st.success("""
    **💬 Asesoría vía WhatsApp**  
    Aquí es donde cerramos el círculo. No te dejamos solo con la tarea. Nuestro equipo utiliza estos Hilos 
    de Trabajo como base para asesorarte directamente por WhatsApp. Te guiamos en el **cómo, cuándo y dónde** 
    implementar cada cambio, asegurando que el insight complejo se convierta en una acción simple y ejecutada.
    """)
    
    st.write("")
    st.markdown("---")
    
    # MÓDULOS DISPONIBLES
    st.markdown("## 📊 Módulos de Análisis Disponibles")
    
    modules_col1, modules_col2 = st.columns(2)
    
    with modules_col1:
        st.markdown("""
        - **😢 Q1: Emociones (Plutchik)** - Análisis emocional profundo
        - **👤 Q2: Personalidad (Aaker)** - Perfil de marca
        - **💬 Q3: Tópicos** - Temas principales de conversación
        - **📜 Q4: Marcos Narrativos (Entman)** - Análisis de narrativas
        - **🌟 Q5: Influenciadores** - Voces clave en tu sector
        """)
    
    with modules_col2:
        st.markdown("""
        - **🚀 Q6: Oportunidades** - Matriz de oportunidades de mercado
        - **🔍 Q7: Sentimiento Detallado** - Análisis de sentimientos
        - **⏰ Q8: Temporal** - Tendencias y evolución
        - **📝 Q9: Recomendaciones** - Acciones estratégicas
        - **📊 Q10: Resumen Ejecutivo** - KPIs y síntesis
        """)
    
    st.write("")
    st.markdown("---")
    
    # CALL TO ACTION
    st.markdown("## 🎯 Comienza Ahora")
    st.write("""
    Selecciona **Dashboard** en el menú lateral para ver un resumen visual de tus análisis, o navega a 
    **Análisis de Redes** para explorar cada módulo en detalle.
    
    Para gestionar las acciones derivadas de los análisis, visita **Hilos de Trabajo**.
    """)
    
    # Show outputs directory info
    api_base_url = os.environ.get("API_BASE_URL", "http://api:8000")
    st.caption(f"🔗 Conectado a: `{api_base_url}`")

elif page == "Wiki":
    st.title("📚 Wiki Metodológica: El Cerebro de Pixely")
    
    st.write("""
    Bienvenido al centro de conocimiento de **Pixely Partners**.
    
    Si la página de Inicio te explicó el **"por qué"** estamos juntos, esta Wiki te explica el **"cómo"** 
    funciona la tecnología que tienes a tu disposición.
    
    Este dashboard no es una simple herramienta de "Social Listening" que cuenta likes y comentarios. 
    Es un **sistema de Inteligencia de Mercado Forense**. A continuación, te explicamos cómo diseccionamos 
    la data para encontrar la verdad sobre tu marca.
    """)
    
    st.markdown("---")
    
    # METODOLOGÍA
    st.markdown("## 🧠 Nuestra Metodología: Ciencia + IA")
    st.write("""
    Las herramientas tradicionales se quedan en la superficie: te dicen **qué se dice**. Nosotros combinamos 
    la potencia de la Inteligencia Artificial moderna con **frameworks científicos validados** de la psicología 
    y la sociología para entender **por qué se dice** y **qué significa para tu negocio**.
    
    Cada uno de los **10 módulos (Q1-Q10)** que verás en el área de "Análisis de Redes" funciona como una 
    lente diferente para observar la misma realidad.
    """)
    
    st.markdown("---")
    
    # GUÍA DE LOS 10 FRAMEWORKS
    st.markdown("## 📖 Guía de los 10 Frameworks de Análisis")
    st.write("A continuación, desglosamos cada módulo, explicando la teoría detrás de él, cómo interpretar su gráfico y, lo más importante, **para qué te sirve estratégicamente**.")
    
    st.write("")
    
    # Q1 - EMOCIONES
    with st.expander("😢 Q1. Análisis de Emociones (Modelo Plutchik)", expanded=False):
        st.markdown("""
        **La Teoría:**  
        Basado en la "Rueda de las Emociones" del psicólogo Robert Plutchik. Superamos el simple "positivo/negativo" 
        para identificar **8 emociones primarias**: Alegría, Confianza, Miedo, Sorpresa, Tristeza, Disgusto, Ira y Anticipación.
        
        **Cómo leer el Gráfico (Radar/Araña):**
        - Busca los **"picos"**. ¿Hacia dónde se estira más la tela de araña?
        - Un pico en **Confianza** o **Alegría** es saludable.
        - Un pico agudo en **Ira** o **Disgusto** es una **alerta roja** de crisis latente.
        - Si la forma es muy pequeña y centrada, tu marca no está generando conexión emocional (es irrelevante).
        
        **Valor para tu Negocio:**  
        Detectar **crisis emocionales** antes de que se conviertan en crisis financieras. Ajustar el tono de tu 
        comunicación para evocar las emociones correctas.
        """)
    
    # Q2 - PERSONALIDAD
    with st.expander("👤 Q2. Personalidad de Marca (Modelo Aaker)", expanded=False):
        st.markdown("""
        **La Teoría:**  
        Utiliza el framework de Jennifer Aaker, que mide cómo los humanos personifican una marca en **5 dimensiones**: 
        Sinceridad, Emoción (Excitement), Competencia, Sofisticación y Rudeza (Ruggedness).
        
        **Cómo leer el Gráfico (Radar):**
        - Este gráfico muestra la **"huella digital"** de cómo te percibe el mercado actualmente.
        - Compáralo mentalmente con **cómo quieres ser percibido**.
        
        **Valor para tu Negocio:**  
        **Análisis de Brecha (Gap Analysis)**. Si tú vendes servicios premium (aspiras a "Sofisticación") pero el 
        mercado te percibe solo como funcional ("Competencia"), tienes un **problema de branding** que este gráfico revela.
        """)
    
    # Q3 - TÓPICOS
    with st.expander("💬 Q3. Modelado de Tópicos (El 'Qué')", expanded=False):
        st.markdown("""
        **La Teoría:**  
        La IA agrupa miles de comentarios dispares en **clústeres temáticos coherentes**. Identifica de qué está 
        hablando la gente realmente, más allá de tus hashtags de campaña.
        
        **Cómo leer el Gráfico (Treemap/Barras):**
        - El **tamaño del bloque** representa el volumen de la conversación. Los temas más grandes son los que dominan 
        la mente de tu audiencia.
        
        **Valor para tu Negocio:**  
        Descubrir **qué le importa realmente** a tu audiencia. A veces descubrirás que hablan más de tu servicio 
        post-venta (para bien o para mal) que de tu nuevo producto estrella.
        """)
    
    # Q4 - MARCOS NARRATIVOS
    with st.expander("📜 Q4. Marcos Narrativos (Modelo Entman - El 'Cómo')", expanded=False):
        st.markdown("""
        **La Teoría:**  
        Basado en la teoría del **Framing**. Analiza cómo se está encuadrando un tema. ¿Tu producto es presentado 
        como la "causa de un problema", la "solución", o una "aspiración"?
        
        **Cómo leer el Gráfico (Dona/Barras):**
        - Muestra la **distribución porcentual** de los encuadres.
        - Si domina el marco de **"Problema/Riesgo"**, estás a la defensiva en la narrativa pública.
        
        **Valor para tu Negocio:**  
        **Gestión de reputación y PR**. Si estás siendo encuadrado negativamente, no basta con negar la acusación; 
        debes trabajar proactivamente para cambiar el marco narrativo hacia la "Solución" o "Beneficio".
        """)
    
    # Q5 - INFLUENCIADORES
    with st.expander("🌟 Q5. Influencers y Líderes de Opinión", expanded=False):
        st.markdown("""
        **La Teoría:**  
        No buscamos a la persona con más seguidores. Buscamos a los **nodos que generan más engagement** y lideran 
        la discusión en los tópicos específicos (Q3) que importan a tu marca.
        
        **Cómo leer la Lista:**
        - Observa **quiénes son**, pero sobre todo, **en qué temas son relevantes** y si su sentimiento hacia ti 
        es positivo o negativo.
        
        **Valor para tu Negocio:**  
        Identificar **aliados auténticos** para colaboraciones (micro-influencers de nicho) y **detractores clave** 
        que necesitan ser monitoreados.
        """)
    
    # Q6 - OPORTUNIDADES
    with st.expander("🚀 Q6. Matriz de Oportunidades (Demanda vs. Impacto)", expanded=False):
        st.markdown("""
        **La Teoría:**  
        Este es el **gráfico más importante para la toma de decisiones**. Cruza dos variables críticas detectadas por la IA:
        - **Eje X (Demanda/Frecuencia):** ¿Qué tan seguido se menciona una necesidad?
        - **Eje Y (Impacto/Intensidad):** ¿Qué tan fuerte es la carga emocional de esa mención?
        
        **Cómo leer la Matriz (2x2):**
        - 🔴 **Cuadrante Superior Derecho (Prioridad Crítica):** Alta Demanda + Alto Impacto. Son problemas urgentes 
        que queman o deseos intensos de muchos clientes. **Atiende esto HOY**.
        - 🟡 **Cuadrante Superior Izquierdo (Nicho Intenso):** Baja Demanda pero Alto Impacto. Oportunidades para 
        innovar y deleitar a un grupo pequeño pero apasionado.
        - ⚪ **Cuadrante Inferior Derecho (Ruido):** Alta Demanda pero Bajo Impacto. Temas recurrentes pero que no 
        mueven la aguja (ej. quejas genéricas sobre el clima).
        
        **Valor para tu Negocio:**  
        **Priorización pura**. Tu hoja de ruta de producto y marketing debería basarse en mover los puntos rojos 
        del cuadrante superior derecho.
        """)
    
    # Q7 - SENTIMIENTO
    with st.expander("🔍 Q7. Sentimiento Global", expanded=False):
        st.markdown("""
        **La Teoría:**  
        Un análisis de sentimiento refinado por IA (Positivo, Negativo, Neutro), capaz de detectar **sarcasmo y matices**.
        
        **Cómo leer el Gráfico (Medidor):**
        - Es tu **termómetro rápido**. Te da la temperatura general de la salud de la marca.
        
        **Valor para tu Negocio:**  
        **KPI de alto nivel** para medir la salud general de la marca a lo largo del tiempo.
        """)
    
    # Q8 - TEMPORAL
    with st.expander("⏰ Q8. Evolución Temporal", expanded=False):
        st.markdown("""
        **La Teoría:**  
        Mapea el **volumen y sentimiento** de las menciones a lo largo del tiempo.
        
        **Cómo leer el Gráfico (Línea de tiempo):**
        - Busca **correlaciones**. ¿Ese pico de sentimiento negativo coincide con el día que cambiaste tus precios? 
        ¿Ese valle de menciones coincide con el fin de semana?
        
        **Valor para tu Negocio:**  
        Medir el **ROI inmediato** de campañas específicas o entender la duración del impacto de una crisis o evento.
        """)
    
    # Q9 - RECOMENDACIONES
    with st.expander("📝 Q9. Recomendaciones Estratégicas (Tu Plan de Acción)", expanded=False):
        st.markdown("""
        **La Teoría:**  
        La IA actúa como un **consultor estratégico senior**. Sintetiza los hallazgos de Q1 a Q8 y genera una lista 
        de **acciones tácticas concretas**, priorizadas por un score de impacto.
        
        **Cómo leer la Lista:**
        - Es tu **"To-Do list" estratégica**.
        
        **Valor para tu Negocio:**  
        Estas recomendaciones son la base para la pestaña **"Hilos de Trabajo"**. Transforman el análisis en tareas ejecutables.
        """)
    
    # Q10 - RESUMEN EJECUTIVO
    with st.expander("📊 Q10. Resumen Ejecutivo", expanded=False):
        st.markdown("""
        **La Teoría:**  
        La IA genera un **"elevator pitch"** condensando todo el análisis en un párrafo digerible.
        
        **Cómo leer el Texto:**
        - Léelo **antes de ver los gráficos** para tener el contexto general.
        
        **Valor para tu Negocio:**  
        Ideal para **compartir rápidamente** el estado de la marca con otros socios o inversores sin obligarlos a 
        ver todos los gráficos.
        """)
    
    st.markdown("---")
    st.info("💡 **Próximo paso:** Dirígete a la sección **Análisis de Redes** para ver estos frameworks en acción con tus datos reales.")

elif page == "Dashboard":
    st.title("📊 Dashboard Principal")
    
    # Get client info
    client = APIClient()
    ficha_id = st.session_state.get("ficha_cliente_id")
    
    if not ficha_id:
        st.error("❌ No se encontró ID de cliente. Por favor cierra sesión e inicia sesión nuevamente.")
        st.stop()
    
    # Load insights for all analyses
    insights = client.get_insights(ficha_id)
    if not insights:
        st.warning("📭 No hay datos de análisis disponibles.")
        st.stop()
    
    st.markdown("### 📈 Resumen Visual de Análisis")
    st.write("Vista consolidada de los análisis más importantes de tu marca")
    
    # Create 2 columns for better layout
    col1, col2 = st.columns(2)
    
    # ============== ANÁLISIS DE EMOCIONES (Plutchik) ==============
    with col1:
        st.subheader("😢 Análisis de Emociones (Plutchik)")
        q1_data = insights.get("q1_emociones", {}).get("results", {})
        emociones_globales = q1_data.get("resumen_global_emociones", {})
        
        if emociones_globales:
            emotions = list(emociones_globales.keys())
            values = list(emociones_globales.values())
            
            fig = go.Figure(data=[go.Bar(x=emotions, y=values, marker_color='#FF6B6B')])
            fig.update_layout(
                xaxis_title="Emoción",
                yaxis_title="Intensidad",
                height=300,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos disponibles")
    
    # ============== PERSONALIDAD DE MARCA (Aaker) ==============
    with col2:
        st.subheader("👤 Personalidad de Marca (Aaker)")
        q2_data = insights.get("q2_personalidad", {}).get("results", {})
        personalidad_global = q2_data.get("resumen_global_personalidad", {})
        
        if personalidad_global:
            dims = {k: v for k, v in personalidad_global.items() if isinstance(v, (int, float))}
            if dims:
                fig = go.Figure(data=[go.Bar(x=list(dims.keys()), y=list(dims.values()), marker_color='#4ECDC4')])
                fig.update_layout(
                    xaxis_title="Rasgo",
                    yaxis_title="Intensidad",
                    height=300,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos disponibles")
        else:
            st.info("No hay datos disponibles")
    
    # ============== TÓPICOS PRINCIPALES ==============
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("💬 Tópicos Principales")
        q3_data = insights.get("q3_topicos", {}).get("results", {})
        analisis_agregado = q3_data.get("analisis_agregado", [])
        
        if analisis_agregado and len(analisis_agregado) > 0:
            # Get top 5 topics
            top_topics = sorted(analisis_agregado, key=lambda x: x.get("frecuencia_relativa", 0), reverse=True)[:5]
            topic_names = [t.get("topic", "Unknown") for t in top_topics]
            topic_freq = [t.get("frecuencia_relativa", 0) for t in top_topics]
            
            fig = go.Figure(data=[go.Bar(x=topic_names, y=topic_freq, marker_color='#95E1D3')])
            fig.update_layout(
                xaxis_title="Tópico",
                yaxis_title="Frecuencia Relativa",
                height=300,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos disponibles")
    
    # ============== SENTIMIENTO GENERAL ==============
    with col4:
        st.subheader("🔍 Sentimiento Detallado")
        q7_data = insights.get("q7_sentimiento", {}).get("results", {})
        analisis_agregado = q7_data.get("analisis_agregado", {})
        
        # Extract sentiment values (Positivo, Negativo, Neutral, Mixto)
        sentiment_dist = {k: v for k, v in analisis_agregado.items() if k in ["Positivo", "Negativo", "Neutral", "Mixto"]}
        
        if sentiment_dist:
            labels = list(sentiment_dist.keys())
            values = list(sentiment_dist.values())
            colors = ['#38A169', '#E53E3E', '#718096', '#F6AD55']
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4, marker=dict(colors=colors))])
            fig.update_layout(
                height=300,
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos disponibles")
    
    # ============== TENDENCIA TEMPORAL ==============
    st.subheader("⏰ Evolución Temporal")
    q8_data = insights.get("q8_temporal", {}).get("results", {})
    series_temporal = q8_data.get("serie_temporal_semanal", [])
    
    if series_temporal:
        dates = [item.get("fecha_semana", "") for item in series_temporal]
        volumes = [item.get("num_comentarios", 0) for item in series_temporal]
        
        fig = go.Figure(data=[go.Scatter(x=dates, y=volumes, mode='lines+markers', 
                                         line=dict(color='#9B59B6', width=3),
                                         marker=dict(size=8))])
        fig.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Volumen de Comentarios",
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos disponibles")

elif page == "Análisis de Redes":
    st.title("🔍 Análisis de Redes Sociales")
    
    # Get client info and last analysis timestamp
    client = APIClient()
    ficha_id = st.session_state.get("ficha_cliente_id")
    
    if not ficha_id:
        st.error("❌ No se encontró ID de cliente. Por favor cierra sesión e inicia sesión nuevamente.")
        st.stop()
    
    # Display last update timestamp
    ficha_data = client.get_ficha_cliente(ficha_id)
    if ficha_data:
        last_timestamp_str = ficha_data.get("last_analysis_timestamp")
        
        if last_timestamp_str:
            from datetime import datetime
            # Parse and calculate time difference
            try:
                last_dt = datetime.fromisoformat(last_timestamp_str.replace('Z', '+00:00'))
                time_diff = datetime.now(last_dt.tzinfo) - last_dt
                hours_ago = int(time_diff.total_seconds() / 3600)
                
                # Display timestamp with color coding
                if hours_ago < 24:
                    st.success(f"📅 **Última actualización:** hace {hours_ago} horas ({last_dt.strftime('%Y-%m-%d %H:%M')})")
                elif hours_ago < 48:
                    st.info(f"📅 **Última actualización:** hace {hours_ago} horas ({last_dt.strftime('%Y-%m-%d %H:%M')})")
                else:
                    days_ago = int(hours_ago / 24)
                    st.warning(f"📅 **Última actualización:** hace {days_ago} días ({last_dt.strftime('%Y-%m-%d %H:%M')})")
            except Exception as e:
                st.caption(f"ℹ️ Error al parsear timestamp: {e}")
    
    # Store insights in session state for view components
    insights = client.get_insights(ficha_id)
    if insights:
        st.session_state.current_insights = insights
    else:
        st.warning("📭 No hay datos de análisis disponibles. El análisis se ejecuta automáticamente cada 24 horas.")
        st.stop()
    
    # Horizontal tabs for analyses
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "😢 Emociones",
        "👤 Personalidad",
        "💬 Tópicos",
        "📜 Marcos",
        "🌟 Influenciadores",
        "🚀 Oportunidades",
        "🔍 Sentimiento",
        "⏰ Temporal",
        "📝 Recomendaciones",
        "📊 Resumen"
    ])
    
    with tab1:
        q1_view.display_q1_emociones()
    
    with tab2:
        q2_view.display_q2_personalidad()
    
    with tab3:
        q3_view.display_q3_topicos()
    
    with tab4:
        q4_view.display_q4_marcos_narrativos()
    
    with tab5:
        q5_view.display_q5_influenciadores()
    
    with tab6:
        q6_view.display_q6_oportunidades()
    
    with tab7:
        q7_view.display_q7_sentimiento()
    
    with tab8:
        q8_view.display_q8_temporal()
    
    with tab9:
        q9_view.display_q9_recomendaciones()
    
    with tab10:
        q10_view.display_q10_resumen_ejecutivo()

elif page == "Hilos de Trabajo":
    # INYECCIÓN CSS ESPECÍFICA PARA ESTA PÁGINA
    st.markdown("""
        <style>
        .action-card {
            background-color: #1a1a1a;
            border: 1px solid #333333;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid #FF1493;
        }
        .impact-badge-high { 
            background-color: #FF1493; 
            color: white; 
            padding: 4px 12px; 
            border-radius: 4px; 
            font-size: 0.8em; 
            font-weight: bold;
        }
        .impact-badge-med { 
            background-color: #FFA500; 
            color: white; 
            padding: 4px 12px; 
            border-radius: 4px; 
            font-size: 0.8em;
            font-weight: bold;
        }
        .whatsapp-button {
            display: inline-flex; 
            align-items: center; 
            justify-content: center;
            background-color: #25D366; 
            color: white !important; 
            padding: 8px 15px; 
            border-radius: 20px; 
            text-decoration: none; 
            font-weight: bold; 
            font-size: 0.85rem; 
            border: none; 
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .whatsapp-button:hover { 
            background-color: #1ebc57;
            transform: translateY(-2px);
        }
        .progress-metric {
            text-align: center;
            padding: 1rem;
            background: #1a1a1a;
            border-radius: 8px;
            border: 1px solid #333333;
        }
        .note-item {
            background: #0f0f0f;
            border-left: 3px solid #FF1493;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🚀 CENTRO DE OPERACIONES: SPRINT DE 30 DÍAS")
    st.markdown("Tu hoja de ruta para transformar los insights en resultados de negocio.")
    
    st.write("")
    
    # 1. CARGAR DATOS DEL CLIENTE Y TAREAS
    client = APIClient()
    ficha_id = st.session_state.get("ficha_cliente_id")
    
    if not ficha_id:
        st.error("❌ No se encontró ID de cliente.")
        st.stop()
    
    # Cargar tareas existentes
    tasks_data = client.get_tasks(ficha_id)
    
    if not tasks_data or tasks_data.get("total_tasks", 0) == 0:
        st.info("📋 No hay tareas asignadas aún. El equipo de Pixely Partners está preparando tu plan de acción personalizado.")
        st.markdown("---")
        st.markdown("""
        ### 🎯 ¿Qué son los Hilos de Trabajo?
        
        Los **Hilos de Trabajo** son tu hoja de ruta ejecutable, diseñada específicamente para tu marca.
        
        **Nuestro equipo:**
        1. Analiza los insights de tu marca (Q1-Q10)
        2. Crea un plan de acción personalizado con tareas priorizadas
        3. Organiza las tareas en un Sprint de 4 semanas
        4. Te acompaña durante toda la ejecución
        
        Las tareas aparecerán aquí cuando estén listas. 🚀
        """)
        st.stop()
    
    # 2. HEADER DE PROGRESO (GAMIFICACIÓN)
    total_tareas = tasks_data.get("total_tasks", 0)
    tareas_completadas = tasks_data.get("completed_tasks", 0)
    progreso = tareas_completadas / total_tareas if total_tareas > 0 else 0
    
    # Calcular días transcurridos desde la primera tarea creada
    from datetime import datetime, timedelta
    
    # Obtener la fecha de creación de la primera tarea (la más antigua)
    all_tasks = (tasks_data.get("week_1", []) + tasks_data.get("week_2", []) + 
                 tasks_data.get("week_3", []) + tasks_data.get("week_4", []))
    
    if all_tasks:
        # Encontrar la tarea más antigua
        oldest_task = min(all_tasks, key=lambda t: t.get('created_at', '9999-12-31'))
        created_at_str = oldest_task.get('created_at', '')
        
        try:
            # Parsear la fecha (formato ISO: "2025-11-21T20:35:35.123456")
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            today = datetime.now()
            
            # Calcular días transcurridos
            dias_transcurridos = (today - created_at).days + 1  # +1 para incluir el día actual
            dias_transcurridos = max(1, dias_transcurridos)  # Mínimo 1 día
        except:
            dias_transcurridos = 1
    else:
        dias_transcurridos = 1
    
    total_dias = 30
    progreso_dias = min(dias_transcurridos / total_dias, 1.0)  # No más de 100%

    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1:
        st.subheader(f"🗓️ ESTADO DEL SPRINT: DÍA {dias_transcurridos} DE {total_dias}")
        st.progress(progreso_dias)
    with col_prog2:
        st.markdown(f"""
            <div class="progress-metric">
                <h3 style="margin: 0; color: #FF1493;">{tareas_completadas}/{total_tareas}</h3>
                <p style="margin: 0; font-size: 0.85rem; color: #999;">Tareas Completadas</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. ESTRUCTURA DE SEMANAS (TABS)
    tab_w1, tab_w2, tab_w3, tab_w4 = st.tabs([
        f"🔥 SEMANA 1 ({len(tasks_data.get('week_1', []))} tareas)", 
        f"🎯 SEMANA 2 ({len(tasks_data.get('week_2', []))} tareas)", 
        f"📢 SEMANA 3 ({len(tasks_data.get('week_3', []))} tareas)", 
        f"🚀 SEMANA 4 ({len(tasks_data.get('week_4', []))} tareas)"
    ])

    # Función helper para generar el link de WhatsApp
    def get_whatsapp_link(task_title):
        phone = "51940239253"  # Número de WhatsApp de Pixely
        message = f"Hola equipo Pixely, necesito asesoría con la tarea: '{task_title}' del dashboard."
        encoded_message = message.replace(" ", "%20").replace("'", "%27").replace('"', "%22")
        return f"https://wa.me/{phone}?text={encoded_message}"

    # Mapeo de estado a valores del select
    STATUS_OPTIONS = ["⏳ Pendiente", "🏃 En Curso", "✅ ¡Hecho!", "🎯 Revisado"]
    STATUS_TO_DB = {
        "⏳ Pendiente": "PENDIENTE",
        "🏃 En Curso": "EN_CURSO",
        "✅ ¡Hecho!": "HECHO",
        "🎯 Revisado": "REVISADO"
    }
    DB_TO_STATUS = {
        "PENDIENTE": "⏳ Pendiente",
        "EN_CURSO": "🏃 En Curso",
        "HECHO": "✅ ¡Hecho!",
        "REVISADO": "🎯 Revisado"
    }

    # Función para renderizar una tarjeta de acción con datos REALES
    def render_action_card(task):
        task_id = task.get('id')
        impact_score = task.get('score_impacto', 0)
        impact_badge = '<span class="impact-badge-high">🔥 IMPACTO ALTO</span>' if impact_score > 75 else '<span class="impact-badge-med">⚡ IMPACTO MEDIO</span>'
        task_title = task.get('title', 'Tarea sin título')
        task_description = task.get('description', '')
        area = task.get('area_estrategica', 'General')
        urgencia = task.get('urgencia', 'MEDIA')
        current_status_db = task.get('status', 'PENDIENTE')
        
        # Convertir status de BD a display
        current_status_display = DB_TO_STATUS.get(current_status_db, "⏳ Pendiente")

        with st.container():
            st.markdown(f"""
            <div class="action-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <h4 style="margin:0; color:#ffffff; flex: 1;">{task_title}</h4>
                    <div>{impact_badge}</div>
                </div>
                <p style="color:#999; font-size: 0.85rem; margin-bottom: 10px;">
                    📋 Área: <strong>{area}</strong> | 
                    ⏰ Urgencia: <strong style="color: {'#FF1493' if urgencia == 'CRÍTICA' else '#FFA500' if urgencia == 'ALTA' else '#4ECDC4'}">{urgencia}</strong> | 
                    💯 Score: <strong>{impact_score}</strong>
                </p>
            """, unsafe_allow_html=True)
            
            # Mostrar descripción detallada si existe
            if task_description:
                with st.expander("📋 Ver descripción detallada"):
                    st.markdown(f"<p style='color: #ddd; line-height: 1.6;'>{task_description}</p>", unsafe_allow_html=True)

            col_act1, col_act2, col_act3 = st.columns([2, 3, 2])
            
            with col_act1:
                # Selectbox para estado con callback
                current_index = STATUS_OPTIONS.index(current_status_display)
                
                new_status_display = st.selectbox(
                    "Estado:", 
                    STATUS_OPTIONS,
                    index=current_index,
                    key=f"status_{task_id}",
                    label_visibility="collapsed"
                )
                
                # Si cambió el estado, actualizar en la BD
                if new_status_display != current_status_display:
                    new_status_db = STATUS_TO_DB[new_status_display]
                    result = client.update_task_status(task_id, new_status_db)
                    if result:
                        st.success(f"✅ Estado actualizado")
                        st.rerun()
            
            with col_act2:
                # Input para notas
                note_content = st.text_input(
                    "Notas:", 
                    placeholder="¿Qué tal fue? Añade tus notas...", 
                    key=f"notes_input_{task_id}",
                    label_visibility="collapsed"
                )
                
                # Si hay contenido, mostrar botón para guardar
                if note_content:
                    if st.button("💾 Guardar Nota", key=f"save_note_{task_id}"):
                        result = client.add_task_note(task_id, note_content)
                        if result:
                            st.success("✅ Nota guardada")
                            st.rerun()
            
            with col_act3:
                # EL GANCHO: Botón de WhatsApp
                whatsapp_link = get_whatsapp_link(task_title)
                st.markdown(f"""
                    <div style="text-align: right; padding-top: 5px;">
                        <a href="{whatsapp_link}" target="_blank" class="whatsapp-button">
                            🆘 ASESORÍA WA
                        </a>
                    </div>
                """, unsafe_allow_html=True)
            
            # Mostrar notas existentes
            notes = client.get_task_notes(task_id)
            if notes and len(notes) > 0:
                with st.expander(f"📝 Ver notas ({len(notes)})"):
                    for note in notes:
                        note_id = note.get('id')
                        created_at = note.get('created_at', '')[:19]
                        content = note.get('content', '')

                        st.markdown("<div class=\"note-item\">", unsafe_allow_html=True)
                        st.write(f"📅 {created_at}")
                        edit_content = st.text_area(
                            "Editar nota:",
                            value=content,
                            key=f"note_edit_content_{note_id}",
                            label_visibility="collapsed",
                            height=100
                        )
                        cols_note = st.columns([1, 1])
                        with cols_note[0]:
                            if st.button("💾 Guardar cambios", key=f"save_edit_note_{note_id}"):
                                result = client.update_task_note(task_id, note_id, edit_content)
                                if result:
                                    st.success("✅ Nota actualizada")
                                    st.rerun()
                        with cols_note[1]:
                            if st.button("🗑️ Eliminar", key=f"delete_note_{note_id}"):
                                ok = client.delete_task_note(task_id, note_id)
                                if ok:
                                    st.success("✅ Nota eliminada")
                                    st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

    # 4. RENDERIZAR LAS TAREAS EN LAS PESTAÑAS
    # SEMANA 1: Quick Wins
    with tab_w1:
        st.markdown("#### 🔥 Foco: Apagar fuegos y victorias rápidas")
        st.write("Tareas de máxima prioridad que requieren atención inmediata.")
        st.write("")
        
        week1_tasks = tasks_data.get("week_1", [])
        if week1_tasks:
            for task in week1_tasks:
                render_action_card(task)
        else:
            st.success("✨ ¡Excelente! No hay tareas para esta semana.")

    # SEMANA 2: Alineación
    with tab_w2:
        st.markdown("#### 🎯 Foco: Alineación de identidad y narrativa")
        st.write("Ajustar personalidad de marca y marcos narrativos para mejor percepción.")
        st.write("")
        
        week2_tasks = tasks_data.get("week_2", [])
        if week2_tasks:
            for task in week2_tasks:
                render_action_card(task)
        else:
            st.info("⏰ No hay tareas asignadas para esta semana.")
    
    # SEMANA 3: Amplificación
    with tab_w3:
        st.markdown("#### 📢 Foco: Amplificación y conexión con influencers")
        st.write("Potenciar alcance, engagement y colaboraciones estratégicas.")
        st.write("")
        
        week3_tasks = tasks_data.get("week_3", [])
        if week3_tasks:
            for task in week3_tasks:
                render_action_card(task)
        else:
            st.info("⏰ No hay tareas asignadas para esta semana.")
        
    # SEMANA 4: Consolidación
    with tab_w4:
        st.markdown("#### 🚀 Foco: Consolidación y planificación futura")
        st.write("Revisar evolución, medir resultados y establecer estrategia post-partnership.")
        st.write("")
        
        week4_tasks = tasks_data.get("week_4", [])
        if week4_tasks:
            for task in week4_tasks:
                render_action_card(task)
        else:
            st.info("⏰ No hay tareas asignadas para esta semana.")
    
    st.markdown("---")
    st.info("💡 **Recuerda:** Cada tarea tiene un botón de asesoría por WhatsApp. No dudes en contactarnos para maximizar los resultados.")

