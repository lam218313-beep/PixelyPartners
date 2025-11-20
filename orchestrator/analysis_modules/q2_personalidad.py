"""
Pixely Partners - Q2: Brand Personality Analysis (Aaker Framework) - Máximo Rendimiento

Analyzes audience comments to determine how the brand is perceived using Aaker's
Five Dimensions of Brand Personality: Sinceridad, Emoción, Competencia, Sofisticación, Rudeza.

Features:
- Resilient API calls with automatic retry (3 attempts, 15s wait)
- Per-post granular personality profiling with independent 0-100 scales
- Strict type sanitization (floats, clamped to [0, 100], always 5 traits)
- Dominant trait detection with top 1-2 ranking
"""

from typing import Dict, Any, List
import json
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class Q2Personalidad(BaseAnalyzer):
    """
    Q2 Brand Personality Analysis using Aaker Framework - MÁXIMO RENDIMIENTO.
    
    Analyzes comments on each client post to derive brand personality dimensions.
    Returns per-post personality profiles and global personality summary.
    
    SCALING: Independent 0-100 per trait (NOT normalized to sum=100)
    TYPES: Floats with capitalized keys (Sinceridad, Emocion, Competencia, Sofisticacion, Rudeza)
    TRAITS: Always 5 traits (zero-filled if missing from LLM)
    DOMINANT: Top 1-2 traits by score
    """
    
    # Define canonical trait names (capitalized for visual display)
    CANONICAL_TRAITS = ["Sinceridad", "Emocion", "Competencia", "Sofisticacion", "Rudeza"]
    
    # Map lowercase → canonical (for LLM flexibility)
    TRAIT_MAPPING = {
        "sinceridad": "Sinceridad",
        "emocion": "Emocion",
        "excitement": "Emocion",
        "competencia": "Competencia",
        "competence": "Competencia",
        "sofisticacion": "Sofisticacion",
        "sophistication": "Sofisticacion",
        "rudeza": "Rudeza",
        "ruggedness": "Rudeza",
    }

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

AUDIENCE COMMENTS (max 15k chars):
"{combined_text[:15000]}"

Rate each of the 5 brand personality dimensions on a INDEPENDENT scale of 0-100:
(A brand can score HIGH on multiple dimensions simultaneously - they are NOT mutually exclusive)

1. Sinceridad (Sincerity): Honest, genuine, down-to-earth, cheerful, wholesome
2. Emocion (Excitement): Daring, spirited, imaginative, fun, cool, young
3. Competencia (Competence): Reliable, intelligent, successful, leader, confident
4. Sofisticacion (Sophistication): Upper-class, charming, glamorous, good-taste, smooth
5. Rudeza (Ruggedness): Tough, strong, outdoorsy, rugged, masculine, adventurous

