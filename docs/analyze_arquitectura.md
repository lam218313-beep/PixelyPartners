Este documento detalla la **Arquitectura de Máximo Rendimiento** del módulo `analyze.py` y sus componentes modulares asociados dentro del Orquestador de Pixely, reflejando el flujo de trabajo interno del sistema y sus puntos de acople con el **Guardián Pydantic** (la API).

La arquitectura se fundamenta en la **Modularidad de Cuatro Capas**.

> Nota (modo single-client): Todos los documentos y las componentes descritas en este archivo han sido adaptadas al modo "single-client". Eso significa que los análisis, visualizaciones y benchmarks se realizan exclusivamente sobre los datos del cliente (o sobre baselines/ventanas históricas del propio cliente). Las referencias a comparativas con competidores externos han sido reemplazadas por benchmarks internos o por umbrales objetivo.

---

# ARQUITECTURA DEL MOTOR CENTRAL: `orchestrator/pipelines/social_media/analyze.py`

## I. FILOSOFÍA DEL SISTEMA Y ESTRUCTURA DE CAPAS

La filosofía de Pixely es pasar de un análisis monolítico a un motor funcional modular.

### 1. Modularidad Funcional (El Motor de Cálculo)

El archivo `analyze.py` se refactoriza para funcionar como el **Orquestador Principal** de la capa funcional, encargándose de la configuración, autenticación y consolidación del *payload*. La lógica de cálculo específica de cada *framework* (Q1 a Q20) se aísla en módulos separados (ej., `q14_formatos.py`, `q12_comunidad.py`), asegurando que si un cálculo estadístico complejo (como la **ANOVA** en Q14 o la **Regresión Predictiva** en Q19) falla, no detenga el resto del análisis.

### 2. Capa Estructural (El Guardián Pydantic)

La **API** con FastAPI utiliza **Pydantic** en `api/schemas.py` como el **Guardián** del sistema. La implementación de la granularidad y la cuantificación (ej., **Z-Score**, **analisis\_por\_publicacion**) en Q1-Q20 requiere que los esquemas Pydantic sean **modificados obligatoriamente** para validar estas estructuras JSON complejas y anidadas. Sin esta actualización, la API rechazaría el *payload*.

---

## II. EL ORQUESTADOR PRINCIPAL: `analyze.py`

El archivo `orchestrator/pipelines/social_media/analyze.py` contiene la infraestructura para ejecutar los análisis cualitativos (vía OpenAI) y cuantitativos (vía Pandas).

| Componente | Función Principal | Fuentes Relevantes |
| :--- | :--- | :--- |
| **Setup y Dependencias** | Carga todas las librerías necesarias: `pandas`, `numpy`, librerías estadísticas (`scipy.stats`, `statsmodels.api`) para Q14 y Q19, y todas las clases **Pydantic Complejas** (`Q1EmocionesCompleto`, `Q16BenchmarkCompetitivo`, etc.) desde `api.schemas`. | |
| **Autenticación** | Utiliza `httpx` para autenticarse con la API interna de Pixely, obteniendo un *token* de acceso utilizando las credenciales `ORCHESTRATOR_USER` y `ORCHESTRATOR_PASSWORD` definidas en `.env`. | |
| **AI Client (OpenAI)** | Configura `AsyncOpenAI`. La función de *completion* utiliza el decorador **`@retry`** (3 intentos, 15s de espera) para mitigar fallos de red/API. Asegura la estructura JSON mediante `response_format={"type": "json_object"}`. | |
| **Control de Flujo** | Llama a las funciones modulares Qx. Consolida los *outputs* JSON de Q1 a Q20 en un único `insight_payload` antes de enviarlo a la API para su almacenamiento. | |

---

## III. ESTÁNDAR DE UN MÓDULO DE ANÁLISIS (QX)

Cada *framework* (Qx) está diseñado bajo la filosofía de Máximo Rendimiento, ya sea exigiendo granularidad a la IA (Cualitativas) o contexto estadístico a Pandas (Cuantitativas).

### A. Módulos Cualitativos (Q1, Q2, Q3, Q4, Q5, Q7, Q8, Q9, Q10)

Todos dependen de OpenAI y comparten dos requisitos arquitectónicos críticos: **Granularidad** y **Evidencia Anidada**.

