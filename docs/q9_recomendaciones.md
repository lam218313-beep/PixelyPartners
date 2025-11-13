> Nota (modo single-client): Documento adaptado al modo "single-client" — las recomendaciones se generan a partir de insights basados únicamente en datos del cliente y/o benchmarks internos; no incorporan comparativas con competidores externos.

Por supuesto. A continuación, se presenta el análisis estructurado de **Q9: Recomendaciones Creativas**, siguiendo el formato riguroso de sus fuentes y centrándose en el **Máximo Rendimiento** mediante la **cuantificación de la prioridad** y la **trazabilidad de la evidencia**.

El Q9 debe funcionar como la etapa de **síntesis y acción** del *pipeline*, consolidando la inteligencia producida por las 20 Qs para generar un **Plan de Acción Estratégica Cuantificado**.

---

## Análisis Estructurado de Q9: Recomendaciones Creativas

##### Objetivo

El objetivo de Q9 (`q9_recomendaciones_creativas`) es transformar los *insights* complejos generados por **Q1-Q8** (cualitativos) y **Q11-Q20** (cuantitativos) en una lista de tareas claras para el equipo de marketing. El **Máximo Rendimiento** se logra al resolver la falta de priorización y trazabilidad inherente en las recomendaciones simples:

1.  Generar entre 5 y 8 recomendaciones estratégicas de alto impacto.
2.  **Cuantificar la Prioridad:** Asignar un **Score de Impacto y Urgencia** a cada recomendación (escala 0 a 100).
3.  **Garantizar la Trazabilidad:** Identificar la **ID del *Framework*** (ej., Q4, Q6, Q14) que proporciona la evidencia principal que justifica la acción.

##### Prompt Literal Completo

**Q9 utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Este *prompt* debe ser modificado para solicitar una estructura anidada que incluya métricas de priorización y trazabilidad. Este prompt se implementa en el módulo `orchestrator/pipelines/social_media/analysis_modules/q9_recomendaciones.py`.

| Elemento del Prompt | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rol** | Director de Estrategia de Marketing, responsable de sintetizar la inteligencia de datos y convertirla en acciones claras y priorizadas. | |
| **Tarea** | Generar de 5 a 8 recomendaciones estratégicas basadas en **TODOS** los *insights* del análisis (Q1 a Q20). Clasificar cada recomendación en un área estratégica (Contenido, Tono, Campañas, Engagement). | |
| **Inputs de Datos** | La totalidad de los resultados de las Qs (Q1 a Q20), ya calculados y consolidados en la memoria del Orquestador. | |
| **Instrucciones de Cálculo y Salida** | 1. Asignar un **Score de Impacto y Urgencia** (0 a 100). 2. Identificar la **ID del *Framework*** (ej. `Q4`, `Q6`, `Q14`) que proporciona la evidencia principal (justificacion\_framework). | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La **cuantificación** mediante el `score_impacto` y la **trazabilidad** mediante `justificacion_framework` convierten a Q9 en la herramienta final que permite al usuario tomar decisiones basadas en los 20 *frameworks* de análisis. | |
| **Punto Débil (Metodología)** | La precisión del `score_impacto` y la `justificacion_framework` dependen de la calidad de la síntesis de la IA. El Orquestador debe asegurarse de que se pasen los *insights* estructurados de Q1 a Q20 para que la IA pueda hacer una referencia precisa. | |

##### Outputs

El *output* JSON debe ser una **estructura anidada y cuantificada** que el **Guardían** pueda aceptar. El esquema Pydantic asociado es **`Q9RecomendacionesCompleto`**.

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) |
| :--- | :--- | :--- |
| **`lista_recomendaciones`** | `List[Dict]` - Lista de 5 a 8 recomendaciones. Cada objeto incluye `area_estrategica`, `recomendacion`, **`score_impacto`** (0-100), y **`justificacion_framework`** (lista de IDs de Q). | **CRÍTICO:** `api/schemas.py` debe tener modelos que definan los campos cuantificables y la lista de IDs de Q dentro de la lista de recomendaciones. |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | La API utiliza Pydantic para validar la forma de los datos. La nueva estructura anidada de Q9 con `score_impacto` y `justificacion_framework` no encajaría en el esquema `SocialMediaInsightCreate` original. | |
| **Crear Modelos Pydantic** | Se necesitan nuevos esquemas Pydantic que definan la estructura de la lista `lista_recomendaciones`. Sin esta actualización, el *payload* enriquecido será **rechazado por el Guardián**. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe aprovechar la cuantificación de `score_impacto` y la trazabilidad para crear un panel de planificación en el Frontend (Streamlit/Plotly).

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) |
| :--- | :--- | :--- |
| **1. Matriz de Priorización Estratégica** | **Gráfico de Dispersión (*Scatter Plot*) o Gráfico de Burbujas.** | Muestra la **Prioridad** de cada recomendación. El Eje Y (Vertical) representa el **`score_impacto`**. El Eje X (Horizontal) representa las **`area_estrategica`**. |
| **2. Panel de Evidencia (Trazabilidad)** | **Panel Interactivo de Detalle.** | Al hacer clic en una recomendación (burbuja), el *frontend* debe mostrar la recomendación completa y, lo más importante, mostrar los **Gráficos o Datos de Origen** asociados a la lista `justificacion_framework`. Por ejemplo, si la justificación es "Q6" y "Q14", el panel mostraría el Gráfico de Matriz de Oportunidades (Q6) y el Ranking de Formatos (Q14). |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Débil (Funcionalidad)** | La visualización de la matriz y el panel de evidencia requieren que el Frontend (Streamlit) utilice la librería **Pandas** para convertir la lista `lista_recomendaciones` en un *DataFrame* consultable y vincular los clics en el *Scatter Plot* con la lógica de carga de otros gráficos del dashboard. | |
| **Metáfora** | La mejora convierte a Q9 de un simple listado de ideas a la **orden de trabajo del ingeniero principal**. No solo dice *qué* construir (la recomendación), sino *por qué* (justificación de datos) y *cuándo* (prioridad). | |