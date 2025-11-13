Este es un mapa estratégico detallado de la arquitectura integral del proyecto Pixely. El sistema está diseñado sobre una **arquitectura de microservicios** que garantiza el máximo rendimiento, la resiliencia y la trazabilidad de los datos, estructurado en **cuatro capas de modularidad** para prevenir fallos en cascada y asegurar la integridad de la información.

## 1. Modularidad Arquitectónica (La Infraestructura de Microservicios)

La base del proyecto está compuesta por siete servicios contenedores, orquestados mediante `docker-compose.yml`.

### A. La Capa de Persistencia (La Despensa)
*   **Base de Datos (`db`):** Utiliza **PostgreSQL** (`postgres:15-alpine`). Es un servicio aislado para la persistencia de datos. El servicio utiliza variables de entorno como `POSTGRES_USER` y `POSTGRES_PASSWORD` para sus credenciales.
*   **Healthcheck Crítico:** La Base de Datos incluye un `healthcheck` (`pg_isready`) con un intervalo de 5 segundos y 5 reintentos, lo que asegura que el servicio esté listo antes de que la API intente conectarse, garantizando el orden de inicio.
*   **Visualizador (`adminer`):** Proporciona una interfaz web para inspeccionar los datos en la DB.

### B. La Capa de Autenticación y Lógica (La Cocina)
*   **API (`api` - FastAPI):** Este es el **Guardián** del sistema. Es un servicio independiente que maneja la lógica de negocio y, crucialmente, la validación de datos.
    *   **Orden de Ejecución:** El comando de inicio (`command`) ejecuta primero las migraciones (`python migrate.py`) y luego inicia el servidor (`uvicorn`), pero solo después de que la DB esté `service_healthy`.
    *   **Seguridad:** Utiliza `auth.py` para la autenticación, con esquemas JWT (`HS256`) y hasheo de contraseñas (`argon2`, `bcrypt`). Expone *endpoints* para la creación de *tokens* (`/token`) y validación de usuario (`/users/me/`).

### C. La Capa del Motor (El Cronómetro)
*   **Orquestador (`orchestrator`):** Es un servicio separado cuya función principal es la ejecución de pipelines de IA y tareas programadas.
    *   **Automatización:** El `orchestrator.Dockerfile` instala el servicio **Cron**.
    *   **Programa:** El archivo `pixely-cron` define la ejecución programada de `run_pipelines.py` **todos los días a las 6:00 AM y a las 2:00 PM**.
    *   **Credenciales:** Utiliza `ORCHESTRATOR_USER` y `ORCHESTRATOR_PASSWORD` (definidas en `.env`) para autenticarse como cliente interno ante la API antes de enviar los *insights* procesados.

### D. La Capa de Presentación y Seguridad
*   **Frontend (`frontend` - Streamlit):** Servicio dedicado a la interfaz de usuario que consume la API. Utiliza una imagen `python:3.11-slim`. Expone el puerto **8501**, que es el que utiliza Streamlit.
*   **Nginx (`nginx`):** Actúa como *Reverse Proxy*.
*   **Certbot (`certbot`):** Gestiona los certificados SSL/TLS, preparado para HTTPS.

## 2. Modularidad Estructural (El Guardián Pydantic)

Esta es la capa más importante para garantizar el **Máximo Rendimiento** y la **Integridad de Datos**, ya que previene el **"Error del Guardián"**.

### A. Estricta Validación de Esquemas (`api/schemas.py`)
La API utiliza **Pydantic** para validar estrictamente la forma de los datos. Esto es vital porque los *frameworks* de Máximo Rendimiento (Q1-Q20) requieren estructuras de datos **anidadas y cuantificadas**:
*   **Reemplazo de Tipos Simples:** El esquema `SocialMediaInsightCreate` ya no utiliza tipos simples (`Optional[str]`) para las métricas Q, sino que debe utilizar nuevos modelos complejos (ej. `Q1EmocionesCompleto`, `Q20KpiGlobal`).
*   **Validación de Granularidad:** Se requiere definir modelos Pydantic anidados para aceptar listas como `analisis_por_publicacion`. Si el Orquestador envía un *payload* que no coincide exactamente con esta estructura, **la API lo rechaza**, manteniendo la integridad de la DB.

### B. Desbloqueo de KPIs por el Modelo ORM (`api/models.py`)
*   **Almacenamiento de Qs:** La tabla `SocialMediaInsight` almacena los resultados de los 20 *frameworks* utilizando columnas de tipo **JSON**.
*   **Desbloqueo de Q12:** Para resolver el estado "No Implementado" de **Q12: Posicionamiento de Comunidad**, la tabla `FichaCliente` fue modificada para incluir campos clave como `seguidores_instagram`, `seguidores_tiktok` y `seguidores_facebook`.

## 3. Modularidad Funcional (El Motor de Inteligencia)

