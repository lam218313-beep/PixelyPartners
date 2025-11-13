from typing import Any, Dict
from .base_analyzer import BaseAnalyzer

class Q4MarcosNarrativos(BaseAnalyzer):
    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        """
        Analiza los datos para identificar los marcos narrativos.
        """
        # Cargar datos ingeridos
        ingested_data = self.load_ingested_data()

        ingested_data = self.load_ingested_data()
        posts = ingested_data.get("posts", [])

        if not posts:
            print("Advertencia: No se encontraron publicaciones para analizar en el Módulo Q4.")
            return {"marcos_narrativos": [], "resumen_marcos": "No hay datos para analizar."}

        # Consolidar el texto de todas las publicaciones
        all_posts_text = " ".join([post.get('caption', '') for post in posts if post.get('caption')])

        if not all_posts_text.strip():
            print("Advertencia: No se encontró texto en las publicaciones para analizar en el Módulo Q4.")
            return {"marcos_narrativos": [], "resumen_marcos": "No hay texto en las publicaciones para analizar."}

        prompt = f"""
        Analiza el siguiente conjunto de textos de publicaciones de redes sociales para identificar los marcos narrativos dominantes. Un marco narrativo es la estructura subyacente de la historia que da forma a cómo se presenta la información.

        Texto de las publicaciones:
        "{all_posts_text}"

        Basado en el texto, identifica y describe hasta 5 marcos narrativos clave. Para cada marco, proporciona una descripción y ejemplos extraídos del texto.

        Formato de salida JSON:
        {{
          "marcos_narrativos": [
            {{
              "marco": "Nombre del Marco Narrativo (ej. El Viaje del Héroe, Nosotros vs. Ellos, Innovación Disruptiva)",
              "descripcion": "Una breve descripción de cómo se utiliza este marco en las publicaciones.",
              "ejemplos": [
                "Ejemplo de texto de una publicación que ilustra este marco.",
                "Otro ejemplo..."
              ]
            }}
          ],
          "resumen_marcos": "Un resumen general de cómo la marca utiliza los marcos narrativos para comunicarse con su audiencia."
        }}
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de estrategias de comunicación y narratología."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            analysis_result = json.loads(response.choices[0].message.content)
            return analysis_result
        except Exception as e:
            print(f"Error al analizar marcos narrativos: {e}")
            return {"marcos_narrativos": [], "resumen_marcos": f"Análisis no disponible debido a un error: {e}"}
