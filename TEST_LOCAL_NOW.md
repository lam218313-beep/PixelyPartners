# ✅ LOCAL TESTING - PASO A PASO (EMPIEZA AQUÍ)

**Status:** ✅ Validación Inicial Pasada  
**Próximo:** Probar Todo en Local

---

## 🎯 Resumen Rápido

Tu proyecto **pasó** la validación inicial. Ahora sigue estos pasos para probar TODO en tu máquina local antes de desplegar:

---

## ⏱️ Tiempo Total: ~15 minutos

---

## 📋 PASO 1: Crea Virtual Environment (2 minutos)

```powershell
# En PowerShell, en la carpeta del proyecto
cd "c:\Users\ronal\Music\0.-pixely_partners_001_v1\Pixely Partners"

# Crea virtual environment
python -m venv venv

# Activa virtual environment
.\venv\Scripts\Activate.ps1

# Deberías ver (venv) al inicio de la línea
```

---

## 📋 PASO 2: Instala Dependencias (3 minutos)

```powershell
# Asegúrate que está activado (venv)
# Luego instala:

pip install -r requirements.txt

# Espera a que termine
# Deberías ver: Successfully installed X packages
```

---

## 📋 PASO 3: Configura .env (1 minuto)

```powershell
# Abre .env en tu editor favorito
code .env

# O con Notepad:
notepad .env
```

**Dentro de .env, reemplaza:**
```
OPENAI_API_KEY=sk-your-api-key-here
```

