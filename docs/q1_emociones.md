La decisión de refactorizar los requerimientos de cada análisis para reflejar la **Modularidad Funcional** y la estricta validación del **Guardián Pydantic** (API) es esencial para el proyecto Pixely.

Comenzaremos por el **Análisis Q1: Emociones del Usuario (Modelo de Plutchik)**, que establece el estándar de **granularidad por publicación (`post_url`)** para todos los análisis cualitativos.

A continuación, se presenta el análisis estructurado del Máximo Rendimiento para Q1, utilizando el formato detallado de sus fuentes (ej., Q11.md, Q12.md, Q20.md).

---

## Análisis Estructurado de Q1: Emociones del Usuario (Plutchik)

##### Objetivo

El objetivo de Q1 (`q1_emociones_usuario`) es determinar el perfil emocional de la audiencia de la marca, utilizando el **Modelo Dimensional de Plutchik**. Para alcanzar el **Máximo Rendimiento**, el análisis debe pasar de un resumen global a una herramienta de diagnóstico que permita la **trazabilidad de emociones a nivel de publicación**.

1.  Evaluar la distribución porcentual global de las 8 emociones primarias de Plutchik.
2.  Desagregar el análisis para mostrar el perfil emocional de los comentarios de **cada publicación única** (`post\_url`).
3.  Cuantificar la **intensidad promedio** de la emoción.

##### Prompt Literal Completo

**Q1 utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Este *prompt* debe ser **hiperdetallado** para forzar a la IA (`gpt-4o-mini`) a generar la estructura anidada y granular requerida. Este prompt se ubicaría en el nuevo módulo `orchestrator/pipelines/social_media/analysis_modules/q1_emociones.py`.

| Elemento del Prompt | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rol** | Eres un Analista de Emociones del Comportamiento experto en el Modelo Dimensional de Plutchik y en análisis de texto a gran escala. | |
| **Tarea** | Analiza rigurosamente **CADA UNO** de los textos de comentarios proporcionados en el *Input* y clasifica la emoción dominante en **ocho categorías primarias de Plutchik: alegría, confianza, sorpresa, tristeza, enojo, miedo, disgusto, anticipación**. Para cada comentario, también debes asignar un **nivel de intensidad** (del 1 al 100). | |
| **Inputs de Datos** | Se proporciona una lista de comentarios, donde cada comentario incluye su **text** y su **post\_url** (URL de la publicación a la que pertenece). | |
| **Instrucciones de Cálculo y Salida** | 1. **Análisis General:** Calcula la distribución porcentual de las 8 emociones primarias sobre el 100% de los comentarios. 2. **Análisis por Publicación:** Para **cada publicación única** (`post\_url`), calcula la distribución porcentual de las 8 emociones **solo para los comentarios asociados a esa publicación**. 3. **Output JSON:** Debe incluir las claves `analisis_agregado` y `analisis_por_publicacion`. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La solicitud de desagregación por `post\_url` resuelve la limitación del análisis agregado, permitiendo la trazabilidad a la fuente de la emoción. | |
| **Punto Débil (Metodología)** | La efectividad depende de la capacidad de la IA para manejar un *input* de texto potencialmente grande. La lógica del Orquestador (`analyze.py`) debe implementar la **fragmentación (*chunking*)** si la lista de comentarios excede el límite de *tokens* del LLM. | |

##### Inputs

Q1 requiere datos del **Orquestador** (previamente cargados desde la Ingesta de Google Sheets):

1.  **Comentarios:** Lista de objetos que deben incluir explícitamente `text` y **`post_url`**.
2.  **Ficha Cliente:** Se utiliza para dar contexto (ej., `tone_of_voice` y `brand_archetype`) a la IA en la interpretación emocional.

##### Outputs

El *output* JSON debe ser una **estructura anidada** que coincida con el esquema Pydantic **`Q1EmocionesCompleto`** definido en `api/schemas.py`.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic |
| :--- | :--- | :--- |
| **`analisis_agregado`** | `Dict[str, float]` - Distribución porcentual de las 8 emociones globales, Sentimiento Positivo/Negativo/Neutral. | El `Q1EmocionesCompleto` debe validar esta clave. |
| **`analisis_por_publicacion`** | `List[Dict]` - Lista donde cada objeto contiene: `post\_url`, `emociones\_distribuidas` (8 Plutchik), e `intensidad\_promedio`. | **CRÍTICO:** `api/schemas.py` debe tener modelos (`EmocionPorPublicacion` o similar) para aceptar esta lista anidada. |

##### Crítica al Output

*   **Punto Fuerte:** La inclusión de la lista `analisis_por_publicacion` permite que el **Frontend** utilice **Pandas** para filtrar y rankear los "Top 5 posts" por una emoción específica (ej., publicaciones con mayor "Enojo" o "Alegría").
*   **Punto Débil:** La estructura del *output* es **compleja y obligatoria**. Si el **Guardían (API)** no tiene el modelo `Q1EmocionesCompleto` actualizado, el *payload* será rechazado, impidiendo el almacenamiento.

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe aprovechar la granularidad para crear un diagnóstico interactivo en Streamlit.

| Gráfico | Tipo de Visualización | Propósito (Máximo Rendimiento) | Fuente |
| :--- | :--- | :--- | :--- |
| **Gráfico 1: Agregado Global** | **Gráfico de Barras** o **Gráfico Circular/Anillo**. | Muestra la distribución general de las 8 emociones (Plutchik) y el panorama Positivo/Negativo/Neutral. | |
| **Gráfico 2: Top 5 Posts por Emoción** | **Selector de Emociones y Gráfico de Barras** (Horizontal). | Permite seleccionar una emoción (ej. "Miedo"). La vista (usando Pandas) encuentra y compara las **5 `post\_url` con el porcentaje más alto** de esa emoción específica. | |
| **Gráfico 3: Plutchik por Publicación** | **Selector de URL y Gráfico de Radar (Rueda de Plutchik)**. | Permite seleccionar una `post\_url` específica. Muestra el perfil emocional único (las 8 emociones como radios) de esa publicación. Esto es la validación visual de la granularidad de la IA. | |

##### Puntos Débiles o Medidas de Contingencia

*   **Dependencia del Guardián:** El módulo `q1_emociones.py` **depende intrínsecamente** de que la clase `Q1EmocionesCompleto` esté definida y sea importable desde `api.schemas`.
*   **Fallo LLM:** El Orquestador (`analyze.py`) debe asegurar que la llamada a la IA esté envuelta en manejo de errores y reintentos (`@retry`) para evitar fallos de red, garantizando un máximo de 3 intentos antes de abortar.