| Framework (Qx) | Tipo de Lógica | Requisitos del Prompt Hiperdetallado (Orquestador) | Output JSON Crítico (API) |
| :--- | :--- | :--- | :--- |
| **Q1 Emociones** | AI/Plutchik | Exigir `analisis_por_publicacion` y `post_url` en el *input* para agrupar las 8 emociones por publicación. | Lista anidada `analisis_por_publicacion`. |
| **Q2 Personalidad** | AI/Aaker | Exigir la clasificación de los 5 rasgos de Aaker y la `intensidad_promedio` **por publicación**. | Lista anidada `analisis_por_publicacion`. |
| **Q3 Tópicos** | AI/Topic Modeling | Exigir la distribución de tópicos y sentimiento **por publicación**. | Lista anidada `analisis_por_publicacion` para Top 5 posts. |
| **Q4 Marcos Narrativos** | AI/Framing Entman | Exigir `analisis_por_publicacion` y el **`comentario más representativo`** (`ejemplos_narrativos`) como evidencia textual. | Estructura con `ejemplos_narrativos` anidados. |
| **Q7 Sentimiento Detallado** | AI/Polaridad Avanzada | Exigir `Score de Subjetividad` (0.0 a 1.0) y la identificación del `ejemplo_mixto` más representativo **por publicación**. | Campos `subjetividad_promedio_global` y lista `ejemplo_mixto`. |
| **Q9 Recomendaciones** | AI/Síntesis | Exigir el **`Score de Impacto y Urgencia`** (0-100) y la **`justificacion_framework`** (ID de Q de origen) para la trazabilidad. | Campos `score_impacto` y `justificacion_framework`. |

### B. Módulos Cuantitativos (Q11, Q12, Q13, Q14, Q15, Q17, Q19, Q20)

Estos módulos se basan en Pandas y en la integración del **Benchmark Competitivo (Q16)** para contextualizar las métricas con el **Z-Score**.

| Framework (Qx) | Lógica de Cálculo (Pandas/Stats) | Integración Crítica | Output JSON Esencial |
| :--- | :--- | :--- | :--- |
| **Q11 Engagement** | Cálculo de ER segmentado por `social_network` y `serie_temporal`. | **Q16:** Cálculo del **`z_score_er`**. | `z_score_er`, `engagement_segmentado_red`. |
| **Q12 Comunidad** | **Desbloqueado** por los datos de seguidores en la **Ficha Cliente**. Calcula el Z-Score basado en los competidores. | **Q16:** Obtiene la media y $\sigma$ de los competidores. | `z_score_tamano_comunidad`, `ranking_por_red_social`. |
| **Q13 Frecuencia** | Cálculo de frecuencia (posts/día) y **`consistencia_desviacion`** (desviación estándar). | **Q16:** Cálculo del **`z_score_frecuencia`**. | `consistencia_desviacion`, `z_score_frecuencia`. |
| **Q14 Formatos** | **Normalización:** Calcula ER / Vistas/Impresiones. **Validación:** Implementa **ANOVA** para el valor P (`p_value`). | **Q13/Q11:** Se utiliza para la correlación de eficiencia (Scatter Plot). | `ranking_por_red_social`, `p_value_general_anova`. |
| **Q15 Hashtags** | **Normalización:** ER normalizado, con filtro de umbral mínimo. **Efectividad Semántica:** Correlación con Q3 (Tópico) y Q17 (Sentimiento). | **Q3/Q17:** Para el enriquecimiento semántico (`topico_dominante`, `sentimiento_asociado`). | `er_normalizado`, `topico_dominante` (enriquecido). |
| **Q16 (Benchmark Interno)** | **CRÍTICO (Interno):** Calcula medias, desviaciones y percentiles sobre series históricas del propio cliente o sobre objetivos/benchmarks internos proporcionados por el negocio. Genera baselines que sirven para normalizar Q11, Q12, Q13 y Q17 sin depender de datos de terceros. | **Ficha Cliente / Histórico:** Utiliza datos del cliente y ventanas temporales históricas para generar el `benchmark_interno`. | `kpi_scores_cliente` (Z-Scores relativos al histórico), `benchmark_interno`. |
| **Q17 Sentimiento Agrupado** | **NSS:** Cálculo del Net Sentiment Score (%Positivo - %Negativo). | **Q16:** Cálculo del **`z_score_nss`** para contextualizar la salud emocional. | `net_sentiment_score`, `z_score_nss`, `serie_temporal_nss`. |
| **Q19 Correlación** | **Modelo Predictivo:** Regresión Lineal (preferiblemente multivariable). | **Q11, Q13, Q14:** Utiliza los *outputs* de estas Qs como variables de entrada. | `correlacion_r2`, `significancia_p`, `ecuacion_modelo`. |
| **Q20 KPI Global** | **Índice Ponderado:** Combina Q11, Q12, Q13, Q17 con ponderaciones dinámicas basadas en el `primary_business_goal` de la Ficha Cliente. | **Q16:** Cálculo del **`z_score_kpi_global`**. | `puntaje_final_escalado`, `z_score_kpi_global`, `contribucion_por_kpi`. |

