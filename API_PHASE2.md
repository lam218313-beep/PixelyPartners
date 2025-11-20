# Pixely Partners - API (Fase 2)

## Descripción

La **Fase 2** transforma tu orquestador de scripts en un servidor web profesional usando **FastAPI**.

El objetivo es exponer los 10 módulos de análisis como endpoints HTTP, permitiendo que clientes externos (frontend, aplicaciones móviles, dashboards) accedan a los análisis de forma programática.

---

## Estructura de Carpetas

```
pixely-partners/
├── api/                     # 🆕 NUEVA CARPETA
│   ├── __init__.py         # Inicialización del paquete
│   ├── schemas.py          # Contratos Pydantic (entrada/salida)
│   ├── dependencies.py     # Configuración y cliente OpenAI
│   └── main.py             # Servidor FastAPI y rutas
│
├── orchestrator/           # Tu lógica existente
│   ├── analysis_modules/
│   ├── data/
│   └── outputs/
│
├── frontend/               # Tu Streamlit existente
├── run_api.py             # Script de inicio rápido
├── requirements-api.txt   # Dependencias de FastAPI
└── .env.example          # Plantilla de variables de entorno
```

---

## Instalación

### 1. Instalar Dependencias

```bash
# Instalar dependencias del API
pip install -r requirements-api.txt

# O instalar todo junto
pip install -r requirements.txt -r requirements-api.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar plantilla
cp .env.example .env

# Editar .env con tus valores
# - OPENAI_API_KEY: Tu clave de OpenAI
# - Otros valores según necesites
```

---

## Ejecución

### Modo Desarrollo (con auto-reload)

```bash
# Usando uvicorn directamente
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# O usando el script helper
python run_api.py
```

La API estará disponible en: **http://localhost:8000**

### Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Modo Producción

```bash
# Con gunicorn y uvicorn workers
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Archivos Creados

### 1. `api/schemas.py`

**Propósito**: Definir los contratos de datos (Pydantic models).

**Contenido**:
- `AnalysisRequest`: Estructura de entrada para solicitar análisis
- `AnalysisResult`: Estructura de salida estándar
- `PipelineResult`: Resultado de ejecutar el pipeline completo
- `HealthCheckResponse`: Respuesta de salud del servidor
- Modelos específicos Q1-Q10 (para validación futura)
- `ErrorResponse`: Respuesta de errores

**Por qué**: Pydantic garantiza que los datos sean válidos y autoconfigurados, y genera documentación automática en Swagger.

### 2. `api/dependencies.py`

**Propósito**: Centralizar configuración y dependencias.

**Contenido**:
- `Settings`: Clase que lee variables de entorno y valida configuración
- `OpenAIClientManager`: Gestiona el cliente AsyncOpenAI como singleton
- `get_settings()`: Inyectable en rutas
- `get_openai_client()`: Inyectable en rutas

**Por qué**: Separación de responsabilidades y manejo centralizado de configuración.

### 3. `api/main.py`

**Propósito**: Servidor FastAPI con todas las rutas.

**Contenido**:
- Lifespan events (startup/shutdown)
- **Rutas de salud**:
  - `GET /` - Bienvenida
  - `GET /health` - Salud detallada
  - `GET /status` - Configuración actual
- **Rutas de análisis**:
  - `POST /analyze` - Ejecutar módulo individual
  - `POST /pipeline` - Ejecutar todos los módulos (Q1-Q10)
- **Rutas módulo-específicas**:
  - `GET /q1/emociones` - Resultado de Q1
  - `GET /q2/personalidad` - Resultado de Q2
  - ... (Q3-Q10)
- Manejo de excepciones centralizado

**Por qué**: Estructura clara y escalable para agregar más endpoints después.

---

## Próximos Pasos

La Fase 2 crea la **estructura base**. Los próximos pasos son:

### Fase 2.1: Conectar Orquestador

```python
# En api/main.py, reemplazar TODO:
# Importar y usar el módulo orchestrator
from orchestrator.analyze import run_analysis

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    result = await run_analysis(request.module, request.client_name)
    return result
```

### Fase 2.2: Endpoint Dinámicos

Generar rutas dinámicamente para cada módulo:

```python
for module in ["q1", "q2", ..., "q10"]:
    @app.get(f"/{module}")
    async def get_module_result():
        # Cargar JSON de outputs/
        return load_result(module)
```

### Fase 2.3: Autenticación

Agregar autenticación JWT o API keys:

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/analyze")
async def analyze(request: AnalysisRequest, credentials = Depends(security)):
    # Validar token...
```

---

## API Endpoints (Resumen)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Bienvenida |
| GET | `/health` | Salud del servidor |
| GET | `/status` | Configuración actual |
| POST | `/analyze` | Ejecutar módulo individual |
| POST | `/pipeline` | Ejecutar todos los módulos |
| GET | `/q1/emociones` | Resultado Q1 |
| GET | `/q2/personalidad` | Resultado Q2 |
| GET | `/q3/temas` | Resultado Q3 |
| GET | `/q4/marcos` | Resultado Q4 |
| GET | `/q5/influenciadores` | Resultado Q5 |
| GET | `/q6/oportunidades` | Resultado Q6 |
| GET | `/q7/sentimiento` | Resultado Q7 |
| GET | `/q8/temporal` | Resultado Q8 |
| GET | `/q9/recomendaciones` | Resultado Q9 |
| GET | `/q10/resumen` | Resultado Q10 |

---

## Ejemplo de Uso

### Desde cURL

```bash
# Health check
curl http://localhost:8000/health

# Ejecutar módulo Q2
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"module": "q2", "client_name": "MiMarca"}'

# Ver resultado Q2
curl http://localhost:8000/q2/personalidad
```

### Desde Python

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/analyze",
        json={"module": "q2", "client_name": "MiMarca"}
    )
    print(response.json())
```

### Desde Frontend (JavaScript)

```javascript
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({module: 'q2', client_name: 'MiMarca'})
});
const data = await response.json();
console.log(data);
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'api'"

**Solución**: Asegúrate de estar en la raíz del proyecto y que `api/__init__.py` existe.

```bash
pwd  # Debería ser: /path/to/pixely-partners/
python -m uvicorn api.main:app --reload
```

### Error: "OPENAI_API_KEY not found"

**Solución**: Crear un archivo `.env` en la raíz con tu clave:

```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Error: "Port 8000 already in use"

**Solución**: Usar otro puerto:

```bash
python -m uvicorn api.main:app --port 9000
```

---

## Documentación Técnica

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic v2](https://docs.pydantic.dev/2.0/)
- [Uvicorn](https://www.uvicorn.org/)
- [OpenAI Async Client](https://github.com/openai/openai-python)

---

**Estado**: Fase 2 - Estructura Base Completa ✅

**Próximo**: Fase 2.1 - Conectar Orquestador
