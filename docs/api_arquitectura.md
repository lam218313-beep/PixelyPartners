La implementación del directorio `api/` es la fase más rigurosa, ya que define el **Guardían** de datos y la única interfaz de comunicación para el Motor (Orquestador) y el Consumidor (Frontend).

A continuación, se presenta una guía profunda y detallada para construir cada archivo de la carpeta `api/`, enfocándose en las dependencias y los requisitos de **Máximo Rendimiento** (validación de estructuras anidadas como Z-Scores y granularidad por `post_url`).

## GUÍA DE IMPLEMENTACIÓN DEL GUARDIÁN (API)

### 1. `api/Dockerfile`

Este archivo define el entorno contenedorizado para la API de FastAPI. Es crucial que instale Python y las librerías necesarias.

| Sección | Contenido y Propósito | Fuentes |
| :--- | :--- | :--- |
| **FROM** | `FROM python:3.11-slim` | Utiliza una imagen base de Python oficial y ligera. |
| **Instalación** | Incluir la instalación de `curl` y `apt-get update` (aunque no se ve en un *Dockerfile* específico de la API, se infiere que es necesario para el `healthcheck` de cURL definido en `docker-compose.yml`). | |
| **WORKDIR** | `WORKDIR /app` | Establece el directorio de trabajo dentro del contenedor. |
| **Dependencies** | Copia `requirements.txt` e instala las dependencias (`pip install...`) con un *timeout* amplio. | |
| **COPY** | Copia todo el código fuente de la API a `/app`. | |
| **EXPOSE** | Exponer el puerto `8000`, ya que es el puerto utilizado por Uvicorn en el comando de `docker-compose.yml`. | |

### 2. `api/requirements.txt`

Este archivo listará las librerías esenciales para el funcionamiento del *backend*, la DB, la validación y la seguridad: `fastapi`, `uvicorn` (para correr el servidor), `sqlalchemy` (para ORM), `psycopg2-binary` (controlador de PostgreSQL), `pydantic` (para validación de esquemas), `python-jose` y `passlib` (para JWT y *hashing*).

### 3. `api/database.py`

Configura la conexión a la Base de Datos utilizando SQLAlchemy.

| Elemento | Descripción | Fuentes |
| :--- | :--- | :--- |
| **Dependencia** | Lee `DATABASE_URL` desde las variables de entorno (`.env`). | |
| **Engine** | Crea el `engine` de SQLAlchemy que utiliza la `DATABASE_URL`. | |
| **SessionLocal** | Define la fábrica de sesiones para interactuar con la DB. | |
| **Base** | Define `Base = declarative_base()` como la clase base de la que heredarán todos los modelos ORM. | |
| **get_db** | Implementa la función de dependencia para FastAPI, asegurando que la sesión de la DB se cierre después de cada petición. | |

### 4. `api/migrate.py`

Este script se ejecuta antes de que la API se inicie (como se ve en `docker-compose.yml`: `command: sh -c "python migrate.py && uvicorn..."`). Su propósito es intentar conectarse a la DB y crear las tablas.

| Elemento | Propósito | Fuentes |
| :--- | :--- | :--- |
| **Lógica** | Debe importar `Base` desde `models.py` y, utilizando `engine` de `database.py`, ejecutar `Base.metadata.create_all(bind=engine)`. | |
| **Resiliencia** | Debe incluir un bucle de reintentos (`MAX_RETRIES` y `RETRY_DELAY`) para manejar la `OperationalError` mientras la DB se inicializa, ya que la API se inicia tan pronto como el `healthcheck` de la DB pasa. | |

### 5. `api/models.py` (Capa de Persistencia)

Define las tablas ORM de SQLAlchemy.