---

## IV. EL GUARDIÁN DE DATOS: `api/schemas.py`

La capa de validación de la API es el punto más crítico para el Máximo Rendimiento.

| Archivo/Esquema | Acción Requerida | Impacto Arquitectónico |
| :--- | :--- | :--- |
| **`api/models.py`** | Inclusión de campos `seguidores_instagram`, etc., en la tabla **`FichaCliente`** para desbloquear Q12. | Desbloquea la ingesta de datos de posicionamiento de comunidad. |
| **`api/schemas.py`** | **Creación de Esquemas Anidados:** Se deben definir modelos Pydantic específicos (ej. `Q1EmocionesCompleto`, `Q14EfectividadFormatos`, `Q16BenchmarkCompetitivo`) que modelen la complejidad de las listas y métricas anidadas (ej. `analisis_por_publicacion`, `z_score_kpi_global`). | Define la "forma" de los datos enriquecidos que la API aceptará. |
| **`SocialMediaInsightCreate`** | **Actualización del Esquema Principal:** Los campos originales (`q1_emociones_usuario`, `q12_crecimiento_seguidores`, etc.) deben ser reemplazados de `Optional[str]` (o JSON simple) por los nuevos **modelos Pydantic Complejos**. | Si no se actualiza, la API **rechazará** el *payload* completo del Orquestador. |

---

## V. VISUALIZACIÓN Y SÍNTESIS (FRONTEND)

La capa de presentación (`frontend/pipelines/social_media/view.py`) consume el JSON validado y lo convierte en inteligencia accionable, utilizando la estructura anidada.

| Framework | Tipo de Visualización Clave | Lógica de Procesamiento |
| :--- | :--- | :--- |
| **Granularidad (Q1, Q2, Q3, Q7)** | **Gráficos Interactivos con Selector de Publicación**. | El Frontend debe usar **Pandas** para convertir la lista `analisis_por_publicacion` en un *DataFrame* consultable, esencial para la lógica de **Top 5 Posts** y filtros. |
| **Benchmark (Q11, Q12, Q13, Q17)** | **Gráfico de Radar (Q16)** y **KPI Cards con Z-Score**. | La visualización se colorea condicionalmente (verde/rojo) según el **signo del Z-Score** para un diagnóstico instantáneo frente al mercado. |
| **Síntesis Ejecutiva (Q10, Q9)** | **Alerta Prioritaria Destacada** y **Matriz de Priorización**. | El Q10 utiliza la clave `alerta_prioritaria` para mostrar un `st.error` o `st.warning` de Streamlit de forma destacada. El Q9 traza las recomendaciones en una **Matriz de Priorización** (Scatter Plot) utilizando el `score_impacto`. |

---

## VI. METÁFORA DEL SISTEMA

El sistema Pixely funciona como una **fábrica de ingeniería**: el **Orquestador** es la grúa que produce piezas de alta precisión (los *insights* JSON anidados y cuantificados). Para que esas piezas puedan ser almacenadas en el **Almacén Central (Base de Datos)**, la **API** debe actuar como un **Guardían** con plantillas de validación (**Pydantic en `schemas.py`**) perfectamente ajustadas. Si el *insight* (la "pieza") no encaja con la "forma" definida por el Guardián (los esquemas), es rechazado, garantizando la integridad de los datos complejos.