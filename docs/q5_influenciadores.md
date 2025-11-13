> Nota (modo single-client): Documento adaptado al modo "single-client" — los criterios de identificación y polaridad de influenciadores se calculan solo sobre los datos del cliente y/o baselines internos; no se comparan perfiles externos.

Continuando con la estructuración de los *frameworks* cualitativos de Máximo Rendimiento, a continuación, se presenta el análisis estructurado de **Q5: Influenciadores Clave**, utilizando el formato detallado de las fuentes y centrándose en la **integración de la polaridad cualitativa** en la métrica de centralidad.

---

## Análisis Estructurado de Q5: Influenciadores Clave

##### Objetivo

El objetivo de Q5 (`q5_influenciadores_clave`) es identificar los nodos más influyentes dentro de la red social de la audiencia de la marca. Para lograr el **Máximo Rendimiento**, la métrica debe ser enriquecida con la **polaridad cualitativa**. Esto transforma el análisis de una simple métrica de centralidad a una **herramienta de gestión de crisis y amplificación de marca**.

1.  Identificar los **Top 10 Influenciadores** mediante métricas de centralidad.
2.  Para cada influenciador, determinar la **Polaridad Dominante** del discurso que amplifican (**Promotor - Positivo** o **Detractor - Negativo**).
3.  Adjuntar evidencia textual (el comentario más influyente) para contextualizar la influencia.

##### Prompt Literal Completo

**Q5 utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Este *prompt* debe ser modificado para obligar a la IA a realizar un análisis secundario de sentimiento en los comentarios de los *top influencers*. Este prompt se implementa en el módulo `orchestrator/pipelines/social_media/analysis_modules/q5_influenciadores.py` (implícito).

| Elemento del Prompt | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rol** | Eres un experto en Análisis de Redes Sociales, Centralidad y un analista de discurso. | |
| **Tarea** | Analiza los comentarios y menciones para identificar a los **Top 10 Influenciadores**. Para cada uno de estos 10 usuarios, realiza un análisis secundario de todos sus comentarios para determinar el **Sentimiento Dominante** del discurso que están amplificando: **Promotor (Positivo)** o **Detractor (Negativo)**. | |
| **Inputs de Datos** | Una lista de comentarios, donde cada comentario incluye **`ownerUsername`**, **`text`** (para extraer menciones y sentimiento) y **`post_url`** (para contexto). | |
| **Instrucciones de Cálculo y Salida** | 1. **Centralidad:** Calcula un *score* de centralidad para los 10 usuarios principales. 2. **Polaridad:** Determina la polaridad dominante (ej. Promotor si > 70% de su discurso es positivo). 3. **Evidencia:** Identifica el **comentario más influyente** (comentario\_evidencia) para cada usuario. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La integración del sentimiento y la centralidad permite al ejecutivo asignar una **bandera de riesgo (roja) o de oportunidad (verde)** a cada nodo de influencia. | |
| **Punto Débil (Metodología)** | La precisión depende de la capacidad de la IA para realizar correctamente el análisis de centralidad (usando menciones y replicación de contenido) y luego el análisis de sentimiento en ese subconjunto de comentarios. | |
| **Dependencia** | Requiere que los datos de entrada (`Comentario`) contengan el `ownerUsername` para rastrear al influenciador. | |

##### Outputs

El *output* JSON debe ser una **estructura anidada** que incluya la cuantificación de la centralidad y la polaridad. El esquema Pydantic asociado es **`Q5InfluenciadoresCompleto`** (implícito).

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) |
| :--- | :--- | :--- |
| **`top_influenciadores_detallado`** | `List[Dict]` - Lista de los Top 10 Influenciadores. Cada objeto incluye `username`, `score_centralidad`, **`polaridad_dominante`** y **`comentario_evidencia`**. | **CRÍTICO:** `api/schemas.py` debe tener modelos que definan la estructura de `top_influenciadores_detallado`. |
| **`resumen_polaridad`** | `Dict[str, int]` - Conteo de promotores vs. detractores. | Validado por `Q5InfluenciadoresCompleto`. |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | El nuevo *payload* JSON con la lista anidada `top_influenciadores_detallado` y campos como `polaridad_dominante` es complejo y sería rechazado por el esquema `SocialMediaInsightCreate` original. | |
| **Crear Modelos Pydantic** | Se necesitan nuevos modelos Pydantic que definan la estructura de cada influenciador, asegurando la integridad del campo `comentario_evidencia`. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe reflejar la dualidad Positivo/Negativo de la influencia, permitiendo una toma de decisiones inmediata sobre a quién mitigar o amplificar.

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) |
| :--- | :--- | :--- |
| **1. Influencia General** | **Gráfico de Barras Doble** o Gráfico de Red. | Muestra el *score* de centralidad. Las barras se **colorean condicionalmente** según la `polaridad_dominante` (verde para Promotor, rojo para Detractor). |
| **2. Filtro de Acción Estratégica** | **Selector de Polaridad** (Streamlit `selectbox`). | Permite al ejecutivo seleccionar "Promotores" o "Detractores". El Frontend (usando **Pandas**) filtra la lista `top_influenciadores_detallado` y muestra solo los Top 5 de la categoría elegida. |
| **3. Evidencia Narrativa (Deep Dive)** | **Cards de Perfil de Influencer** y *Tooltip* de Comentario. | Al seleccionar un usuario, se muestra su `score_centralidad` y, lo más crucial, el **`comentario_evidencia`**. Esto convierte la métrica abstracta en contexto real, esencial para el equipo de marketing. |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Débil (Funcionalidad)** | La eficiencia de la visualización (Gráfico 2 y 3) depende de que el Frontend (Streamlit) utilice la librería **Pandas** para procesar la lista anidada `top_influenciadores_detallado` y realizar el filtrado de Promotores/Detractores. | |
| **Dependencia del Guardián** | La actualización de los esquemas Pydantic en `api/schemas.py` para `Q5InfluenciadoresCompleto` es una **modificación obligatoria**. | |