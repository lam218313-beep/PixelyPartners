# Orchestrator Inputs - Multi-Cliente

Esta carpeta contiene las configuraciones de todos los clientes que serán procesados por el orchestrator.

## Estructura

```
inputs/
├── Cliente_01/
│   └── config.json
├── Cliente_02/
│   └── config.json
└── Cliente_XX/
    └── config.json
```

## Configuración por Cliente

Cada carpeta `Cliente_XX` debe contener un archivo `config.json` con la siguiente estructura:

```json
{
  "client_id": "uuid-de-la-ficha-cliente",
  "client_name": "Nombre del Cliente",
  "google_sheets_url": "https://docs.google.com/spreadsheets/d/...",
  "google_sheets_spreadsheet_id": "ID_DEL_SPREADSHEET",
  "credentials_path": "/app/credentials.json",
  "enabled": true
}
```

### Campos

- **client_id**: UUID de la ficha cliente en la base de datos (obtenido al crear la ficha)
- **client_name**: Nombre descriptivo del cliente
- **google_sheets_url**: URL completa del Google Sheets (para referencia)
- **google_sheets_spreadsheet_id**: Solo el ID extraído de la URL
- **credentials_path**: Ruta al archivo de credenciales de Google (normalmente `/app/credentials.json`)
- **enabled**: `true` para procesar este cliente, `false` para omitirlo

## Agregar Nuevo Cliente

1. Crear nueva carpeta `Cliente_XX` (donde XX es el siguiente número)
2. Crear archivo `config.json` dentro con la estructura indicada
3. Asegurarse de:
   - Obtener el UUID de la ficha cliente de la base de datos
   - Compartir el Google Sheets con el Service Account: `pixely-partners-inputs@massive-tea-473421-n4.iam.gserviceaccount.com`
   - Configurar `enabled: true` para activar el procesamiento

## Ejemplo de URL de Google Sheets

De esta URL:
```
https://docs.google.com/spreadsheets/d/1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4/edit?gid=381912157#gid=381912157
```

Extraer solo el `spreadsheet_id`:
```
1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4
```

## Automatización

El orchestrator automáticamente:
1. Lee todas las carpetas en `inputs/`
2. Carga el `config.json` de cada carpeta
3. Procesa solo los clientes con `enabled: true`
4. Ejecuta análisis incremental para cada cliente
5. Actualiza el `last_analysis_timestamp` de cada ficha en la BD
