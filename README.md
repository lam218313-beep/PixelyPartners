# Pixely Partners - Sistema de Análisis de Redes Sociales

Sistema automático de análisis cualitativo para redes sociales con **arquitectura multi-cliente**, ingesta desde Google Sheets y análisis incremental mediante IA.

## 🚀 Características Principales

- **Multi-Cliente**: Procesa múltiples clientes automáticamente desde configuraciones independientes
- **Análisis Automático**: Ejecución programada cada 24 horas (6:00 AM)
- **Análisis Incremental**: Solo procesa posts nuevos desde última ejecución por cliente
- **Google Sheets Integration**: Ingesta automática desde spreadsheets individuales por cliente
- **10 Módulos de Análisis**: Q1-Q10 (Emociones, Personalidad, Tópicos, Marcos Narrativos, etc.)
- **API REST**: FastAPI con autenticación JWT
- **Frontend**: Dashboard Streamlit para visualización
- **Base de Datos**: PostgreSQL con migraciones Alembic

## 📁 Arquitectura Multi-Cliente

Cada cliente tiene su propia configuración en `orchestrator/inputs/Cliente_XX/config.json`:

```
orchestrator/
├── inputs/
│   ├── Cliente_01/
│   │   └── config.json    # Cliente 1: Tech Innovators
│   ├── Cliente_02/
│   │   └── config.json    # Cliente 2: Fashion Brand
│   └── Cliente_XX/
│       └── config.json    # Cliente N
```

**Ventajas**:
- ✅ Agregar clientes sin modificar código
- ✅ Cada cliente con su Google Sheets independiente
- ✅ Análisis incremental por cliente
- ✅ Habilitar/deshabilitar clientes individualmente

## 📋 Módulos de Análisis (Q1-Q10)

- Q1: Emotional Analysis (Plutchik model)
- Q2: Personality Analysis (Aaker framework)
- Q3: Topic Modeling
- Q4: Narrative Framing (Entman)
- Q5: Influencers & Key Voices
- Q6: Opportunities Detection
- Q7: Detailed Sentiment Analysis
- Q8: Temporal Trends
- Q9: Recommendations
- Q10: Executive Summary

## 🔧 Instalación y Configuración

### 1. Requisitos

- Docker & Docker Compose
- Python 3.11+ (para desarrollo local)
- Google Cloud Service Account (para integración con Sheets)
- OpenAI API Key

### 2. Configurar Variables de Entorno

Copiar `.env` y completar los valores:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-YourKeyHere
OPENAI_MODEL=gpt-4o-mini

# Orchestrator
ORCHESTRATOR_USER=admin
ORCHESTRATOR_PASSWORD=secure_password

# Multi-Client Configuration (NO requiere FICHA_CLIENTE_ID individual)
# Cada cliente se configura en orchestrator/inputs/Cliente_XX/config.json

# Database
DATABASE_URL=postgresql://pixely_user:secret_password_123@localhost:5432/pixely_db
POSTGRES_USER=pixely_user
POSTGRES_PASSWORD=secret_password_123
POSTGRES_DB=pixely_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Configurar Google Sheets (Para Cada Cliente)

#### A. Crear Service Account en Google Cloud

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto o seleccionar existente
3. Navegar a "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "Service Account"
5. Asignar rol "Editor"
6. Generar JSON key (se descarga como `credentials.json`)

#### B. Habilitar Google Sheets API

1. En Google Cloud Console: "APIs & Services" > "Library"
2. Buscar "Google Sheets API"
3. Click "Enable"

#### C. Copiar Credenciales

```bash
# Copiar credentials.json a la raíz del proyecto
cp ~/Downloads/your-credentials.json ./credentials.json
```

**Nota**: Un solo archivo `credentials.json` se comparte entre todos los clientes.

### 4. Agregar Clientes

Para cada cliente, crear una carpeta en `orchestrator/inputs/`:

```bash
# Ejemplo: Cliente_01
mkdir orchestrator/inputs/Cliente_01
```

Crear `orchestrator/inputs/Cliente_01/config.json`:

```json
{
  "client_id": "uuid-de-la-ficha-cliente",
  "client_name": "Tech Innovators",
  "google_sheets_url": "https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit",
  "google_sheets_spreadsheet_id": "SPREADSHEET_ID",
  "credentials_path": "/app/credentials.json",
  "enabled": true
}
```

