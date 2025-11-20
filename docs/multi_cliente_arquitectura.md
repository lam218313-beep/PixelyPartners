# 🔄 Arquitectura Multi-Cliente - Pixely Partners

## Cambio de Arquitectura

**Antes**: Un solo cliente por instancia de orchestrator (usando variables `FICHA_CLIENTE_ID` y `GOOGLE_SHEETS_SPREADSHEET_ID`)

**Ahora**: **Múltiples clientes** procesados automáticamente desde carpetas de configuración

---

## 📁 Estructura de Carpetas

```
orchestrator/
├── inputs/
│   ├── README.md                    # Documentación
│   ├── Cliente_01/
│   │   └── config.json              # Configuración Cliente 1
│   ├── Cliente_02/
│   │   └── config.json              # Configuración Cliente 2
│   ├── Cliente_03/
│   │   └── config.json              # Configuración Cliente 3
│   └── Cliente_XX/
│       └── config.json              # Configuración Cliente N
├── outputs/
│   └── ...                          # Resultados de análisis
└── __main__.py                      # Entry point (ahora multi-cliente)
```

---

## 📋 Formato del config.json

Cada carpeta `Cliente_XX` debe tener un archivo `config.json` con la siguiente estructura:

```json
{
  "client_id": "uuid-de-la-ficha-cliente",
  "client_name": "Nombre del Cliente",
  "google_sheets_url": "https://docs.google.com/spreadsheets/d/ID_DEL_SHEET/edit",
  "google_sheets_spreadsheet_id": "ID_DEL_SPREADSHEET",
  "credentials_path": "/app/credentials.json",
  "enabled": true
}
```

### Campos Explicados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `client_id` | UUID | UUID de la ficha cliente en la base de datos (obtenido al crear la ficha con la API) |
| `client_name` | string | Nombre descriptivo del cliente (para logs y referencia) |
| `google_sheets_url` | string | URL completa del Google Sheets (opcional, para referencia visual) |
| `google_sheets_spreadsheet_id` | string | **REQUERIDO**: ID extraído de la URL del spreadsheet |
| `credentials_path` | string | Ruta al archivo de credenciales de Google (normalmente `/app/credentials.json`) |
| `enabled` | boolean | `true` = procesar este cliente, `false` = omitir |

---

## 🔑 Obtener el `client_id` (UUID de Ficha)

### Opción 1: Crear nueva ficha con la API

```bash
# 1. Login
curl -X POST http://localhost:8000/token \
  -d "username=admin@pixelypartners.com&password=pixelyadmin2025"

# Copiar el token del response

# 2. Crear ficha cliente
curl -X POST http://localhost:8000/fichas_cliente \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Nuevo Cliente Ejemplo",
    "primary_business_goal": "Aumentar engagement",
    "industry": "Tecnología",
    "target_audience": "Millennials tech-savvy",
    "preferred_platforms": ["instagram", "tiktok"],
    "language": "es"
  }'

# El response incluirá el "id" (UUID) de la ficha creada
```

### Opción 2: Listar fichas existentes

```bash
curl -X GET http://localhost:8000/fichas_cliente \
  -H "Authorization: Bearer YOUR_TOKEN"
```

El response incluye todas las fichas con sus UUIDs.

---

## 📊 Extraer Spreadsheet ID de la URL

De esta URL de Google Sheets:
```
https://docs.google.com/spreadsheets/d/1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4/edit?gid=381912157#gid=381912157
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

Extraer solo el `spreadsheet_id`:
```
1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4
```

---

## ➕ Agregar Nuevo Cliente

### Paso 1: Crear Carpeta

```bash
# En la raíz del proyecto
mkdir orchestrator/inputs/Cliente_03
```

### Paso 2: Crear config.json

Crear archivo `orchestrator/inputs/Cliente_03/config.json`:

```json
{
  "client_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "client_name": "Mi Nuevo Cliente",
  "google_sheets_url": "https://docs.google.com/spreadsheets/d/ABC123.../edit",
  "google_sheets_spreadsheet_id": "ABC123DEF456GHI789JKL012MNO345PQR678",
  "credentials_path": "/app/credentials.json",
  "enabled": true
}
```

### Paso 3: Compartir Google Sheets

1. Abrir el Google Sheets del cliente
2. Click en "Share"
3. Agregar este email con permisos de **Editor**:
   ```
   pixely-partners-inputs@massive-tea-473421-n4.iam.gserviceaccount.com
   ```

### Paso 4: Verificar Estructura del Spreadsheet

Asegurarse de que el spreadsheet tenga dos hojas:

#### Hoja "Posts"
| post_url | platform | created_at | content | likes | comments_count | shares | views |
|----------|----------|------------|---------|-------|----------------|--------|-------|

#### Hoja "Comments"
| post_url | comment_text | ownerUsername | created_at | likes |
|----------|--------------|---------------|------------|-------|

### Paso 5: Reiniciar Orchestrator

```bash
docker compose restart orchestrator
```

El orchestrator detectará automáticamente el nuevo cliente en el próximo ciclo.

---

## 🔄 Flujo de Procesamiento

### 1. Inicio del Orchestrator

```
🚀 ORCHESTRATOR INICIADO (MULTI-CLIENT)
🔐 Authenticating with API...
✅ Orchestrator authenticated successfully
📂 Loading client configurations from /app/orchestrator/inputs/...
✅ Found 3 enabled clients
```

### 2. Procesamiento por Cliente

Para cada cliente habilitado:

```
================================================================================
📋 Processing Client: Tech Innovators
   UUID: eca2c18c-364e-4877-99ef-189b58c1905b
   Spreadsheet ID: 1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4
