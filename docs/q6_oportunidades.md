> Nota (modo single-client): Documento adaptado al modo "single-client" — las oportunidades y la actividad competitiva descritas se calculan sobre datos del cliente, su histórico o baselines internos; las comparativas frente a competidores externos están deshabilitadas.

Absolutamente. Procederemos con el análisis estructurado de **Q6: Oportunidades de Mercado**, siguiendo el formato riguroso de las fuentes.

El objetivo de **Máximo Rendimiento** para Q6 es transformar las oportunidades detectadas de un simple texto con justificaciones en una **matriz estratégica cuantificable**, que permita a los ejecutivos medir la urgencia y el potencial de cada oportunidad.

---

## Análisis Estructurado de Q6: Oportunidades de Mercado

##### Objetivo

El objetivo de Q6 (`q6_oportunidades_mercado`) es identificar los nichos de conversación y temas no abordados por la marca que son relevantes para el mercado y cubiertos por la competencia. El Máximo Rendimiento se logra al generar una **Matriz de Priorización**, donde la inteligencia debe ser **cuantificable**:

1.  Identificar hasta **5 oportunidades** claras donde la conversación es escasa o ausente, pero es relevante estratégicamente.
2.  Para cada oportunidad, cuantificar el **Score de Urgencia/Gap** (Brecha Estratégica) y la **Actividad Competitiva**.
3.  Generar una recomendación accionable por oportunidad.

##### Prompt Literal Completo

**Q6 utiliza un *prompt* literal dirigido al modelo de IA (LLM)**. Este *prompt* debe ser modificado para obligar a la IA a cuantificar la brecha y el nivel de actividad de los competidores. Este prompt se implementa en el módulo `orchestrator/pipelines/social_media/analysis_modules/q6_oportunidades.py` (implícito).

| Elemento del Prompt | Descripción | Fuente |
| :--- | :--- | :--- |
| **Rol** | Eres un Consultor de Estrategia de Mercado experto en Análisis de Brechas (*Gap Analysis*) y en contextualización de inteligencia competitiva. | |
| **Tarea** | Analiza los comentarios y la Ficha Cliente (pilares de contenido, competencia, objetivos) para identificar **oportunidades de mercado y nichos no abordados** por la marca. Para cada oportunidad, debes estimar el tamaño de la brecha y el nivel de actividad de los competidores en ese tema. | |
| **Inputs de Datos** | Textos de comentarios (para detectar ausencias), Ficha Cliente (para pilares y competidores). | |
| **Instrucciones de Cálculo y Salida** | 1. Identifica hasta **5 oportunidades** claras. 2. Asigna un **Score de Urgencia/Gap** (de 0 a 100). 3. Estima la **Actividad Competitiva** (Baja, Media, Alta). 4. Genera una **Recomendación Accionable** (tipo de contenido o campaña). | |

##### Crítica al Cálculo

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Fuerte (Funcionalidad)** | La cuantificación mediante el **gap\_score** transforma la oportunidad cualitativa en un punto trazable en una matriz. Esto permite que la oportunidad sea **priorizada** automáticamente. | |
| **Punto Débil (Metodología)** | La precisión del *gap\_score* y la *actividad\_competitiva* depende de la capacidad de la IA para interpretar correctamente la información de la Ficha Cliente (pilares y competidores) y la ausencia de conversación en los datos. | |
| **Dependencia** | Q6 depende intrínsecamente de la **Ficha Cliente** para definir los pilares y la lista de competidores. | |

##### Outputs

El *output* JSON debe ser una **estructura anidada** que contenga la cuantificación de la urgencia y la competencia. El esquema Pydantic asociado es **`Q6OportunidadesCompleto`** (implícito).

| Clave del JSON | Estructura Esperada | Requisito de Pydantic (Guardían) |
| :--- | :--- | :--- |
| **`lista_oportunidades`** | `List[Dict]` - Lista de 5 oportunidades. Cada objeto incluye `tema`, `gap_score` (0-100), `actividad_competitiva` (string) y `recomendacion_accion`. | **CRÍTICO:** `api/schemas.py` debe tener modelos que definan los campos `gap_score` y `actividad_competitiva` dentro de la lista de oportunidades. |

##### Modificación de la Arquitectura de la API (El Guardián)

| Acción Requerida | Razón | Fuente |
| :--- | :--- | :--- |
| **Actualizar `api/schemas.py`** | La API (Guardían Pydantic) debe ser actualizada para validar y almacenar la nueva estructura JSON anidada y cuantificada, especialmente los campos `gap_score` y `actividad_competitiva`. | |
| **Crear Modelos Pydantic** | Se necesitan nuevos esquemas Pydantic que definan la estructura de la lista `lista_oportunidades`. Sin esto, el *payload* del Orquestador será rechazado. | |

##### La Forma en que Usa el Output para Visualizarse (Gráfico)

La visualización debe presentar Q6 como una **Matriz de Priorización Estratégica**, permitiendo una toma de decisiones inmediata sobre la inversión en contenido.

| Gráfico | Tipo de Visualización | Propósito y Cómo se Construye (Plotly/Streamlit) |
| :--- | :--- | :--- |
| **1. Matriz de Priorización Estratégica** | **Gráfico de Dispersión (*Scatter Plot*)**. | El eje Y (Vertical) representa la **Urgencia Estratégica** (`gap_score`). El eje X (Horizontal) representa la **Barrera de Entrada** (`actividad_competitiva`). |
| **2. Zonas de Acción** | **Coloración Condicional (Burbujas)**. | La zona superior izquierda (Alta Urgencia / Baja Competencia) debe ser la zona **Verde (Alta Prioridad)**. Los puntos en la zona inferior derecha (Baja Urgencia / Alta Competencia) serían de **Baja Prioridad (Roja)**. |
| **3. Detalle de Oportunidad** | **Etiqueta Interactiva / *Tooltip***. | Al pasar el cursor sobre una burbuja, el *tooltip* debe mostrar la descripción del `tema`, la `justificacion` y la `recomendacion_accion`, transformando la posición gráfica en contexto estratégico. |

##### Puntos Débiles o Medidas de Contingencia

| Punto | Descripción | Fuente |
| :--- | :--- | :--- |
| **Punto Débil (Funcionalidad)** | El rendimiento del Frontend depende de que la lista de oportunidades sea correctamente parseada y convertida a un **DataFrame de Pandas** para alimentar el *Scatter Plot* con sus ejes `gap_score` y `actividad_competitiva`. | |
| **Dependencia del Guardián** | La actualización de los esquemas Pydantic en `api/schemas.py` para `Q6OportunidadesCompleto` es una **modificación obligatoria** para evitar el fallo de validación de la API. | |
| **Valor de la Cuantificación** | La fiabilidad del análisis se basa en la capacidad de la IA para generar el `gap_score` de forma consistente, ya que este número es el motor de la matriz de priorización. | |