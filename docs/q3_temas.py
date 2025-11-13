import pandas as pd
from typing import Dict, Any, List
import json
from .base_analyzer import BaseAnalyzer
import logging

class Q3Temas(BaseAnalyzer):
    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        """
        Realiza el análisis de tópicos y sentimiento asociado sobre los COMENTARIOS de cada publicación.
        Carga los datos, agrupa los comentarios por publicación y analiza el texto consolidado.
        """
        logging.info("Q3Temas: Starting real analysis.")
        ingested_data = self._load_ingested_data()
        posts = ingested_data.get("posts", [])
        comments = ingested_data.get("comments", [])

        if not comments:
            logging.warning("Advertencia: No se encontraron comentarios para analizar en el Módulo Q3.")
            return {
                "analisis_agregado": [],
                "analisis_por_publicacion": []
            }

        comments_df = pd.DataFrame(comments)
        
        analisis_por_publicacion_results = []
        all_comments_text = []

        for post in posts:
            post_url = post.get("post_url")
            if not post_url:
                continue

            post_comments_df = comments_df[comments_df['post_url'] == post_url]
            
            if post_comments_df.empty:
                continue
            
            comments_text = " ".join(post_comments_df['comment_text'].dropna().astype(str))
            all_comments_text.append(comments_text)

            if not comments_text.strip():
                continue

            prompt = f"""Eres un experto en Modelado de Tópicos (Topic Modeling) y Análisis de Sentimiento.
            Analiza CADA UNO de los comentarios proporcionados. Aplica modelado de tópicos para identificar los principales temas, clasifica el tópico dominante y su sentimiento (Positivo, Neutro, Negativo).

            Inputs de Datos: Una lista de comentarios, donde cada comentario incluye su text y su post_url.

            Instrucciones de Cálculo y Salida:
            Para la publicación con URL: {post_url}, calcula la distribución de tópicos porcentual y el sentimiento promedio asociado a esos tópicos solo dentro de esta publicación.

            Texto de comentarios para analizar: "{comments_text}"

            Formato de salida JSON:
            {{
                "post_url": "string",
                "temas_distribucion": {{
                    "tema1": float, // percentage, e.g., 0.6
                    "tema2": float
                }},
                "sentimiento_promedio_por_tema": {{
                    "tema1": float, // -1 for Negative, 0 for Neutral, 1 for Positive
                    "tema2": float
                }}
            }}
            """
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Eres un experto en Modelado de Tópicos y Análisis de Sentimiento."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                analysis_result = json.loads(response.choices[0].message.content)
                analisis_por_publicacion_results.append(analysis_result)

            except Exception as e:
                logging.error(f"Error al analizar tópicos para la URL {post_url}: {e}")
                analisis_por_publicacion_results.append({
                    "post_url": post_url,
                    "temas_distribucion": {},
                    "sentimiento_promedio_por_tema": {},
                    "error": f"Análisis no disponible debido a un error: {e}"
                })
        
        # Global analysis for analisis_agregado
        global_comments_text = " ".join(all_comments_text)
        if not global_comments_text.strip():
            analisis_agregado_results = []
        else:
            global_prompt = f"""Eres un experto en Modelado de Tópicos (Topic Modeling) y Análisis de Sentimiento.
            Analiza el siguiente texto, que es una compilación de todos los comentarios de varias publicaciones en redes sociales.
            Calcula la frecuencia porcentual y el sentimiento promedio de los principales tópicos para el 100% de los comentarios.

            Texto de todos los comentarios: "{global_comments_text}"

            Formato de salida JSON:
            {{
                "analisis_agregado": [
                    {{
                        "tema": "string",
                        "frecuencia_porcentaje": float,
                        "sentimiento_promedio": float // -1 for Negative, 0 for Neutral, 1 for Positive
                    }}
                ]
            }}
            """
            try:
                global_response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Eres un experto en Modelado de Tópicos y Análisis de Sentimiento."},
                        {"role": "user", "content": global_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                global_analysis_result = json.loads(global_response.choices[0].message.content)
                analisis_agregado_results = global_analysis_result.get("analisis_agregado", [])
            except Exception as e:
                logging.error(f"Error al realizar el análisis agregado de tópicos: {e}")
                analisis_agregado_results = []

        return {
            "analisis_agregado": analisis_agregado_results,
            "analisis_por_publicacion": analisis_por_publicacion_results
        }