#### Obtener `client_id` (UUID de Ficha)

```bash
# 1. Login
curl -X POST http://localhost:8000/token \
  -d "username=admin@pixelypartners.com&password=pixelyadmin2025"

# 2. Crear ficha cliente
curl -X POST http://localhost:8000/fichas_cliente \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Tech Innovators",
    "primary_business_goal": "Aumentar engagement",
    "industry": "Tecnología",
    "target_audience": "Millennials",
    "preferred_platforms": ["instagram", "tiktok"],
    "language": "es"
  }'

# Copiar el "id" (UUID) del response
```

#### Compartir Spreadsheet con Service Account

1. Abrir spreadsheet del cliente
2. Click "Share"
3. Agregar email del Service Account (de `credentials.json`):
   ```
   pixely-partners-inputs@massive-tea-473421-n4.iam.gserviceaccount.com
   ```
4. Dar permisos de **Editor**

**Ver guía completa**: `docs/multi_cliente_arquitectura.md`

### 5. Iniciar Sistema

```bash
# Iniciar base de datos
docker compose up -d db

# Esperar que inicie (10 segundos)
timeout /t 10 /nobreak

# Aplicar migraciones (local con venv activo)
.\venv\Scripts\activate
alembic upgrade head

# Iniciar API
docker compose up -d api

# Ejecutar script de configuración inicial (solo primera vez)
python setup_initial.py
```

El script creará:
- Tenant "Pixely Partners Agency"
- Usuario admin: `admin@pixelypartners.com` / `pixelyadmin2025`

### 6. Rebuild y Lanzar Sistema Completo

```bash
# Rebuild orchestrator con nuevas dependencias
docker compose build orchestrator

# Lanzar todos los servicios
docker compose up -d

# Ver logs del orchestrator procesando múltiples clientes
docker logs -f pixely_orchestrator
```

### 7. Logs Esperados (Multi-Cliente)

```
🚀 PIXELY PARTNERS - ORCHESTRATOR INICIADO (MULTI-CLIENT)
🔐 Authenticating with API...
✅ Orchestrator authenticated successfully
📂 Loading client configurations from /app/orchestrator/inputs/...
✅ Loaded client: Tech Innovators (ID: eca2c18c-...)
✅ Found 1 enabled clients

================================================================================
📋 Processing Client: Tech Innovators
   UUID: eca2c18c-364e-4877-99ef-189b58c1905b
   Spreadsheet ID: 1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4
================================================================================
📅 Last analysis timestamp: None (first run)
📊 Fetching data from Google Sheets for Tech Innovators...
✅ Found 25 new posts and 87 comments
🔄 Starting analysis modules (Q1-Q10) for Tech Innovators...
✅ Analysis completed for Tech Innovators

================================================================================
📊 EXECUTION SUMMARY
   ✅ Processed: 1 clients
   ⏸️  Skipped: 0 clients (no new data)
   ❌ Failed: 0 clients
================================================================================
✅ ORCHESTRATOR EXECUTION COMPLETED
```

## 🎯 Verificación de Funcionamiento

### 1. Verificar Migración Aplicada

```sql
-- Conectar con Adminer: http://localhost:8080
-- Server: db, User: pixely_user, Password: secret_password_123

SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'fichas_cliente' 
AND column_name = 'last_analysis_timestamp';
```

### 2. Verificar Cron Activo

```bash
docker exec -it pixely_orchestrator ps aux | grep cron
# Debe mostrar: root ... cron -f
```

### 3. Ver Logs de Orchestrator

```bash
# Logs de primera ejecución
docker logs pixely_orchestrator

# Logs de cron (después de las 6:00 AM)
docker exec -it pixely_orchestrator tail -f /app/orchestrator/outputs/cron.log
```

### 4. Probar API

```bash
# Health check
curl http://localhost:8000/

# Login
curl -X POST http://localhost:8000/token \
  -d "username=admin@pixelypartners.com&password=pixelyadmin2025"

# Listar fichas
curl http://localhost:8000/fichas_cliente \
  -H "Authorization: Bearer {token}"
```

### 5. Acceder Frontend

