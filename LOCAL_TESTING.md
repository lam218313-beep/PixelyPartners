# 🧪 LOCAL TESTING GUIDE - Prueba Todo en Local Primero

**Pixely Partners v1.0.0**  
**IMPORTANTE: Siempre testa localmente antes de desplegar**

---

## 🎯 Objetivo

Verificar que **TODOS** los componentes funcionan correctamente en tu máquina local antes de hacer deployment.

---

## ⏱️ Tiempo Total: ~20 minutos

---

## 📋 Paso 1: Validación Inicial (2 minutos)

```bash
cd "c:\Users\ronal\Music\0.-pixely_partners_001_v1\Pixely Partners"

# Verifica que todo está en su lugar
python validate.py

# Deberías ver:
# ✓ All checks passed! Project is ready.
```

Si ves errores aquí, **STOP**. Revisa la sección Troubleshooting.

---

## 📋 Paso 2: Crear Virtual Environment (2 minutos)

```bash
# Crea virtual environment
python -m venv venv

# Activa virtual environment
.\venv\Scripts\activate

# Deberías ver (venv) en la terminal
```

---

## 📋 Paso 3: Instalar Dependencias (5 minutos)

```bash
# Verifica que está en (venv)
# Luego instala
pip install -r requirements.txt

# Espera a que termine
# Deberías ver: Successfully installed X packages
```

**Si hay errores:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Reinstala
pip install -r requirements.txt
```

---

## 📋 Paso 4: Configurar Variables de Entorno (2 minutos)

```bash
# Abre archivo .env
# Windows PowerShell:
notepad .env

# O con tu editor favorito (VS Code):
code .env
```

**Archivo .env debe verse así:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
ORCHESTRATOR_USER=admin
ORCHESTRATOR_PASSWORD=secure_password
PIXELY_OUTPUTS_DIR=./orchestrator/outputs
```

**¡IMPORTANTE!** Reemplaza `sk-proj-xxxxxxxxxxxxx` con tu clave REAL de OpenAI.

**¿No tienes clave?** Consíguela aquí: https://platform.openai.com/api-keys

---

## 📋 Paso 5: Prueba el Orchestrator (5 minutos)

```bash
# Asegúrate de estar en (venv)
# En la MISMA terminal:

python orchestrator/analyze.py

# Deberías ver algo como:
# Loading analysis modules...
# Running analysis for q1_emociones...
# Running analysis for q2_personalidad...
# ... (más módulos)
# Analysis complete! Results saved to orchestrator/outputs/
```

**¿Qué significa cada mensaje?**

```
"Loading analysis modules..."
→ El orchestrator está cargando los 10 módulos

"Running analysis for qX_nombre..."
→ Ejecutando análisis (esto toma un tiempo con LLM)

"Analysis complete! Results saved..."
→ ¡ÉXITO! Se crearon los JSONs
```

**Verifica que se crearon archivos:**

```bash
# En OTRA terminal (sin cerrar la anterior):
dir orchestrator\outputs\

# Deberías ver:
# q1_emociones.json
# q2_personalidad.json
# q3_topicos.json
# ... (todos 10)
```

**Abre uno para ver que tiene datos:**

```bash
# En PowerShell:
type orchestrator\outputs\q1_emociones.json

# O en VS Code:
code orchestrator\outputs\q1_emociones.json
```

Deberías ver JSON estructurado con `{"metadata": {...}, "results": {...}, "errors": [...]}`

---

## 📋 Paso 6: Prueba el Frontend (5 minutos)

**En OTRA terminal nueva** (mantén el orchestrator corriendo):

```bash
# Activa venv si no está activado
.\venv\Scripts\activate

# Inicia Streamlit
streamlit run frontend/app.py

# Deberías ver algo como:
# 
#   You can now view your Streamlit app in your browser.
#
#   Network URL: http://192.168.x.x:8501
#   External URL: http://xxx.xxx.xxx.xxx:8501
#
#   Welcome to Streamlit 👋 If you get permission errors...
```

