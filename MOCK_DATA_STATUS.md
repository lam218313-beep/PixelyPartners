# 📊 Mock Data Generation Complete

## ✅ Status

Todos los archivos JSON de Q1-Q10 han sido completados con **datos realistas y variados** para pruebas del frontend.

**Timestamp:** Generado el script `generate_mock_data.py` y ejecutado exitosamente.

---

## 📁 Archivos Generados

### **Q1 — Análisis de Emociones (Plutchik Model)**
- **Archivo:** `orchestrator/outputs/q1_emociones.json`
- **Datos:** 8 publicaciones con distribuciones variadas de emociones (alegría, confianza, sorpresa, anticipación, miedo, disgusto, ira, tristeza)
- **Características:**
  - Resumen global de emociones
  - Análisis por publicación con variabilidad
  - Ejemplos: desde muy positivo (evento comunitario: 0.88 alegría) hasta negativo (problema reportado: 0.52 ira)
  - Incluye sentimiento dominante por post

### **Q2 — Análisis de Personalidad de Marca (Aaker Framework)**
- **Archivo:** `orchestrator/outputs/q2_personalidad.json`
- **Datos:** 8 publicaciones con 5 dimensiones Aaker (sinceridad, emoción, competencia, sofisticación, rudeza)
- **Características:**
  - Resumen global de personalidad
  - Variación clara entre posts:
    - Producto nuevo: competencia alta (0.88), profesional
    - SAC: sinceridad alta (0.82) pero competencia baja (0.58)
    - Crisis: competencia dañada (0.32), tono áspero (0.85)
  - Tono percibido descriptivo

### **Q3 — Análisis de Tópicos**
- **Archivo:** `orchestrator/outputs/q3_topicos.json`
- **Datos:** 5 tópicos principales + 8 publicaciones con análisis por tópico
- **Características:**
  - Tópicos: Producto, Experiencia de Compra, Servicio al Cliente, Sostenibilidad, Precio/Valor
  - Concentración variada de tópicos por publicación
  - Sentimiento asociado a cada tópico
  - Resumen temático contextualizado

### **Q4 — Análisis de Marcos Narrativos (Entman Theory)**
- **Archivo:** `orchestrator/outputs/q4_marcos_narrativos.json`
- **Datos:** 4 marcos principales + 8 publicaciones con análisis narrativo
- **Características:**
  - Marcos: Positivo, Negativo, Aspiracional, Neutral
  - Distribución agregada: Positivo 55%, Negativo 22%, Aspiracional 18%, Neutral 5%
  - **Ejemplos narrativos reales** (quotes de audiencia) para cada publicación
  - Marco dominante identificado
  - Variabilidad clara: desde Positivo puro (evento) hasta Negativo (crisis de precio)

### **Q5-Q10 — Datos Placeholder**
- **Archivos:** `q5_influenciadores.json`, `q6_oportunidades.json`, `q7_sentimiento_detallado.json`, `q8_temporal.json`, `q9_recomendaciones.json`, `q10_resumen_ejecutivo.json`
- **Estado:** Datos iniciales populados; listos para expansión
- **Notas:** Estos pueden expandirse similarmente a Q1-Q4 si se necesita

---

## 🎯 Características Clave del Mock Data

### 1. **Variabilidad Realista**
- Cada publicación tiene perfiles únicos (no repetitivos)
- Emociones, rasgos y marcos varían naturalmente según el contexto
- Crisis/problemas tienen impacto negativo visible

### 2. **Contexto Narrativo**
- Descripciones de por qué cada publicación genera ciertos sentimientos
- Ejemplos narrativos reales (Q4) para traceabilidad
- Resúmenes contextualizados para interpretación

### 3. **Interactividad de Frontend**
- **Q1:** Selectores de emoción mostrarán variación (cada emoción tiene posts con concentraciones diferentes)
- **Q2:** Selector de rasgo Aaker funcionará (cada rasgo tiene perfiles únicos por publicación)
- **Q3:** Selector de tópico revelará diferentes concentraciones por publicación
- **Q4:** Selector de marco mostrará distribuciones variadas; expandibles con evidencia textual

