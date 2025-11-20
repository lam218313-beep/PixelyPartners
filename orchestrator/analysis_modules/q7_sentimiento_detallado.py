"""
Pixely Partners - Q7: Detailed Sentiment Analysis (Máximo Rendimiento)

Analyzes audience comments to classify sentiment at GRANULAR level (post-by-post).
Uses normalized sentiment scoring (Positivo, Negativo, Neutral) that sums to 1.0.

Features:
- Post-granular analysis (NOT global-only): Fills analisis_por_publicacion list
- Normalized sentiment scores (0-1, sum=1.0) for Plotly pie charts
- Strict float typing (converts AI responses to float before normalization)
- Weighted global aggregation (by num_comentarios per post)
- Resilient API calls with tenacity (@retry, 3 attempts, 2s wait)
- Comprehensive logging and per-post error isolation
"""

from typing import Dict, Any, List
import json
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

# Configure logger to use the shared orchestrator configuration
logger = logging.getLogger(__name__)


class Q7SentimientoDetallado(BaseAnalyzer):
    """
    Q7 Detailed Sentiment Analysis using post-granular decomposition.
    
    Analyzes comments at POST level (not global-combined) to classify sentiment
    into 3 dimensions:
    - Positivo (Satisfaction, praise, positive sentiment)
    - Negativo (Complaints, criticism, negative sentiment)
    - Neutral (Factual, informational, neutral sentiment)
    
    Features:
    - Post-granular analysis: Iterates post-by-post with isolated error handling
    - Normalized sentiment scores: Raw scores (0-100) normalized to (0-1) summing to 1.0
    - Strict type enforcement: Forced float conversion before normalization
    - Weighted global aggregation: Final sentimiento_general is weighted average
    - Resilient API calls: Automatic retry (3 attempts, 2s wait between)
    - Comprehensive logging: Per-post analysis tracked with logger
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
            params["max_tokens"] = 1000
            
        return params

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _analyze_post_sentiment(self, post_url: str, comments_text: str) -> Dict[str, Any]:
        """
        Analyzes sentiment for a single post with automatic retry logic.
        
        Retries automatically on failure (max 3 attempts with 2s wait between attempts).
        
        Args:
            post_url: URL identifier of the post
            comments_text: Aggregated comment text to analyze
            
        Returns:
            Analysis result dict with sentiment scores
            
        Raises:
            Exception: If all 3 retry attempts fail
        """
        
        prompt = f"""You are an expert sentiment analyst. Analyze the following audience comments to classify overall sentiment.

AUDIENCE COMMENTS:
"{comments_text[:10000]}"

Classify the sentiment into exactly 3 dimensions with INTENSITY SCORES (0-100):
1. Positivo (Satisfaction, praise, positive sentiment, confidence, trust)
2. Negativo (Complaints, problems, criticism, dissatisfaction)
3. Neutral (Factual, informational, objective statements)

IMPORTANT: Return THREE numeric scores that represent the INTENSITY of each sentiment in the text:
- If 80% of comments are positive, positivo=80
- If 10% are negative, negativo=10
- If 10% are neutral, neutral=10

The three scores do NOT need to sum to 100 - we will normalize them in Python.

