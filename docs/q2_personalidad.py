import pandas as pd
import re
from typing import Dict, Any
import json
from .base_analyzer import BaseAnalyzer

class Q2Personalidad(BaseAnalyzer):
    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        super().__init__(openai_client, config)

    async def analyze(self) -> Dict[str, Any]:
        """
        Realiza el análisis de personalidad de marca (Aaker) sobre los COMENTARIOS de cada publicación.
        """
        ingested_data = self.load_ingested_data()
        posts = ingested_data.get("posts", [])
        comments = ingested_data.get("comments", [])
        client_info = ingested_data.get("client_info", {})

        if not comments:
            print("Advertencia: No se encontraron comentarios para analizar en el Módulo Q2.")
            return {
                "analisis_agregado": {},
                "analisis_por_publicacion": []
            }

        comments_df = pd.DataFrame(comments)
        
        # Contexto del cliente para el prompt
        narrativa = client_info.get("narrativa", "No disponible")
        arquetipo = client_info.get("arquetipo_marca", "No disponible")
        tono_voz = client_info.get("tono_voz", "No disponible")

        analisis_por_publicacion = []
        all_traits_data = []

        for post in posts:
            post_url = post.get("post_url")
            if not post_url:
                continue

            post_comments_df = comments_df[comments_df['post_url'] == post_url]
            
            if post_comments_df.empty:
                continue
            
            comments_text = " ".join(post_comments_df['comment_text'].dropna().astype(str))

            if not comments_text.strip():
                continue

            prompt = f"""
            **Rol:** Eres un Analista de Personalidad de Marca experto en el Modelo de Aaker y en contextualización estratégica.

            **Contexto de Marca:**
            - **Narrativa:** {narrativa}
            - **Arquetipo:** {arquetipo}
            - **Tono de Voz:** {tono_voz}

            **Tarea:**
            Analiza el siguiente texto, que es una compilación de comentarios de una publicación. Clasifica la percepción manifestada en los cinco rasgos de Aaker: sinceridad, emoción, competencia, sofisticación y robustez. Para cada comentario, identifica el rasgo dominante y asigna un puntaje de intensidad (del 1 al 100) para ese rasgo.

            **Texto de Comentarios:** "{comments_text}"

            **Instrucciones de Cálculo y Salida:**
            1.  **Análisis de Rasgos:** Calcula la distribución porcentual de los 5 rasgos de marca para el conjunto de comentarios. La suma de los 5 porcentajes debe ser 100.
            2.  **Intensidad Promedio:** Calcula la intensidad promedio del rasgo dominante percibido.
            3.  **Output JSON:** Devuelve un único objeto JSON con la siguiente estructura:
                {{
                    "rasgos_distribuidos": {{
                        "sinceridad": float,
                        "emocion": float,
                        "competencia": float,
                        "sofisticacion": float,
                        "robustez": float
                    }},
                    "intensidad_promedio": float
                }}
            """
            # If openai_client is available, use it; otherwise use a lightweight heuristic
            if getattr(self, 'openai_client', None):
                try:
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Eres un asistente experto en análisis de personalidad de marca de audiencias."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )

                    analysis_result = json.loads(response.choices[0].message.content)

                    # Validar que la suma de la distribución sea cercana a 100
                    total_dist = sum(analysis_result.get("rasgos_distribuidos", {}).values())
                    if not (99 <= total_dist <= 101):
                        print(f"Advertencia: La distribución de rasgos para {post_url} no suma 100 (suma: {total_dist}). Se omitirá del análisis agregado.")
                    else:
                        all_traits_data.append(analysis_result["rasgos_distribuidos"])

                    analisis_por_publicacion.append({
                        "post_url": post_url,
                        "rasgos_distribuidos": analysis_result.get("rasgos_distribuidos", {}),
                        "intensidad_promedio": analysis_result.get("intensidad_promedio", 0.0)
                    })

                except Exception as e:
                    print(f"Error al analizar personalidad para la URL {post_url}: {e}")
                    analisis_por_publicacion.append({
                        "post_url": post_url,
                        "rasgos_distribuidos": {},
                        "intensidad_promedio": 0.0,
                        "error": f"Análisis no disponible: {e}"
                    })
            else:
                # Heuristic offline analysis for testing: simple keyword counts per trait
                def heuristic_analyze(text: str) -> Dict[str, Any]:
                    if not text or not text.strip():
                        return {"rasgos_distribuidos": {}, "intensidad_promedio": 0.0}

                    # keyword lists (small, illustrative)
                    keywords = {
                        'sinceridad': [r"honest", r"sincer", r"real", r"genuine", r"autent"],
                        'emocion': [r"love", r"amazing", r"increibl", r"emoc", r"❤️", r"💖", r"😍"],
                        'competencia': [r"expert", r"professional", r"competent", r"knowledge"],
                        'sofisticacion': [r"elegant", r"sophist", r"premium", r"sofistic"],
                        'robustez': [r"strong", r"solid", r"robust", r"reliable"]
                    }

                    counts = {k: 0 for k in keywords}
                    text_lower = text.lower()
                    for k, pats in keywords.items():
                        for p in pats:
                            matches = re.findall(p, text_lower)
                            counts[k] += len(matches)

                    total = sum(counts.values())
                    if total == 0:
                        # fallback: distribute by simple heuristics based on punctuation and length
                        # use emoticons/exclamation to favor 'emocion'
                        emoc_score = text.count('!') + text.count('❤️') + text.count('😍')
                        avg_len = max(1, len(text.split()))
                        base = {
                            'sinceridad': 1,
                            'emocion': 1 + emoc_score,
                            'competencia': 1,
                            'sofisticacion': 1,
                            'robustez': 1
                        }
                        total = sum(base.values())
                        dist = {k: (v / total) * 100 for k, v in base.items()}
                        intensity = min(100.0, 10.0 + (avg_len / 5.0))
                        return {"rasgos_distribuidos": dist, "intensidad_promedio": intensity}

                    # normalize counts -> percentages summing to 100
                    dist = {k: (v / total) * 100 for k, v in counts.items()}

                    # intensity heuristic: based on density of matches and punctuation
                    density = total / max(1, len(text.split()))
                    emphasis = text.count('!') * 0.5
                    intensity = min(100.0, (density * 100.0) + emphasis)

                    return {"rasgos_distribuidos": dist, "intensidad_promedio": round(float(intensity), 2)}

                try:
                    analysis_result = heuristic_analyze(comments_text)
                    # accumulate only if non-empty distribution
                    if analysis_result.get('rasgos_distribuidos'):
                        all_traits_data.append(analysis_result['rasgos_distribuidos'])
                    analisis_por_publicacion.append({
                        'post_url': post_url,
                        'rasgos_distribuidos': analysis_result.get('rasgos_distribuidos', {}),
                        'intensidad_promedio': analysis_result.get('intensidad_promedio', 0.0)
                    })
                except Exception as e:
                    print(f"Heuristic analysis failed for {post_url}: {e}")
                    analisis_por_publicacion.append({
                        'post_url': post_url,
                        'rasgos_distribuidos': {},
                        'intensidad_promedio': 0.0,
                        'error': f'Heuristic failed: {e}'
                    })

        # Calcular el análisis agregado global
        analisis_agregado = {}
        if all_traits_data:
            avg_traits = pd.DataFrame(all_traits_data).mean().to_dict()
            total = sum(avg_traits.values())
            if total > 0:
                # Normalizar para que la suma sea 100%
                analisis_agregado = {k: (v / total) * 100 for k, v in avg_traits.items()}
        # Construir lista 'actors' agregando por ownerUsername (cliente + competidores)
        # Mapeo post_url -> ownerUsername
        post_owner = {p.get('post_url'): p.get('ownerUsername') for p in posts if p.get('post_url')}

        # Agrupar rasgos e intensidades por ownerUsername
        actors_map = {}
        for item in analisis_por_publicacion:
            url = item.get('post_url')
            owner = post_owner.get(url)
            if not owner:
                continue
            actors_map.setdefault(owner, {'rasgos': [], 'intensidades': []})
            rasgos = item.get('rasgos_distribuidos') or {}
            if rasgos:
                actors_map[owner]['rasgos'].append(rasgos)
            intensidad = item.get('intensidad_promedio', 0.0)
            actors_map[owner]['intensidades'].append(float(intensidad or 0.0))

        # Helper to find followers for a username from client_ficha or competitor_landscape
        def find_followers_for(username: str):
            try:
                # client followers
                cf = ingested_data.get('client_ficha', {})
                client_name = cf.get('client_name', '')
                if username and client_name and username.lower() in client_name.lower():
                    return cf.get('seguidores_instagram') or cf.get('seguidores_instagram', None)

                # competitors
                for c in cf.get('competitor_landscape', []) or []:
                    insta = c.get('instagram') or ''
                    # extract username from url if possible
                    if insta and username and username.lower() in insta.lower():
                        return c.get('instagram_followers')
                return None
            except Exception:
                return None

        actors = []
        for owner, vals in actors_map.items():
            rasgos_list = vals.get('rasgos', [])
            intensidades = vals.get('intensidades', [])
            avg_rasgos = {}
            if rasgos_list:
                avg_rasgos = pd.DataFrame(rasgos_list).mean().to_dict()
            avg_int = float(pd.Series(intensidades).mean()) if intensidades else 0.0

            followers = find_followers_for(owner)

            actors.append({
                'actor': owner,
                'username': owner,
                'followers': followers,
                'rasgos_distribuidos': avg_rasgos,
                'intensidad_promedio': avg_int
            })

        # Filter actors to client-only (system single-client by design)
        actors = self.filter_to_client_actors(actors, ingested_data)

        return {
            "analisis_agregado": analisis_agregado,
            "analisis_por_publicacion": analisis_por_publicacion,
            "actors": actors
        }