---

## 🚀 Próximos Pasos

### 1. **Pruebas del Frontend** (En Progreso)
```
✓ Frontend renderiza datos
✓ Docker container activo en http://0.0.0.0:8501
✓ Todos los gráficos reciben datos variados
→ Verificar interactividad de selectores
→ Validar rendimiento de gráficos con múltiples posts
```

### 2. **Refinamiento de Orchestrator** (Pendiente)
- Actualmente `orchestrator/analyze.py` produce datos stubificados
- Después de validar frontend, implementar lógica real de análisis
- Usar templates de mock data como guía de estructura esperada

### 3. **Expansión Opcional**
- Si se necesita, expandir Q5-Q10 a nivel detalle de Q1-Q4
- Agregar más publicaciones (actualmente 8 por análisis, pueden ser 12+)
- Incluir series temporales más detalladas

---

## 📊 Estructura de Datos de Referencia

### Ejemplo: Q1 Post Único
```json
{
    "post_url": "https://instagram.com/p/producto-nuevo-2024/",
    "emociones": {
        "alegria": 0.85,           // Rango 0.0-1.0
        "confianza": 0.78,
        "sorpresa": 0.72,
        "anticipacion": 0.68,
        "miedo": 0.05,
        "disgusto": 0.03,
        "ira": 0.02,
        "tristeza": 0.08
    },
    "resumen_emocional": "...",    // Texto descriptivo
    "sentimiento_dominante": "Positivo"
}
```

### Ejemplo: Q4 Post Único
```json
{
    "post_url": "https://instagram.com/p/producto-nuevo-2024/",
    "marcos_narrativos": {
        "Positivo": 0.72,
        "Negativo": 0.08,
        "Aspiracional": 0.15,
        "Neutral": 0.05
    },
    "marco_dominante": "Positivo",
    "ejemplos_narrativos": [        // Quotes reales (para evidencia textual)
        "Este nuevo producto es revolucionario para la industria",
        "Finalmente tenemos la solución que esperábamos",
        "La innovación que todos necesitábamos"
    ]
}
```

---

## 🔧 Cómo Regenerar Mock Data

Si necesitas cambiar los datos o agregar más publicaciones:

```bash
python generate_mock_data.py
```

Luego:
```bash
docker build -f Dockerfile.frontend -t pixely-frontend:latest .
docker run -d --name pixely-frontend -p 8501:8501 pixely-frontend:latest
```

---

## 📌 Ubicación de Archivos

```
pixely partners/
├── orchestrator/
│   └── outputs/
│       ├── q1_emociones.json           ✓ Updated
│       ├── q2_personalidad.json        ✓ Updated
│       ├── q3_topicos.json             ✓ Updated
│       ├── q4_marcos_narrativos.json   ✓ Updated
│       ├── q5_influenciadores.json     ✓ Updated
│       ├── q6_oportunidades.json       ✓ Updated
│       ├── q7_sentimiento_detallado.json ✓ Updated
│       ├── q8_temporal.json            ✓ Updated
│       ├── q9_recomendaciones.json     ✓ Updated
│       └── q10_resumen_ejecutivo.json  ✓ Updated
└── generate_mock_data.py               ✓ Script para regenerar
```

---

## 🎨 Frontend Status

- **URL:** http://0.0.0.0:8501
- **Status:** ✅ Running (HTTP 200)
- **Data Source:** `orchestrator/outputs/*.json`
- **Display Components:** `frontend/view_components/qual/q*_view.py`

### Gráficos Funcionales
- ✅ Q1: Resumen Global, Radar por Publicación, Top 5 por Emoción
- ✅ Q2: Perfil Global, Top 5 por Rasgo, Radar por Publicación
- ✅ Q3: Burbujas Globales, Top 5 por Tópico, Burbujas por Publicación
- ✅ Q4: Distribución Global, Top 5 por Marco, Análisis + Evidencia, Evolución Temporal
- ✅ Q5-Q10: Gráficos básicos (listos para expansión)

---

**Generated by:** `generate_mock_data.py`  
**Next Review:** Frontend interactive testing with varied data