```
http://localhost:8501
```

### 6. Acceder Adminer (BD Management)

```
http://localhost:8080
Server: db
User: pixely_user
Password: secret_password_123
Database: pixely_db
```

## 📚 Endpoints de API

### Autenticación
- `POST /register` - Registrar tenant y usuario
- `POST /token` - Login (obtener JWT)
- `GET /users/me` - Info del usuario actual

### Gestión de Usuarios (Admin only)
- `GET /users` - Listar usuarios del tenant
- `GET /users/{id}` - Obtener usuario específico
- `POST /users` - Crear nuevo usuario
- `PATCH /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario

### Fichas Cliente
- `POST /fichas_cliente` - Crear ficha
- `GET /fichas_cliente` - Listar fichas del tenant
- `GET /fichas_cliente/{id}` - Obtener ficha específica
- `DELETE /fichas_cliente/{id}` - Eliminar ficha
- `PATCH /fichas_cliente/{id}/last_analysis_timestamp` - Actualizar timestamp (orchestrator)

### Social Media Posts
- `POST /social_media_posts` - Crear post
- `GET /social_media_posts` - Listar posts

### Insights
- `GET /insights` - Obtener resultados de análisis

### Análisis Q1-Q10
- `POST /analyze/q1` - Análisis de Emociones
- `POST /analyze/q2` - Personalidad de Marca
- `POST /analyze/q3` - Análisis de Tópicos
- `POST /analyze/q4` - Marcos Narrativos
- `POST /analyze/q5` - Influenciadores
- `POST /analyze/q6` - Oportunidades
- `POST /analyze/q7` - Sentimiento Detallado
- `POST /analyze/q8` - Análisis Temporal
- `POST /analyze/q9` - Recomendaciones
- `POST /analyze/q10` - Resumen Ejecutivo

## 🔐 Roles de Usuario

- **admin**: Puede gestionar usuarios, fichas, y ejecutar análisis manualmente
- **analyst**: Puede ver y crear fichas, ejecutar análisis
- **viewer**: Solo puede visualizar resultados en el frontend

## 🕐 Cron Schedule

El orchestrator se ejecuta:
- **Al iniciar el contenedor**: Análisis inmediato
- **Cada día a las 6:00 AM**: Análisis programado

Para cambiar el horario, editar `Dockerfile.orchestrator`:
```dockerfile
# Ejemplo: Ejecutar a las 2:00 AM
RUN echo "0 2 * * * cd /app && python -m orchestrator >> /app/orchestrator/outputs/cron.log 2>&1" > /etc/cron.d/orchestrator-cron
```

## 🐛 Troubleshooting

### Error: "Credentials file not found"
```bash
# Verificar montaje
docker exec -it pixely_orchestrator ls -la /app/credentials.json

# Si falta, recrear contenedor
docker compose down
docker compose up -d
```

### Error: "FICHA_CLIENTE_ID not set"
```bash
# Verificar .env
cat .env | grep FICHA_CLIENTE_ID

# Recrear orchestrator
docker compose up -d --force-recreate orchestrator
```

### Error: "Permission denied" en Google Sheets
1. Verificar que el spreadsheet está compartido con el Service Account
2. Email del Service Account está en `credentials.json` → `client_email`

### Cron no ejecuta
```bash
# Verificar timezone
docker exec -it pixely_orchestrator date

# Ver crontab
docker exec -it pixely_orchestrator crontab -l
```

## 📖 Documentación Adicional

- `docs/multi_cliente_arquitectura.md` - **NUEVO**: Arquitectura multi-cliente completa
- `orchestrator/inputs/README.md` - Guía para agregar clientes
- `docs/especificaciones_sistema.md` - Especificaciones completas
- `docs/configuracion_orchestrator.md` - Guía de configuración detallada
- `docs/resumen_implementacion.md` - Resumen técnico de implementación
- `docs/verificacion_funcionalidades_api.md` - Verificación de endpoints

## 🤝 Contribuir

1. Fork del repositorio
2. Crear branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto es privado y confidencial.

## 👥 Contacto

- **Owner**: lam218313-beep
- **Repository**: https://github.com/lam218313-beep/PixelyPartners

---

**Versión**: 2.0.0  
**Fecha**: Noviembre 2025