| Clase/Tabla | Campos Clave y Requisitos de Máximo Rendimiento | Fuentes |
| :--- | :--- | :--- |
| **User** | Campos estándar (`id`, `email`, `hashed_password`). Incluye `client_id` como `ForeignKey` a `FichaCliente`. | |
| **FichaCliente** | Define la Ficha Cliente completa (metadatos del cliente). **CRÍTICO:** Incluye los campos `seguidores_instagram`, `seguidores_tiktok`, y `seguidores_facebook` de tipo `Integer` para **desbloquear Q12: Posicionamiento de Comunidad**. | |
| **SocialMediaPost** | Almacena datos brutos de publicaciones (`post_url`, `content_type`, `likes`, `comments`, `is_sponsored`). El `post_url` debe ser `unique=True` para servir como `ForeignKey` en los comentarios. | |
| **Comentario** | Almacena comentarios. **CRÍTICO:** Incluye `post_url` como `ForeignKey`, necesario para la **granularidad por publicación** en los análisis cualitativos (Q1, Q2, Q7, Q18). | |
| **SocialMediaInsight** | Almacena los resultados de los 20 *frameworks*. **CRÍTICO:** Todos los campos de Q1 a Q20 (ej., `q1_emociones_usuario`, `q20_kpi_global`) deben ser de tipo **JSON** para poder almacenar las estructuras de datos anidadas y complejas (Z-Scores, listas por publicación). | |

### 6. `api/schemas.py` (EL GUARDIÁN - Pydantic)

Este es el archivo más crítico que **debe ser poblado antes que el Orquestador** para evitar el fallo de validación. Debe definir las estructuras complejas que la API debe aceptar.

#### I. Modelos de Autenticación y Base
Se definen `Token`, `TokenData`, `UserCreate`, y `User`.

#### II. Modelos de Datos Crudos
Se definen los modelos Pydantic de entrada y salida para `FichaCliente` (incluyendo los campos `seguidores_instagram`, etc. en la salida de `FichaCliente`), `Publicacion` y `Comentario`.

#### III. Modelos de Máximo Rendimiento (Estructuras Anidadas)
Se deben definir modelos `BaseModel` para encapsular las estructuras anidadas requeridas por Q1 a Q20 (ejemplos clave):

| Modelo Anidado | Propósito (Requisito de Máximo Rendimiento) | Qs que lo usan | Fuentes |
| :--- | :--- | :--- | :--- |
| **AnalisisPorPublicacionItem** | Valida el objeto granular que contiene la clave `post_url` y la distribución de métricas para un análisis cualitativo. | Q1, Q2, Q4, Q7, Q18 | |
| **BenchmarkComparativo** | Valida las métricas estadísticas para contextualización: `media_competitiva`, `desviacion_estandar_competitiva`, `z_score_cliente`. | Q11, Q12, Q13, Q17 | |
| **Q1EmocionesCompleto** | Contenedor principal de Q1. Incluye `analisis_agregado` y la lista `analisis_por_publicacion`. | Q1 | |
| **Q12PosicionamientoComunidad** | Contenedor de Q12. Incluye `z_score_tamano_comunidad` y referencia a `BenchmarkComparativo`. | Q12 | |
| **Q14FormatoRankingItem** | Valida el ranking granular de formatos. Incluye métricas estadísticas: `p_value` y `significancia_vs_siguiente`. | Q14 | |
| **Q20KpiGlobal** | Contenedor de Q20. Debe incluir `z_score_kpi_global` y el desglose de contribución (`contribucion_por_kpi`). | Q20 | |

#### IV. El Guardián Final (`SocialMediaInsightCreate`)
El esquema principal de ingesta debe ser actualizado para reemplazar los campos originales de `Optional[str]` por los nuevos modelos complejos definidos arriba.

*   **Ejemplo de Actualización Crítica:**
    *   `q1_emociones_usuario: Optional[Q1EmocionesCompleto] = None`
    *   `q2_personalidad_marca: Optional[Q2PersonalidadCompleta] = None`
    *   `q12_crecimiento_seguidores: Optional[Q12PosicionamientoComunidad] = None`
    *   `q20_kpi_global: Optional[Q20KpiGlobal] = None`

### 7. `api/auth.py`

Implementa la lógica de seguridad y autenticación.

