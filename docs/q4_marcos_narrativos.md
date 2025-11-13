> Nota (modo single-client): Documento adaptado a modo "single-client" — los marcos, evidencias y métricas descritas se extraen exclusivamente de los datos del cliente o de baselines internos; las comparativas con competidores externos están deshabilitadas.

Absolutamente. Para el Análisis Q4: Marcos Narrativos, utilizaremos la estructura de sus fuentes (ej., Q11.md, Q12.md) y la **teoría del *Framing*** para asegurar el **Máximo Rendimiento** al forzar la granularidad por publicación y la trazabilidad de la evidencia textual.

Este enfoque se alinea con la arquitectura modular ya establecida, la cual requiere la modificación del Orquestador (para el *prompt* hiperdetallado), la API (para la validación Pydantic de la estructura anidada) y el Frontend (para la visualización de la matriz de priorización).

---

## Análisis Estructurado de Q4: Marcos Narrativos (Teoría del *Framing*)

##### Objetivo

El objetivo de Q4 (`q4_marcos_narrativos`) es determinar la **intención narrativa dominante** del discurso de la audiencia. El máximo rendimiento transforma esta métrica de discurso estática en un **diagnóstico dinámico** que responda: ¿Qué contenido específico está impulsando las narrativas aspiracionales o negativas?.

1.  Clasificar la intención narrativa en tres marcos: **Positivo**, **Negativo** o **Aspiracional**.
2.  Desagregar el análisis para mostrar la distribución de los marcos narrativos **para cada publicación única** (`post\_url`).
3.  Proporcionar el **comentario más representativo** (evidencia) para cada marco dentro de la publicación.

##### Prompt Literal Completo

**Q4 utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Este *prompt* debe ser **hiperdetallado** para forzar la granularidad y la extracción de evidencia textual. Este prompt se implementa en el módulo `orchestrator/pipelines/social_media/analysis_modules/q4_marcos_narrativos.py` (dentro del Orquestador).

| Elemento del Prompt | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rol** | Eres un experto en la **Teoría del *Framing*** de Entman y en análisis de discurso en redes sociales. | |
| **Tarea** | Analiza **CADA UNO** de los comentarios. Clasifica la intención narrativa dominante en tres marcos: **Positivo** (afirmaciones, satisfacción), **Negativo** (quejas, reclamos) o **Aspiracional** (sugerencias de mejora, deseos de futuro, potencial). | |
| **Inputs de Datos** | Una lista de comentarios, donde cada comentario incluye su `text` y su **`post_url`**. | |
| **Instrucciones de Cálculo y Salida** | 1. **Análisis General (Gráfico 1):** Calcula la distribución porcentual global de los 3 marcos narrativos. 2. **Análisis por Publicación (Granular):** Para **cada publicación única** (`post\_url`), calcula la distribución porcentual de los 3 marcos narrativos y proporciona el **comentario más representativo** (más de 10 palabras) como evidencia. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La desagregación por `post\_url` junto con la evidencia textual transforma el análisis en un **sistema de rastreo forense**. Permite saber si el discurso negativo se originó en una publicación específica. | |
| **Punto Débil (Metodología)** | La IA debe ser capaz de manejar la carga de trabajo de análisis granular y extracción de la mejor evidencia por marco y por publicación. | |
| **Dependencia** | El análisis depende de que los datos de comentarios de entrada contengan la clave **`post_url`**. | |

##### Outputs

El *output* JSON debe ser una **estructura anidada** que incluya la granularidad y la evidencia, y debe coincidir con el esquema Pydantic **`Q4MarcosCompleto`** (implícito) en `api/schemas.py`.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) |
| :--- | :--- | :--- |
| **`analisis_agregado`** | `Dict[str, float]` - Distribución porcentual global de los 3 marcos narrativos. | Validado por `Q4MarcosCompleto`. |
| **`analisis_por_publicacion`** | `List[Dict]` - Lista donde cada objeto contiene: `post\_url`, `distribucion\_marcos` (los 3 porcentajes) y **`ejemplos\_narrativos`** (texto de evidencia por marco). | **CRÍTICO:** `api/schemas.py` debe tener modelos (`analisis\_por\_publicacion` y `ejemplos\_narrativos`) para validar esta lista anidada. |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | El nuevo *output* JSON con la lista `analisis_por_publicacion` y `ejemplos_narrativos` es una estructura anidada que el esquema `SocialMediaInsightCreate` original **no aceptaría**. | |
| **Crear Modelos Pydantic** | Se deben crear nuevos modelos Pydantic (ej. `Q4MarcosCompleto`) que definan la estructura de `ejemplos_narrativos` y `analisis_por_publicacion` para que la API pueda actuar como **Guardián** de la integridad de los datos. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe transformar el discurso en una herramienta de planificación de contenido interactiva.

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) |
| :--- | :--- | :--- |
| **1. Distribución Global** | **Gráfico de Barras Apiladas** (100%) o Gráfico Circular. | Muestra la distribución general de los marcos narrativos (ej., 25% Negativo, 60% Positivo, 15% Aspiracional). |
| **2. Posts con Mayor Impacto de *Framing*** | **Selector de Marcos + Gráfico de Barras por Post.** | Permite al usuario seleccionar el marco "Aspiracional" o "Negativo". El Frontend (usando **Pandas** para procesar la lista granular) encuentra y compara las **5 `post\_url`** que generaron la mayor proporción de ese discurso. |
| **3. Análisis Narrativo por Publicación** | **Selector de Publicaciones + Cards de Evidencia.** | El usuario selecciona un `post\_url`. Se muestra un Gráfico de Barras aislado de los tres marcos para ese *post* y, **críticamente**, se muestran los **`ejemplos\_narrativos`** de los comentarios más representativos, proporcionando la **prueba textual directa** de la narrativa. |
| **4. Evolución del Discurso** | **Gráfico de Línea o Área Apilada Temporal.** | Muestra si la narrativa negativa o aspiracional está creciendo o disminuyendo con el tiempo, permitiendo la correlación con eventos de marketing (Integración con Q8). |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Débil (Funcionalidad)** | La eficacia depende de la precisión de la IA para seleccionar el "comentario más representativo". | |
| **Dependencia del Guardián** | El campo `q4_marcos_narrativos` requiere la actualización de `api/schemas.py`. Sin esta modificación, el JSON anidado del Orquestador será rechazado. | |
| **Procesamiento Frontend** | La funcionalidad de *ranking* y selección interactiva (Gráficos 2 y 3) depende de que el Frontend utilice **Pandas** para convertir la lista `analisis_por_publicacion` en un *DataFrame* consultable. | |