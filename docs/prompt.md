## Prompt estandarizado y mejorado para implementar Qx

Propósito
--------
Este prompt especifica, paso a paso y con controles de calidad, cómo implementar el siguiente módulo Qx del orquestador y su vista frontend en el proyecto Pixely. Evita errores comunes (nombres, rutas, claves de datos, placeholders) y obliga a comprobaciones previas antes de tocar código.

Reglas iniciales (leer antes de tocar código)
--------------------------------------------
- Leer obligatoriamente: `inicio.md` y `estandarización.md` antes de cualquier cambio.
- No crear nuevos directorios ni cambiar la estructura de carpetas del repo.
- No ejecutar pipelines ni comandos de shell salvo que se indique explícitamente.
- No usar APIs externas fuera de las dependencias ya presentes en el repo.
- Documentar cualquier suposición mínima que se haga.

Contrato del trabajo (entregables)
----------------------------------
- Backend:
	- Archivo: `pixely_stable/orchestrator/pipelines/social_media/analysis_modules/qX_nombre_modulo.py`
	- Clase: `QXNombreModulo(BaseAnalyzer)` con:
		- `def __init__(self, openai_client: Any, config: Dict[str, Any])` → debe llamar a `super().__init__`.
		- `async def analyze(self) -> Dict[str, Any]` → debe:
			- Cargar datos con `self.load_ingested_data()`.
			- Validar las claves usadas (documentarlas).
			- Preparar prompt (o plantilla de prompt) y llamar a `self.openai_client` (permitido el placeholder documentado).
			- Devolver un dict estructurado (no escribir archivos; el orquestador maneja la serialización).
- Frontend:
	- Archivo: `pixely_stable/frontend/pipelines/social_media/view_components/{qual|quant}/qX_nombre_modulo_view.py`
	- Función: `def display_qX_nombre_modulo()` que:
		- Resuelva la ruta a `orchestrator/outputs` de forma robusta (ver apartado "Rutas").
		- Si el JSON no existe, muestre un mensaje instructivo con la ruta esperada.
		- Muestre `metadata` y `results` defensivamente (usar `.get()`).
- Registro:
	- Asegurarse que la clase está registrada en `ANALYSIS_MODULES` dentro de `orchestrator/pipelines/social_media/analyze.py` si aplica.

Resolución de rutas (recomendación)
----------------------------------
- Usar esta prioridad para localizar outputs:
	1. Variable de entorno: `PIXELY_OUTPUTS_DIR` (o `ORCHESTRATOR_OUTPUTS` / `OUTPUTS_DIR`).
	2. Ruta de contenedor (si aplica): `/app/orchestrator/outputs`.
	3. Ruta repo-relative: `<repo>/pixely_stable/orchestrator/outputs`.
- Implementar o reusar un utilitario `get_outputs_dir()` para evitar `../../..` frágiles en vistas.

Checklist operativo (pasos concretos y verificables)
--------------------------------------------------
1. Inspección inicial:
	 - Leer `orchestrator/pipelines/social_media/analyze.py` y listar Qx ya registrados en `ANALYSIS_MODULES`.
	 - Leer `orchestrator/outputs/ingested_data.json` para confirmar nombres de claves (p.ej. `caption`, `viewsCount`, `ownerUsername`).
	 - Abrir `docs/qX_*.md` para entender el objetivo del módulo.
2. Implementación backend:
	 - Crear/editar `qX_nombre_modulo.py` con la clase `QXNombreModulo`.
	 - Implementar `__init__` y `async analyze()` siguiendo el contrato.
	 - Validar datos leídos (ej.: `posts = data.get('posts', [])`) y documentar muestras/keys.
	 - En `analyze()`, capturar excepciones y devolverlas en `errors` (no lanzar).
3. Registro y naming:
	 - Confirmar que `analyze.py` genera nombres de salida en formato `q{n}_{snake_case_name}.json` a partir del nombre de clase CamelCase → snake_case; si no, corregir `analyze.py`.
4. Implementación frontend:
	 - Crear `qX_nombre_modulo_view.py` en `qual` o `quant`.
	 - Resolver outputs con `get_outputs_dir()`.
	 - Si archivo ausente, mostrar ruta esperada y mensaje instruccional.
	 - Mostrar `metadata` y `results` con `st.json`, `st.table`, `st.bar_chart`. Usar `.get()` y defaults para evitar excepciones.
5. Validación local leve (sin ejecutar pipelines):
	 - Importar el módulo desde un REPL para detectar errores de importación.
	 - Ejecutar un chequeo de sintaxis (p. ej. intentar `import` en Python).
	 - Verificar que la vista no lanza excepciones si el JSON falta.

Gates de calidad (antes de marcar completado)
------------------------------------------
- Syntax / Lint: el módulo cuando se importa no debe lanzar errores de sintaxis.
- Tests mínimos: al menos una verificación simple (ej.: la clase existe y `analyze` es coroutine).
- Robustez frontend: vista maneja ausencia de JSON con mensaje amigable.
- Naming: output final debe llamarse `q{n}_{snake_case}.json`.

Errores comunes y cómo evitarlos
-------------------------------
- Placeholder sin reemplazar: no dejar la llamada a la IA comentada; si no se puede ejecutar, encapsular y documentar un stub inyectable.
- Claves incorrectas: siempre inspeccionar `ingested_data.json` y usar `.get('caption', '')` (ejemplo).
- Rutas frágiles en frontend: evitar joins con múltiples `..`; usar utilitario con env var y rutas conocidas.
- Naming inconsistent: clase CamelCase → archivo / salida snake_case (ej. Q4MarcosNarrativos → q4_marcos_narrativos.json).
- No tocar otros archivos no relacionados: cambiar sólo los archivos del módulo Qx y los view components necesarios.

Plantilla mínima de salida desde `analyze()`
-------------------------------------------
"""
Inputs: datos retornados por `self.load_ingested_data()` (dict).
Outputs: dict con:
{
	"metadata": {"module": "QX Nombre", "version": 1},
	"results": {...},        # estructura libre pero documentada
	"errors": []             # lista de strings o dicts con errores capturados
}
Se deben capturar excepciones y colocarlas en `errors` en vez de lanzar.
"""

Ejemplo breve de `analyze()` (pseudocódigo)
------------------------------------------
- data = self.load_ingested_data()
- posts = [p.get('caption','') for p in data.get('posts', [])]
- if not posts: append to errors and return metadata+errors
- prompt = build_prompt(posts[:N])
- try:
		response = await self.openai_client.call(prompt)
		results = parse_response(response)
	except Exception as e:
		errors.append(str(e))
- return {"metadata": {...}, "results": results, "errors": errors}

Checklist para PR / revisión
----------------------------
- Documenté las claves usadas del ingested_data.json.
- La clase está registrada en `ANALYSIS_MODULES` si corresponde.
- Las vistas usan `get_outputs_dir()` o similar.
- No hay placeholders sin documentar.
- Paso rápido de import para verificar sintaxis.

Acciones automáticas opcionales que puedo hacer ahora
----------------------------------------------------
- Aplicar este prompt limpio a `prompt.md` en el repo (sobrescribir).  (Hecho)
- Añadir `TODO_Qx.md` con la checklist automatizada para seguir en PRs.
- Crear/actualizar `frontend/.../_outputs.py` (si lo deseas centralizado) — ya existe si quieres reusar.

— Fin del prompt mejorado —
