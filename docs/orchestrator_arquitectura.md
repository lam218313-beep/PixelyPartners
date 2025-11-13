Este documento detalla la **Arquitectura del Motor Central (Orquestador)**, centrada en el archivo `orchestrator/pipelines/social_media/analyze.py` y sus componentes modulares. El objetivo es ilustrar cómo esta capa ejecuta la lógica de **Máximo Rendimiento** trabajando en modo "single-client" (análisis y entregables exclusivamente sobre un único cliente), gestiona la complejidad de los datos (Pandas/AI) y se acopla estrictamente con el **Guardián Pydantic** (la API).

---

# ARQUITECTURA DEL ORQUESTADOR: `analyze.py`

## I. ROL Y ESTRUCTURA CENTRAL DEL ORQUESTADOR

El servicio **Orquestador** es el "Motor" o la "Grúa" responsable de la ejecución de los **20 *frameworks* de análisis (Q1 a Q20)** en modo cliente-único (single-client). Reside en un contenedor independiente, definido por `orchestrator.Dockerfile`, y está programado para ejecutarse periódicamente (ej., 6:00 AM y 2:00 PM) mediante el servicio `cron`.

### 1. Modularidad Funcional (Aislamiento de Lógica)

La arquitectura de Máximo Rendimiento se basa en la **modularidad funcional**. En lugar de un archivo monolítico, la lógica de cálculo y generación de *insights* de cada *framework* (Qx) está aislada en su propio módulo (ej., `q14_efectividad_formatos.py`, `q12_comunidad.py`), asegurando el **aislamiento de errores**. Si un cálculo estadístico complejo, como la **Regresión Predictiva (Q19)**, falla, no detiene la ejecución de análisis esenciales como **Q1 (Emociones)**.

## II. INFRAESTRUCTURA DE `orchestrator/pipelines/social_media/analyze.py`

El archivo `analyze.py` centraliza la configuración, la gestión de datos, la autenticación y el control de errores.

### 1. Configuración y Dependencias

El *core* del Orquestador (`analyze.py`) se inicializa con importaciones de librerías para manejar tanto la lógica cuantitativa como la cualitativa:
*   **Cuantitativas/Estadísticas:** `pandas`, `numpy`, y librerías estadísticas como `scipy.stats` y `statsmodels.api` (esenciales para el **ANOVA en Q14** y la **Regresión en Q19**).
*   **API/Validación:** Importa **todos** los **Esquemas Pydantic Complejos** (ej., `Q1EmocionesCompleto`, `Q16BenchmarkCompetitivo`, `Q20KpiGlobal`) desde `api.schemas`. Esto es crítico para asegurar que el *payload* final coincida con la estructura que el Guardián espera.

### 2. Autenticación y Conexión Asíncrona

El Orquestador debe autenticarse contra la API para obtener los datos de entrada y, crucialmente, para enviar el *payload* final (`SocialMediaInsightCreate`).
*   **Credenciales:** Utiliza `ORCHESTRATOR_USER` y `ORCHESTRATOR_PASSWORD` cargados desde `.env`.
*   **Cliente HTTP:** Emplea `httpx.AsyncClient` para peticiones asíncronas.
*   **Control de Errores:** La función auxiliar `api_request` está decorada con **`@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))`**, mitigando fallos transitorios de red o de la API.

### 3. Manejo de la IA (GPT)

Las Qs cualitativas (Q1 a Q10) dependen de la correcta ejecución de las llamadas a OpenAI, gestionadas por `get_openai_completion`:
*   **Cliente:** Utiliza `AsyncOpenAI` con la clave `OPENAI_API_KEY`.
*   **Mitigación de Errores Críticos:** La función de *completion* está protegida por un decorador **`@retry(stop_after_attempt(3), wait_fixed(15))`**.
*   **Estructura del Output:** Obliga a que la respuesta de la IA sea JSON estructurado mediante **`response_format={"type": "json_object"}`**. Esto evita que la IA genere formatos ficticios o texto libre que el Guardián Pydantic rechazaría.
*   **Nota Single-Client:** Los prompts y la evidencia solicitada deben limitarse a los datos del cliente (posts, comentarios y metadatos incluidos en `ingested_data.json`). No se deben incluir ni solicitar datos de competidores; cualquier campo de "paisaje competitivo" debe ser opcional o ignorado por el Orquestador.

## III. ESTÁNDARES DE EJECUCIÓN MODULAR (QX)

### 1. Estándar Cualitativo (Granularidad y Evidencia)

Para alcanzar el Máximo Rendimiento, el Orquestador debe preparar los datos de entrada para la IA con el identificador de publicación (`post_url`).

