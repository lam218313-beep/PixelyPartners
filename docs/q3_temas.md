> Nota (modo single-client): Este documento está adaptado al modo "single-client"; los ejemplos y las métricas asumen datos del cliente y/o baselines históricos internos. No se realizan comparativas frente a competidores externos.

Silenciosamente, asumiremos que se refiere al **Análisis Q3: Tópicos Principales (Modelado de Tópicos)**.

El Análisis Q3, al ser un *framework* cualitativo que se beneficia de la granularidad, sigue la misma estrategia arquitectónica que Q1 (Emociones) y Q2 (Personalidad de Marca): se debe obligar a la IA a desagregar el análisis por **`post_url`** y la API debe estar lista para validar esta estructura anidada.

A continuación, se presenta el análisis estructurado de **Q3: Tópicos Principales**, utilizando el formato detallado de sus fuentes y centrado en la implementación del **Máximo Rendimiento**.

---

## Análisis Estructurado de Q3: Tópicos Principales (Modelado de Tópicos)

##### Objetivo

El objetivo de Q3 (`q3_temas_principales`) es identificar los temas clave tratados por la audiencia de la marca. Para extraer el **Máximo Rendimiento**, debemos migrar de una lista agregada a una **herramienta de diagnóstico semántico y de contenido** que permita:

1.  Determinar la frecuencia porcentual y el sentimiento promedio de los tópicos globales.
2.  Desagregar el análisis para mostrar la distribución de tópicos y el sentimiento asociado **para cada publicación única** (`post\_url`).
3.  Permitir al Frontend filtrar y rankear los **Top 5 posts** que tienen mayor concentración de un tópico seleccionado.

##### Prompt Literal Completo

**Q3 utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Este *prompt* debe ser **hiperdetallado** para forzar la granularidad y la integración del sentimiento. Este prompt se ubicaría en el módulo `orchestrator/pipelines/social_media/analysis_modules/q3_temas.py`.

| Elemento del Prompt | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rol** | Eres un experto en Modelado de Tópicos (Topic Modeling) y Análisis de Sentimiento. | |
| **Tarea** | Analiza **CADA UNO** de los comentarios proporcionados. Aplica modelado de tópicos para identificar los principales temas, clasifica el **tópico dominante** y su **sentimiento** (Positivo, Neutro, Negativo). | |
| **Inputs de Datos** | Una lista de comentarios, donde cada comentario incluye su **text** y su **post\_url**. | |
| **Instrucciones de Cálculo y Salida** | **1. Análisis General:** Calcula la frecuencia porcentual y el sentimiento promedio de los principales tópicos para el **100% de los comentarios**. **2. Análisis por Publicación:** Para **cada publicación única** (`post\_url`), calcula la distribución de tópicos porcentual y el sentimiento promedio asociado a esos tópicos **solo dentro de esa publicación**. **3. Output JSON:** Debe incluir las claves `analisis_agregado` y la lista `analisis_por_publicacion`. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La desagregación por `post\_url` es el motor de la interactividad. Permite vincular la discusión de un tópico específico (ej. "Precios") con el contenido específico que lo impulsó. | |
| **Punto Débil (Metodología)** | La efectividad del *topic modeling* por la IA depende de la claridad del *prompt* y el volumen de datos. El Orquestador debe asegurar que la lista de comentarios enviada al LLM contenga la **`post_url`** para que la IA pueda agrupar correctamente. | |

##### Outputs

El *output* JSON debe ser una **estructura anidada y compleja** que el **Guardían** pueda aceptar. El esquema Pydantic asociado es **`Q3TemasCompleto`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic |
| :--- | :--- | :--- |
| **`analisis_agregado`** | `Dict` o `List[Dict]` - Lista de tópicos globales con frecuencia y sentimiento promedio. | Validado por `Q3TemasCompleto`. |
| **`analisis_por_publicacion`** | `List[Dict]` - Lista de objetos donde cada objeto representa una publicación (`post\_url`) y contiene la distribución de tópicos y sentimiento para ese *post*. | **CRÍTICO:** `api/schemas.py` debe tener un modelo que valide esta lista anidada. |

##### Modificación de la Arquitectura de la API (El Guardián)

Esta es una **modificación obligatoria y crítica**.

*   **Acción Requerida:** Se deben crear nuevos modelos **Pydantic** en `api/schemas.py` para modelar con precisión la granularidad por publicación (la lista `analisis_por_publicacion`).
*   **Validación:** El esquema principal **`SocialMediaInsightCreate`** debe actualizarse para que su campo `q3_temas_principales` referencie el nuevo modelo complejo `Q3TemasCompleto`. Si esto no se realiza, el *payload* enriquecido enviado por el Orquestador será **rechazado por la API**, ya que no encajará en la "forma" de datos definida por el Guardián.

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe destacar la distribución temática y permitir la **consulta interactiva** en el Frontend.

| Gráfico | Tipo de Visualización | Propósito (Máximo Rendimiento) | Fuente |
| :--- | :--- | :--- | :--- |
| **Gráfico 1: Tópicos Globales** | **Gráfico de Burbujas** o de Barras. | La visualización de burbujas es óptima, donde el **tamaño** es la frecuencia y el **color** es el sentimiento promedio. | |
| **Gráfico 2: Posts con Mayor Concentración Tópica** | **Selector de Tópicos** (Streamlit `selectbox`) y Gráfico de Barras por Post. | Permite seleccionar un tópico (ej. "Precio"). El Frontend utiliza **Pandas** para consultar el `analisis_por_publicacion` y encontrar las **5 `post\_url`** que tienen la mayor concentración porcentual de ese tópico. | |
| **Gráfico 3: Tópicos por Publicación** | **Selector de Publicaciones** y Gráfico de Burbujas. | El usuario selecciona una `post\_url`. Se renderiza el gráfico de burbujas temáticas **solo para los comentarios de esa publicación**, validando visualmente la granularidad de la IA. | |

##### Puntos Débiles o Medidas de Contingencia

*   **Dependencia Estricta:** El módulo `q3_temas.py` depende de que la clase `Q3TemasCompleto` sea importable y coincida con la definición del Guardián.
*   **Procesamiento Frontend:** La complejidad visual y la interactividad (Gráfico 2 y 3) requieren que el Frontend (Streamlit) utilice la librería **Pandas** para convertir la lista anidada (`analisis_por_publicacion`) en un `DataFrame` consultable.