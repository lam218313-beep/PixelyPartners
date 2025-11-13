import json
from typing import Any, Dict, List
from .base_analyzer import BaseAnalyzer

class Q7SentimientoDetallado(BaseAnalyzer):
    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        """
        Analiza el sentimiento detallado, incluyendo ambivalencia y subjetividad.
        """
        # Cargar datos ingeridos
        ingested_data = self.load_ingested_data()
        comments = ingested_data.get("comments", [])
        
        if not comments:
            print("Advertencia: No se encontraron comentarios para analizar en el Módulo Q7.")
            return {
                "analisis_agregado": {
                    "positivo": 0,
                    "negativo": 0,
                    "neutro": 0,
                    "mixto": 0,
                    "subjetividad_promedio_global": 0
                },
                "analisis_por_publicacion": []
            }

        # Agrupar comentarios por post_url
        comments_by_post = {}
        for comment in comments:
            post_url = comment.get("post_url", "unknown")
            if post_url not in comments_by_post:
                comments_by_post[post_url] = []
            comments_by_post[post_url].append({
                "text": comment.get("comment_text", ""),
                "username": comment.get("ownerUsername", "anonymous")
            })

        # Analizar cada publicación
        results_by_post = []
        total_comments = len(comments)
        total_positivos = 0
        total_negativos = 0
        total_neutros = 0
        total_mixtos = 0
        total_subjetividad = 0

        for post_url, post_comments in comments_by_post.items():
            # Preparar datos para el prompt
            comments_text = [
                f"Comment {i+1}: {comment['text']}"
                for i, comment in enumerate(post_comments[:50])  # Limitar a 50 comentarios por post
            ]
            
            comments_text = "\n".join(comments_text)

            prompt = f"""
            Rol: Eres un Analista de Discurso y Sentimiento altamente avanzado, especializado en la detección de ambivalencia y subjetividad.

            Tarea: Analiza los siguientes comentarios de una publicación y clasifícalos según su sentimiento y subjetividad.
            Asigna cada comentario a una de estas categorías: Positivo, Negativo, Neutro o Mixto.
            Además, calcula un score de subjetividad (0.0 a 1.0) donde:
            - 0.0 significa completamente objetivo (hechos puros)
            - 1.0 significa completamente subjetivo (opiniones puras)

            Comentarios a analizar:
            {comments_text}

            Instrucciones:
            1. Analiza cada comentario y determina su categoría y subjetividad.
            2. Calcula las distribuciones porcentuales.
            3. Identifica el comentario más representativo del sentimiento "Mixto".

            Devuelve un JSON con esta estructura:
            {{
                "distribucion": {{
                    "positivo": float,
                    "negativo": float,
                    "neutro": float,
                    "mixto": float
                }},
                "subjetividad_promedio": float,
                "ejemplo_mixto": {{
                    "texto": "string (comentario más representativo del sentimiento mixto)",
                    "username": "string (usuario que lo escribió)"
                }}
            }}
            """

            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un experto en análisis de sentimiento y detección de ambivalencia en texto."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                post_analysis = response.choices[0].message.content
                post_results = json.loads(post_analysis)
                
                # Actualizar totales globales
                total_positivos += len(post_comments) * post_results["distribucion"]["positivo"]
                total_negativos += len(post_comments) * post_results["distribucion"]["negativo"]
                total_neutros += len(post_comments) * post_results["distribucion"]["neutro"]
                total_mixtos += len(post_comments) * post_results["distribucion"]["mixto"]
                total_subjetividad += len(post_comments) * post_results["subjetividad_promedio"]

                # Guardar resultados de esta publicación
                results_by_post.append({
                    "post_url": post_url,
                    "distribucion": post_results["distribucion"],
                    "subjetividad_promedio": post_results["subjetividad_promedio"],
                    "ejemplo_mixto": post_results["ejemplo_mixto"],
                    "total_comentarios": len(post_comments)
                })

            except Exception as e:
                print(f"Error al analizar post {post_url}: {str(e)}")
                continue

        # Calcular promedios globales
        return {
            "analisis_agregado": {
                "positivo": total_positivos / total_comments if total_comments > 0 else 0,
                "negativo": total_negativos / total_comments if total_comments > 0 else 0,
                "neutro": total_neutros / total_comments if total_comments > 0 else 0,
                "mixto": total_mixtos / total_comments if total_comments > 0 else 0,
                "subjetividad_promedio_global": total_subjetividad / total_comments if total_comments > 0 else 0
            },
            "analisis_por_publicacion": sorted(
                results_by_post,
                key=lambda x: x["distribucion"]["mixto"],
                reverse=True
            )
        }
