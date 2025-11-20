# Variables de Entorno para Orchestrator Automático

## Configuración requerida para el funcionamiento completo del sistema

### 1. API Configuration
```bash
API_BASE_URL=http://api:8000
```

### 2. Orchestrator Authentication
```bash
ORCHESTRATOR_USER=admin
ORCHESTRATOR_PASSWORD=secure_password
```

### 3. Client Configuration
```bash
# UUID de la ficha cliente a analizar
FICHA_CLIENTE_ID=<uuid-de-la-ficha>
```

### 4. Google Sheets Integration
```bash
# ID del spreadsheet de Google Sheets del cliente
GOOGLE_SHEETS_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms

# Ruta al archivo de credenciales de Google Service Account
GOOGLE_CREDENTIALS_PATH=/app/credentials.json
```

### 5. OpenAI Configuration (ya existente)
```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

### 6. Database Configuration (ya existente)
```bash
DATABASE_URL=postgresql://pixely_user:secret_password_123@db:5432/pixely_db
POSTGRES_USER=pixely_user
POSTGRES_PASSWORD=secret_password_123
POSTGRES_DB=pixely_db
```

### 7. JWT Configuration (ya existente)
```bash
SECRET_KEY=pixely_partners_super_secret_key_jwt_2025
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Cómo obtener las credenciales de Google Sheets

### Paso 1: Crear Service Account en Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Navega a "APIs & Services" > "Credentials"
4. Click en "Create Credentials" > "Service Account"
5. Asigna un nombre (ej: "pixely-orchestrator")
6. En "Role", selecciona "Editor" o "Owner"
7. Click "Done"

### Paso 2: Generar JSON Key
1. En la lista de Service Accounts, encuentra el que acabas de crear
2. Click en los 3 puntos (⋮) > "Manage keys"
3. Click "Add Key" > "Create new key"
4. Selecciona "JSON"
5. Se descargará un archivo `credentials.json`

### Paso 3: Habilitar Google Sheets API
1. En Google Cloud Console, navega a "APIs & Services" > "Library"
2. Busca "Google Sheets API"
3. Click "Enable"

### Paso 4: Compartir el Spreadsheet
1. Abre el spreadsheet del cliente en Google Sheets
2. Click en "Share"
3. Copia el email del Service Account (termina en `@<proyecto>.iam.gserviceaccount.com`)
4. Pégalo en el campo de compartir
5. Asigna permisos de "Viewer" o "Editor"
6. Click "Share"

### Paso 5: Obtener el Spreadsheet ID
El ID del spreadsheet está en la URL:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                       Este es el SPREADSHEET_ID
```

### Paso 6: Montar credentials.json en Docker
Agregar en `docker-compose.yml`:
```yaml
orchestrator:
  image: pixely_orchestrator
  volumes:
    - ./credentials.json:/app/credentials.json:ro  # :ro = read-only
  environment:
    - GOOGLE_CREDENTIALS_PATH=/app/credentials.json
    - GOOGLE_SHEETS_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

## Estructura Esperada del Google Sheets

### Hoja "Posts"
| post_url | platform | created_at | content | likes | comments_count | shares | views |
|----------|----------|------------|---------|-------|----------------|--------|-------|
| https://instagram.com/p/001/ | instagram | 2025-01-15T10:30:00 | Contenido... | 150 | 25 | 10 | 5000 |

**Columnas obligatorias:**
- `post_url` (String, único)
- `platform` (instagram/tiktok/facebook)
- `created_at` (Formato ISO 8601: YYYY-MM-DDTHH:MM:SS)
- `content` (Text)
- `likes` (Integer)
- `comments_count` (Integer)
- `shares` (Integer)
- `views` (Integer, opcional)

### Hoja "Comments"
| post_url | comment_text | ownerUsername | created_at | likes |
|----------|--------------|---------------|------------|-------|
| https://instagram.com/p/001/ | Me encanta! | user123 | 2025-01-15T11:00:00 | 5 |

**Columnas obligatorias:**
- `post_url` (FK a Posts.post_url)
- `comment_text` (Text)
- `ownerUsername` (String)
- `created_at` (Formato ISO 8601)
- `likes` (Integer, opcional)

## Verificación de Funcionamiento

### 1. Verificar que cron está corriendo
```bash
docker exec -it pixely_orchestrator bash
ps aux | grep cron
# Debería mostrar: root ... cron -f
```

### 2. Ver logs de cron
```bash
docker exec -it pixely_orchestrator tail -f /app/orchestrator/outputs/cron.log
```

### 3. Ver logs de orchestrator
```bash
docker exec -it pixely_orchestrator tail -f /app/orchestrator/outputs/orchestrator_debug.log
```

### 4. Forzar ejecución manual (para testing)
```bash
docker exec -it pixely_orchestrator python -m orchestrator
```

### 5. Verificar timestamp en base de datos
```sql
-- Conectarse con Adminer (http://localhost:8080)
SELECT 
    id, 
    brand_name, 
    last_analysis_timestamp,
    created_at
FROM fichas_cliente;
```

## Troubleshooting

### Error: "Credentials file not found"
**Solución:** Verificar que `credentials.json` está montado correctamente en el contenedor.
```bash
docker exec -it pixely_orchestrator ls -la /app/credentials.json
```

### Error: "FICHA_CLIENTE_ID environment variable not set"
**Solución:** Agregar la variable en `docker-compose.yml`:
```yaml
orchestrator:
  environment:
    - FICHA_CLIENTE_ID=<uuid-de-tu-ficha>
```

### Error: "gspread.exceptions.WorksheetNotFound: Posts"
**Solución:** Verificar que el spreadsheet tiene una hoja llamada exactamente "Posts" (case-sensitive).

### Error: "Permission denied"
**Solución:** Compartir el spreadsheet con el email del Service Account.

### Cron no ejecuta a las 6:00 AM
**Solución:** Verificar timezone del contenedor:
```bash
docker exec -it pixely_orchestrator date
# Si está en UTC, ajustar cron: 6 AM UTC = 1 AM EST, 11 PM PST
```

## Ejemplo de .env completo
```bash
# OpenAI
OPENAI_API_KEY=sk-proj-YigU2FrscKJRalcqGIp83vPT...
OPENAI_MODEL=gpt-4o-mini

# Orchestrator
ORCHESTRATOR_USER=admin
ORCHESTRATOR_PASSWORD=secure_password
PIXELY_OUTPUTS_DIR=/app/orchestrator/outputs

# API
API_BASE_URL=http://api:8000

# Client
FICHA_CLIENTE_ID=a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Google Sheets
GOOGLE_SHEETS_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GOOGLE_CREDENTIALS_PATH=/app/credentials.json

# Database
DATABASE_URL=postgresql://pixely_user:secret_password_123@db:5432/pixely_db
POSTGRES_USER=pixely_user
POSTGRES_PASSWORD=secret_password_123
POSTGRES_DB=pixely_db

# JWT
SECRET_KEY=pixely_partners_super_secret_key_jwt_2025_production_change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