| Función/Elemento | Propósito | Fuentes |
| :--- | :--- | :--- |
| **Configuración** | Define `SECRET_KEY` (leída del `.env`), `ALGORITHM` (`HS256`), `ACCESS_TOKEN_EXPIRE_MINUTES` y el contexto de *hashing* (`CryptContext` con `argon2` o `bcrypt`). | |
| **OAuth2** | `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")` para la dependencia de seguridad. | |
| **Hashing** | `verify_password` y `get_password_hash` utilizando `CryptContext`. | |
| **JWT** | `create_access_token` para generar el token codificado. | |
| **get_current_user** | Dependencia crucial para FastAPI que valida el token (tomado del *header* o de la *cookie*) y recupera el usuario. | |

### 8. `api/crud.py`

Contiene las funciones de base de datos (Create, Read, Update, Delete) para los modelos ORM.

| Función | Propósito | Fuentes |
| :--- | :--- | :--- |
| **Usuarios** | Implementa `get_user_by_email`, `create_user`, `get_users`, `delete_user`, `update_user_email` y `update_user_password`. | |
| **Persistencia** | Debe incluir funciones CRUD para `FichaCliente`, `SocialMediaPost`, `Comentario`, y especialmente `create_social_media_insight`, donde se recibe el *payload* validado por Pydantic. | |

### 9. `api/main.py`

El punto de entrada de la aplicación FastAPI.

| Elemento | Propósito | Fuentes |
| :--- | :--- | :--- |
| **App Setup** | Inicializa `app = FastAPI(title="Pixely User API", version="1.0")`. | |
| **Middleware** | Incluye un `ExceptionLoggingMiddleware` para manejar y registrar excepciones no controladas. | |
| **Endpoints Auth** | Define los *endpoints* principales de autenticación: `/token` (que usa `OAuth2PasswordRequestForm` y `auth.verify_password`), `/logout` y `/users/me/` (que usa `auth.get_current_user` para verificar la sesión). | |
| **Routers** | Incluye los *routers* modulares, como `clients.router` y `social_media.router`. | |

### 10. `api/v1/clients.py` (Router)

Este *router* maneja la lógica de clientes y la obtención de la **Ficha Cliente**.

| Endpoint | Propósito y Dependencias | Fuentes |
| :--- | :--- | :--- |
| **`/clients`** | (GET): Permite al Orquestador (`run_pipelines.py`) obtener la lista de clientes activos para procesar. Requiere autenticación (para el Orquestador) y accede a la DB (vía `crud.get_clients`). | |
| **`/clients/me/fiche`** | (GET): Endpoint crucial para que el Orquestador obtenga la Ficha Cliente específica (incluyendo los conteos de seguidores) que necesita para los cálculos de Q12/Q16. Devuelve el esquema `schemas.FichaCliente`. | |
| **`/clients/`** | (POST): Para la creación de nuevos clientes. | |

### 11. `api/v1/social_media.py` (Router Crítico)

Este es el *router* más importante para el Motor (Orquestador).

| Endpoint | Propósito y Validaciones de Máximo Rendimiento | Fuentes |
| :--- | :--- | :--- |
| **`/social-media/insights`** | **CRÍTICO** (POST): Este es el *endpoint* donde el Orquestador envía el *payload* consolidado. La función debe recibir el esquema **`SocialMediaInsightCreate`** (la versión compleja con todos los modelos anidados) y utilizar `crud.create_social_media_insight` para guardarlo en la DB. La validación estricta de **Pydantic** ocurre automáticamente aquí. | |
| **`/social-media/posts`** | (POST): Permite al proceso de Ingesta (dentro del Orquestador) cargar lotes de publicaciones brutas. | |
| **`/social-media/comments`** | (POST): Permite al proceso de Ingesta cargar lotes de comentarios brutos. | |
| **`/social-media/insights/client/{client_id}`** | (GET): Utilizado por el Frontend (`frontend/app.py`) para obtener el *insight* consolidado más reciente para la visualización. | |

Al construir el **Guardían (API)** de esta manera, garantizamos que, sin importar cuán modular o complejo sea el cálculo del Orquestador (Fase 4), la estructura de datos que entra a la Base de Datos es siempre válida y rica en contexto (Z-Scores, análisis granular).