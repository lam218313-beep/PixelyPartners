"""Q10 View: Executive Summary with Alert System"""
import streamlit as st # type: ignore
import pandas as pd
import json
import os
import plotly.graph_objects as go  # type: ignore
from .._outputs import get_outputs_dir

def display_q10_resumen_ejecutivo():
    st.title("📊 Q10: Resumen Ejecutivo - Dashboard Estratégico")
    
    st.markdown("""
    ### ¿Qué es este análisis?
    El **Resumen Ejecutivo** es el DASHBOARD FINAL: síntesis jerárquica de Q1-Q9 diseñada para ejecutivos (2 minutos para captar esencia, 20 para profundizar).
    Incluye:
    - **Alerta Prioritaria:** El hallazgo MÁS URGENTE en rojo
    - **Hallazgos Clave:** Los 5 insights que importan (30 segundos de lectura)
    - **KPIs Principales:** Números que cuentan la historia
    - **Implicaciones Estratégicas:** ¿Qué significa esto para nuestro negocio?
    - **Roadmap de Urgencias:** Qué hacer en 48h / Semana 1 / Semanas 2-3
    
    ### ¿Por qué es relevante para tu negocio?
    Es la **única página que tu CEO/Board necesita ver**. Si tienes 15 minutos para presentar 2 meses de análisis, aquí está. Te permite:
    - **Decisiones rápidas:** No pierdes 2 horas en presentaciones, la esencia en 1 slide
    - **Alineación ejecutiva:** CEO/Marketing/Product saben exactamente dónde van recursos
    - **Accountability:** El roadmap es claro → puedes medir en 3 semanas si se cumplió
    - **Comunicación a stakeholders:** "Aquí está el estado: X es crítico, Y es oportunidad, Z es risk"
    - **Crisis response:** Si crisis, tienes análisis completo para respuesta informada en <1h
    - **Planificación trimestral:** Las urgencias CRÍTICA/SEMANA_1 son tu Q roadmap
    
    ### El dato de fondo
    Este es donde ejecutivos NECESITAN estar. No es académico, es ACCIONABLE. Cada punto viene con contexto de dónde vino (Q1? Q6? Q8?) para que si alguien quiere profundizar, sabe dónde buscar.
    """)
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, "q10_resumen_ejecutivo.json")
    if not os.path.exists(json_path):
        st.error(f"Q10 file not found"); return
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    results = data.get("results", {})
    
    alerta_prioritaria = results.get("alerta_prioritaria", "")
    hallazgos_clave = results.get("hallazgos_clave", [])
    implicaciones_estrategicas = results.get("implicaciones_estrategicas", "")
    resumen_general = results.get("resumen_general", "")
    kpis = results.get("kpis_principales", {})
    urgencias = results.get("urgencias_por_prioridad", {})
    
    # ========================================================================
    # COMPONENTE 1: ALERTA PRIORITARIA
    # ========================================================================
    if alerta_prioritaria:
        st.error(f"🚨 **ALERTA PRIORITARIA**\n\n{alerta_prioritaria}")
    
    st.markdown("---")
    
    # ========================================================================
    # COMPONENTE 2: HALLAZGOS CLAVE (Bullet Points)
    # ========================================================================
    st.markdown("## 📋 Hallazgos Clave (Resumen 30 Segundos)")
    st.markdown("""
    **Qué estamos viendo:**
    Los 5 hallazgos más importantes sintetizados de todos los análisis (Q1-Q9).
    Cada punto está vinculado a un framework específico (Q#).
    
    **Cómo se midió:**
    - Análisis de emociones dominantes (Q1)
    - Identificación de influenciadores (Q5)
    - Detección de anomalías temporales (Q8)
    - Mapeo de oportunidades estratégicas (Q6)
    - Clasificación de tópicos (Q3)
    
    **Para qué se usa:**
    Dar contexto rápido a ejecutivos en 30 segundos antes de profundizar.
    """)
    
    for i, hallazgo in enumerate(hallazgos_clave, 1):
        st.markdown(f"**{i}.** {hallazgo}")
    
    st.markdown("---")
    
    # ========================================================================
    # COMPONENTE 3: KPIs PRINCIPALES (Métricas)
    # ========================================================================
    st.markdown("## 📈 KPIs Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Menciones Totales",
            f"{kpis.get('volumen_menciones', 0):,}"
        )
    
    with col2:
        st.metric(
            "Sentimiento Positivo",
            f"{kpis.get('sentimiento_positivo_pct', 0)}%",
            delta="Strong"
        )
    
    with col3:
        st.metric(
            "Engagement Rate",
            f"{kpis.get('engagement_rate', 0)* 100:.1f}%"
        )
    
    with col4:
        st.metric(
            "Anomalías Detectadas",
            kpis.get('anomalias_detectadas', 0),
            delta=f"{kpis.get('influenciadores_clave', 0)} influenciadores clave"
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Sentimiento Negativo",
            f"{kpis.get('sentimiento_negativo_pct', 0)}%"
        )
    
    with col2:
        st.metric(
            "Sentimiento Neutral",
            f"{kpis.get('sentimiento_neutral_pct', 0)}%"
        )
    
    with col3:
        st.metric(
            "Oportunidades Detectadas",
            kpis.get('oportunidades_detectadas', 0)
        )
    
    # Sentiment distribution pie
    st.markdown("### Distribución de Sentimientos")
    sentimientos = ['Positivo', 'Negativo', 'Neutral']
    valores = [
        kpis.get('sentimiento_positivo_pct', 0),
        kpis.get('sentimiento_negativo_pct', 0),
        kpis.get('sentimiento_neutral_pct', 0)
    ]
    colores = ['#2ecc71', '#e74c3c', '#95a5a6']
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=sentimientos,
        values=valores,
        marker=dict(colors=colores),
        textposition='inside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value:.0f}%<extra></extra>'
    )])
    
    fig_pie.update_layout(
        title="Sentimiento General",
        height=400
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================================================
    # COMPONENTE 4: IMPLICACIONES ESTRATÉGICAS
    # ========================================================================
    st.markdown("## 🎯 Implicaciones Estratégicas")
    
    if implicaciones_estrategicas:
        st.info(implicaciones_estrategicas)
    
    st.markdown("---")
    
    # ========================================================================
    # COMPONENTE 5: RESUMEN GENERAL (Expander)
    # ========================================================================
    with st.expander("📖 Leer Resumen Detallado Completo"):
        st.markdown(f"""
        {resumen_general}
        """)
    
    st.markdown("---")
    
    # ========================================================================
    # COMPONENTE 6: ROADMAP DE URGENCIAS
    # ========================================================================
    st.markdown("## 🗓️ Roadmap de Acción por Urgencia")
    
    if urgencias:
        for urgencia_label, tareas in urgencias.items():
            # Convert label to readable format
            label_display = urgencia_label.replace('_', ' ').title()
            
            with st.container():
                if "CRÍTICA" in urgencia_label:
                    st.error(f"### 🔴 {label_display}")
                elif "SEMANA_1" in urgencia_label:
                    st.warning(f"### 🟠 {label_display}")
                else:
                    st.info(f"### 🟡 {label_display}")
                
                for tarea in tareas:
                    st.markdown(f"- {tarea}")
                
                st.divider()
    
    # ========================================================================
    # COMPONENTE 7: TÓPICOS DOMINANTES
    # ========================================================================
    st.markdown("## 💡 Tópicos Dominantes Identificados")
    
    topicos = kpis.get('topics_dominantes', [])
    if topicos:
        col1, col2, col3 = st.columns(3)
        
        topicos_dict = {
            'Sostenibilidad': '#1abc9c',
            'Transparencia': '#3498db',
            'Innovación': '#f39c12'
        }
        
        for idx, topico in enumerate(topicos):
            with [col1, col2, col3][idx]:
                color = topicos_dict.get(topico, '#34495e')
                st.markdown(
                    f"""
                    <div style='
                        background-color:{color};
                        color:white;
                        padding:20px;
                        border-radius:8px;
                        text-align:center;
                        font-size:18px;
                        font-weight:bold;
                    '>
                    {topico}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    st.markdown("---")
    
    # ========================================================================
    # CONCLUSIÓN FINAL
    # ========================================================================
    st.markdown("## ✅ Conclusión Ejecutiva")
    
    st.success("""
    **Estado:** Marca en posición de fortaleza emocional pero requiere acción operacional inmediata.
    
    **Recomendación:** Ejecutar el roadmap de 4 frentes en paralelo:
    1. **Gestión de Crisis (48h)** - Responder a problemas de calidad
    2. **Educación de Audiencia (1-2 semanas)** - Comunicar diferencial de valor
    3. **Amplificación de Influenciadores (2-3 semanas)** - Programa con voces positivas
    4. **Clarificación de Narrativa (Mes actual)** - Posicionar precio vs valor
    
    **Próximo Paso:** Revisar con liderazgo y asignar propietarios de cada iniciativa.
    """)