CRITICAL: Return ONLY valid JSON with raw scores (0-100 as numbers, not strings or percentages):
{{
    "sinceridad": <integer 0-100>,
    "emocion": <integer 0-100>,
    "competencia": <integer 0-100>,
    "sofisticacion": <integer 0-100>,
    "rudeza": <integer 0-100>,
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

    def _sanitize_trait_value(self, raw_value: Any, trait_name: str) -> float:
        """
        Sanitize a trait value from LLM: convert to float, clamp to [0, 100].
        
        Args:
            raw_value: Value from LLM (could be int, float, str, null)
            trait_name: Trait name (for logging)
            
        Returns:
            Sanitized float in range [0, 100]
        """
        try:
            # Convert to float
            if raw_value is None:
                valor_float = 0.0
            else:
                valor_float = float(str(raw_value).replace('%', '').replace('+', '').strip())
            
            # Clamp to [0, 100]
            valor_float = max(0.0, min(100.0, valor_float))
            
            return valor_float
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid trait value for '{trait_name}': {raw_value}. Using 0.0.")
            return 0.0

    def _build_canonical_traits_dict(self, rasgos_raw: Dict[str, Any]) -> Dict[str, float]:
        """
        Build canonical traits dictionary with capitalized keys.
        
        - Normalizes lowercase keys to canonical form
        - Sanitizes all values to float [0, 100]
        - Ensures ALL 5 traits are present (zero-filled if missing)
        
        Args:
            rasgos_raw: Raw traits dict from LLM
            
        Returns:
            Dict with canonical trait names as keys, floats [0, 100] as values
        """
        rasgos_sanitized = {}
        
        # First pass: sanitize and normalize provided traits
        for raw_key, raw_value in rasgos_raw.items():
            if raw_key in ["analisis_cualitativo", "dimensiones_dominantes"]:
                continue  # Skip non-trait keys
            
            # Normalize key to lowercase for lookup
            key_lower = str(raw_key).lower().strip()
            
            # Find canonical name
            canonical_key = self.TRAIT_MAPPING.get(key_lower)
            
            if canonical_key:
                # Sanitize value
                sanitized_value = self._sanitize_trait_value(raw_value, canonical_key)
                rasgos_sanitized[canonical_key] = sanitized_value
            else:
                logger.warning(f"Unknown trait key from LLM: {raw_key}. Skipping.")
        
        # Second pass: ensure all 5 traits are present
        rasgos_final = {}
        for canonical_trait in self.CANONICAL_TRAITS:
            rasgos_final[canonical_trait] = rasgos_sanitized.get(canonical_trait, 0.0)
        
        logger.debug(f"Final canonical traits: {rasgos_final}")
        return rasgos_final

    def _get_dominant_traits(self, rasgos: Dict[str, float], top_n: int = 2) -> List[str]:
        """
        Identify top dominant traits.
        
        Logic:
        - Sort by score descending
        - Return top 1-2 traits
        - If clear gap (>5%), return only top 1
        - If close race, return top 2
        
        Args:
            rasgos: Traits dict with scores
            top_n: Maximum traits to return (1 or 2)
            
        Returns:
            List of 1-2 dominant trait names
        """
        if not rasgos or all(v == 0 for v in rasgos.values()):
            return ["Neutral"]
        
        # Sort by score descending
        sorted_traits = sorted(rasgos.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_traits) == 0:
            return ["Neutral"]
        
        # Always include top trait
        dominantes = [sorted_traits[0][0]]
        
        # Check if we should include second trait
        if len(sorted_traits) > 1 and top_n >= 2:
            top_score = sorted_traits[0][1]
            second_score = sorted_traits[1][1]
            
            # If difference is < 5 points, include both
            if top_score > 0 and (top_score - second_score) < 5:
                dominantes.append(sorted_traits[1][0])
        
        return dominantes

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
        
        WORKFLOW:
        1. Load ingested data (posts, comments, client_ficha)
        2. For each post: aggregate comments, call LLM, sanitize traits
        3. Build canonical traits dict (always 5 traits, 0-100 independent)
        4. Calculate global averages
        5. Return per-post and global results
        
        Returns:
            Dictionary with metadata, per-post analysis, global summary, and errors
        """
        errors = []
        analisis_por_publicacion = []
        
        try:
            logger.info("Starting Q2 Brand Personality Analysis (MÁXIMO RENDIMIENTO)")
            print("   📊 Analizando personalidad de marca (Aaker)...")
            
            posts = self.get_posts_data()
            comments = self.get_comments_data()
            
            # Get client ficha from config
            client_ficha = self.config.get("client_ficha", {})
            
            logger.info(f"Processing {len(posts)} posts with {len(comments)} comments")
            print(f"   📍 {len(posts)} posts, {len(comments)} comentarios")
            
            if not comments:
                logger.warning("No comments found for Q2 analysis")
                errors.append("No comments found for analysis")
                return {
                    "metadata": {
                        "module": "Q2 Personalidad",
                        "version": 3,
                        "description": "Brand personality analysis using Aaker Framework (Máximo Rendimiento)"
                    },
                    "results": {
                        "analisis_por_publicacion": [],
                        "resumen_global_personalidad": {trait: 0.0 for trait in self.CANONICAL_TRAITS}
                    },
                    "errors": errors
                }
            
            # Extract brand context for LLM
            brand_context = self._extract_brand_context(client_ficha)
            logger.debug(f"Brand context: {brand_context}")
            
            # Group comments by post
            comments_by_post = {}
            for comment in comments:
                link = comment.get("link")
                if link:
                    if link not in comments_by_post:
                        comments_by_post[link] = []
                    comments_by_post[link].append(comment.get("comment_text", ""))
            
            logger.info(f"Comments grouped into {len(comments_by_post)} posts")
            
            # Analyze personality traits for each post
            rasgos_globales = {trait: [] for trait in self.CANONICAL_TRAITS}
            
            for idx, post in enumerate(posts, 1):
                link = post.get("link")
                
                if not link or link not in comments_by_post:
                    logger.warning(f"Skipping post {idx}: No comments found")
                    continue
                
                post_comments = comments_by_post[link]
                if not post_comments:
                    continue
                
                combined_text = " ".join(post_comments)
                num_comentarios = len(post_comments)
                
                logger.info(f"Analyzing post {idx}/{len(posts)}: {num_comentarios} comments")
                print(f"   • Post {idx}/{len(posts)}: {num_comentarios} comments")
                
                try:
                    # Call OpenAI with retry logic
                    analysis_result = await self._call_openai_for_personality(combined_text, brand_context)
                    
                    # Build canonical traits dictionary
                    rasgos_canonicos = self._build_canonical_traits_dict(analysis_result)
                    
                    # Get dominant traits
                    dominantes = self._get_dominant_traits(rasgos_canonicos)
                    
                    # Collect global data
                    for trait, score in rasgos_canonicos.items():
                        rasgos_globales[trait].append(score)
                    
                    # Build per-post analysis
                    post_analysis = {
                        "link": link,
                        "num_comentarios": num_comentarios,
                        "rasgos_aaker": rasgos_canonicos,
                        "rasgos_distribuidos": rasgos_canonicos.copy(),  # Alias for future architecture
                        "dimensiones_dominantes": dominantes,
                        "analisis_cualitativo": analysis_result.get("analisis_cualitativo", ""),
                        "personalidad_dominante": dominantes[0] if dominantes else "Neutral"
                    }
                    
                    analisis_por_publicacion.append(post_analysis)
                    logger.info(f"✓ Post analyzed successfully (dominant: {', '.join(dominantes)})")
                    print(f"     ✓ Dominante(s): {', '.join(dominantes)}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing post {link}: {str(e)}", exc_info=True)
                    errors.append(f"Failed to analyze post {link}: {str(e)}")
                    print(f"     ✗ Error: {str(e)}")
                    continue
            
            # Calculate global personality summary
            resumen_global = {}
            for trait in self.CANONICAL_TRAITS:
                if rasgos_globales[trait]:
                    promedio = sum(rasgos_globales[trait]) / len(rasgos_globales[trait])
                    resumen_global[trait] = round(promedio, 1)
                else:
                    resumen_global[trait] = 0.0
            
            logger.info(f"Q2 analysis completed: {len(analisis_por_publicacion)} posts analyzed")
            print(f"   ✅ {len(analisis_por_publicacion)} posts analizados")
            
        except Exception as e:
            logger.error(f"Critical error in Q2 analysis: {str(e)}", exc_info=True)
            errors.append(f"Critical error: {str(e)}")
            print(f"   ❌ Error crítico: {str(e)}")
        
        return {
            "metadata": {
                "module": "Q2 Personalidad",
                "version": 3,
                "description": "Brand personality analysis using Aaker Framework (Máximo Rendimiento)",
                "traits_scale": "0-100 independent (NOT normalized to sum=100)"
            },
            "results": {
                "analisis_por_publicacion": analisis_por_publicacion,
                "resumen_global_personalidad": resumen_global,
                "analisis_agregado": resumen_global  # Alias for consistency
            },
            "errors": errors
        }