Return ONLY valid JSON:
{{
    "positivo": 75,
    "negativo": 15,
    "neutral": 10
}}"""
        
        try:
            # Use Responses API for GPT-5 models
            if self.model_name and "gpt-5" in self.model_name:
                logger.debug(f"Using Responses API for model: {self.model_name}")
                
                # Determine appropriate reasoning.effort value
                reasoning_effort = "low"
                
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
                        "content": "You are an expert sentiment analyst. Return valid JSON only with sentiment scores."
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
            logger.error(f"Error calling OpenAI API for sentiment analysis of {post_url}: {str(e)}", exc_info=True)
            raise

    def _normalize_sentiment_scores(self, raw_scores: Dict[str, Any]) -> Dict[str, float]:
        """
        Normalize raw sentiment scores (0-100) to probabilities that sum to 1.0.
        
        CRITICAL for Plotly pie charts: values MUST sum to 1.0 exactly.
        
        Args:
            raw_scores: Dict with raw scores from AI (positivo, negativo, neutral)
            
        Returns:
            Dict with normalized scores that sum to 1.0
        """
        sentiment_keys = ["positivo", "negativo", "neutral"]
        
        # Extract and validate scores, FORCE to float
        cleaned = {}
        for key in sentiment_keys:
            score = raw_scores.get(key, 0)
            try:
                val = float(score)
            except (ValueError, TypeError):
                logger.warning(f"Invalid score for '{key}': {score}. Using 0.0")
                val = 0.0
            # Clamp to [0, 100]
            val = max(0.0, min(100.0, val))
            cleaned[key] = val

        total = sum(cleaned.values())

        # Normalize to [0, 1] with 3 decimal places
        normalized = {}
        if total == 0:
            # If no information, distribute equally
            equal = round(1.0 / len(sentiment_keys), 3)
            for key in sentiment_keys:
                normalized[key] = equal
            return normalized

        for key, val in cleaned.items():
            normalized[key] = round(val / total, 3)

        # Ensure sum is 1.0 (fix rounding errors)
        actual_sum = sum(normalized.values())
        if abs(actual_sum - 1.0) > 0.001:
            # Adjust largest value to fix rounding
            max_key = max(normalized.keys(), key=lambda k: normalized[k])
            normalized[max_key] = round(1.0 - sum(v for k, v in normalized.items() if k != max_key), 3)

        return normalized

    async def analyze(self) -> Dict[str, Any]:
        """
        Execute sentiment analysis at POST LEVEL with complete schema including:
        - analisis_agregado: Global sentiment + Mixto classification
        - analisis_por_publicacion: Per-post analysis with Mixto and distribucion_sentimiento
        - resumen_global: Summary statistics
        
        Returns:
            Dictionary with metadata, all required sections, and errors
        """
        errors = []
        analisis_por_publicacion = []
        
        # For weighted global aggregation
        weighted_sentiment_scores = {}  # sentiment_type -> (total_weighted_score, total_weight)
        all_comments_list = []
        
        try:
            logger.info("Starting Q7 Detailed Sentiment Analysis")
            
            posts = self.get_posts_data()
            comments = self.get_comments_data()
            
            logger.info(f"Processing {len(posts)} posts with {len(comments)} comments")
            
            if not comments:
                errors.append("No comments found for analysis")
                return {
                    "metadata": {
                        "module": "Q7 Sentimiento Detallado",
                        "version": 3,
                        "description": "Detailed sentiment analysis with Mixto classification and complete schema"
                    },
                    "results": {
                        "analisis_agregado": {},
                        "analisis_por_publicacion": [],
                        "resumen_global": {}
                    },
                    "errors": errors
                }
            
            # Group comments by post
            comments_by_post = {}
            for comment in comments:
                link = comment.get("link")
                if link:
                    if link not in comments_by_post:
                        comments_by_post[link] = []
                    comments_by_post[link].append(comment.get("comment_text", ""))
                    all_comments_list.append(comment.get("comment_text", ""))
            
            # Analyze sentiment for each post
            post_count = 0
            subjetividad_acumulada = 0.0
            mixto_acumulada = 0.0
            
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
                print(f"   ⏳ Analizando publicación {idx}/{len(posts)}... ", end="")
                
                try:
                    # Call OpenAI with retry logic
                    analysis_result = await self._analyze_post_sentiment(link, combined_text)
                    
                    # Extract raw scores from response
                    raw_scores = {
                        "positivo": analysis_result.get("positivo", 0),
                        "negativo": analysis_result.get("negativo", 0),
                        "neutral": analysis_result.get("neutral", 0),
                    }
                    
                    # Normalize scores to sum to 1.0 (CRITICAL for pie charts)
                    sentimiento_normalizado = self._normalize_sentiment_scores(raw_scores)
                    
                    # Calculate Mixto: when both Positivo and Negativo are present
                    mixto_score = min(sentimiento_normalizado["positivo"], sentimiento_normalizado["negativo"]) * 2
                    mixto_score = min(mixto_score, 1.0)  # Cap at 1.0
                    
                    # Calculate subjetividad (ambiguity/mixed sentiment ratio)
                    subjetividad = max(sentimiento_normalizado["positivo"], sentimiento_normalizado["negativo"])
                    
                    # Accumulate weighted scores for global aggregation
                    for sentiment_type, score in sentimiento_normalizado.items():
                        weighted_score = score * num_comments  # Weighted by comment count
                        if sentiment_type not in weighted_sentiment_scores:
                            weighted_sentiment_scores[sentiment_type] = (0.0, 0.0)
                        old_score, old_weight = weighted_sentiment_scores[sentiment_type]
                        weighted_sentiment_scores[sentiment_type] = (
                            old_score + weighted_score,
                            old_weight + num_comments
                        )
                    
                    subjetividad_acumulada += subjetividad
                    mixto_acumulada += mixto_score
                    
                    # Build distribucion_sentimiento dict
                    distribucion_sentimiento = {
                        "Positivo": sentimiento_normalizado["positivo"],
                        "Negativo": sentimiento_normalizado["negativo"],
                        "Neutral": sentimiento_normalizado["neutral"],
                        "Mixto": mixto_score
                    }
                    
                    # Build per-post analysis with ALL required fields
                    post_analysis = {
                        "link": link,
                        "num_comentarios": num_comments,
                        "sentimiento_positivo": sentimiento_normalizado["positivo"],
                        "sentimiento_negativo": sentimiento_normalizado["negativo"],
                        "sentimiento_neutral": sentimiento_normalizado["neutral"],
                        "porcentaje_mixto": mixto_score,
                        "distribucion_sentimiento": distribucion_sentimiento,
                        "subjetividad_promedio": subjetividad,
                        "ejemplo_mixto": post_comments[0][:200] if post_comments else "N/A"  # First comment as example
                    }
                    
                    analisis_por_publicacion.append(post_analysis)
                    post_count += 1
                    print("✓")
                    logger.info(f"Successfully analyzed post with sentiment distribution: {sentimiento_normalizado}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing post {link}: {str(e)}", exc_info=True)
                    errors.append(f"Error analyzing post {link}: {str(e)}")
                    print("✗")
                    # Continue with next post (omit this one from aggregation)
                    continue
            
            # Calculate global sentiment from weighted scores
            sentimiento_general_norm = {}
            if weighted_sentiment_scores:
                # Calculate weighted averages
                sentiment_keys = ["positivo", "negativo", "neutral"]
                for sentiment_type in sentiment_keys:
                    if sentiment_type in weighted_sentiment_scores:
                        weighted_sum, total_weight = weighted_sentiment_scores[sentiment_type]
                        if total_weight > 0:
                            sentimiento_general_norm[sentiment_type] = round(weighted_sum / total_weight, 3)
                        else:
                            sentimiento_general_norm[sentiment_type] = 0.0
                    else:
                        sentimiento_general_norm[sentiment_type] = 0.0
                
                # Ensure sum is 1.0 (fix any rounding errors from weighted averaging)
                suma = sum(sentimiento_general_norm.values())
                if abs(suma - 1.0) > 0.001 and suma > 0:
                    # Normalize if needed
                    for key in sentiment_keys:
                        sentimiento_general_norm[key] = round(sentimiento_general_norm[key] / suma, 3)
            
            # Build analisis_agregado for frontend
            analisis_agregado = {
                "Positivo": sentimiento_general_norm.get("positivo", 0),
                "Negativo": sentimiento_general_norm.get("negativo", 0),
                "Neutral": sentimiento_general_norm.get("neutral", 0),
                "Mixto": round(mixto_acumulada / max(post_count, 1), 3),
                "subjetividad_promedio_global": round(subjetividad_acumulada / max(post_count, 1), 3)
            }
            
            # Build resumen_global
            resumen_global = {
                "total_publicaciones_analizadas": post_count,
                "promedio_porcentaje_mixto": round(mixto_acumulada / max(post_count, 1), 3),
                "promedio_subjetividad": round(subjetividad_acumulada / max(post_count, 1), 3),
                "distribucion_global": {
                    "Positivo": sentimiento_general_norm.get("positivo", 0),
                    "Negativo": sentimiento_general_norm.get("negativo", 0),
                    "Neutral": sentimiento_general_norm.get("neutral", 0)
                }
            }
            
            logger.info(f"Q7 analysis completed. {post_count} posts analyzed. Global sentiment: {sentimiento_general_norm}")
            
            print(f"   ✅ Análisis completado: {post_count} publicaciones analizadas")
            
        except Exception as e:
            logger.error(f"Critical error in Q7 analysis: {str(e)}", exc_info=True)
            errors.append(f"Critical error: {str(e)}")
            print(f"   ❌ Error fatal: {str(e)}")
        
        return {
            "metadata": {
                "module": "Q7 Sentimiento Detallado",
                "version": 3,
                "description": "Detailed sentiment analysis with Mixto classification and complete schema"
            },
            "results": {
                "analisis_agregado": analisis_agregado,
                "analisis_por_publicacion": analisis_por_publicacion,
                "resumen_global": resumen_global
            },
            "errors": errors
        }

