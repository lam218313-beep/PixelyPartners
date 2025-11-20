# 🚀 Inicio Rápido - Pixely Partners

## ✅ Estado Actual del Sistema

### Completado
- ✅ Base de datos PostgreSQL configurada y ejecutando
- ✅ API FastAPI con 25+ endpoints (incluido CRUD de usuarios)
- ✅ Migraciones Alembic aplicadas (field `last_analysis_timestamp`)
- ✅ Google Credentials configuradas (`credentials.json`)
- ✅ Usuario admin creado: `admin@pixelypartners.com` / `pixelyadmin2025`
- ✅ Tenant creado: Pixely Partners Agency
- ✅ Ficha cliente creada: Tech Innovators (UUID: `eca2c18c-364e-4877-99ef-189b58c1905b`)
- ✅ Orchestrator rebuild con dependencias (gspread, oauth2client, httpx)
- ✅ Cron job configurado (ejecución diaria 6:00 AM)
- ✅ Frontend con indicador de última actualización

### ⏳ Pendiente (Requiere Acción del Usuario)

**1. Configurar Google Sheets Spreadsheet ID**

Necesitas crear o proporcionar un Google Sheets con la estructura correcta.

---

## 📊 Opción A: Crear Nuevo Spreadsheet

### 1. Crear Spreadsheet en Google Sheets

