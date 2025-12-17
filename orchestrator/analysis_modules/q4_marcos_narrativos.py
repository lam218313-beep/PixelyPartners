"""
Pixely Partners - Q4: Narrative Frameworks Analysis (Máximo Rendimiento)

Analyzes audience comments to identify dominant narrative frames using Entman Framing Theory.
Classifies narratives into 3 dimensions: Positivo, Negativo, Aspiracional.

Features:
- Dynamic model parameter compatibility (max_tokens vs max_completion_tokens)
- Resilient API calls with automatic retry (3 attempts, 2s wait)
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
from datetime import datetime, timedelta

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
    - Dynamic model parameter compatibility for GPT-5, o1, and legacy models
    - Resilient API calls with automatic retry (3 attempts with 2s wait between attempts)
    - Extended context window (15k chars) for better framing detection
    - Strict sanitization for frame scores (0-100) normalized to 1.0
    - Per-post granular analysis with forensic quote extraction
    - Weighted aggregation: post volume drives global priority
    - Frame dominance detection per post
    """

    def _get_model_params(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generates API parameters compatible with GPT-5-mini and other models.
        
        GPT-5-mini requires minimal parameter specification for best results.
        
        Args:
            messages: List of message dicts for the API call
            
        Returns:
            Dict with all parameters for chat.completions.create()
        """
        model_name = self.model_name
        
        params = {
            "model": model_name,
            "messages": messages,
        }

        # For gpt-5 and o1 models, use minimal parameters
        if isinstance(model_name, str) and any(x in model_name for x in ["gpt-5", "o1"]):
            # Don't add temperature or token limits for gpt-5-mini
            pass
        else:
            # Legacy models support temperature and max_tokens
            params["temperature"] = 0.7
            params["max_tokens"] = 1500
            
        return params

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _analyze_post_framing(self, post_url: str, comments_text: str) -> Dict[str, Any]:
        """
        Analyzes narrative frames for a single post with automatic retry logic.
        
        Retries automatically on failure (max 3 attempts with 2s wait between attempts).
        
        Args:
            post_url: URL identifier of the post
            comments_text: Aggregated comment text to analyze
            
        Returns:
            Analysis result dict with frame scores and quotes
            
        Raises:
            Exception: If all 3 retry attempts fail
        """
        
        prompt = f"""You are an expert media analyst specializing in Entman Framing Theory.

Analyze the following audience comments to identify the dominant narrative frames.

AUDIENCE COMMENTS:
"{comments_text[:15000]}"

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
    "distribucion_marcos": {{
        "Positivo": 75,
        "Negativo": 20,
        "Aspiracional": 50
    }},
    "ejemplos_narrativos": {{
        "Positivo": "Este producto cambio mi vida...",
        "Negativo": "El precio es demasiado alto...",
        "Aspiracional": null
    }}
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
                content = response.output_text.strip()
            else:
                # Chat Completions for other models
                logger.debug(f"Using Chat Completions API for model: {self.model_name}")
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert media analyst. Analyze narrative frames and return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                params = self._get_model_params(messages)
                response = await self.openai_client.chat.completions.create(**params)
                content = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_part = content.split("```json")[1].split("```")[0].strip()
                    data = json.loads(json_part)
                elif "```" in content:
                    json_part = content.split("```")[1].split("```")[0].strip()
                    data = json.loads(json_part)
                else:
                    raise json.JSONDecodeError("Could not extract JSON from response", content, 0)
            
            return data
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API for frames analysis of {post_url}: {str(e)}", exc_info=True)
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
        cleaned = {}
        for marco in marcos_keys:
            score = marcos_scores.get(marco, 0)
            try:
                val = float(score)
            except (ValueError, TypeError):
                logger.warning(f"Invalid score for '{marco}': {score}. Using 0.0")
                val = 0.0
            # Clamp to [0, 100]
            val = max(0.0, min(100.0, val))
            cleaned[marco] = val

        total = sum(cleaned.values())

        marcos_normalizados = {}
        marco_dominante = None

        if total == 0:
            # If no information, distribute equally and set no dominant frame
            equal = round(1.0 / len(marcos_keys), 3)
            for marco in marcos_keys:
                marcos_normalizados[marco] = equal
            marco_dominante = None
            return marcos_normalizados, marco_dominante

        # Normalize so values sum to 1.0 (with 3 decimal places)
        for marco, val in cleaned.items():
            marcos_normalizados[marco] = round(val / total, 3)

        # Determine dominant frame (highest normalized value). If tie, pick None.
        sorted_items = sorted(marcos_normalizados.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_items) >= 2 and abs(sorted_items[0][1] - sorted_items[1][1]) < 1e-6:
            marco_dominante = None
        else:
            marco_dominante = sorted_items[0][0]

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
        temporal_frame_scores = {}  # week -> marco -> (total_weighted_score, total_weight)
        
        try:
            logger.info("Starting Q4 Narrative Frames Analysis")
            
            posts = self.get_posts_data()
            comments = self.get_comments_data()
            
            logger.info(f"Processing {len(posts)} posts with {len(comments)} comments")
            
            # Debug: Check if posts have posted_at field
            for idx, post in enumerate(posts[:2]):
                post_date = post.get("created_at") or post.get("posted_at") or post.get("post_date") or post.get("fecha") or post.get("timestamp")
                logger.info(f"Post {idx}: {post.get('link', 'NO_LINK')} - created_at: {post_date}")
                logger.debug(f"Post {idx} available fields: {list(post.keys())}")
            
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
            posts_by_date = {}  # For temporal evolution
            
            for comment in comments:
                link = comment.get("link")
                if link:
                    if link not in comments_by_post:
                        comments_by_post[link] = []
                    comments_by_post[link].append(comment.get("comment_text", ""))
            
            # Group posts by date for temporal analysis
            for post in posts:
                link = post.get("link")
                post_date = post.get("created_at") or post.get("posted_at") or post.get("post_date") or post.get("fecha") or post.get("timestamp")
                if link:
                    if post_date:
                        try:
                            # Parse date (format: YYYY-MM-DD or similar)
                            if isinstance(post_date, str):
                                post_dt = datetime.fromisoformat(post_date[:10])
                            else:
                                post_dt = post_date
                            # Get week number for temporal bucketing
                            week_num = post_dt.isocalendar()[1]
                            if week_num not in posts_by_date:
                                posts_by_date[week_num] = []
                            posts_by_date[week_num].append(link)
                        except Exception as e:
                            logger.warning(f"Could not parse date {post_date}: {e}")
                            # Default to week 1 if parsing fails
                            if 1 not in posts_by_date:
                                posts_by_date[1] = []
                            posts_by_date[1].append(link)
                    else:
                        # Default to week 1 if no date
                        if 1 not in posts_by_date:
                            posts_by_date[1] = []
                        posts_by_date[1].append(link)
            
            # Analyze frames for each post
            for idx, post in enumerate(posts, 1):
                link = post.get("link")
                
                if not link or link not in comments_by_post:
                    logger.warning(f"Skipping post {idx}: No comments found")
                    continue
                
                post_comments = comments_by_post[link]
                if not post_comments:
                    continue
                
                combined_text = " ".join(post_comments)
                num_comments = len(post_comments)
                
                logger.info(f"Analyzing post {idx}/{len(posts)}: {link} ({num_comments} comments)...")
                
                try:
                    # Call OpenAI with retry logic
                    analysis_result = await self._analyze_post_framing(link, combined_text)
                    
                    # Extract raw data from response
                    raw_scores = analysis_result.get("distribucion_marcos", {})
                    raw_quotes = analysis_result.get("ejemplos_narrativos", {})
                    
                    # Normalize frame scores to probabilities
                    marcos_normalizados, marco_dominante = self._normalize_frame_scores(raw_scores)
                    
                    # Sanitize quotes
                    ejemplos_sanitizados = self._sanitize_quotes(raw_quotes)
                    
                    # Determine which week this post belongs to for temporal analysis
                    post_week = 1  # default
                    for week_num, post_urls in posts_by_date.items():
                        if link in post_urls:
                            post_week = week_num
                            break
                    
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
                        
                        # Also accumulate for temporal analysis
                        if post_week not in temporal_frame_scores:
                            temporal_frame_scores[post_week] = {}
                        if marco not in temporal_frame_scores[post_week]:
                            temporal_frame_scores[post_week][marco] = (0.0, 0.0)
                        old_score, old_weight = temporal_frame_scores[post_week][marco]
                        temporal_frame_scores[post_week][marco] = (
                            old_score + weighted_score,
                            old_weight + num_comments
                        )
                    
                    # Build per-post analysis
                    post_analysis = {
                        "link": link,
                        "num_comentarios": num_comments,
                        "marco_dominante": marco_dominante,
                        "distribucion_marcos": marcos_normalizados,
                        "marcos_narrativos": marcos_normalizados.copy(),  # Legacy compatibility
                        "ejemplos_narrativos": ejemplos_sanitizados,
                    }
                    
                    analisis_por_publicacion.append(post_analysis)
                    logger.info(f"Successfully analyzed post (dominant: {marco_dominante})")
                    
                except Exception as e:
                    logger.error(f"Error analyzing post {link}: {str(e)}", exc_info=True)
                    errors.append(f"Error analyzing post {link}: {str(e)}")
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
            
            # Calculate temporal evolution
            evolucion_temporal = []
            marcos_keys = ["Positivo", "Negativo", "Aspiracional"]
            
            for week_num in sorted(temporal_frame_scores.keys()):
                week_data = temporal_frame_scores[week_num]
                marcos_distribucion = {}
                
                for marco in marcos_keys:
                    if marco in week_data:
                        weighted_sum, total_weight = week_data[marco]
                        if total_weight > 0:
                            marcos_distribucion[marco] = round(weighted_sum / total_weight, 3)
                        else:
                            marcos_distribucion[marco] = 0.0
                    else:
                        marcos_distribucion[marco] = 0.0
                
                # Normalize to sum to 1.0
                suma = sum(marcos_distribucion.values())
                if abs(suma - 1.0) > 0.001 and suma > 0:
                    for marco in marcos_keys:
                        marcos_distribucion[marco] = round(marcos_distribucion[marco] / suma, 3)
                
                evolucion_temporal.append({
                    "semana": week_num,
                    "marcos_distribucion": marcos_distribucion
                })
            
            logger.info(f"Q4 analysis completed. Aggregated: {analisis_agregado}")
            logger.info(f"Temporal evolution generated: {len(evolucion_temporal)} weeks")
            
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
                "resumen_marcos": resumen_marcos,
                "evolucion_temporal": evolucion_temporal
            },
            "errors": errors
        }
