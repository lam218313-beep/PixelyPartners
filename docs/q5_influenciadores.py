
import json
from typing import Any, Dict, List
import pandas as pd
from .base_analyzer import BaseAnalyzer

class Q5Influenciadores(BaseAnalyzer):
    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        """
        Identifica a los 10 principales influenciadores a partir de los comentarios,
        analiza la polaridad de su discurso y extrae un comentario de evidencia.
        """
        ingested_data = self.load_ingested_data()
        comments = ingested_data.get("comments", [])

        if not comments:
            print("Advertencia: No se encontraron comentarios para analizar en el Módulo Q5.")
            return {
                "top_influenciadores_detallado": [],
                "resumen_polaridad": {"Promotor": 0, "Detractor": 0},
                "actors": []
            }

        # Para evitar un prompt demasiado grande, podemos trabajar con una muestra representativa
        # o con un resumen pre-procesado. Aquí, usaremos una muestra de hasta 500 comentarios.
        comments_sample = comments[:500]
        
        # Convertir solo los campos necesarios para el prompt a una cadena JSON
        comments_for_prompt = json.dumps([
            {
                "username": c.get("ownerUsername"),
                "comment_text": c.get("comment_text")
            }
            for c in comments_sample
        ], indent=2)

        prompt = f"""
        Rol: Eres un experto en Análisis de Redes Sociales, Centralidad y un analista de discurso.

        Tarea: Analiza la siguiente lista de comentarios para identificar a los **Top 10 Influenciadores**. La influencia se mide por la frecuencia y el engagement que generan sus comentarios (aunque no tengamos likes, la frecuencia y la fuerza del lenguaje son proxies).

        Para cada uno de estos 10 usuarios, realiza un análisis secundario de todos sus comentarios en la muestra para determinar el **Sentimiento Dominante** de su discurso: **"Promotor" (Positivo)** o **"Detractor" (Negativo)**.

        Finalmente, para cada influenciador, extrae su comentario más representativo o influyente como evidencia.

        Datos de Comentarios:
        {comments_for_prompt}

        Instrucciones de Salida:
        Devuelve un único objeto JSON con la siguiente estructura:
        {{
          "top_influenciadores_detallado": [
            {{
              "username": "string",
              "score_centralidad": "float (de 0 a 1, donde 1 es la máxima influencia)",
              "polaridad_dominante": "string (Promotor o Detractor)",
              "comentario_evidencia": "string (el texto del comentario más representativo)"
            }}
          ],
          "resumen_polaridad": {{
            "Promotor": "integer (conteo total de promotores)",
            "Detractor": "integer (conteo total de detractores)"
          }}
        }}
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en Análisis de Redes Sociales y análisis de discurso."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Initialize with default structure to ensure consistency
            analysis_result = {
                "top_influenciadores_detallado": [],
                "resumen_polaridad": {"Promotor": 0, "Detractor": 0}
            }

            openai_response_content = json.loads(response.choices[0].message.content)
            
            if "top_influenciadores_detallado" in openai_response_content:
                analysis_result["top_influenciadores_detallado"] = openai_response_content["top_influenciadores_detallado"]
            
            if "resumen_polaridad" in openai_response_content:
                analysis_result["resumen_polaridad"] = openai_response_content["resumen_polaridad"]

            # Validate and ensure 'polaridad_dominante' and 'score_centralidad' exist for each influencer
            for influencer in analysis_result["top_influenciadores_detallado"]:
                if "polaridad_dominante" not in influencer:
                    influencer["polaridad_dominante"] = "Desconocido" # Default value
                if "score_centralidad" not in influencer:
                    influencer["score_centralidad"] = 0.0 # Default numeric value
            # Build actors list from top influencers for frontend compatibility
            try:
                actors = []
                for inf in analysis_result.get("top_influenciadores_detallado", []):
                    actors.append({
                        "actor": inf.get("username"),
                        "username": inf.get("username"),
                        "score_centralidad": float(inf.get("score_centralidad", 0.0))
                    })
                # Filter actors to client-only (system single-client by design)
                actors = self.filter_to_client_actors(actors, ingested_data)
                analysis_result["actors"] = actors
            except Exception:
                analysis_result["actors"] = []

            return analysis_result
        except Exception as e:
            print(f"Error al analizar influenciadores en Módulo Q5: {e}")
            return {
                "top_influenciadores_detallado": [],
                "resumen_polaridad": {"Promotor": 0, "Detractor": 0},
                "error": str(e)
            }
