> Nota (modo single-client): Este documento está adaptado al modo "single-client"; todos los análisis y ejemplos se aplican exclusivamente sobre datos del cliente o benchmarks internos basados en su histórico. No se incluyen comparativas con competidores externos.

Silenciosamente, asumiremos que se refiere al **Análisis Q2: Personalidad de Marca (Modelo Aaker)**.

Al igual que con el Análisis Q1 (Emociones/Plutchik), el objetivo central de Q2 es transformar un *insight* cualitativo de resumen en una herramienta de diagnóstico que permita la **granularidad por publicación** y la **trazabilidad**. Esto obliga a modificar las tres capas de la arquitectura (Orquestador, API y Frontend).

A continuación, se presenta el análisis estructurado del **Máximo Rendimiento** para **Q2: Personalidad de Marca**, utilizando el formato detallado y riguroso establecido para las otras métricas.

---

## Análisis Estructurado de Q2: Personalidad de Marca (Modelo Aaker)

##### Objetivo

El objetivo de Q2 (`q2_personalidad_marca`) es determinar la percepción de la marca manifestada por la audiencia, clasificándola según los **cinco rasgos de Aaker: Sinceridad, Emoción, Competencia, Sofisticación y Robustez**. Para alcanzar el **Máximo Rendimiento**, se debe:

1.  Evaluar la distribución porcentual global de los 5 rasgos de Aaker a través de todos los comentarios.
2.  Desagregar el análisis para mostrar el perfil de personalidad de marca en los comentarios de **cada publicación única** (`post\_url`).
3.  Cuantificar la **intensidad promedio** del rasgo dominante a nivel de publicación.

##### Prompt Literal Completo

**Q2 utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Este *prompt* debe ser **hiperdetallado** para forzar a la IA a generar la estructura anidada y granular requerida. Este prompt se ubicaría en el nuevo módulo `orchestrator/pipelines/social_media/analysis_modules/q2_personalidad.py`.

| Elemento del Prompt | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rol** | Eres un Analista de Personalidad de Marca experto en el **Modelo de Aaker** y en contextualización estratégica. | |
| **Tarea** | Analiza **CADA UNO** de los comentarios. Clasifica la percepción manifestada en los **cinco rasgos de Aaker: sinceridad, emoción, competencia, sofisticación y robustez**. Para cada comentario, identifica el **rasgo dominante** y asigna un **puntaje de intensidad** (del 1 al 100) para ese rasgo. | |
| **Inputs de Datos** | Una lista de comentarios, donde cada comentario incluye su **text** y su **post\_url**. | |
| **Instrucciones de Cálculo y Salida** | **1. Análisis Agregado (Global):** Calcula la distribución porcentual global de los 5 rasgos de marca. **2. Análisis por Publicación (Granular):** Para **cada publicación única** (`post\_url`), calcula la distribución porcentual de los 5 rasgos **solo para los comentarios asociados a esa publicación**. **3. Output JSON:** Debe incluir las claves `analisis_agregado` y la lista `analisis_por_publicacion`. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La desagregación por `post\_url` permite al ejecutivo identificar qué publicaciones están **reforzando o debilitando** la personalidad de marca deseada (ej., un post que impulsa "Emoción" vs. otro que solo impulsa "Robustez"). | |
| **Punto Débil (Metodología)** | La IA requiere la **Ficha Cliente** (narrativa, arquetipo, tono de voz) para interpretar correctamente la *intención* y la *percepción* de marca, por lo que el *prompt* debe contextualizarse con estos datos. | |

##### Inputs

Q2 requiere datos del **Orquestador**:

1.  **Comentarios:** Lista de objetos que deben incluir explícitamente `text` y **`post_url`**.
2.  **Ficha Cliente:** Se utiliza para dar contexto a la IA sobre el **Arquetipo de Marca** y el **Tono de Voz**.

##### Outputs

El *output* JSON debe ser una **estructura anidada** que coincida con el esquema Pydantic **`Q2PersonalidadCompleta`** definido en `api/schemas.py`.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic |
| :--- | :--- | :--- |
| **`analisis_agregado`** | `Dict[str, float]` - Distribución porcentual de los 5 rasgos de Aaker a nivel global. | El `Q2PersonalidadCompleta` debe validar esta clave. |
| **`analisis_por_publicacion`** | `List[Dict]` - Lista donde cada objeto contiene: `post\_url`, `rasgos\_distribuidos` (5 rasgos porcentuales), e `intensidad\_promedio`. | **CRÍTICO:** `api/schemas.py` debe tener modelos (`RasgosPorPublicacion` o similar) para aceptar esta lista anidada. |

##### Crítica al Output

*   **Punto Fuerte:** El *output* JSON con granularidad permite que el Frontend use **Pandas** para implementar el **Gráfico de Top 5 Posts por Percepción**, filtrando y rankeando las publicaciones más efectivas para cada rasgo.
*   **Punto Débil:** La API actúa como **Guardían**. Si el esquema Pydantic para `Q2PersonalidadCompleta` no está implementado para aceptar la lista `analisis_por_publicacion`, el *payload* será rechazado.

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe destacar la posición relativa y permitir la trazabilidad de la percepción.

| Gráfico | Tipo de Visualización | Propósito (Máximo Rendimiento) | Fuente |
| :--- | :--- | :--- | :--- |
| **Gráfico 1: Perfil Global** | **Gráfico de Barras Aaker** (o Gráfico de Radar). | Muestra el perfil general de la marca (los 5 rasgos) según la percepción de la audiencia. | |
| **Gráfico 2: Top 5 Posts por Percepción** | **Selector de Rasgo** (Streamlit `selectbox`) y Gráfico de Barras por Post. | Permite seleccionar un rasgo (ej. "Sinceridad"). El *frontend* encuentra y compara las **5 `post\_url` que generaron la mayor proporción o intensidad de ese rasgo**. | |
| **Gráfico 3: Aaker por Publicación** | **Selector de URL** y Gráfico de Radar/Barras. | El usuario selecciona una `post\_url`. Se muestra el perfil de los 5 rasgos de Aaker **únicamente para los comentarios de esa publicación**. | |

##### Puntos Débiles o Medidas de Contingencia

*   **Dependencia del Guardián:** El módulo `q2_personalidad.py` **depende intrínsecamente** de que la clase `Q2PersonalidadCompleta` esté correctamente definida y sea importable desde `api.schemas`.
*   **Procesamiento Frontend:** El módulo de vista debe implementar la lógica **Pandas** para convertir la lista `analisis_por_publicacion` en un `DataFrame` consultable, lo cual es la clave para alimentar los selectores interactivos y la lógica de "Top 5 posts".
*   **Consistencia de Datos:** La implementación de Q2, junto con Q1, Q3, Q4, Q7 y Q18, requiere que los datos de entrada de comentarios contengan la clave **`post_url`** para que la IA pueda realizar la agregación granular.