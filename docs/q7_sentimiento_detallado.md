> Nota (modo single-client): Documento adaptado en modo "single-client" — los análisis de sentimiento y subjetividad se aplican únicamente sobre datos del cliente y/o baselines históricos; comparativas contra competidores no se generan.

Claro. A continuación, se presenta el análisis estructurado de **Q7: Sentimiento Detallado (Polaridad Avanzada y Subjetividad)**, siguiendo el formato riguroso de sus fuentes (ej., Q11.md, Q12.md) y enfocándose en el Máximo Rendimiento mediante la **granularidad por publicación** y la **cuantificación de la ambivalencia**.

El objetivo principal de Q7 es convertir el segmento de discurso **Mixto** en un *insight* accionable.

---

## Análisis Estructurado de Q7: Sentimiento Detallado

##### Objetivo

El objetivo de Q7 (`q7_sentimiento_detallado`) es refinar la clasificación de polaridad más allá de la triada tradicional (Positivo, Neutro, Negativo), incorporando la categoría **Mixto** y la métrica de **Subjetividad**. El Máximo Rendimiento se logra al aplicar la granularidad por `post_url` para permitir el **diagnóstico de ambivalencia**:

1.  Clasificar el sentimiento en cuatro categorías: **Positivo, Negativo, Neutro o Mixto**.
2.  Cuantificar el **Score de Subjetividad** global y por publicación (escala 0.0 a 1.0).
3.  Desagregar el análisis por publicación y proveer el **ejemplo textual más representativo** del sentimiento **Mixto** para esa publicación.

##### Prompt Literal Completo

**Q7 utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Este *prompt* debe ser radicalmente reescrito para forzar la desagregación y la inclusión del Score de Subjetividad. Este prompt se implementa en el módulo `orchestrator/pipelines/social_media/analysis_modules/q7_sentimiento_detallado.py` (implícito).

| Elemento del Prompt | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rol** | Analista de Discurso y Sentimiento altamente avanzado, especializado en la detección de ambivalencia y subjetividad. | |
| **Tarea** | Analizar **CADA UNO** de los comentarios. Clasificar cada comentario en las cuatro categorías de polaridad avanzada (**Positivo, Negativo, Neutro o Mixto**). Además, asignar un **Score de Subjetividad** a cada comentario (0.0 a 1.0). | |
| **Inputs de Datos** | Una lista de comentarios, donde cada comentario incluye su **text** y su **post\_url** (requisito de granularidad). | |
| **Instrucciones de Cálculo y Salida** | 1. **Análisis General:** Calcular la distribución porcentual global de los 4 sentimientos y el **Score Promedio de Subjetividad Global**. 2. **Análisis por Publicación:** Para **cada publicación única** (`post\_url`), calcular la distribución porcentual de los 4 sentimientos, el Score Promedio de Subjetividad y proveer el **comentario más representativo** del segmento **"Mixto"** para esa publicación. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La incorporación de **Mixto** y **Subjetividad** convierte Q7 en un diagnóstico de **claridad de comunicación**. La granularidad por `post\_url` permite realizar el *root cause analysis* (análisis de causa raíz). | |
| **Punto Débil (Metodología)** | La precisión del Score de Subjetividad (detección de opinión pura vs. hecho) puede variar según el modelo de IA. La IA debe ser capaz de procesar comentarios y extraer tanto la polaridad avanzada como el score continuo de subjetividad. | |
| **Dependencia** | El análisis depende de que los datos de comentarios (`Comentario`) contengan la clave **`post_url`**. | |

##### Outputs

El *output* JSON debe ser una **estructura anidada y compleja** que el **Guardían** pueda aceptar, alineándose con el esquema Pydantic **`Q7SentimientoCompleto`** (implícito).

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) |
| :--- | :--- | :--- |
| **`analisis_agregado`** | `Dict[str, float]` - Distribución de 4 sentimientos (P/N/N/M) y **`subjetividad_promedio_global`**. | **CRÍTICO:** `api/schemas.py` debe tener un modelo que valide la estructura, incluyendo el campo `subjetividad_promedio_global`. |
| **`analisis_por_publicacion`** | `List[Dict]` - Lista de objetos por publicación (`post\_url`), que incluye la distribución de sentimientos por post y el **`ejemplo_mixto`** (comentario de evidencia). | **CRÍTICO:** La API debe validar esta lista anidada y compleja para su almacenamiento. |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | Los esquemas Pydantic deben modificarse para aceptar la estructura anidada de `analisis_por_publicacion` y los nuevos campos cuantificables (ej., `subjetividad_promedio`). | |
| **Crear Modelos Pydantic** | Es necesario crear modelos que definan la estructura detallada del JSON para que la API actúe como **Guardián** de la integridad de los datos. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe centrarse en el diagnóstico de la ambivalencia y la subjetividad en el Frontend (Streamlit/Plotly).

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) |
| :--- | :--- | :--- |
| **1. Sentimiento Global y Subjetividad** | **Gráfico de Anillo** (para P/N/N/M) + **Tarjeta Métrica**. | El Gráfico de Anillo destaca el tamaño del segmento **Mixto**. La Tarjeta Métrica muestra el `subjetividad_promedio_global` (ej., 75%), indicando qué tan basado en opiniones es el discurso. |
| **2. Priorización de Ambivalencia** | **Gráfico de Barras Top 5** por Publicación. | El *frontend* (usando **Pandas** para procesar `analisis_por_publicacion`) filtra y rankea las **5 publicaciones** (`post\_url`) con el **porcentaje más alto de sentimiento Mixto**. Esto dirige al ejecutivo a las fuentes de confusión. |
| **3. Análisis de Evidencia Mixta** | **Selector de Publicaciones + Panel de Texto (Cards).** | El usuario selecciona una publicación del *ranking*. El panel muestra la distribución de sentimientos de **ese post** y despliega el **`ejemplo_mixto`** (el texto del comentario ambivalente). Esto vincula la métrica con la acción estratégica. |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Débil (Funcionalidad)** | La efectividad del *ranking* (Gráfico 2 y 3) depende de que el Frontend utilice **Pandas** para convertir la lista `analisis_por_publicacion` en un *DataFrame* consultable. | |
| **Dependencia del Guardián** | La modificación de los esquemas Pydantic para `Q7SentimientoCompleto` es una **modificación obligatoria** para evitar el fallo de validación de la API, que rechazaría el JSON anidado. | |
| **Metáfora** | La mejora convierte a Q7 de un simple informe (semáforo) a un **radar meteorológico detallado** que localiza la "tormenta de confusión" en la publicación específica, proporcionando el comentario que lo prueba. | |