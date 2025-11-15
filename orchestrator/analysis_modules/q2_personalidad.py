"""
Pixely Partners - Q2: Brand Personality Analysis (Aaker Framework)

Analyzes audience comments to determine how the brand is perceived using Aaker's
Five Dimensions of Brand Personality: Sincerity, Excitement, Competence, Sophistication, Ruggedness.

Single-client analysis: Analyzes perceived brand personality based on post comments.

Features:
- Resilient API calls with automatic retry (3 attempts, 15s wait)
- Extended context window (15k chars) for nuanced personality analysis
- Strict type conversion for personality values (0-100 integer, normalized to percentages)
- Per-post granular personality profiling with strategic context
"""

from typing import Dict, Any, List
import json
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

# Configure logger to use the shared orchestrator configuration
logger = logging.getLogger(__name__)


class Q2Personalidad(BaseAnalyzer):
    """
    Q2 Brand Personality Analysis using Aaker Framework.
    
    Analyzes comments on each client post to derive brand personality dimensions.
    Returns per-post personality profiles and global personality summary.
    
    Features:
    - Resilient API calls with automatic retry (3 attempts, 15s wait)
    - Extended context window (15k chars) for better analysis
    - Strict normalization for personality values (0-100 → normalized percentages)
    - Strategic context injection (brand archetype, tone of voice)
    """

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
    async def _call_openai_for_personality(self, combined_text: str, brand_context: str) -> Dict[str, Any]:
        """
        Resilient wrapper for OpenAI API call to analyze brand personality.
        
        Retries automatically on failure (max 3 attempts with 15s wait between attempts).
        
        Args:
            combined_text: Aggregated comment text to analyze
            brand_context: Brand identity context (archetype, tone, narrative)
            
        Returns:
            Analysis result dict with rasgos (personality traits)
            
        Raises:
            Exception: If all 3 retry attempts fail
        """
        prompt = f"""You are an expert brand strategist specializing in Aaker's Five Dimensions of Brand Personality.

Based on the following audience comments about a brand, analyze how the brand is PERCEIVED:

BRAND CONTEXT:
{brand_context}

AUDIENCE COMMENTS:
"{combined_text[:15000]}"

Rate each of the 5 brand personality dimensions on a scale of 0-100 (where 0 = not present, 100 = very strong):

1. Sinceridad (Sincerity): Honest, genuine, down-to-earth, cheerful, wholesome
2. Emocion (Excitement): Daring, spirited, imaginative, fun, cool, young
3. Competencia (Competence): Reliable, intelligent, successful, leader, confident
4. Sofisticacion (Sophistication): Upper-class, charming, glamorous, good-taste, smooth
5. Rudeza (Ruggedness): Tough, strong, outdoorsy, rugged, masculine, adventurous

IMPORTANT: Return ONLY valid JSON with raw scores (0-100), not percentages:
{{
    "sinceridad": <integer 0-100>,
    "emocion": <integer 0-100>,
    "competencia": <integer 0-100>,
    "sofisticacion": <integer 0-100>,
    "rudeza": <integer 0-100>,
    "dimensiones_dominantes": ["<strongest dimension>", "<second strongest>"],
    "analisis_cualitativo": "<2-3 sentence analysis of perceived brand personality>"
}}"""

        try:
            # Use Responses API for GPT-5 models
            if self.model_name and "gpt-5" in self.model_name:
                logger.debug(f"Using Responses API for model: {self.model_name}")
                
                # Determine appropriate reasoning.effort value based on model
                if "gpt-5.1" in self.model_name or "gpt-5" == self.model_name:
                    reasoning_effort = "low"  # 'none', 'low', 'medium', 'high'
                else:
                    reasoning_effort = "minimal"  # 'minimal', 'low', 'medium', 'high' for mini/nano
                
                response = await self.openai_client.responses.create(
                    model=self.model_name,
                    input=prompt,
                    reasoning={"effort": reasoning_effort},
                    text={"verbosity": "low"}
                )
                response_text = response.output_text.strip()
            else:
                # Chat Completions for other models
                logger.debug(f"Using Chat Completions API for model: {self.model_name}")
                params = {
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a branding analyst. Return ONLY valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                }

                if not any(x in self.model_name for x in ["gpt-5", "o1"]):
                    params["temperature"] = 0.7
                    params["max_tokens"] = 500

                response = await self.openai_client.chat.completions.create(**params)
                response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            try:
                analysis_result = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from markdown code blocks
                if "```json" in response_text:
                    json_part = response_text.split("```json")[1].split("```")[0].strip()
                    analysis_result = json.loads(json_part)
                elif "```" in response_text:
                    json_part = response_text.split("```")[1].split("```")[0].strip()
                    analysis_result = json.loads(json_part)
                else:
                    raise json.JSONDecodeError("Could not extract JSON from response", response_text, 0)

            return analysis_result

        except Exception as e:
            logger.error(f"Error calling OpenAI API for personality analysis: {str(e)}", exc_info=True)
            raise

    def _normalize_personality_values(self, rasgos_raw: Dict[str, int]) -> Dict[str, float]:
        """
        Normalize raw personality scores (0-100) to percentages that sum to 100%.
        
        Ensures mathematical precision for visualizations.
        
        Args:
            rasgos_raw: Raw scores dict from LLM (0-100 per dimension)
            
        Returns:
            Normalized dict with float percentages summing to 100.0
        """
        # Define expected dimensions
        dimensiones = ["sinceridad", "emocion", "competencia", "sofisticacion", "rudeza"]
        
        # Extract and validate values
        valores_limpios = {}
        for dim in dimensiones:
            valor = rasgos_raw.get(dim, 0)
            try:
                valor_int = int(float(valor))
                valor_int = max(0, min(100, valor_int))  # Clamp to [0, 100]
                valores_limpios[dim] = valor_int
            except (ValueError, TypeError):
                logger.warning(f"Invalid value for '{dim}': {valor}. Using 0.")
                valores_limpios[dim] = 0
        
        # Calculate sum
        suma_total = sum(valores_limpios.values())
        
        # Normalize to percentages
        if suma_total == 0:
            # Equal distribution if all zeros
            rasgos_normalizados = {dim: 20.0 for dim in dimensiones}
        else:
            rasgos_normalizados = {dim: round((valores_limpios[dim] / suma_total) * 100.0, 2) 
                                    for dim in dimensiones}
        
        # Ensure sum is exactly 100.0 (fix rounding errors)
        suma_calculada = sum(rasgos_normalizados.values())
        if suma_calculada != 100.0:
            diferencia = 100.0 - suma_calculada
            # Adjust the largest dimension to fix rounding
            dim_mayor = max(dimensiones, key=lambda d: rasgos_normalizados[d])
            rasgos_normalizados[dim_mayor] = round(rasgos_normalizados[dim_mayor] + diferencia, 2)
        
        return rasgos_normalizados

    def _extract_brand_context(self, client_ficha: Dict[str, Any]) -> str:
        """
        Extract strategic brand context from client_ficha for LLM prompt.
        
        Args:
            client_ficha: Client brand information dict
            
        Returns:
            Formatted context string for personality analysis
        """
        nombre = client_ficha.get("client_name", "Unknown Brand")
        arquetipo = client_ficha.get("brand_archetype", "Unknown")
        tono = client_ficha.get("tone_of_voice", "Neutral")
        
        context = f"""
Brand: {nombre}
Archetype: {arquetipo}
Tone of Voice: {tono}
"""
        return context.strip()

    async def analyze(self) -> Dict[str, Any]:
        """
        Execute brand personality analysis on all posts.
        
        Returns:
            Dictionary with metadata, per-post analysis, global summary, and errors
        """
        errors = []
        analisis_por_publicacion = []
        
        try:
            logger.info("Starting Q2 Brand Personality Analysis")
            
            ingested_data = self.load_ingested_data()
            client_ficha = ingested_data.get("client_ficha", {})
            posts = ingested_data.get("posts", [])
            comments = ingested_data.get("comments", [])
            
            logger.info(f"Processing {len(posts)} posts with {len(comments)} comments")
            
            if not comments:
                errors.append("No comments found for analysis")
                return {
                    "metadata": {
                        "module": "Q2 Personalidad",
                        "version": 2,
                        "description": "Brand personality analysis using Aaker Framework"
                    },
                    "results": {
                        "analisis_por_publicacion": [],
                        "analisis_agregado": {},
                        "resumen_global_personalidad": {}
                    },
                    "errors": errors
                }
            
            # Extract brand context for LLM
            brand_context = self._extract_brand_context(client_ficha)
            
            # Group comments by post
            comments_by_post = {}
            for comment in comments:
                post_url = comment.get("post_url")
                if post_url:
                    if post_url not in comments_by_post:
                        comments_by_post[post_url] = []
                    comments_by_post[post_url].append(comment.get("comment_text", ""))
            
            # Analyze personality traits for each post
            rasgos_globales = {
                "sinceridad": [],
                "emocion": [],
                "competencia": [],
                "sofisticacion": [],
                "rudeza": []
            }
            
            for idx, post in enumerate(posts, 1):
                post_url = post.get("post_url")
                
                if not post_url or post_url not in comments_by_post:
                    logger.warning(f"Skipping post {idx}: No comments found")
                    continue
                
                post_comments = comments_by_post[post_url]
                if not post_comments:
                    continue
                
                combined_text = " ".join(post_comments)
                
                logger.info(f"Analyzing post {idx}/{len(posts)}: {post_url}...")
                
                try:
                    # Call OpenAI with retry logic
                    analysis_result = await self._call_openai_for_personality(combined_text, brand_context)
                    
                    # Normalize personality values
                    rasgos_raw = {k: analysis_result.get(k, 0) 
                                 for k in ["sinceridad", "emocion", "competencia", "sofisticacion", "rudeza"]}
                    rasgos_normalizados = self._normalize_personality_values(rasgos_raw)
                    
                    # Collect global data
                    for dim in rasgos_normalizados:
                        rasgos_globales[dim].append(rasgos_normalizados[dim])
                    
                    # Build per-post analysis
                    post_analysis = {
                        "post_url": post_url,
                        "num_comentarios": len(post_comments),
                        "rasgos_distribuidos": rasgos_normalizados,
                        "rasgos_aaker": rasgos_normalizados.copy(),  # Legacy compatibility
                        "dimensiones_dominantes": analysis_result.get("dimensiones_dominantes", []),
                        "analisis_cualitativo": analysis_result.get("analisis_cualitativo", "")
                    }
                    
                    analisis_por_publicacion.append(post_analysis)
                    logger.info(f"Successfully analyzed post (dominant: {', '.join(post_analysis['dimensiones_dominantes'])})")
                    
                except Exception as e:
                    logger.error(f"Error analyzing post {post_url}: {str(e)}", exc_info=True)
                    errors.append(f"Failed to analyze post {post_url}: {str(e)}")
                    continue
            
            # Calculate global personality summary
            analisis_agregado = {}
            for dim in rasgos_globales:
                if rasgos_globales[dim]:
                    promedio = sum(rasgos_globales[dim]) / len(rasgos_globales[dim])
                    analisis_agregado[dim] = round(promedio, 2)
                else:
                    analisis_agregado[dim] = 0.0
            
            logger.info("Q2 analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Critical error in Q2 analysis: {str(e)}", exc_info=True)
            errors.append(f"Critical error: {str(e)}")
        
        return {
            "metadata": {
                "module": "Q2 Personalidad",
                "version": 2,
                "description": "Brand personality analysis using Aaker Framework (Máximo Rendimiento)"
            },
            "results": {
                "analisis_por_publicacion": analisis_por_publicacion,
                "analisis_agregado": analisis_agregado,
                "resumen_global_personalidad": analisis_agregado  # Legacy compatibility
            },
            "errors": errors
        }
