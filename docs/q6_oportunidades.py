import json
from typing import Any, Dict, List
from .base_analyzer import BaseAnalyzer

class Q6Oportunidades(BaseAnalyzer):
    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        """
        Identifica oportunidades clave a partir de los datos ingeridos.
        """
        ingested_data = self.load_ingested_data()
        comments = ingested_data.get("comments", [])
        posts = ingested_data.get("posts", [])

        if not comments and not posts:
            print("Advertencia: No se encontraron comentarios ni publicaciones para analizar en el Módulo Q6.")
            return {
                "oportunidades_identificadas": [],
                "resumen_ejecutivo": "No hay datos disponibles para identificar oportunidades."
            }

        # Usar una muestra de comentarios y posts para el prompt
        comments_sample = comments[:200] # Limit to 200 comments
        posts_sample = posts[:50] # Limit to 50 posts

        # Prepare data for prompt
        data_for_prompt = {
            "comments": [
                {"username": c.get("ownerUsername"), "comment_text": c.get("comment_text")}
                for c in comments_sample
            ],
            "posts": [
                {"caption": p.get("caption"), "likes": p.get("likesCount"), "comments_count": p.get("commentsCount")}
                for p in posts_sample
            ]
        }
        
        data_json_string = json.dumps(data_for_prompt, indent=2, ensure_ascii=False)

        prompt = f"""
        Rol: Eres un Consultor de Estrategia de Mercado experto en Análisis de Brechas (Gap Analysis) y en contextualización de inteligencia competitiva.

        Tarea: Analiza los datos proporcionados para identificar oportunidades de mercado y nichos no abordados por la marca. Para cada oportunidad, debes estimar el tamaño de la brecha y el nivel de actividad de los competidores.

        Datos Ingeridos:
        {data_json_string}

        Instrucciones de Salida:
        Devuelve un único objeto JSON con la siguiente estructura, identificando exactamente 5 oportunidades relevantes:
        {{
          "lista_oportunidades": [
            {{
              "tema": "string (nombre corto y descriptivo de la oportunidad)",
              "gap_score": "número entre 0 y 100 que representa la urgencia estratégica",
              "actividad_competitiva": "string ('Baja', 'Media' o 'Alta') que representa la barrera de entrada",
              "justificacion": "string (evidencias que justifican el gap_score y la actividad_competitiva)",
              "recomendacion_accion": "string (acción específica y detallada para aprovechar la oportunidad)"
            }}
          ],
          "metadata": {{
            "fecha_analisis": "YYYY-MM-DD",
            "total_oportunidades": 5,
            "promedio_gap": "número promedio de gap_score",
            "distribucion_actividad": {{
              "Baja": "número de oportunidades con actividad baja",
              "Media": "número de oportunidades con actividad media",
              "Alta": "número de oportunidades con actividad alta"
            }}
          }}
        }}
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de datos de redes sociales y estrategia de contenido."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            analysis_result = json.loads(response.choices[0].message.content)
            # add lightweight actors list as top authors in comments/posts for compatibility
            try:
                actors = []
                # top commenters
                commenters = [c.get('ownerUsername') for c in comments_sample if c.get('ownerUsername')]
                top_commenters = []
                from collections import Counter
                cnt = Counter(commenters)
                for user, count in cnt.most_common(5):
                    actors.append({"actor": user, "username": user, "comment_count": int(count)})

                # top post authors
                post_authors = [p.get('ownerUsername') or p.get('owner') for p in posts_sample if p.get('ownerUsername') or p.get('owner')]
                cnt2 = Counter(post_authors)
                for user, count in cnt2.most_common(5):
                    actors.append({"actor": user, "username": user, "post_count": int(count)})

                # Filter actors to client-only (single-client system)
                actors = self.filter_to_client_actors(actors, ingested_data)
                analysis_result['actors'] = actors
            except Exception:
                analysis_result['actors'] = []

            return analysis_result
        except Exception as e:
            print(f"Error al analizar oportunidades en Módulo Q6: {e}")
            return {
                "oportunidades_identificadas": [],
                "resumen_ejecutivo": f"Error al procesar: {str(e)}",
                "error": str(e),
                "actors": []
            }