"""
Pixely Partners - Q1: Emotional Analysis (Plutchik Model)

Analyzes the emotional profile of client audience through comments on posts.
Uses Plutchik's dimensional model of emotions (8 primary emotions).

Single-client analysis: focuses only on client post comments.
"""

from typing import Dict, Any
import json
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

# Configure logger to use the shared orchestrator configuration
logger = logging.getLogger(__name__)


class Q1Emociones(BaseAnalyzer):
    """
    Q1 Emotional Analysis using Plutchik's model.
    
    Analyzes comments on each client post and derives emotional profiles.
    Returns per-post emotional analysis and global emotional summary.
    
    Features:
    - Resilient API calls with automatic retry (3 attempts, 15s wait)
    - Extended context window (15k chars) for better analysis
    - Strict type conversion for emotion values (float 0.0-1.0)
    - Per-post intensity averaging for quality assurance
    """

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
    async def _call_openai_for_emotions(self, combined_text: str) -> Dict[str, Any]:
        """
        Resilient wrapper for OpenAI API call to analyze emotions.
        
        Retries automatically on failure (max 3 attempts with 15s wait between attempts).
        
        Args:
            combined_text: Aggregated comment text to analyze
            
        Returns:
            Analysis result dict with emociones, resumen_emocional, sentimiento_dominante
            
        Raises:
            Exception: If all 3 retry attempts fail
        """
        prompt = f"""Analyze the following text from audience comments on a social media post.
Identify and score the 8 primary emotions from Plutchik's model on a 0-1 scale:
alegria (joy), confianza (trust), sorpresa (surprise), anticipacion (anticipation),
miedo (fear), disgusto (disgust), ira (anger), tristeza (sadness).

Also provide an emotional summary and dominant sentiment.

Text: "{combined_text[:15000]}"

Return ONLY valid JSON (no markdown, no code blocks):
{{
    "emociones": {{
        "alegria": <float 0.0-1.0>,
        "confianza": <float 0.0-1.0>,
        "sorpresa": <float 0.0-1.0>,
        "anticipacion": <float 0.0-1.0>,
        "miedo": <float 0.0-1.0>,
        "disgusto": <float 0.0-1.0>,
        "ira": <float 0.0-1.0>,
        "tristeza": <float 0.0-1.0>
    }},
    "resumen_emocional": "<string>",
    "sentimiento_dominante": "<string>"
}}"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in emotional analysis using Plutchik's model. Return valid JSON only."
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
            logger.error(f"Error calling OpenAI API for emotions analysis: {str(e)}", exc_info=True)
            raise

    def _clean_emotion_values(self, emociones: Dict[str, Any]) -> Dict[str, float]:
        """
        Clean and sanitize emotion values to ensure float type in range [0.0, 1.0].
        
        Converts string numbers to float, handles None/null values, and ensures type safety.
        This prevents frontend crashes from unexpected data types.
        
        Args:
            emociones: Raw emotion dictionary from LLM
            
        Returns:
            Cleaned emotion dictionary with all values as float in [0.0, 1.0]
        """
        cleaned = {}
        
        for emotion_name, value in emociones.items():
            valor_limpio = 0.0
            
            if value is not None and value != "null":
                try:
                    valor_limpio = float(value)
                    # Clamp to [0.0, 1.0] range
                    valor_limpio = max(0.0, min(1.0, valor_limpio))
                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Invalid emotion value for '{emotion_name}': {value} ({type(value).__name__}). "
                        f"Using default 0.0. Error: {str(e)}"
                    )
                    valor_limpio = 0.0
            
            cleaned[emotion_name] = valor_limpio
        
        return cleaned

    def _calculate_intensity_average(self, emociones: Dict[str, float]) -> float:
        """
        Calculate the average intensity across all emotions.
        
        Args:
            emociones: Cleaned emotion dictionary with float values
            
        Returns:
            Average intensity score (0.0-1.0)
        """
        if not emociones or len(emociones) == 0:
            logger.warning("Empty emotions dictionary provided for intensity calculation")
            return 0.0
        
        total = sum(emociones.values())
        average = total / len(emociones)
        
        return round(average, 3)

    async def analyze(self) -> Dict[str, Any]:
        """
        Execute Q1 emotional analysis with maximum resilience and data quality.
        
        Returns:
            {
                "metadata": {...},
                "results": {
                    "analisis_por_publicacion": [
                        {
                            "post_url": "...",
                            "num_comentarios": int,
                            "emociones": {...},
                            "intensidad_promedio": float,
                            "resumen_emocional": "...",
                            "sentimiento_dominante": "..."
                        },
                        ...
                    ],
                    "resumen_global_emociones": {...}
                },
                "errors": [...]
            }
        """
        errors = []
        results = {
            "analisis_por_publicacion": [],
            "resumen_global_emociones": {},
        }

        try:
            logger.info("Starting Q1 Emotional Analysis")
            
            ingested_data = self.load_ingested_data()
            posts = ingested_data.get("posts", [])
            comments = ingested_data.get("comments", [])

            if not comments:
                error_msg = "No comments found for analysis"
                logger.warning(error_msg)
                errors.append(error_msg)
                
                return {
                    "metadata": {
                        "module": "Q1 Emociones",
                        "version": 2,
                        "description": "Emotional analysis of audience using Plutchik model (Máximo Rendimiento)",
                    },
                    "results": results,
                    "errors": errors,
                }

            # Group comments by post_url
            comments_by_post = {}
            for comment in comments:
                post_url = comment.get("post_url")
                if post_url:
                    if post_url not in comments_by_post:
                        comments_by_post[post_url] = []
                    comments_by_post[post_url].append(comment.get("comment_text", ""))

            logger.info(f"Processing {len(posts)} posts with {len(comments)} comments")

            # Analyze each post
            all_emotions = {}
            post_count = 0
            
            for post in posts:
                post_url = post.get("post_url")
                if not post_url or post_url not in comments_by_post:
                    continue

                post_comments = comments_by_post[post_url]
                if not post_comments:
                    continue

                try:
                    # Concatenate comments text
                    combined_text = " ".join(post_comments)

                    logger.info(f"Analyzing post {post_count + 1}/{len(posts)}: {post_url[:50]}...")

                    # Call OpenAI with resilience (3 retries, 15s wait)
                    analysis_result = await self._call_openai_for_emotions(combined_text)

                    # SANITIZATION: Clean emotion values to ensure float type in [0.0, 1.0]
                    emociones_raw = analysis_result.get("emociones", {})
                    emociones_cleaned = self._clean_emotion_values(emociones_raw)

                    # CALCULATE: Per-post intensity average
                    intensidad_promedio = self._calculate_intensity_average(emociones_cleaned)

                    # Build result for this post
                    post_analysis = {
                        "post_url": post_url,
                        "num_comentarios": len(post_comments),
                        "emociones": emociones_cleaned,
                        "intensidad_promedio": intensidad_promedio,
                        "resumen_emocional": analysis_result.get("resumen_emocional", ""),
                        "sentimiento_dominante": analysis_result.get("sentimiento_dominante", ""),
                    }

                    results["analisis_por_publicacion"].append(post_analysis)

                    # Accumulate for global summary
                    for emotion, score in emociones_cleaned.items():
                        if emotion not in all_emotions:
                            all_emotions[emotion] = []
                        all_emotions[emotion].append(score)

                    post_count += 1
                    logger.info(f"Successfully analyzed post (intensity: {intensidad_promedio})")

                except Exception as e:
                    error_msg = f"Error analyzing post {post_url}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
                    continue

            # Calculate global emotional summary
            if all_emotions:
                for emotion, scores in all_emotions.items():
                    results["resumen_global_emociones"][emotion] = round(sum(scores) / len(scores), 3)
                
                logger.info(f"Q1 Analysis complete: {post_count} posts analyzed, global emotions calculated")
            else:
                logger.warning("No emotions data available for global summary")

        except Exception as e:
            fatal_error = f"Fatal error in Q1 analysis: {str(e)}"
            logger.error(fatal_error, exc_info=True)
            errors.append(fatal_error)

        return {
            "metadata": {
                "module": "Q1 Emociones",
                "version": 2,
                "description": "Emotional analysis of audience using Plutchik model (Máximo Rendimiento)",
            },
            "results": results,
            "errors": errors,
        }

