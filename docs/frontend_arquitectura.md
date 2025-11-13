Este documento detalla la arquitectura del servicio **Frontend** de Pixely, construido en **Streamlit**, enfocándose en su rol como la capa de presentación modular que consume y traduce la inteligencia compleja generada por el Orquestador y validada por la API. Está orientado al modo *single-client*: todas las vistas y comparativas se generan a partir de datos del cliente (o de baselines internos), no de comparativas entre competidores.

---

# ARQUITECTURA DETALLADA DEL SERVICIO FRONTEND

## I. INFRAESTRUCTURA Y ENTORNOS DE CONSTRUCCIÓN

El Frontend existe como un microservicio independiente, orquestado por `docker-compose.yml`.

### A. `Dockerfile` (Construcción del Contenedor)
La construcción del contenedor del Frontend está definida en su propio `Dockerfile`.

| Fase | Archivo/Comando | Detalle Arquitectónico | Fuente |
| :--- | :--- | :--- | :--- |
| **Imagen Base** | `FROM python:3.11-slim` | Utiliza una imagen base de Python oficial y ligera. | |
| **Directorio de Trabajo** | `WORKDIR /app` | Establece el directorio de trabajo dentro del contenedor. | |
| **Dependencias** | `COPY requirements.txt` y `RUN pip install...` | Instala librerías críticas como **Streamlit**, **Pandas**, **Plotly**, y **`st-cookies-manager`**. | |
| **Puerto Expuesto** | `EXPOSE 8501` | El puerto por defecto que utiliza Streamlit. | |
| **Comando de Inicio (`CMD`)** | `CMD ["streamlit", "run", "app.py", ...]` | Comando que inicia la aplicación de Streamlit, asegurando la accesibilidad externa con `—server.address=0.0.0.0`. | |

### B. Dependencias Críticas
Las librerías instaladas vía `requirements.txt` son esenciales para el Máximo Rendimiento de la visualización:
*   **Streamlit:** Framework principal para construir el *dashboard* interactivo.
*   **Pandas:** Esencial para la manipulación y estructuración de los datos anidados del JSON antes de la visualización.
*   **Plotly:** Utilizado para generar todos los gráficos complejos e interactivos (ej., *Radar Chart*, *Scatter Plots* y *Gráficos de Barras Agrupadas*).
*   **`st-cookies-manager`:** Utilizado para gestionar la sesión y el *token* de autenticación JWT.

## II. LÓGICA DEL NÚCLEO DE LA APLICACIÓN: `app.py`

El archivo `frontend/app.py` actúa como el orquestador de la aplicación, manejando la sesión, la autenticación y la invocación de las vistas modulares.

### A. Autenticación y Sesión
*   **Conexión a la API:** La URL de conexión al *backend* está definida como `BACKEND_API_URL = "http://api:8000"`.
*   **Gestión de Tokens:** Utiliza `st_cookies_manager.EncryptedCookieManager` para gestionar las *cookies* de sesión.
*   **Login:** La función `login_user` realiza una petición `POST` al *endpoint* `/token` de la API para obtener el **Token JWT**.

### B. Consumo de Datos (API Fetching)
Las funciones de obtención de datos (`get_data_from_endpoint`, `get_q11_insight_for_client`, etc.) consumen la API del *backend*:
*   **Autorización:** Todas las solicitudes a la API incluyen el *token* JWT en el encabezado `Authorization: Bearer <token>`.
*   **Caché:** Utiliza el decorador **`@st.cache_data(ttl=X)`** para optimizar el rendimiento y evitar llamadas repetitivas a la API.
*   **Consumo Focalizado:** Se asume la existencia de *endpoints* específicos para obtener *insights* detallados (ej., `/api/v1/social-media/insights/client/{client_id}/q11`).

## III. ARQUITECTURA DE PRESENTACIÓN MODULAR: `view.py`

El archivo `frontend/pipelines/social_media/view.py` es el módulo central que organiza el *dashboard* de Redes Sociales, implementando la **Modularidad en la Presentación**.

### A. Desglose Modular
*   **Orquestación:** La función principal `draw_dashboard` utiliza pestañas (`st.tabs`) para organizar los 20 *frameworks* de análisis.
*   **Módulos de Vista:** La lógica de visualización para cada *framework* se aísla en archivos específicos (ej., `q11_view.py`, `q12_view.py`). Esto asegura que si una visualización es muy compleja (ej., el *Radar Chart* de Q16), su lógica no sature el archivo principal.

### B. Procesamiento de Datos Críticos (Uso de Pandas)
La implementación del Máximo Rendimiento obliga al Frontend a utilizar **Pandas** para procesar las estructuras JSON anidadas y complejas enviadas por el Orquestador.

