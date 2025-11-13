"""
Pixely Partners - Q4: Narrative Frameworks Analysis (Máximo Rendimiento)

Analyzes audience comments to identify dominant narrative frames using Entman Framing Theory.
Classifies narratives into 3 dimensions: Positivo, Negativo, Aspiracional.

Features:
- Resilient API calls with automatic retry (3 attempts, 15s wait)
- Extended context window (15k chars) for nuanced framing analysis
- Strict type conversion for frame scores (0-100, normalized to 1.0)
- Per-post granular analysis with forensic quote extraction
- Weighted aggregation: posts with more comments have proportional influence
- Frame dominance detection per post
"""

from typing import Dict, Any, List
import json
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

# Configure logger to use the shared orchestrator configuration
logger = logging.getLogger(__name__)


class Q4MarcosNarrativos(BaseAnalyzer):
    """
    Q4 Narrative Frameworks Analysis using Entman Framing Theory.
    
    Analyzes comments to classify narratives into 3 dimensions:
    - Positivo (Satisfaction, praise, positive sentiment)
    - Negativo (Complaints, problems, negative sentiment)
    - Aspiracional (Desires, suggestions, future vision)
    
    Features:
    - Resilient API calls with automatic retry (3 attempts, 15s wait)
    - Extended context window (15k chars) for better framing detection
    - Strict sanitization for frame scores (0-100) normalized to 1.0
    - Per-post granular analysis with forensic quote extraction
    - Weighted aggregation: post volume drives global priority
    - Frame dominance detection per post
    """

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
    async def _call_openai_for_frames(self, combined_text: str) -> Dict[str, Any]:
        """
        Resilient wrapper for OpenAI API call to analyze narrative frames.
        
        Retries automatically on failure (max 3 attempts with 15s wait between attempts).
        
        Args:
            combined_text: Aggregated comment text to analyze
            
        Returns:
            Analysis result dict with frame scores and quotes
            
        Raises:
            Exception: If all 3 retry attempts fail
        """
        prompt = f"""You are an expert media analyst specializing in Entman Framing Theory.

Analyze the following audience comments to identify the dominant narrative frames.

AUDIENCE COMMENTS:
"{combined_text[:15000]}"

Classify the narrative into exactly 3 dimensions:
1. Positivo (Satisfaction, praise, positive sentiment, confidence, trust)
2. Negativo (Complaints, problems, criticism, dissatisfaction)
3. Aspiracional (Desires, suggestions, future vision, innovation requests)

For each dimension:
- Assign a relevance score (0-100) indicating how much that frame is present in the comments.
- Extract a direct quote (exact text from the comments) that BEST represents that frame.
- If a frame is not present or has no clear quote, the quote must be null.

Return ONLY valid JSON:
{{
    "marcos_scores": {{
        "Positivo": 75,
        "Negativo": 20,
        "Aspiracional": 50
    }},
    "ejemplos_quotes": {{
        "Positivo": "Este producto cambio mi vida...",
        "Negativo": "El precio es demasiado alto...",
        "Aspiracional": null
    }},
    "analisis_breve": "<One sentence overall framing assessment>"
}}"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert media analyst. Analyze narrative frames and return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

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
            logger.error(f"Error calling OpenAI API for frames analysis: {str(e)}", exc_info=True)
            raise

    def _normalize_frame_scores(self, marcos_scores: Dict[str, int]) -> tuple:
        """
        Normalize raw frame scores (0-100) to probabilities that sum to 1.0.
        Also determine dominant frame.
        
        Args:
            marcos_scores: Raw scores dict (0-100)
            
        Returns:
            Tuple of (normalized_dict, dominant_frame_name)
        """
        marcos_keys = ["Positivo", "Negativo", "Aspiracional"]
        
        # Extract and validate scores
        valores_limpios = {}
        for marco in marcos_keys:
            score = marcos_scores.get(marco, 0)
            try:
                val = float(score)
                val = max(0.0, min(100.0, val))  # Clamp to [0, 100]
                valores_limpios[marco] = val
            except (ValueError, TypeError):
                logger.warning(f"Invalid score for '{marco}': {score}. Using 0.0")
                valores_limpios[marco] = 0.0
        
        # Calculate sum
        suma_total = sum(valores_limpios.values())
        
        # Normalize to probabilities (sum = 1.0)
        if suma_total == 0:
            # Equal distribution if all zeros
            marcos_normalizados = {marco: 0.333 for marco in marcos_keys}
            marco_dominante = None
        else:
            marcos_normalizados = {marco: round(valores_limpios[marco] / suma_total, 3) 
                                   for marco in marcos_keys}
            # Determine dominant frame
            marco_dominante = max(marcos_keys, key=lambda m: marcos_normalizados[m])
        
        # Ensure sum is exactly 1.0 (fix rounding errors)
        suma_calculada = sum(marcos_normalizados.values())
        if abs(suma_calculada - 1.0) > 0.001:
            diferencia = 1.0 - suma_calculada
            if marco_dominante:
                marcos_normalizados[marco_dominante] = round(
                    marcos_normalizados[marco_dominante] + diferencia, 3
                )
        
        return marcos_normalizados, marco_dominante

    def _sanitize_quotes(self, ejemplos_quotes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize and validate quotes (should be strings or null).
        
        Args:
            ejemplos_quotes: Raw quotes dict from LLM
            
        Returns:
            Cleaned quotes dict
        """
        marcos_keys = ["Positivo", "Negativo", "Aspiracional"]
        clean_quotes = {}
        
        for marco in marcos_keys:
            quote = ejemplos_quotes.get(marco)
            if quote is None or quote == "":
                clean_quotes[marco] = None
            elif isinstance(quote, str):
                # Ensure quote is reasonable length (max 500 chars)
                clean_quotes[marco] = quote[:500] if len(quote) > 500 else quote
            else:
                logger.warning(f"Invalid quote type for '{marco}': {type(quote)}. Using null")
                clean_quotes[marco] = None
        
        return clean_quotes

    async def analyze(self) -> Dict[str, Any]:
        """
        Execute narrative frames analysis on all posts with weighted aggregation.
        
        Returns:
            Dictionary with metadata, per-post analysis, global summary, and errors
        """
        errors = []
        analisis_por_publicacion = []
        
        # For weighted aggregation
        weighted_frame_scores = {}  # marco -> (total_weighted_score, total_weight)
        
        try:
            logger.info("Starting Q4 Narrative Frames Analysis")
            
            ingested_data = self.load_ingested_data()
            posts = ingested_data.get("posts", [])
            comments = ingested_data.get("comments", [])
            
            logger.info(f"Processing {len(posts)} posts with {len(comments)} comments")
            
            if not comments:
                errors.append("No comments found for analysis")
                return {
                    "metadata": {
                        "module": "Q4 Marcos Narrativos",
                        "version": 2,
                        "description": "Narrative frames analysis with weighted aggregation (Máximo Rendimiento)"
                    },
                    "results": {
                        "analisis_por_publicacion": [],
                        "analisis_agregado": {},
                        "resumen_marcos": {}
                    },
                    "errors": errors
                }
            
            # Group comments by post
            comments_by_post = {}
            for comment in comments:
                post_url = comment.get("post_url")
                if post_url:
                    if post_url not in comments_by_post:
                        comments_by_post[post_url] = []
                    comments_by_post[post_url].append(comment.get("comment_text", ""))
            
            # Analyze frames for each post
            for idx, post in enumerate(posts, 1):
                post_url = post.get("post_url")
                
                if not post_url or post_url not in comments_by_post:
                    logger.warning(f"Skipping post {idx}: No comments found")
                    continue
                
                post_comments = comments_by_post[post_url]
                if not post_comments:
                    continue
                
                combined_text = " ".join(post_comments)
                num_comments = len(post_comments)
                
                logger.info(f"Analyzing post {idx}/{len(posts)}: {post_url} ({num_comments} comments)...")
                
                try:
                    # Call OpenAI with retry logic
                    analysis_result = await self._call_openai_for_frames(combined_text)
                    
                    # Extract raw data from response
                    raw_scores = analysis_result.get("marcos_scores", {})
                    raw_quotes = analysis_result.get("ejemplos_quotes", {})
                    
                    # Normalize frame scores to probabilities
                    marcos_normalizados, marco_dominante = self._normalize_frame_scores(raw_scores)
                    
                    # Sanitize quotes
                    ejemplos_sanitizados = self._sanitize_quotes(raw_quotes)
                    
                    # Accumulate weighted scores for global aggregation
                    for marco, score in marcos_normalizados.items():
                        weighted_score = score * num_comments  # Weighted by comment count
                        if marco not in weighted_frame_scores:
                            weighted_frame_scores[marco] = (0.0, 0.0)
                        old_score, old_weight = weighted_frame_scores[marco]
                        weighted_frame_scores[marco] = (
                            old_score + weighted_score,
                            old_weight + num_comments
                        )
                    
                    # Build per-post analysis
                    post_analysis = {
                        "post_url": post_url,
                        "num_comentarios": num_comments,
                        "marco_dominante": marco_dominante,
                        "distribucion_marcos": marcos_normalizados,
                        "marcos_narrativos": marcos_normalizados.copy(),  # Legacy compatibility
                        "ejemplos_narrativos": ejemplos_sanitizados,
                        "analisis_breve": analysis_result.get("analisis_breve", "")
                    }
                    
                    analisis_por_publicacion.append(post_analysis)
                    logger.info(f"Successfully analyzed post (dominant: {marco_dominante})")
                    
                except Exception as e:
                    logger.error(f"Error analyzing post {post_url}: {str(e)}", exc_info=True)
                    errors.append(f"Failed to analyze post {post_url}: {str(e)}")
                    # Continue with next post (omit this one from aggregation)
                    continue
            
            # Calculate global analysis from weighted scores
            analisis_agregado = {}
            if weighted_frame_scores:
                # Calculate weighted averages
                marcos_keys = ["Positivo", "Negativo", "Aspiracional"]
                for marco in marcos_keys:
                    if marco in weighted_frame_scores:
                        weighted_sum, total_weight = weighted_frame_scores[marco]
                        if total_weight > 0:
                            analisis_agregado[marco] = round(weighted_sum / total_weight, 3)
                        else:
                            analisis_agregado[marco] = 0.0
                    else:
                        analisis_agregado[marco] = 0.0
                
                # Ensure sum is 1.0
                suma = sum(analisis_agregado.values())
                if abs(suma - 1.0) > 0.001:
                    # Normalize if needed
                    if suma > 0:
                        for marco in marcos_keys:
                            analisis_agregado[marco] = round(analisis_agregado[marco] / suma, 3)
            
            # Create summary (legacy compatibility)
            resumen_marcos = analisis_agregado.copy()
            
            logger.info(f"Q4 analysis completed. Aggregated: {analisis_agregado}")
            
        except Exception as e:
            logger.error(f"Critical error in Q4 analysis: {str(e)}", exc_info=True)
            errors.append(f"Critical error: {str(e)}")
        
        return {
            "metadata": {
                "module": "Q4 Marcos Narrativos",
                "version": 2,
                "description": "Narrative frames analysis with weighted aggregation (Máximo Rendimiento)"
            },
            "results": {
                "analisis_por_publicacion": analisis_por_publicacion,
                "analisis_agregado": analisis_agregado,
                "resumen_marcos": resumen_marcos
            },
            "errors": errors
        }