**Con tu clave REAL de OpenAI** (obtenida de https://platform.openai.com/api-keys):
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Guarda el archivo.**

---

## 📋 PASO 4A: Prueba Orchestrator (5 minutos)

```powershell
# Asegúrate que (venv) está activado
# Ejecuta:

python orchestrator/analyze.py

# Deberías ver:
# - Loading analysis modules...
# - Running analysis for q1_emociones...
# - Running analysis for q2_personalidad...
# - ... (más módulos Q3-Q10)
# - Analysis complete! Results saved to orchestrator/outputs/
```

**¿Qué sucede?**
- El orchestrator ejecuta todos los 10 módulos
- Cada módulo hace llamadas a OpenAI
- Los resultados se guardan en JSON files
- Esto puede tardar 30 segundos a 2 minutos (depende de OpenAI)

**✅ Si ves "Analysis complete!"** → ¡ÉXITO PASO 4!

---

## 📋 PASO 4B: Verifica que se Crearon JSONs (2 minutos)

```powershell
# En OTRA terminal con (venv) activado, verifica:

dir orchestrator\outputs\

# Deberías ver 11 archivos:
# ingested_data.json (original)
# q1_emociones.json
# q2_personalidad.json
# q3_topicos.json
# q4_marcos_narrativos.json
# q5_influenciadores.json
# q6_oportunidades.json
# q7_sentimiento_detallado.json
# q8_temporal.json
# q9_recomendaciones.json
# q10_resumen_ejecutivo.json

# Abre uno para verificar contenido:
cat orchestrator\outputs\q1_emociones.json

# Deberías ver JSON bien formado:
# {
#     "metadata": { ... },
#     "results": { ... },
#     "errors": [ ]
# }
```

---

## 📋 PASO 5: Prueba Frontend (3 minutos)

```powershell
# En OTRA terminal NUEVA (mantén orchestrator en primer terminal):

# Activa venv (si no está activado):
.\venv\Scripts\Activate.ps1

# Inicia Streamlit:
streamlit run frontend/app.py

# Deberías ver algo como:
#   You can now view your Streamlit app in your browser.
#
#   Local URL: http://localhost:8501
#
#   Is this your first time using Streamlit? Yes
```

---

## 📋 PASO 6: Abre en el Navegador (2 minutos)

```
1. Abre tu navegador
2. Ve a: http://localhost:8501
3. Deberías ver la aplicación Pixely Partners
4. En el sidebar izquierdo, verás lista de módulos
```

**Prueba:**
```
✓ Haz clic en "Q1: Emociones" → Deberías ver tabla con emociones
✓ Haz clic en "Q2: Personalidad" → Deberías ver personalidad
✓ Navega por Q3-Q10 → Todos deberían cargar sin errores
```

---

## 🧪 PASO 7: Ejecuta Tests (2 minutos)

```powershell
# En OTRA terminal con (venv):

pytest tests/ -v

# Deberías ver:
# test_imports.py::TestOrchestrator::test_base_analyzer_import PASSED
# test_imports.py::TestOrchestrator::test_analyze_main_import PASSED
# test_imports.py::TestOrchestrator::test_all_q_modules_import PASSED
# ... (más tests)
# ===================== X passed in Y.XXs =====================
```

---

## 🐳 PASO 8: Prueba con Docker (Opcional, 5 minutos)

```powershell
# Detén Streamlit (Ctrl+C en terminal)
# Detén Orchestrator (Ctrl+C en terminal)

# Luego:
docker-compose up --build

# Espera a que build termine (2-3 minutos)
# Abre navegador: http://localhost:8501
# Verifica que funciona igual

# Para detener:
# Ctrl+C
docker-compose down
```

---

## ✅ CHECKLIST DE ÉXITO

Marca cada paso como ✅:

```
[ ] Paso 1: Virtual environment creado y activado
[ ] Paso 2: pip install exitoso (Successfully installed X packages)
[ ] Paso 3: .env configurado con OPENAI_API_KEY real
[ ] Paso 4A: orchestrator/analyze.py ejecutó (Analysis complete!)
[ ] Paso 4B: 10 JSON files creados en outputs/
[ ] Paso 4B: Los JSONs tienen estructura correcta
[ ] Paso 5: streamlit run frontend/app.py inició
[ ] Paso 6: http://localhost:8501 carga
[ ] Paso 6: Puedo navegar entre Q1-Q10
[ ] Paso 7: pytest pasó todos los tests (X passed)
[ ] Paso 8: Docker build exitoso (opcional)
```

**SI TODOS ✅ → ¡LISTO PARA DESPLEGAR!**

---

## 🐛 Problemas Comunes & Soluciones

### Problema 1: "ModuleNotFoundError: No module named 'streamlit'"

```powershell
# Solución:
pip install -r requirements.txt --upgrade
```

### Problema 2: "OPENAI_API_KEY not found"

```powershell
# Verifica .env:
type .env

# Deberías ver: OPENAI_API_KEY=sk-proj-xxxx
# Si está vacío:

notepad .env
# Agrega tu clave real
```

### Problema 3: Port 8501 en uso

```powershell
# Usa otro puerto:
streamlit run frontend/app.py --server.port 8502
```

### Problema 4: "No such file or directory: ingested_data.json"

```powershell
# Verifica que existe:
dir orchestrator\outputs\ingested_data.json

# Si no existe, cópialo desde docs:
copy docs\ingested_data.json orchestrator\outputs\
```

### Problema 5: Análisis tarda mucho o error "API error"

```powershell
# Causas posibles:
# 1. API key expirada
# 2. Sin créditos en OpenAI
# 3. Network timeout

# Soluciones:
# - Verifica tu API key en https://platform.openai.com/account/api-keys
# - Verifica que tienes créditos
# - Intenta de nuevo en 5 minutos
```

---

## 📚 Documentación Completa

Para guía **más detallada** de testing:
→ `LOCAL_TESTING.md`

Contiene:
- 10 pasos detallados
- Explicación de cada paso
- Troubleshooting completo
- Tips de debugging
- Cómo monitorear en tiempo real

---

## 🚀 Próximo: Desplegar

Cuando TODO ✅ esté verde:

1. **Elige plataforma:** Lee `DEPLOY_QUICK_START.md`
2. **Deploy:** Sigue los pasos para tu plataforma

**Opciones:**
- Heroku (10 min, más fácil)
- DigitalOcean ($5/mes, simple)
- AWS (escalable)
- Google Cloud (flexible)
- Docker (local)

---

## 💡 Comandos de Referencia

```powershell
# Virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
deactivate

# Instalar & Probar
pip install -r requirements.txt
python validate.py
pytest tests/ -v

# Ejecutar
python orchestrator/analyze.py     # Backend
streamlit run frontend/app.py      # Frontend

# Docker
docker-compose up --build
docker-compose down

# Limpiar
deactivate
rm -r venv
```

---

## ✨ ¡EMPIEZA AHORA!

**Próximo paso inmediato:**

```powershell
cd "c:\Users\ronal\Music\0.-pixely_partners_001_v1\Pixely Partners"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Luego sigue PASO 3 arriba.

**¿Preguntas?** Revisa `LOCAL_TESTING.md` para detalles completos.

**¡Éxito!** 🎉