---

## 🌐 Paso 7: Prueba en el Navegador (3 minutos)

**Abre tu navegador:**

```
http://localhost:8501
```

**Deberías ver:**

1. ✅ Página de inicio con título "Pixely Partners"
2. ✅ Sidebar izquierdo con "Select Analysis"
3. ✅ Lista con:
   - Home
   - 😢 Q1: Emociones
   - 👤 Q2: Personalidad
   - 📊 Q3: Topicos
   - ... (y más)

---

## ✨ Prueba Interactiva (2 minutos)

En el navegador:

```
1. Haz clic en "Q1: Emociones"
   → Deberías ver tabla con emociones (Alegría, Tristeza, etc.)

2. Haz clic en "Q2: Personalidad"
   → Deberías ver rasgos de personalidad

3. Navega por todos los módulos
   → Todos deberían cargar sin errores

4. Verifica en Developer Tools (F12)
   → No deberían haber errores rojos en Console
```

---

## 🐳 Paso 8: Prueba con Docker (Opcional pero Recomendado)

```bash
# Para si quieres probar exactamente como va a estar en producción

# 1. Detén Streamlit (Ctrl+C en la terminal)

# 2. Build Docker images
docker-compose up --build

# Espera a que termine (2-3 minutos)
# Deberías ver:
# - Building orchestrator...
# - Building frontend...
# - Starting pixely-frontend...
# - Starting pixely-orchestrator...

# 3. Abre navegador
# http://localhost:8501

# 4. Verifica que funciona igual que local

# 5. Ver logs
docker-compose logs -f

# 6. Para detener
# Ctrl+C
docker-compose down
```

---

## 🧪 Paso 9: Ejecuta los Tests (2 minutos)

```bash
# En terminal con (venv) activado:

pytest tests/ -v

# Deberías ver:
# tests/test_imports.py::TestOrchestrator::test_base_analyzer_import PASSED
# tests/test_imports.py::TestOrchestrator::test_analyze_main_import PASSED
# tests/test_imports.py::TestOrchestrator::test_all_q_modules_import PASSED
# ... (más tests)
# ===================== X passed in Y.XXs =====================
```

Si hay FAILED, revisa qué módulo falla y sigue troubleshooting.

---

## 📊 Paso 10: Verifica Logs y Errores (2 minutos)

```bash
# En VS Code, abre "Problems" panel (Ctrl+Shift+M)
# Deberías ver: 0 errors, 0 warnings

# En terminal, durante ejecutar orchestrator:
# NO deberían haber Tracebacks rojos
# Solo info messages azules

# En navegador (F12 → Console):
# No deberían haber errores HTTP rojos
```

---

## ✅ TESTING CHECKLIST

Marca todo como ✅:

```
[ ] validate.py pasó
[ ] venv creado y activado
[ ] pip install exitoso
[ ] .env configurado con OPENAI_API_KEY
[ ] orchestrator/analyze.py ejecutó sin errores
[ ] Se crearon 10 JSON files en outputs/
[ ] JSONs tienen estructura correcta
[ ] streamlit run frontend/app.py inició
[ ] http://localhost:8501 carga
[ ] Puedo navegar entre módulos
[ ] Todos los módulos cargan sin errores
[ ] pytest tests/ -v pasó todos tests
[ ] No hay errores en console (F12)
[ ] docker-compose up --build funciona
```

**Si todos ✅ → ¡LISTO PARA DESPLEGAR!**

---

## 🐛 TROUBLESHOOTING

### Error 1: "ModuleNotFoundError: No module named 'streamlit'"

```bash
# Solución:
pip install -r requirements.txt --upgrade

# Verifica:
pip list | grep streamlit
```

### Error 2: "OPENAI_API_KEY not found"

```bash
# Verifica .env existe:
dir .env

# Si no existe:
copy .env.example .env

# Abre en editor:
notepad .env

# Reemplaza: sk-your-api-key-here
# Con tu clave real: sk-proj-xxxxxxxxxxxx
```

