> Nota (modo single-client): Documento adaptado al modo "single-client" — las correlaciones temporales y anomalías se calculan sobre datos del cliente y su histórico; no se generan comparativas externas con competidores.

Por supuesto. A continuación, se presenta el análisis estructurado de **Q8: Comportamiento Temporal**, siguiendo el formato riguroso de sus fuentes y centrándose en el **Máximo Rendimiento** mediante el **Diagnóstico de Eventos Contextualizado**.

El objetivo de Q8 es migrar de unndose en el **Máximo Rendimiento** mediante el **Diagnóstico de Eventos Contextualizado**.

El objetivo de Q8 es migrar de un simple gráfico de tendencias a un sistema de alerta que no solo detecte picos o caídas (*anomalías*), sino que también las vincule con la **causa semántica** (tópicos y publicaciones) que las generó, cumpliendo así con el requisito de correlación del *framework*.

---

## Análisis Estructurado de Q8: Comportamiento Temporal

##### Objetivo

El objetivo de Q8 (`q8_comportamiento_temporal`) es mapear la respuesta del público a lo largo del tiempo para identificar patrones y eventos significativos. El **Máximo Rendimiento** se logra al transformar el análisis de tendencias en un **Diagnóstico de Eventos Contextualizado**:

1.  Construir una **serie temporal unificada** de polaridad (sentimiento positivo/negativo) y temas dominantes, agregada por intervalos semanales.
2.  Identificar las **Top 3 Anomalías** (picos o valles abruptos de sentimiento).
3.  Vincular cada anomalía con la **publicación específica** (`post\_url`) y la **causa primaria** (tópico dominante) que la generó.

##### Prompt Literal Completo

**Q8 utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Este *prompt* debe ser hiperdetallado para forzar la correlación entre la fecha, el sentimiento y el tópico, y para exigir la identificación de la causa. Este prompt se implementa en el módulo `orchestrator/pipelines/social_media/analysis_modules/q8_comportamiento_temporal.py` (implícito).

| Elemento del Prompt | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rol** | Analista de Series Temporales y Correlación experto, responsable de mapear la respuesta del público a lo largo del tiempo. | |
| **Tarea** | Analizar todos los comentarios, utilizando su **fecha (`timestamp`)** para construir una serie temporal de sentimiento y temas. Identificar las **Top 3 Anomalías** (picos o caídas). | |
| **Inputs de Datos** | Una lista de comentarios, donde cada comentario incluye su **`text`**, **`timestamp`** y **`post_url`** (esencial para la contextualización). | |
| **Instrucciones de Cálculo y Salida** | 1. **Serie Temporal:** Generar una lista de objetos, uno por semana, que contenga: `fecha_semana`, `porcentaje_positivo`, `porcentaje_negativo` y el `topico_dominante` de esa semana. 2. **Detección de Anomalías:** Identificar y estructurar las 3 anomalías más significativas. Para cada anomalía, reportar la fecha, el sentimiento dominante y la **`post_url` de la publicación más viral** asociada al evento. | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La vinculación de picos de sentimiento con la `post\_url` y el tópico dominante transforma a Q8 en un **sistema de alerta y diagnóstico**, permitiendo una intervención inmediata. | |
| **Punto Débil (Metodología)** | La **calidad del *timestamp*** en los datos de entrada es crítica. Si la ingesta no garantiza fechas consistentes en el *DataFrame* de comentarios, el análisis temporal será inválido. | |
| **Mitigación de Errores** | El Orquestador debe utilizar el decorador `@retry` (3 intentos con 15 segundos de espera) para la solicitud de OpenAI, y `response_format={"type": "json_object"}` para asegurar la estructura de salida y evitar fallos de formato. | |

##### Outputs

El *output* JSON debe ser una **estructura anidada** que permita la visualización de la tendencia y la alerta de los eventos, alineándose con el esquema Pydantic **`Q8ComportamientoTemporalCompleto`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) |
| :--- | :--- | :--- |
| **`serie_temporal_semanal`** | `List[Dict]` - Lista de objetos por semana, con polaridad y tópico dominante. | **CRÍTICO:** `api/schemas.py` debe tener modelos que definan esta estructura de lista anidada. |
| **`anomalias_detectadas`** | `List[Dict]` - Lista de los Top 3 eventos, incluyendo `fecha`, `sentimiento_dominante` y **`post_url_viral`**. | **CRÍTICO:** La API debe validar y almacenar esta lista de alertas contextualizadas. |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | El nuevo *payload* JSON de Q8 incluye estructuras anidadas (listas de objetos para la serie temporal y las anomalías). Los esquemas Pydantic deben ser modificados para aceptar y validar esta complejidad. | |
| **Crear Modelos Pydantic** | Se necesitan modelos que definan la estructura de `serie_temporal_semanal` y `anomalias_detectadas` para que la API actúe como **Guardián** de la integridad de los datos. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe centrarse en la **contextualización de los eventos** en el Frontend (Streamlit/Plotly), en lugar de ser un gráfico de líneas pasivo.

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) |
| :--- | :--- | :--- |
| **1. Gráfico Principal** | **Gráfico de Líneas** y **Scatter Plot Superpuesto**. | El gráfico de líneas muestra la tendencia semanal del Sentimiento Positivo/Negativo. Se superpone un *Scatter Plot* (marcadores) en las fechas de las `anomalias_detectadas`. |
| **2. Marcadores Contextuales** | **Coloración Condicional y Tooltip Integrado**. | Los marcadores de anomalía se colorean (Verde para Positivo, Rojo para Negativo). El *tooltip* (al pasar el cursor) debe mostrar el **tópico dominante** de esa semana, cumpliendo con el análisis de series temporales temáticas. |
| **3. Panel de Diagnóstico** | **Cards de Alerta Prioritaria**. | Se utiliza un componente de Streamlit para mostrar las Top 3 anomalías, mostrando la URL (`post\_url\_viral`) y la causa primaria (`tópico dominante`), permitiendo al ejecutivo acceder al contenido viral de forma inmediata. |
| **4. Gráfico de Correlación Temática** | **Gráfico de Barras Segmentado**. | Un selector permite al usuario hacer *drill-down* en una semana anómala, mostrando la distribución de tópicos **solo durante ese período** para aislar la causa primaria del pico/valle. |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Débil (Funcionalidad)** | La eficacia de la visualización depende de que la API de la IA pueda generar el campo `topico_dominante` de manera consistente en la serie temporal. | |
| **Dependencia del Guardián** | La modificación de los esquemas Pydantic para `Q8ComportamientoTemporalCompleto` es una **modificación obligatoria** en `api/schemas.py` para evitar el fallo de validación de la API. | |
| **Metáfora** | La mejora convierte a Q8 en un **Electrocardiograma (ECG) con monitor de bolsa de valores**. Muestra el ritmo del corazón de la marca (sentimiento) y localiza los **puntos de arritmia** (anomalías), proporcionando la **ficha del paciente** (`post\_url`) que causó el evento, permitiendo la intervención inmediata. | |