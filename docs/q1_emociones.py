import pandas as pd
from typing import Dict, Any
import json
from .base_analyzer import BaseAnalyzer

class Q1Emociones(BaseAnalyzer):
    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        """
        Realiza el análisis de emociones sobre los COMENTARIOS de cada publicación.
        Carga los datos, agrupa los comentarios por publicación y analiza el texto consolidado.
        """
        ingested_data = self.load_ingested_data()
        posts = ingested_data.get("posts", [])
        comments = ingested_data.get("comments", [])

        if not comments:
            print("Advertencia: No se encontraron comentarios para analizar en el Módulo Q1.")
            return {
                "analisis_por_publicacion": [],
                "resumen_global_emociones": {}
            }

        comments_df = pd.DataFrame(comments)
        
        analisis_por_publicacion = []
        all_emotions_data = []

        for post in posts:
            post_url = post.get("post_url")
            if not post_url:
                continue

            # Filtrar comentarios para la publicación actual
            post_comments_df = comments_df[comments_df['post_url'] == post_url]
            
            if post_comments_df.empty:
                continue
            
            # Concatenar el texto de todos los comentarios para esta publicación
            # Se asume que la columna con el texto del comentario se llama 'comment_text'
            comments_text = " ".join(post_comments_df['comment_text'].dropna().astype(str))

            if not comments_text.strip():
                continue

            prompt = f"""Analiza el siguiente texto, que es una compilación de comentarios de una publicación en redes sociales. Devuelve un objeto JSON con las 8 emociones principales (alegria, tristeza, miedo, ira, sorpresa, disgusto, anticipacion, confianza) y sus puntuaciones (entre 0 y 1). También incluye un resumen emocional de los comentarios.

            Texto: "{comments_text}"

            Formato de salida JSON:
            {{
                "emociones": {{
                    "alegria": float,
                    "tristeza": float,
                    "miedo": float,
                    "ira": float,
                    "sorpresa": float,
                    "disgusto": float,
                    "anticipacion": float,
                    "confianza": float
                }},
                "resumen_emocional": "string"
            }}
            """
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Eres un asistente experto en análisis de emociones de audiencias."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                analysis_result = json.loads(response.choices[0].message.content)
                
                analisis_por_publicacion.append({
                    "post_url": post_url,
                    "emociones": analysis_result["emociones"],
                    "resumen_emocional": analysis_result["resumen_emocional"]
                })
                all_emotions_data.append(analysis_result["emociones"])

            except Exception as e:
                print(f"Error al analizar emociones para la URL {post_url}: {e}")
                analisis_por_publicacion.append({
                    "post_url": post_url,
                    "emociones": {},
                    "resumen_emocional": f"Análisis no disponible debido a un error: {e}"
                })

        # Calculate global summary
        resumen_global_emociones = {}
        if all_emotions_data:
            avg_emotions = pd.DataFrame(all_emotions_data).mean().to_dict()
            resumen_global_emociones = avg_emotions

        # Build lightweight actors list (top commenters) to align with project convention
        actors = []
        try:
            from collections import Counter
            commenters = [c.get('ownerUsername') for c in comments if c.get('ownerUsername')]
            cnt = Counter(commenters)
            for user, count in cnt.most_common(5):
                actors.append({"actor": user, "username": user, "comment_count": int(count)})
        except Exception:
            actors = []

        # Apply client-only actor filtering (system is single-client by design)
        actors = self.filter_to_client_actors(actors, ingested_data)

        return {
            "analisis_por_publicacion": analisis_por_publicacion,
            "resumen_global_emociones": resumen_global_emociones,
            "actors": actors
        }