### Error 3: "Port 8501 already in use"

```bash
# Encuentra qué usa el puerto:
netstat -ano | findstr :8501

# O usa otro puerto:
streamlit run frontend/app.py --server.port 8502
```

### Error 4: "Cannot find orchestrator/outputs"

```bash
# El directorio debería existir, pero si no:
mkdir orchestrator\outputs

# Verifica que ingested_data.json está:
dir orchestrator\outputs\ingested_data.json
```

### Error 5: "Docker build fails"

```bash
# Limpia Docker:
docker system prune

# Reinicia Docker

# Intenta de nuevo:
docker-compose up --build
```

### Error 6: Análisis tarda mucho o nunca termina

```bash
# Posibles causas:
# 1. API key expirada/sin créditos
# 2. Network timeout
# 3. LLM respondiendo lentamente

# Solución:
# - Verifica API key en https://platform.openai.com/account/api-keys
# - Verifica que tienes créditos
# - Intenta de nuevo en 5 minutos
# - Verifica tu conexión internet
```

### Error 7: "JSON decode error"

```bash
# Verifica que orchestrator completó exitosamente
# Si el archivo q1_emociones.json está corrupto:

# 1. Borra todos los JSONs:
del orchestrator\outputs\q*.json

# 2. Ejecuta de nuevo:
python orchestrator/analyze.py

# 3. Verifica que se crearon correctamente:
type orchestrator\outputs\q1_emociones.json
```

---

## 💡 TIPS DE TESTING

### Tip 1: Usa Múltiples Terminales

```
Terminal 1: python orchestrator/analyze.py
Terminal 2: streamlit run frontend/app.py
Terminal 3: (para otros comandos)
```

### Tip 2: Monitorea en Tiempo Real

```bash
# En otra terminal, monitorea outputs:
while ($true) { dir orchestrator\outputs\; sleep 5; clear }
```

### Tip 3: Test Incrementalmente

```
1. Valida (python validate.py)
2. Instala deps (pip install...)
3. Prueba orchestrator solo
4. Prueba frontend solo
5. Prueba ambos juntos
6. Prueba Docker
7. Prueba tests
```

### Tip 4: Usa VS Code para Debugging

```
1. Abre VS Code en proyecto
2. Terminal → New Terminal
3. Ejecuta python orchestrator/analyze.py
4. Agrega breakpoints
5. F5 para debug
```

---

## 🎯 PRÓXIMOS PASOS

### Si TODO ✅ pasó:

1. **Documentar:**
   ```bash
   git add .
   git commit -m "Local testing passed - all systems go"
   ```

2. **Desplegar:**
   - Lee `DEPLOY_QUICK_START.md`
   - Elige plataforma
   - Sigue deployment guide

### Si Algo ❌ falló:

1. Revisa error específico
2. Busca en TROUBLESHOOTING arriba
3. Si no está, ejecuta `python validate.py` para más detalles
4. Lee logs en detail

---

## 📞 ÚLTIMAS NOTAS

**Tiempo total si todo va bien:** ~20 minutos

**Archivos clave:**
- `validate.py` - Validación
- `requirements.txt` - Dependencias
- `.env` - Configuración
- `orchestrator/analyze.py` - Backend
- `frontend/app.py` - Frontend

**Comandos clave:**
```bash
python validate.py                      # Valida proyecto
pip install -r requirements.txt         # Instala deps
python orchestrator/analyze.py          # Ejecuta análisis
streamlit run frontend/app.py           # Inicia frontend
pytest tests/ -v                        # Ejecuta tests
docker-compose up --build               # Docker
```

---

## ✨ ¡LISTO PARA TESTING!

**Empieza con:**
```bash
cd "c:\Users\ronal\Music\0.-pixely_partners_001_v1\Pixely Partners"
python validate.py
```

Luego sigue los 10 pasos arriba.

**Cuando todo ✅ esté verde, estarás listo para desplegar.** 🚀