1. Ir a [Google Sheets](https://sheets.google.com/)
2. Click en "Blank" para crear nuevo spreadsheet
3. Nombrar: `Pixely Partners - Tech Innovators Data`

### 2. Crear Estructura de Hojas

#### Hoja 1: "Posts"

**Renombrar Sheet1 a "Posts"** y crear las siguientes columnas:

| post_url | platform | created_at | content | likes | comments_count | shares | views |
|----------|----------|------------|---------|-------|----------------|--------|-------|

**Datos de ejemplo:**
```
https://instagram.com/p/CyABC123/    instagram    2025-01-15T10:30:00    Nuevo lanzamiento de producto! 🚀    1500    85    45    12000
https://tiktok.com/@brand/video/001    tiktok    2025-01-16T14:20:00    Tutorial rápido de uso    3200    150    89    45000
https://facebook.com/brand/posts/002    facebook    2025-01-17T09:15:00    Gracias por su apoyo!    980    42    18    8500
```

#### Hoja 2: "Comments"

**Crear nueva hoja llamada "Comments"** con las siguientes columnas:

| post_url | comment_text | ownerUsername | created_at | likes |
|----------|--------------|---------------|------------|-------|

**Datos de ejemplo:**
```
https://instagram.com/p/CyABC123/    Me encanta este producto! 😍    user_maria_21    2025-01-15T11:00:00    25
https://instagram.com/p/CyABC123/    ¿Cuándo llegará a mi país?    john_techie    2025-01-15T11:30:00    8
https://tiktok.com/@brand/video/001    Super útil! Gracias!    tech_lover_99    2025-01-16T14:45:00    15
```

### 3. Compartir con Service Account

1. Click en botón "Share" (esquina superior derecha)
2. En el campo "Add people and groups", pegar:
   ```
   pixely-partners-inputs@massive-tea-473421-n4.iam.gserviceaccount.com
   ```
3. Seleccionar permisos: **Editor**
4. Desmarcar "Notify people" (no es necesario notificar a una cuenta de servicio)
5. Click "Done"

### 4. Copiar Spreadsheet ID

De la URL del spreadsheet:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                       Este es tu SPREADSHEET_ID
```

### 5. Actualizar .env

Abrir archivo `.env` y reemplazar:
```bash
GOOGLE_SHEETS_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

---

## 📊 Opción B: Usar Spreadsheet Existente

Si ya tienes un spreadsheet con datos:

### 1. Verificar Estructura

Asegúrate de que el spreadsheet tenga:
- Hoja "Posts" con columnas: `post_url`, `platform`, `created_at`, `content`, `likes`, `comments_count`, `shares`, `views`
- Hoja "Comments" con columnas: `post_url`, `comment_text`, `ownerUsername`, `created_at`, `likes`

### 2. Compartir con Service Account

Igual que en Opción A, paso 3.

### 3. Copiar Spreadsheet ID

Igual que en Opción A, paso 4.

### 4. Actualizar .env

Igual que en Opción A, paso 5.

---

## 🚀 Lanzar Sistema

Una vez configurado el `GOOGLE_SHEETS_SPREADSHEET_ID` en `.env`:

```powershell
# 1. Detener servicios actuales
docker compose down

# 2. Lanzar todos los servicios
docker compose up -d

# 3. Verificar que todos los contenedores estén corriendo
docker ps
```

Deberías ver 5 contenedores:
- `pixely_db` - PostgreSQL database
- `pixely_api` - FastAPI backend
- `pixely_orchestrator` - Análisis automático
- `pixely_frontend` - Streamlit dashboard
- `pixely_adminer` - Database UI

---

## 🔍 Verificar Funcionamiento

### 1. Verificar Logs del Orchestrator

```powershell
docker logs -f pixely_orchestrator
```

Deberías ver:
```
[INFO] Authenticating with API...
[INFO] Authentication successful
[INFO] Fetching last analysis timestamp...
[INFO] Last analysis: None (first run)
[INFO] Connecting to Google Sheets...
[INFO] Found X new posts since last analysis
[INFO] Running analysis modules...
[INFO] Analysis completed successfully
[INFO] Updated last_analysis_timestamp
```

### 2. Verificar Cron Activo

```powershell
docker exec -it pixely_orchestrator ps aux | findstr cron
```

Debe mostrar: `root ... cron -f`

### 3. Acceder a los Servicios

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Frontend** | http://localhost:8501 | - |
| **API Docs** | http://localhost:8000/docs | Token JWT |
| **Adminer** | http://localhost:8080 | Server: `db`<br>User: `pixely_user`<br>Pass: `secret_password_123` |

### 4. Probar API

```powershell
# Health check
curl http://localhost:8000/

# Login
curl -X POST http://localhost:8000/token -d "username=admin@pixelypartners.com&password=pixelyadmin2025"

# Obtener token y guardarlo
$token = "eyJ..."  # Copiar del response

# Listar fichas
curl http://localhost:8000/fichas_cliente -H "Authorization: Bearer $token"
```

---

## 🧪 Probar Análisis Incremental

Para verificar que el análisis incremental funciona:

### 1. Primera Ejecución
- El orchestrator procesará todos los posts del spreadsheet
- Guardará el timestamp de análisis

### 2. Agregar Nuevos Posts
- Agregar 2-3 posts nuevos en Google Sheets con `created_at` reciente
- Asegurarse de que el timestamp sea **posterior** al último análisis

### 3. Ejecutar Manualmente
```powershell
docker exec -it pixely_orchestrator python -m orchestrator
```

### 4. Verificar Logs
Deberías ver:
```
[INFO] Last analysis: 2025-01-20 10:30:00
[INFO] Found 3 new posts since last analysis
[INFO] Processing only new posts...
```

---

## ⏰ Programación Automática

El orchestrator se ejecuta automáticamente:
- **Al iniciar el contenedor**: Primera ejecución inmediata
- **Cada día a las 6:00 AM**: Análisis programado (cron job)

Para cambiar el horario, editar `Dockerfile.orchestrator` línea 27:
```dockerfile
# Cambiar "0 6" a la hora deseada (formato: minuto hora)
RUN echo "0 2 * * * cd /app && /usr/local/bin/python -m orchestrator >> /app/orchestrator/outputs/cron.log 2>&1" > /etc/cron.d/orchestrator-cron
```

Luego rebuild:
```powershell
docker compose build orchestrator
docker compose up -d orchestrator
```

---

## 🐛 Solución de Problemas

### Error: "Credentials file not found"
```powershell
# Verificar que credentials.json existe
ls credentials.json

# Verificar montaje en contenedor
docker exec -it pixely_orchestrator ls -la /app/credentials.json
```

### Error: "Spreadsheet not found"
1. Verificar que el Spreadsheet ID en `.env` es correcto
2. Verificar que el spreadsheet está compartido con el Service Account
3. Verificar email del Service Account en `credentials.json` → `client_email`

### Error: "No new posts to analyze"
- Esto es normal si no hay posts nuevos desde el último análisis
- El sistema está funcionando correctamente (análisis incremental)

### Orchestrator no ejecuta cron
```powershell
# Verificar cron está corriendo
docker exec -it pixely_orchestrator ps aux | findstr cron

# Ver crontab configurado
docker exec -it pixely_orchestrator crontab -l

# Ver logs de cron
docker exec -it pixely_orchestrator tail -f /app/orchestrator/outputs/cron.log
```

---

## 📖 Próximos Pasos

1. ✅ Configurar `GOOGLE_SHEETS_SPREADSHEET_ID` en `.env`
2. ✅ Lanzar sistema con `docker compose up -d`
3. ✅ Verificar logs del orchestrator
4. ✅ Acceder al frontend en http://localhost:8501
5. ✅ Agregar posts nuevos para probar análisis incremental
6. ✅ Esperar a las 6:00 AM para verificar ejecución automática

---

## 🆘 Soporte

Si encuentras problemas:
1. Revisar logs: `docker logs pixely_orchestrator`
2. Verificar estado de contenedores: `docker ps -a`
3. Revisar documentación en `docs/`
4. Consultar `docs/configuracion_orchestrator.md` para guía detallada

---

**Estado**: Sistema 95% listo. Solo falta configurar `GOOGLE_SHEETS_SPREADSHEET_ID`.