| Estrategia de Prompt (Qx) | Propósito de Máximo Rendimiento | Requisito de Datos de Entrada |
| :--- | :--- | :--- |
| **Q1 (Emociones) / Q2 (Personalidad)** | Exigir `analisis_por_publicacion`. | La lista de comentarios debe incluir `text` y **`post_url`**. |
| **Q4 (Marcos Narrativos)** | Exigir `analisis_por_publicacion` y la **evidencia textual** (`ejemplos_narrativos`) para la trazabilidad. | Los datos de comentarios deben ser accesibles para la IA. |
| **Q9 (Recomendaciones)** | Exigir **`score_impacto`** (0-100) y **`justificacion_framework`** (ID de Q de origen). | Requiere que **TODAS** las Qs previas (Q1-Q8, Q11-Q20) hayan producido su *output* correctamente. |

### 2. Estándar Cuantitativo (Pandas, Normalización y Contexto)

La lógica de cálculo reside directamente en los módulos de Python/Pandas del Orquestador y depende de la integración con **Q16 (Benchmark Competitivo)**.

| Framework (Qx) | Lógica de Cálculo Central | Integración Crítica (Q16 / Benchmark Interno) |
| :--- | :--- | :--- |
| **Q11, Q13, Q17** | Calculan los valores absolutos (ER, Frecuencia, NSS) y `serie_temporal`. | Consumirán baselines internos (media y desviación calculadas sobre ventanas históricas del mismo cliente) para generar indicadores normalizados y Z-Scores relativos al historial del cliente. |
| **Q12 (Comunidad)** | **Desbloqueado** al consumir los conteos de seguidores de la **Ficha Cliente**. | Calcula la posición del cliente respecto a su propio historial o a umbrales de referencia definidos por la consultoría (no requiere datos de terceros). |
| **Q14 (Formatos)** | Implementa la **normalización** (ER/Vistas) y ejecuta el **Análisis de Varianza (ANOVA)** para generar el **Valor P**. | Lógica estadística compleja que se aísla en su módulo y que puede compararse con ventanas históricas internas para detectar cambios significativos. |
| **Q16 (Benchmark Interno)** | **PRODUCE** la inteligencia crítica: calcula medias, desviaciones y percentiles sobre series históricas del propio cliente o sobre objetivos/benchmarks internos proporcionados por el negocio. | En modo single-client el benchmark es interno (histórico o target); no requiere ni consume perfiles de competidores externos. |
| **Q20 (KPI Global)** | Aplica la **Ponderación Estratégica** dinámica (basada en el `primary_business_goal` de la Ficha Cliente) a las métricas constituyentes (Q11, Q12, Q17). | Consume las métricas normalizadas y los Z-Scores internos para calcular un `z_score_kpi_global` relativo al histórico del cliente. |

## IV. FLUJO DE DATOS Y ACOPLAMIENTO CRÍTICO (EL GUARDIÁN)

La capa del Orquestador está fuertemente acoplada con la capa de la API, donde reside el **Guardián Pydantic** (`api/schemas.py`).

| Proceso | Rol del Orquestador | Acoplamiento Crítico (Fuente) |
| :--- | :--- | :--- |
| **Consolidación** | Combina los *outputs* JSON de Q1 a Q20 en un único `insight_payload` (modelo `SocialMediaInsightCreate`). | El Orquestador **debe** importar las **clases Pydantic complejas** de `api.schemas` para validar internamente el *payload* antes de enviarlo. El *payload* asume un único `client_id` y estructuras diseñadas para un solo cliente; campos relacionados con paisajes competitivos deben ser opcionales o estar ausentes. |
| **Validación** | Envía el `insight_payload` al *endpoint* de la API `/api/v1/social-media/insights`. | Si el *output* del Orquestador no coincide exactamente con la nueva estructura anidada (ej., la lista `analisis_por_publicacion` de Q1 o el `z_score_er` de Q11), la API lo **rechazará**. Dado el enfoque single-client, la API debe aceptar payloads sin `perfiles_competitivos` o campos relacionados con competidores. |
| **Data Ingesta (Input)** | El Orquestador consume datos de la API. Por ejemplo, para **Q12**, el Orquestador consulta la **Ficha Cliente** (`FichaCliente`) para obtener los conteos de seguidores, asumiendo que la API previamente aceptó los nuevos campos (`seguidores_instagram`, etc.). | Depende de la ingesta previa del `ingest_utils.py` y de la correcta definición de los modelos ORM (`models.py`) que incluyen `seguidores_instagram`. |

El Orquestador es la máquina de producción. La precisión de su resultado es doble: la precisión del cálculo (Pandas/AI) y la precisión de la **forma del JSON** (Pydantic), que es la única forma de garantizar que el *insight* se almacene correctamente.

---
**Metáfora Arquitectónica:**

Si la API es el **Guardián** que utiliza un molde exacto (los esquemas Pydantic) para asegurar que los datos no se corrompan, el **Orquestador** es el ingeniero que debe construir **20 componentes diferentes**. El Máximo Rendimiento exige que el Orquestador no solo construya componentes complejos (como los que llevan el **Z-Score** o la **Evidencia Anidada**), sino que se asegure de que cada uno se ajuste **perfectamente al molde estricto** del Guardián, garantizando que la carga entera del análisis (el *insight_payload*) sea aceptada.