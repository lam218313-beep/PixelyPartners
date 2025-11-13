"""
Pixely Partners - Q3: Topics Analysis (Máximo Rendimiento)

Analyzes audience comments to identify main topics and their associated sentiment.
Uses weighted aggregation to reflect conversation volume and importance.

Features:
- Resilient API calls with automatic retry (3 attempts, 15s wait)
- Extended context window (15k chars) for comprehensive topic extraction
- Strict type conversion for topic relevance (0-100) and sentiment (-1.0 to 1.0)
- Per-post granular topic analysis with strategic context
- Weighted aggregation: posts with more comments have proportional influence
- Top 20 global topics extracted for relevance and diversity
"""

from typing import Dict, Any, List
import json
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

# Configure logger to use the shared orchestrator configuration
logger = logging.getLogger(__name__)


class Q3Topicos(BaseAnalyzer):
    """
    Q3 Topics Analysis with Weighted Aggregation.
    
    Analyzes comments on each client post to derive main topics and sentiment.
    Returns per-post topic profiles and global topic summary with weighting.
    
    Features:
    - Resilient API calls with automatic retry (3 attempts, 15s wait)
    - Extended context window (15k chars) for better topic extraction
    - Strict sanitization for topic scores (0-100) and sentiment (-1.0 to 1.0)
    - Weighted aggregation: post volume drives global priority
    - Top 20 topics in global analysis
    """

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
    async def _call_openai_for_topics(self, combined_text: str) -> Dict[str, Any]:
        """
        Resilient wrapper for OpenAI API call to analyze topics and sentiment.
        
        Retries automatically on failure (max 3 attempts with 15s wait between attempts).
        
        Args:
            combined_text: Aggregated comment text to analyze
            
        Returns:
            Analysis result dict with topics_relevance and topics_sentiment
            
        Raises:
            Exception: If all 3 retry attempts fail
        """
        prompt = f"""You are an expert data analyst specializing in topic extraction and sentiment analysis.

Analyze the following audience comments to identify the main topics and their associated sentiment.

AUDIENCE COMMENTS:
"{combined_text[:15000]}"

Extract the top 5-8 most significant distinct topics from these comments.

IMPORTANT RULES:
1. Topics must be NOUNS representing subjects or themes (e.g., "Price", "Quality", "Shipping", "Design").
2. Topics must NOT be adjectives or sentiments (e.g., do NOT use "Good", "Bad", "Expensive").
3. Estimate the RELEVANCE score (0-100) for each topic based on how much it is discussed.
4. Assign a SENTIMENT score (-1.0 to 1.0) for each topic based on audience perception.
   - -1.0 = Very negative (complaints)
   - 0.0 = Neutral
   - 1.0 = Very positive (praise)

Return ONLY valid JSON with two dictionaries:
{{
    "topics_relevance": {{"Topic1": 85, "Topic2": 60, "Topic3": 40}},
    "topics_sentiment": {{"Topic1": -0.3, "Topic2": 0.8, "Topic3": 0.2}},
    "summary": "<One sentence summary of the main topics discussed>"
}}"""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert data analyst. Extract topics as NOUNS only. Return valid JSON."
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
            logger.error(f"Error calling OpenAI API for topics analysis: {str(e)}", exc_info=True)
            raise

    def _sanitize_topic_scores(self, topics_relevance: Dict[str, Any], topics_sentiment: Dict[str, Any]) -> tuple:
        """
        Sanitize and validate topic scores to strict numeric types.
        
        Args:
            topics_relevance: Raw relevance dict (0-100)
            topics_sentiment: Raw sentiment dict (-1.0 to 1.0)
            
        Returns:
            Tuple of (clean_relevance_dict, clean_sentiment_dict)
        """
        clean_relevance = {}
        clean_sentiment = {}
        
        # Sanitize relevance (0-100)
        for topic, score in (topics_relevance or {}).items():
            try:
                val = float(score)
                val = max(0.0, min(100.0, val))  # Clamp to [0, 100]
                clean_relevance[str(topic)] = val
            except (ValueError, TypeError):
                logger.warning(f"Invalid relevance score for '{topic}': {score}. Using 0.0")
                clean_relevance[str(topic)] = 0.0
        
        # Sanitize sentiment (-1.0 to 1.0)
        for topic, score in (topics_sentiment or {}).items():
            try:
                val = float(score)
                val = max(-1.0, min(1.0, val))  # Clamp to [-1.0, 1.0]
                clean_sentiment[str(topic)] = val
            except (ValueError, TypeError):
                logger.warning(f"Invalid sentiment score for '{topic}': {score}. Using 0.0")
                clean_sentiment[str(topic)] = 0.0
        
        # Ensure same set of keys in both dicts
        all_topics = set(clean_relevance.keys()) | set(clean_sentiment.keys())
        for topic in all_topics:
            if topic not in clean_relevance:
                clean_relevance[topic] = 0.0
            if topic not in clean_sentiment:
                clean_sentiment[topic] = 0.0
        
        return clean_relevance, clean_sentiment

    async def analyze(self) -> Dict[str, Any]:
        """
        Execute topics analysis on all posts with weighted aggregation.
        
        Returns:
            Dictionary with metadata, per-post analysis, global summary, and errors
        """
        errors = []
        analisis_por_publicacion = []
        
        # For weighted aggregation
        weighted_topic_scores = {}  # topic -> (total_weighted_score, total_weight)
        
        try:
            logger.info("Starting Q3 Topics Analysis")
            
            ingested_data = self.load_ingested_data()
            posts = ingested_data.get("posts", [])
            comments = ingested_data.get("comments", [])
            
            logger.info(f"Processing {len(posts)} posts with {len(comments)} comments")
            
            if not comments:
                errors.append("No comments found for analysis")
                return {
                    "metadata": {
                        "module": "Q3 Topicos",
                        "version": 2,
                        "description": "Topics analysis using weighted aggregation (Máximo Rendimiento)"
                    },
                    "results": {
                        "analisis_por_publicacion": [],
                        "analisis_agregado": [],
                        "topicos_principales": []
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
            
            # Analyze topics for each post
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
                    analysis_result = await self._call_openai_for_topics(combined_text)
                    
                    # Extract raw data from response
                    raw_relevance = analysis_result.get("topics_relevance", {})
                    raw_sentiment = analysis_result.get("topics_sentiment", {})
                    
                    # Sanitize data
                    topics_relevance, topics_sentiment = self._sanitize_topic_scores(raw_relevance, raw_sentiment)
                    
                    # Limit to top 8 topics per post
                    if len(topics_relevance) > 8:
                        sorted_topics = sorted(topics_relevance.items(), key=lambda x: x[1], reverse=True)[:8]
                        topics_relevance = {t: s for t, s in sorted_topics}
                        topics_sentiment = {t: topics_sentiment.get(t, 0.0) for t in topics_relevance.keys()}
                    
                    # Accumulate weighted scores for global aggregation
                    for topic, relevance in topics_relevance.items():
                        weighted_score = relevance * num_comments  # Weighted by comment count
                        if topic not in weighted_topic_scores:
                            weighted_topic_scores[topic] = (0.0, 0.0)
                        old_score, old_weight = weighted_topic_scores[topic]
                        weighted_topic_scores[topic] = (
                            old_score + weighted_score,
                            old_weight + num_comments
                        )
                    
                    # Build per-post analysis
                    post_analysis = {
                        "post_url": post_url,
                        "num_comentarios": num_comments,
                        "topicos": topics_relevance,
                        "sentimiento": topics_sentiment,
                        "resumen": analysis_result.get("summary", "")
                    }
                    
                    analisis_por_publicacion.append(post_analysis)
                    logger.info(f"Successfully analyzed post with {len(topics_relevance)} topics")
                    
                except Exception as e:
                    logger.error(f"Error analyzing post {post_url}: {str(e)}", exc_info=True)
                    errors.append(f"Failed to analyze post {post_url}: {str(e)}")
                    # Continue with empty topics for this post
                    analisis_por_publicacion.append({
                        "post_url": post_url,
                        "num_comentarios": num_comments,
                        "topicos": {},
                        "sentimiento": {},
                        "resumen": ""
                    })
                    continue
            
            # Calculate global analysis from weighted scores
            analisis_agregado = []
            if weighted_topic_scores:
                # Calculate weighted averages
                global_topics = []
                for topic, (weighted_sum, total_weight) in weighted_topic_scores.items():
                    if total_weight > 0:
                        weighted_relevance = weighted_sum / total_weight
                        # Calculate average sentiment across posts that mention this topic
                        sentiments = []
                        for post in analisis_por_publicacion:
                            if topic in post.get("sentimiento", {}):
                                sentiments.append(post["sentimiento"][topic])
                        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
                        
                        global_topics.append({
                            "topic": topic,
                            "frecuencia_relativa": round(weighted_relevance, 2),
                            "sentimiento_promedio": round(avg_sentiment, 2)
                        })
                
                # Sort by relevance and take top 20
                global_topics = sorted(global_topics, key=lambda x: x["frecuencia_relativa"], reverse=True)[:20]
                analisis_agregado = global_topics
            
            topicos_principales = [t["topic"] for t in analisis_agregado[:5]]
            
            logger.info(f"Q3 analysis completed. Found {len(analisis_agregado)} topics globally")
            
        except Exception as e:
            logger.error(f"Critical error in Q3 analysis: {str(e)}", exc_info=True)
            errors.append(f"Critical error: {str(e)}")
        
        return {
            "metadata": {
                "module": "Q3 Topicos",
                "version": 2,
                "description": "Topics analysis using weighted aggregation (Máximo Rendimiento)"
            },
            "results": {
                "analisis_por_publicacion": analisis_por_publicacion,
                "analisis_agregado": analisis_agregado,
                "topicos_principales": topicos_principales
            },
            "errors": errors
        }
