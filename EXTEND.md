# 🔧 Guía de Extensión - Agregar Nuevos Módulos

Si necesitas agregar un nuevo módulo de análisis (Q11, Q12, etc.), sigue estos pasos.

---

## 📋 Paso a Paso

### 1. Crear el Módulo de Análisis

Crea `orchestrator/analysis_modules/qX_nombre.py`:

```python
from orchestrator.base_analyzer import BaseAnalyzer
from typing import Optional
import json


class QXNombre(BaseAnalyzer):
    """
    Descripción del módulo QX.
    
    Propósito: Explicar qué analiza
    Entrada: Comentarios/posts de la audiencia
    Salida: JSON con resultados
    """

    async def analyze(self) -> dict:
        """
        Analiza los datos ingested y retorna resultados estructurados.
        """
        try:
            # Cargar datos
            ingested_data = self.load_ingested_data()
            
            # Tu lógica de análisis aquí
            results = {
                "per_post": [],      # Resultados por post
                "global_summary": {} # Resumen global
            }
            
            # Ejemplo: procesar cada post
            for post in ingested_data.get("posts", []):
                post_result = {
                    "post_url": post.get("post_url"),
                    "analysis": "tu análisis aquí"
                }
                results["per_post"].append(post_result)
            
            # Ejemplo: generar resumen global
            results["global_summary"] = {
                "total_posts": len(ingested_data.get("posts", [])),
                "insight": "tu insight aquí"
            }
            
            return {
                "metadata": {
                    "module": "qX_nombre",
                    "version": "1.0",
                },
                "results": results,
                "errors": []
            }
            
        except Exception as e:
            return {
                "metadata": {
                    "module": "qX_nombre",
                    "version": "1.0",
                },
                "results": {},
                "errors": [str(e)]
            }
```

---

### 2. Registrar el Módulo

Edita `orchestrator/analyze.py` y agrega la importación y registro:

```python
# Importar
from analysis_modules.qX_nombre import QXNombre

# En ANALYSIS_MODULES
ANALYSIS_MODULES = {
    "q1_emociones": Q1Emociones,
    "q2_personalidad": Q2Personalidad,
    # ... otros ...
    "qX_nombre": QXNombre,  # ← AGREGA AQUÍ
}
```

---

### 3. Crear la Vista de Frontend

Crea `frontend/view_components/qual/qX_view.py`:

```python
import streamlit as st
import json
from frontend.view_components._outputs import get_outputs_dir


def display_qX_nombre():
    """Display results for QX: Nombre Descriptivo."""
    st.header("📊 QX: Nombre Descriptivo")
    
    outputs_dir = get_outputs_dir()
    output_file = f"{outputs_dir}/qX_nombre.json"
    
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Mostrar metadata
        meta = data.get("metadata", {})
        st.write(f"**Versión:** {meta.get('version')}")
        
        # Mostrar errores si los hay
        errors = data.get("errors", [])
        if errors:
            st.error("Errores encontrados:")
            for error in errors:
                st.write(f"- {error}")
            return
        
        # Mostrar resultados
        results = data.get("results", {})
        
        # Ejemplo: mostrar summary
        summary = results.get("global_summary", {})
        st.metric("Total Posts", summary.get("total_posts", 0))
        
        # Ejemplo: mostrar tabla de resultados
        if results.get("per_post"):
            st.write("### Análisis por Post")
            st.table(results["per_post"][:10])  # Primeros 10
            
    except FileNotFoundError:
        st.warning("No data available. Run orchestrator first.")
    except json.JSONDecodeError as e:
        st.error(f"Error reading JSON: {e}")
```

---

### 4. Registrar la Vista en el Menú

Edita `frontend/app.py` e importa y agrega la nueva vista:

```python
# Importar
import frontend.view_components.qual.qX_view as qX_view

# En el radio selector
page = st.sidebar.radio("Select Analysis", [
    "🏠 Home",
    "😢 Q1: Emociones",
    # ... otros ...
    "📊 QX: Nombre Descriptivo",  # ← AGREGA AQUÍ
])

# En el selector
if page == "📊 QX: Nombre Descriptivo":
    qX_view.display_qX_nombre()
```

---

## 🧪 Prueba tu Módulo

```bash
# 1. Validar sintaxis
python -m py_compile orchestrator/analysis_modules/qX_nombre.py

# 2. Ejecutar orquestador
python orchestrator/analyze.py

# 3. Verificar que se creó qX_nombre.json
ls orchestrator/outputs/qX_nombre.json

# 4. Ejecutar frontend
streamlit run frontend/app.py

# 5. Navegar a tu nuevo módulo en el sidebar
```

---

## 📐 Estructura de Salida Recomendada

```json
{
  "metadata": {
    "module": "qX_nombre",
    "timestamp": "2025-01-15T10:30:00Z",
    "version": "1.0",
    "description": "Descripción del análisis"
  },
  "results": {
    "per_post": [
      {
        "post_url": "...",
        "post_id": "...",
        "caption": "...",
        "analysis_field_1": "...",
        "analysis_field_2": "..."
      }
    ],
    "global_summary": {
      "total_posts_analyzed": 12,
      "key_insight_1": "...",
      "key_insight_2": "...",
      "distribution": {
        "category_1": 5,
        "category_2": 7
      }
    }
  },
  "errors": []
}
```

---

## 🏆 Mejores Prácticas

✅ **Haz:**
- Documenta el propósito del módulo en el docstring
- Maneja excepciones sin dejar que causen crash
- Retorna siempre el formato JSON estándar
- Procesa per_post y global_summary
- Usa nombres consistentes (snake_case en archivos)

❌ **No hagas:**
- Modificar los datos ingested
- Escribir archivos aparte de JSON en outputs/
- Usar imports que no están en requirements.txt
- Olvidar return del formato estándar

---

## 🔗 Integración con LLM

Para usar OpenAI en tu módulo:

```python
from openai import AsyncOpenAI
import os

class QXNombre(BaseAnalyzer):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def analyze(self) -> dict:
        ingested_data = self.load_ingested_data()
        
        # Llamada a LLM
        prompt = f"Analiza esto: {ingested_data}"
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        # ... procesar resultado ...
```

---

## 📦 Actualizar Documentación

Después de agregar tu módulo:

1. Edita `README.md` - Agrega descripción en tabla de módulos
2. Edita `INDEX.md` - Actualiza conteo de líneas si aplica
3. Ejecuta `python validate.py` - Debe reconocer tu módulo

---

## 🤔 Preguntas Frecuentes

**P: ¿Cuántos módulos pueden haber?**  
R: Ilimitado. La arquitectura escala automáticamente.

**P: ¿Qué pasa si mi módulo falla?**  
R: Los errores se capturan y guardan en `"errors"` del JSON. Otros módulos continúan ejecutándose.

**P: ¿Puedo ejecutar solo mi módulo?**  
R: Sí, puedo editar `orchestrator/analyze.py` temporalmente para filtrar módulos durante desarrollo.

**P: ¿Cómo integro datos externos?**  
R: Tu módulo puede hacer requests HTTP. Solo asegúrate de capturar excepciones.

---

## 📚 Ejemplos Completos

Ver los módulos Q1-Q10 en `orchestrator/analysis_modules/` para ejemplos completos.

Módulos más detallados:
- `q1_emociones.py` (135 líneas) - Buen ejemplo con estructura compleja
- `q7_sentimiento_detallado.py` (135 líneas) - Alternativa con enfoque diferente

Módulos más simples:
- `q2_personalidad.py` (~12 líneas) - Mínima viable
- `q3_topicos.py` (~12 líneas) - Otra opción simple
