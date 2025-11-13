Claro. A continuación, se presenta un documento que detalla la arquitectura de la **Base de Datos (DB)**, que es un servicio aislado de **PostgreSQL** fundamental para la persistencia y la integridad de los datos en Pixely.

El documento se enfoca en el rol de la DB y su acoplamiento con la capa del **Guardían** (la API), utilizando la información proporcionada en las fuentes sobre `docker-compose`, `models.py` y las variables de entorno.

---

# ARQUITECTURA DETALLADA DEL SERVICIO DE BASE DE DATOS (POSTGRESQL)

## I. INFRAESTRUCTURA DE LA DB

El servicio de Base de Datos está definido como un microservicio independiente en el `docker-compose.yml`, diseñado para la robustez y la accesibilidad de los demás componentes.

### 1. Definición en `docker-compose.yml`

| Componente | Configuración | Detalle Arquitectónico | Fuente |
| :--- | :--- | :--- | :--- |
| **Servicio** | `db:` | El nombre del servicio dentro de la red Docker es `db`. | |
| **Imagen** | `image: postgres:15-alpine` | Utiliza una imagen ligera y estable de PostgreSQL, versión 15. | |
| **Nombre** | `container_name: pixely_db` | Nombre fijo del contenedor. | |
| **Persistencia** | `volumes: - postgres_data:/var/lib/postgresql/data/` | Utiliza un volumen (`postgres_data`) para asegurar que los datos persistan incluso si el contenedor se detiene o se reinicia. | |
| **Red** | `networks: - pixely_net` | Opera en la red interna de Docker (`pixely_net`) para comunicarse con la API y el Orquestador. | |
| **Puerto** | `ports: - "5432:5432"` | Expone el puerto por defecto de PostgreSQL. | |

### 2. Configuración de Credenciales y Entorno

Las credenciales y la URL de conexión se gestionan a través de variables de entorno, lo cual garantiza la seguridad y la reusabilidad en otros servicios:

*   **Variables de Entorno:** Utiliza `POSTGRES_USER`, `POSTGRES_PASSWORD`, y `POSTGRES_DB` (todos configurados como `pixely` en el `.env`) para la inicialización de la Base de Datos.
*   **`DATABASE_URL`:** El URL de conexión completo es `postgresql://pixely:pixely@db:5432/pixely`, que es consumido por la API en `database.py` para configurar el motor SQLAlchemy.

### 3. Mecanismo de Salud (*Healthcheck*)

El servicio de Base de Datos es fundamental para la dependencia de la API.

| Configuración | Propósito | Fuente |
| :--- | :--- | :--- |
| **`healthcheck`** | Asegura que la Base de Datos está lista para aceptar conexiones antes de que la API intente iniciarse. | |
| **Test** | `["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]` | Verifica la disponibilidad de la DB usando el comando interno de PostgreSQL. | |
| **Dependencia** | El servicio `api` espera que el servicio `db` tenga la condición `service_healthy` antes de iniciar. | |

## II. MODELADO DE DATOS (API/MODELS.PY)

El archivo **`api/models.py`** es el corazón de la arquitectura de la DB, ya que define la estructura relacional (ORM con SQLAlchemy) para todos los datos del *pipeline*.

### 1. Tablas Centrales de Social Media

| Tabla (Modelo) | Función Principal | Campos Críticos | Fuente |
| :--- | :--- | :--- | :--- |
| **`FichaCliente`** | Repositorio de la información estratégica del cliente. | `brand_name`, `primary_business_goal`, `competitors_details`. **Campos de Posicionamiento:** `seguidores_instagram`, `seguidores_tiktok`, `seguidores_facebook` (desbloquea Q12). | |
| **`SocialMediaPost`** | Almacena los metadatos de las publicaciones. | `post_url` (índice único), `likes`, `comments`, **`views`** (esencial para la normalización en Q14, Q15, Q18). | |
| **`Comentario`** | Almacena el texto de los comentarios. | `post_url` (Foreign Key), `text`, `timestamp`, `ownerUsername` (esencial para la granularidad de Q1, Q2, Q3, Q7). | |
| **`SocialMediaInsight`** | **Repositorio Final de los 20 Frameworks.** Almacena el *payload* JSON completo que el Orquestador produce. | 20 campos de tipo `JSON` (ej. `q1_emociones_usuario`, `q20_kpi_global`). Estos campos deben ser actualizados por el **Guardían Pydantic** para aceptar la complejidad anidada. | |

### 2. Estructura de Otros Pipelines (Ejemplos)

La Base de Datos está diseñada para un entorno multi-pipeline, asegurando que todos los *insights* de diferentes áreas de negocio coexistan de manera estructurada:

*   **Estudios de Mercado:** Tablas como `datasets_estudio` y `briefs_estudio`.
*   **Finanzas/Contabilidad:** Tablas transaccionales como `Ingreso`, `Gasto`, y tablas de *reporting* como `EstadoResultados`, `BalanceGeneral`.

## III. MIGRACIÓN Y ACOPLAMIENTO CON EL GUARDIÁN

La integridad de la Base de Datos está garantizada por la API (el Guardián) y el proceso de migración:

### 1. Proceso de Migración

El script **`migrate.py`** es el responsable de crear las tablas si estas no existen.

*   **Activación:** El comando de inicio del contenedor `api` es `sh -c "python migrate.py && uvicorn main:app..."`. Esto garantiza que la migración se ejecute **antes** de que el servidor FastAPI inicie.
*   **Lógica de Creación:** `migrate.py` importa `models.Base` y utiliza `models.Base.metadata.create_all(bind=engine)` para crear las estructuras de tabla definidas en `models.py`.

### 2. El Vínculo Crítico con Pydantic

El almacenamiento de los *insights* complejos (Q1 a Q20) en la Base de Datos depende de la validación de la API:

*   **`api/schemas.py` (Validación):** Si el Orquestador genera un JSON complejo (ej., la lista `analisis_por_publicacion` para Q1), el campo correspondiente en la tabla `SocialMediaInsight` debe ser de tipo `JSON`. Sin embargo, la API requiere que el esquema Pydantic en `api/schemas.py` sea el que defina explícitamente la forma de esa lista anidada.
*   **El Guardián:** Si los esquemas Pydantic no se actualizan para reflejar la complejidad (ej., `Q1EmocionesCompleto`), la API rechazará el *payload*, impidiendo que los datos lleguen a la Base de Datos.

La Base de Datos es la **plataforma de anclaje** para la inteligencia. Su arquitectura está diseñada para ser estricta en su modelado relacional (`models.py`) y para recibir datos validados por el "filtro de forma" impuesto por la capa de la API (`schemas.py`).