================================================================================
📅 Last analysis timestamp: 2025-11-19 10:30:00
📊 Fetching data from Google Sheets...
✅ Found 15 new posts and 47 comments
🔄 Starting analysis modules (Q1-Q10)...
✅ Analysis completed
📝 Updating last_analysis_timestamp...
✅ Analysis completed for Tech Innovators
```

### 3. Resumen Final

```
================================================================================
📊 EXECUTION SUMMARY
   ✅ Processed: 2 clients
   ⏸️  Skipped: 1 clients (no new data)
   ❌ Failed: 0 clients
================================================================================
✅ ORCHESTRATOR EXECUTION COMPLETED
```

---

## 🎛️ Habilitar/Deshabilitar Clientes

Para **pausar temporalmente** el procesamiento de un cliente sin eliminar su configuración:

```json
{
  "client_id": "...",
  "client_name": "Cliente Pausado",
  "enabled": false  // ← Cambiar a false
}
```

El orchestrator omitirá automáticamente los clientes con `enabled: false`.

---

## 🐛 Troubleshooting

### Error: "config.json not found in Cliente_XX"

**Solución**: Verificar que cada carpeta `Cliente_XX` tenga su archivo `config.json`.

### Error: "Spreadsheet not found"

**Causas posibles**:
1. `google_sheets_spreadsheet_id` incorrecto
2. Spreadsheet no compartido con el Service Account
3. Service Account sin permisos de "Editor"

**Solución**:
- Verificar el Spreadsheet ID en `config.json`
- Compartir con: `pixely-partners-inputs@massive-tea-473421-n4.iam.gserviceaccount.com`

### Error: "Client not found in database"

**Causa**: El `client_id` (UUID de ficha) no existe en la base de datos.

**Solución**:
1. Listar fichas existentes: `GET /fichas_cliente`
2. Crear nueva ficha: `POST /fichas_cliente`
3. Actualizar `client_id` en `config.json` con el UUID correcto

### No se procesan clientes nuevos

**Solución**: Reiniciar orchestrator después de agregar nuevos clientes:
```bash
docker compose restart orchestrator
```

---

## 📅 Programación Automática

El orchestrator se ejecuta:
- **Al iniciar el contenedor**: Primera ejecución inmediata
- **Cada día a las 6:00 AM**: Análisis programado (cron job)

Procesa **todos los clientes habilitados** en cada ejecución.

---

## 🔐 Seguridad

- **Un archivo de credenciales** (`credentials.json`) se comparte entre todos los clientes
- **Isolation a nivel de base de datos**: Cada cliente tiene su propia `ficha_cliente` con `last_analysis_timestamp` independiente
- **Control de acceso**: Solo clientes con `enabled: true` son procesados

---

## 📖 Ejemplo Completo

### Cliente_01: Tech Innovators (Activo)

**Archivo**: `orchestrator/inputs/Cliente_01/config.json`
```json
{
  "client_id": "eca2c18c-364e-4877-99ef-189b58c1905b",
  "client_name": "Tech Innovators",
  "google_sheets_url": "https://docs.google.com/spreadsheets/d/1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4/edit",
  "google_sheets_spreadsheet_id": "1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4",
  "credentials_path": "/app/credentials.json",
  "enabled": true
}
```

### Cliente_02: Fashion Brand (Pausado)

**Archivo**: `orchestrator/inputs/Cliente_02/config.json`
```json
{
  "client_id": "f1e2d3c4-b5a6-7890-1234-567890abcdef",
  "client_name": "Fashion Brand Co.",
  "google_sheets_url": "https://docs.google.com/spreadsheets/d/2xYZ...",
  "google_sheets_spreadsheet_id": "2xYZABC123DEF456...",
  "credentials_path": "/app/credentials.json",
  "enabled": false
}
```

---

## ✅ Checklist para Nuevo Cliente

- [ ] Crear carpeta `Cliente_XX` en `orchestrator/inputs/`
- [ ] Crear archivo `config.json` con campos requeridos
- [ ] Obtener UUID de ficha cliente (API o base de datos)
- [ ] Extraer Spreadsheet ID de la URL de Google Sheets
- [ ] Compartir spreadsheet con Service Account
- [ ] Verificar estructura de hojas ("Posts" y "Comments")
- [ ] Configurar `enabled: true` en `config.json`
- [ ] Reiniciar orchestrator: `docker compose restart orchestrator`
- [ ] Verificar logs: `docker logs -f pixely_orchestrator`

---

**Ventajas de la Nueva Arquitectura**:
- ✅ Escalable: Agregar clientes sin modificar código
- ✅ Mantenible: Configuración centralizada por cliente
- ✅ Flexible: Habilitar/deshabilitar clientes individualmente
- ✅ Aislado: Cada cliente con su timestamp y datos independientes