El Orquestador es la "fábrica" que produce los *insights* complejos. La lógica de análisis se fragmenta para asegurar el **aislamiento de errores**.

### A. Modularidad y Aislamiento de Errores
La lógica de cálculo de los 20 *frameworks* está separada en 20 archivos (ej. `q1_emociones.py`, `q12_comunidad.py`, `q14_formatos.py`) dentro de la carpeta `analysis_modules/`.
*   **Beneficio:** Si la implementación de **Q19 (Regresión Predictiva)** falla, no detiene la ejecución de **Q1 (Emociones)**.

### B. Requisitos de Máximo Rendimiento para el Motor

#### B.1. Granularidad Cualitativa (AI - Q1, Q2, Q4, Q7, Q18)
La IA (**GPT-4o-mini**) debe ser forzada a desagregar los resultados:
*   **Prompts Hiperdetallados:** Los *prompts* literales (ej. Q1, Q2, Q7) deben instruir al LLM a analizar **"CADA UNO"** de los comentarios y devolver los resultados agrupados **"por publicación única (post\_url)"**.
*   **Resiliencia LLM:** El Orquestador utiliza funciones asíncronas con el decorador `@retry` (3 intentos, 15 segundos de espera) y asegura que la respuesta de OpenAI sea siempre JSON estructurado (`response_format={"type": "json_object"}`).

#### B.2. Cuantificación Contextual (Pandas/Stats - Q11, Q12, Q13, Q16, Q17, Q20)
*   **Q16 Benchmark (La Base):** Desbloqueado, su función es calcular la media ($\mu$) y desviación estándar ($\sigma$) de los competidores en métricas clave.
*   **Z-Score:** El cálculo del **Z-Score** ($Z = \frac{X - \mu}{\sigma}$) es la métrica central de contextualización. Se aplica a Q11 (Engagement), Q12 (Comunidad), Q13 (Frecuencia), Q17 (Sentimiento) y Q20 (KPI Global).
*   **Q14 (Formatos):** Requiere **normalización** por Engagement Rate y la aplicación de la **prueba estadística ANOVA** para validar la significancia de la eficiencia de los formatos.
*   **Q19 (Correlación):** Debe implementar un **Modelo de Regresión Predictiva** (ej. Lineal Multivariable) para calcular el $R^2$ y el P-value.
*   **Q20 (KPI Global):** Debe ser un **Índice Ponderado Estratégico**, donde los pesos de los KPIs internos (Q11, Q12, Q17, etc.) se asignan dinámicamente según el `primary_business_goal` del cliente.

## 4. Modularidad en la Presentación (El Consumidor)

El Frontend (Streamlit) consume la inteligencia compleja y la traduce a elementos visuales accionables.

### A. Consumo de Datos Complejos (`frontend/app.py`)
El archivo principal maneja la autenticación y la recuperación de datos. Utiliza funciones de API (como `get_data_from_endpoint`) para obtener el *insight* consolidado, que luego es procesado por los módulos de vista.

### B. Visualización de Máximo Rendimiento (`view_components/`)
La lógica de visualización se segmenta por Q, permitiendo un consumo focalizado:
*   **Tarjetas KPI con Contexto:** Las **KPI Cards** de Streamlit muestran el valor absoluto junto al **Z-Score** asociado, utilizando coloración condicional para un diagnóstico inmediato.
*   **Gráfico de Radar:** Es la visualización óptima para el **Benchmark Competitivo (Q16)**, permitiendo comparar holísticamente al cliente con el mercado en varias dimensiones (Q11, Q12, Q13, etc.).
*   **Drill-Down Granular:** Utiliza *widgets* de Streamlit (`st.selectbox`) para que el usuario pueda seleccionar una `post_url` o un Tópico y ver el perfil detallado del *insight* (ej., Gráfico de Plutchik para un solo post, Q1).
*   **Síntesis Ejecutiva:** Muestra la **Alerta Prioritaria (Q10)** en una tarjeta destacada (`st.error` o `st.warning`) y el **Gráfico de Desglose de Contribución (Q20)** para hacer transparente la composición del KPI Global.

---

**Metáfora Integral de la Arquitectura:**

El proyecto Pixely es una **fábrica modular y resiliente**. La **Base de Datos** es el almacén de materia prima. El **Orquestador (Motor)** es la línea de producción segmentada (los 20 módulos `qX_analisis.py`) donde las máquinas de IA y Pandas trabajan para crear productos complejos (el JSON anidado). La **API** es el control de calidad estricto (el **Guardián Pydantic**) que solo permite que los productos que tienen la forma perfecta (la estructura Pydantic) sean almacenados. Finalmente, el **Frontend** es la sala de exposición interactiva, donde los productos (los *insights* complejos) se traducen en gráficos de radar y alertas ejecutivas para el cliente.