| Tarea de Procesamiento | Frameworks Afectados | Razón Arquitectónica | Fuente |
| :--- | :--- | :--- | :--- |
| **Conversión a DataFrame** | Q1, Q2, Q3, Q7 | El *frontend* recibe la lista `analisis_por_publicacion` del JSON. Este debe ser convertido a un **DataFrame de Pandas** para realizar consultas (ej., `df.query()`). | |
| **Top 5 Ranking** | Q1, Q2, Q7, Q4 | Se utiliza Pandas para filtrar y ordenar el *DataFrame* (ej., encontrar las 5 `post_url` con el mayor porcentaje de sentimiento Mixto o una emoción específica). | |
| **Filtros Interactivos** | Q14, Q3, Q4 | Se consulta el *DataFrame* de Pandas para actualizar dinámicamente el gráfico cuando el usuario usa un `st.selectbox` para filtrar por `social_network` o `tópico`. | |

### IV. IMPLEMENTACIÓN VISUAL DE MÁXIMO RENDIMIENTO

La visualización traduce las métricas cuantificadas (Z-Scores, ANOVA, etc.) en un diagnóstico ejecutable, siempre en contexto del cliente único o de sus baselines internos.

### A. Elementos de Contextualización Interna / Baseline (Q11, Q12, Q13, Q16, Q17, Q20)
Las vistas que consumen datos *benchmarked* priorizan la contextualización interna:
*   **KPI Cards Baseline:** Las métricas clave (Q11 ER, Q17 NSS, Q13 Frecuencia) se muestran en tarjetas (`st.metric`). El color y un indicador se basan en el **Z-Score** calculado respecto al baseline interno (histórico del cliente o umbrales objetivos), para ofrecer un **diagnóstico instantáneo** (verde si supera el baseline/histórico, rojo si está por debajo).
*   **Gráfico de Radar (*Radar Chart*):** Para **Q16** el Radar Chart representa múltiples métricas del cliente contra su baseline o contra objetivos internos (no muestra competidores externos). Esto permite visualizar el perfil del cliente respecto a su propio histórico.
*   **Banner de Modo:** El Frontend mostrará una pequeña banda o banner que indique claramente "Modo: cliente único" y, cuando proceda, un aviso sobre que los comparativos competitivos están deshabilitados en esta configuración.
*   **Datos de Ejemplo para Cualitativos:** Las vistas Q1–Q10 pueden cargarse desde JSONs de ejemplo (presentes en `orchestrator/outputs/`) para permitir demos y pruebas sin ejecutar LLMs en tiempo real.

### B. Elementos de Granularidad y Causalidad (Q1, Q2, Q7, Q4, Q18)
La visualización debe exponer la evidencia textual y la desagregación por publicación:
*   **Selector de Publicaciones:** Componente `st.selectbox` que permite al usuario seleccionar una `post_url` para ver el perfil específico de sentimientos (Q7) o emociones (Q1) de esa publicación.
*   **Tooltip Integrado:** En gráficos como el *Scatter Plot* de **Q18 (Anomalías)** o el *Ranking* de **Q15 (Hashtags)**, el *tooltip* de Plotly se utiliza para mostrar la información cualitativa anidada (ej., **Tópico Dominante**, **Sentimiento Asociado**, o la **Clasificación de la Anomalía**).
*   **Panel de Evidencia (Q4, Q7):** Al seleccionar una publicación, el Frontend despliega el **ejemplo textual** más representativo (`ejemplo_mixto` en Q7 o `ejemplos_narrativos` en Q4), vinculando la métrica abstracta con la evidencia del comentario real.

### C. Elementos de Síntesis Ejecutiva (Q10, Q9)
La presentación final está jerarquizada:
*   **Alerta Prioritaria (Q10):** Se muestra en una **Tarjeta de Alerta Destacada** (`st.error` o `st.warning`) en la parte superior del *dashboard*, utilizando la clave `alerta_prioritaria` del JSON para forzar la atención ejecutiva.
*   **Matriz de Priorización (Q9):** Utiliza un **Gráfico de Dispersión** (*Scatter Plot*) donde el eje Y es el **`score_impacto`**. El *frontend* implementa la interactividad para mostrar el **Panel de Evidencia** de los *frameworks* de origen (`justificacion_framework`) al hacer clic en una burbuja.

---
**Metáfora Final de la Arquitectura del Frontend:**

El Frontend es la **Cabina de Control** de la nave. Recibe paquetes de datos complejos y crípticos (el JSON validado por Pydantic). Su arquitectura modular con **Pandas** y **Plotly** le permite **desempaquetar y ensamblar** estos datos en herramientas de navegación que no solo indican la velocidad (KPI Global), sino que también diagnostican la salud de cada motor (Z-Scores) y señalan dónde se concentran las oportunidades y los riesgos (Matriz de Priorización y Gráficos con Tooltips Semánticos).