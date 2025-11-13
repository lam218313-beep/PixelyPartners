import json
import os
from typing import Any, Dict, List
from datetime import datetime

from .base_analyzer import BaseAnalyzer


class Q9Recomendaciones(BaseAnalyzer):
    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        """
        Q9: Genera recomendaciones accionables, priorizadas y trazables a partir
        de los resultados de los demás Q (Q1-Q20) y los datos ingeridos.
        Devuelve un JSON con la clave `lista_recomendaciones` (5-8 items) y `metadata`.
        """
        ingested_data = self.load_ingested_data()

        # Buscar outputs existentes (Q1..Q20) en el directorio de outputs
        insights: Dict[str, Any] = {}
        try:
            files = os.listdir(self.outputs_dir)
        except Exception:
            files = []

        for fname in files:
            if not fname.lower().endswith('.json'):
                continue
            # Evitar leer el propio archivo de salida (si ya existe)
            if fname.lower().startswith('q9_'):
                continue

            parts = fname.split('_')
            if len(parts) == 0:
                continue
            module_id = parts[0].upper()  # e.g., 'q1'
            try:
                with open(os.path.join(self.outputs_dir, fname), 'r', encoding='utf-8') as f:
                    insights[module_id] = json.load(f)
            except Exception:
                # Si no se puede leer, omitir
                continue

        # System is single-client by design; do not include Q16 competitor aggregates in recommendations
        try:
            if 'Q16' in insights:
                insights.pop('Q16', None)
        except Exception:
            pass

        # Preparar prompt: concatenar un resumen de los insights para enviar al LLM
        # Para evitar prompts excesivamente grandes, incluimos solo claves y pequeños samples.
        insights_summary: Dict[str, Any] = {}
        for k, v in insights.items():
            try:
                # Limitar el sample a contenidos relevantes
                if isinstance(v, dict):
                    sample = {key: (v[key] if isinstance(v[key], (str, int, float)) else str(type(v[key]))) for key in list(v.keys())[:8]}
                else:
                    sample = str(type(v))
            except Exception:
                sample = "<no_sample>"
            insights_summary[k] = sample

        data_for_prompt = {
            "ingested_posts_count": len(ingested_data.get('posts', [])),
            "available_insights": list(insights.keys()),
            "insights_summary": insights_summary
        }

        prompt = f"""
        Rol: Director de Estrategia de Marketing. Tu tarea es sintetizar los insights disponibles
        y generar entre 5 y 8 recomendaciones accionables para el equipo de marketing.

        Requisitos estrictos de salida (devuelve SOLO JSON):
        - lista_recomendaciones: lista de 5 a 8 objetos con las claves:
            * area_estrategica (Contenido | Tono | Campañas | Engagement | Formatos)
            * recomendacion (string, acción clara y específica)
            * score_impacto (entero 0-100)
            * justificacion_framework (lista de IDs, ej. ["Q4","Q6"]) que justifican la recomendación
            * evidencia (breve texto que referencia los insights usados)
        - metadata: {{ fecha_analisis: YYYY-MM-DD, total_recomendaciones: N, promedio_score: número }}

        Datos disponibles:
        {json.dumps(data_for_prompt, ensure_ascii=False, indent=2)}

        Instrucciones: Prioriza recomendaciones accionables y cuantificables. Asegúrate de que
        `justificacion_framework` haga referencia a los Qs presentes en `available_insights`.
        """

        try:
            # Intentar llamada al LLM (si está disponible en el entorno)
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en estrategia de marketing y síntesis de insights."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # Validación mínima: asegurar keys esperadas
            if 'lista_recomendaciones' not in result:
                raise ValueError('Respuesta del LLM no tiene lista_recomendaciones')

            return result

        except Exception as e:
            # Fallback: generar recomendaciones heurísticas a partir de posts ingeridos
            try:
                posts = ingested_data.get('posts', [])
                # Calcular engagement por post
                for p in posts:
                    likes = p.get('likesCount') or 0
                    comments = p.get('commentsCount') or 0
                    views = p.get('viewsCount') or 0
                    try:
                        # views can be empty string
                        views = int(views) if views not in ("", None) else 0
                    except Exception:
                        views = 0
                    p['__engagement'] = int(likes) + int(comments) + int(views)

                df_posts = sorted(posts, key=lambda x: x.get('__engagement', 0), reverse=True)
                top_types = {}
                for p in df_posts[:200]:
                    ct = p.get('content_type', 'Desconocido')
                    top_types.setdefault(ct, []).append(p.get('__engagement', 0))

                avg_by_type = {k: int(sum(v)/len(v)) for k, v in top_types.items()} if top_types else {}
                # Pick top content types
                sorted_types = sorted(avg_by_type.items(), key=lambda x: x[1], reverse=True)

                recommendations: List[Dict[str, Any]] = []
                # Create up to 5 heuristic recs
                areas = ['Contenido', 'Tono', 'Campañas', 'Engagement', 'Formatos']
                for i in range(5):
                    area = areas[i % len(areas)]
                    if i < len(sorted_types):
                        ct, score = sorted_types[i]
                        rec_text = f"Aumentar el uso de formatos tipo '{ct}' (mejor rendimiento promedio: {score}) en las próximas 4 semanas."
                        justification = ["Q8"] if 'Q8' in insights else []
                        s = min(90, 50 + int((score / (max(1, sum(avg_by_type.values())/len(avg_by_type))) - 1) * 20))
                    else:
                        rec_text = "Reforzar llamadas a la acción (CTA) claras y consistentes en publicaciones con buen rendimiento." 
                        justification = ["Q6"] if 'Q6' in insights else []
                        s = 60

                    recommendations.append({
                        "area_estrategica": area,
                        "recomendacion": rec_text,
                        "score_impacto": int(s),
                        "justificacion_framework": justification,
                        "evidencia": "Basado en engagement agregado de publicaciones ingestadas."
                    })

                metadata = {
                    "fecha_analisis": datetime.utcnow().strftime('%Y-%m-%d'),
                    "total_recomendaciones": len(recommendations),
                    "promedio_score": int(sum([r['score_impacto'] for r in recommendations]) / len(recommendations))
                }

                return {"lista_recomendaciones": recommendations, "metadata": metadata, "fallback": True, "error": str(e)}

            except Exception as ex2:
                # Último recurso: devolver estructura vacía con error
                metadata = {"fecha_analisis": datetime.utcnow().strftime('%Y-%m-%d'),
                            "total_recomendaciones": 0, "promedio_score": 0}
                return {"lista_recomendaciones": [], "metadata": metadata, "fallback": True, "error": f"Primary error: {e}; fallback error: {ex2}"}
