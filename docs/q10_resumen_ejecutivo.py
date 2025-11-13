import json
import os
from typing import Any, Dict
from datetime import datetime

from .base_analyzer import BaseAnalyzer


class Q10ResumenEjecutivo(BaseAnalyzer):
	def __init__(self, openai_client: Any, config: Dict[str, Any]):
		super().__init__(openai_client, config)

	async def analyze(self) -> Dict[str, Any]:
		"""
		Q10: Resumen Ejecutivo. Sintetiza los resultados de las demás Qs
		en un objeto JSON jerárquico listo para consumo ejecutivo.

		Implementación segura: intenta llamar al LLM y, si falla,
		devuelve un resumen heurístico mínimo basado en los outputs
		disponibles en el directorio de outputs.
		"""
		ingested = self.load_ingested_data()

		# Cargar insights previos (Q1..Q9, etc.) para trazabilidad
		insights = {}
		try:
			files = os.listdir(self.outputs_dir)
		except Exception:
			files = []

		for fname in files:
			if not fname.lower().endswith('.json'):
				continue
			# evitar leer errores o el propio Q10 si existe
			if fname.lower().startswith('q10_') or fname.lower().endswith('_error.json'):
				continue
			key = fname.split('_')[0].upper()
			try:
				with open(os.path.join(self.outputs_dir, fname), 'r', encoding='utf-8') as f:
					insights[key] = json.load(f)
			except Exception:
				continue

		# Construir prompt compacto (evitar enviar todo el contenido por tamaño)
		available = list(insights.keys())
		prompt_summary = {
			"ingested_posts": len(ingested.get('posts', [])),
			"available_insights": available
		}

		prompt = f"""
		Rol: Eres un analista ejecutivo. Toma los insights disponibles y genera un resumen ejecutivo
		corto (máximo 5 viñetas) y una sección de prioridades (Top 3 acciones) con justificación.

		Datos resumidos:
		{json.dumps(prompt_summary, ensure_ascii=False)}

		Devuelve SOLO un JSON con las claves: resumen (lista de strings), prioridades (lista de objetos con acción, impacto_score 0-100, frameworks_relevantes).
		"""

		try:
			response = await self.openai_client.chat.completions.create(
				model="gpt-4o",
				messages=[
					{"role": "system", "content": "Eres un Director de Estrategia de Marketing para ejecutivos."},
					{"role": "user", "content": prompt}
				],
				response_format={"type": "json_object"}
			)
			content = response.choices[0].message.content
			result = json.loads(content)

			# Inserta metadata mínima
			result.setdefault('metadata', {})
			result['metadata'].setdefault('fecha_analisis', datetime.utcnow().strftime('%Y-%m-%d'))
			return result

		except Exception as e:
			# Fallback heurístico: generar un resumen simple
			resumen = []
			prioridades = []

			# Tomar pequeñas piezas de texto de los Qs disponibles para construir una síntesis mínima
			for k in sorted(available)[:5]:
				try:
					snippet = ''
					v = insights.get(k)
					if isinstance(v, dict):
						# intentar extraer campos comunes
						snippet = v.get('resumen_ejecutivo') or v.get('summary') or str(list(v.keys())[:3])
					else:
						snippet = str(type(v))
					resumen.append(f"Fuente {k}: {str(snippet)[:240]}")
				except Exception:
					continue

			# Prioridades heurísticas simples
			prioridades = [
				{"accion": "Mejorar CTA en posts con alto engagement", "impacto_score": 75, "frameworks_relevantes": [f for f in available if 'Q6' in available]},
				{"accion": "Aumentar formatos de video corto (Reels) en momentos pico", "impacto_score": 70, "frameworks_relevantes": [f for f in available if 'Q8' in available]},
				{"accion": "Refinar mensajes clave detectados en análisis de tópicos", "impacto_score": 65, "frameworks_relevantes": [f for f in available if 'Q3' in available]}
			]

			metadata = {"fecha_analisis": datetime.utcnow().strftime('%Y-%m-%d'), "nota": "fallback"}
			return {"resumen": resumen, "prioridades": prioridades, "metadata": metadata, "fallback": True, "error": str(e)}

