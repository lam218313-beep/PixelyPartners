"""
Pixely Partners - Q5: Influencers and Key Voices Analysis (Máximo Rendimiento)

Identifies key opinion leaders and domain experts from audience comments.
Uses identity-aware analysis: [username]: comment_text format for proper attribution.

Features:
- Identity Awareness: Enriches comments with username for proper influencer attribution
- Quality Filter: Skeptical prompt filters generic praise vs. domain authority
- Strict Typing: Converts autoridad/afinidad to float (0-100)
- Score Separation: Autoridad (expertise) vs. Afinidad (sentiment)
- Resiliency: Retry logic with tenacity + comprehensive logging
"""

from typing import Dict, Any, List
import json
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

# Configure logger to use the shared orchestrator configuration
logger = logging.getLogger(__name__)


class Q5Influenciadores(BaseAnalyzer):
    """
    Q5 Influencers and Key Voices Analysis.
    
    Identifies domain experts and influencers from audience comments using identity-aware analysis.
    Returns per-post influencers and global influencer ranking.
    
    Key Features:
    - Rule 1: Identity Awareness - [username]: comment_text enrichment
    - Rule 2: Quality Filter - Skeptical prompt filters generic praise
    - Rule 3: Strict Typing - Converts scores to float
    - Rule 4: Score Separation - Autoridad vs. Afinidad distinction
    - Rule 5: Resiliency - Tenacity retry + logging
    """

    def _enrich_comments_with_identity(self, comments: List[Dict[str, Any]]) -> str:
        """
        RULE 1: IDENTITY AWARENESS
        
        Enriches comments with username for proper influencer identification.
        Format: [username]: comment_text
        
        This allows the AI to identify WHO said WHAT and return exact usernames.
        
        Args:
            comments: List of comment objects with 'ownerUsername' and 'comment_text'
            
        Returns:
            Enriched text with identity markers
        """
        enriched_lines = []
        
        for comment in comments:
            username = comment.get('ownerUsername', 'usuario_anonimo')
            text = comment.get('comment_text', '')
            
            if text.strip():  # Only include non-empty comments
                # Inject identity: [username]: text
                enriched_line = f"[{username}]: {text}"
                enriched_lines.append(enriched_line)
        
        return "\n".join(enriched_lines)

    def _clean_influencer_scores(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        RULE 3: STRICT TYPING
        
        Converts LLM-returned scores to float (0-100).
        Handles common LLM outputs like "90%", "90/100", "High", etc.
        
        Args:
            raw_data: Raw response from LLM (may have string scores)
            
        Returns:
            Cleaned data with float scores
        """
        def parse_score(value: Any, default: float = 0.0) -> float:
            """Convert any score format to float [0, 100]"""
            if isinstance(value, (int, float)):
                return float(max(0.0, min(100.0, value)))
            
            if isinstance(value, str):
                try:
                    # Remove common suffixes: %, /100, etc.
                    cleaned = value.replace('%', '').replace('/100', '').strip()
                    score = float(cleaned)
                    return float(max(0.0, min(100.0, score)))
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse score '{value}', using default {default}")
                    return default
            
            return default
        
        cleaned = raw_data.copy()
        cleaned['autoridad'] = parse_score(raw_data.get('autoridad', 0.0))
        cleaned['afinidad'] = parse_score(raw_data.get('afinidad', 50.0))
        
        return cleaned

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
    async def _call_openai_for_influencers(self, enriched_text: str) -> List[Dict[str, Any]]:
        """
        RULE 5: RESILIENCY + RULE 1: IDENTITY AWARENESS
        
        Resilient wrapper for OpenAI API call to identify influencers.
        Uses identity-enriched text [username]: comment_text.
        
        Retries automatically on failure (max 3 attempts with 15s wait).
        
        Args:
            enriched_text: Enriched comments with [username]: text format
            
        Returns:
            List of influencer objects with username, autoridad, afinidad, etc.
            
        Raises:
            Exception: If all 3 retry attempts fail
        """
        prompt = f"""You are an expert in identifying key voices and engaged community members from social media comments.

Your task: Analyze the following comments to identify VOICES - users who demonstrate influence, expertise, or strong engagement.

IMPORTANT: Be INCLUSIVE, not exclusive. An influencer can be:
1. Domain experts (technical jargon, in-depth analysis)
2. Professional/leadership voices (business experience, expertise claims)
3. Passionate advocates (detailed positive/critical feedback, repeated engagement)
4. Thoughtful critics (substantive concerns, informed questions)

WHAT TO IGNORE:
- Generic one-word praise ("great", "love it", "thanks")
- Pure emoji reactions
- Spam or promotional content only

The "username" in output MUST exactly match [username] from the input.

SCORE DEFINITIONS:
- "autoridad" (0-100): How much expertise/credibility they demonstrate (0=none, 100=recognized expert)
- "afinidad" (0-100): Sentiment (0=detractor, 50=neutral/factual, 100=strong advocate)

EXAMPLE INPUT:
[user123]: I've implemented this approach in my agency and the ROI is 3.5x better than the previous method.
[user456]: Love this! Best post today!
[user789]: As a CTO, I'd recommend caution with this implementation - the security implications need review.

EXPECTED OUTPUT:
[
  {{"username": "user123", "autoridad": 75, "afinidad": 85, "evidencia": "I've implemented this approach in my agency...", "razon": "Professional experience with quantified results"}},
  {{"username": "user789", "autoridad": 80, "afinidad": 55, "evidencia": "As a CTO, I'd recommend caution...", "razon": "Leadership position with security expertise"}}
]
Note: user456 was excluded (generic praise only)

AUDIENCE COMMENTS (Format: [username]: comment):
{enriched_text[:15000]}

Return ONLY valid JSON array. If few qualify as voices (even 1-2), include them. Return [] only if ALL are pure spam/emoji/generic.
[
  {{
    "username": "<exact username from [username]: format>",
    "autoridad": <integer 0-100>,
    "afinidad": <integer 0-100>,
    "evidencia": "<direct quote that qualifies them>",
    "razon": "<why they are a voice worth noting>"
  }}
]
"""

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
                # Fallback to Chat Completions API for other models
                logger.debug(f"Using Chat Completions API for model: {self.model_name}")
                params = {
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                }
                
                # Add temperature and max_tokens only for non-GPT5 models
                if not any(x in self.model_name for x in ["gpt-5", "o1"]):
                    params["temperature"] = 0.7
                    params["max_tokens"] = 1000

                response = await self.openai_client.chat.completions.create(**params)
                response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            try:
                influencers_list = json.loads(response_text)
                if not isinstance(influencers_list, list):
                    logger.warning(f"Response is not a list: {type(influencers_list)}")
                    return []
                return influencers_list
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}, response_text: {response_text[:500]}")
                # If JSON parsing fails, try to extract JSON from markdown code blocks
                if "```json" in response_text:
                    json_part = response_text.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_part)
                elif "```" in response_text:
                    json_part = response_text.split("```")[1].split("```")[0].strip()
                    return json.loads(json_part)
                elif response_text.strip() == "[]":
                    return []
                else:
                    logger.error(f"Response text for debugging: {response_text[:500]}")
                    raise json.JSONDecodeError("Could not extract JSON from response", response_text, 0)

        except Exception as e:
            logger.error(f"Error calling OpenAI API for influencers analysis: {str(e)}", exc_info=True)
            raise

    async def analyze(self) -> Dict[str, Any]:
        """
        Execute Q5 influencers analysis with identity awareness and quality filtering.
        
        Returns:
            {
                "metadata": {...},
                "results": {
                    "analisis_influenciadores": [
                        {
                            "post_url": "...",
                            "num_comentarios": int,
                            "influenciadores": [
                                {
                                    "username": "...",
                                    "autoridad": float,
                                    "afinidad": float,
                                    "evidencia": "...",
                                    "razon": "..."
                                },
                                ...
                            ]
                        },
                        ...
                    ],
                    "influenciadores_globales": [
                        {
                            "username": "...",
                            "autoridad_promedio": float,
                            "afinidad_promedio": float,
                            "menciones": int,
                            "razon": "..."
                        }
                    ]
                },
                "errors": [...]
            }
        """
        errors = []
        results = {
            "analisis_influenciadores": [],
            "influenciadores_globales": [],
        }

        try:
            logger.info("Starting Q5 Influencers Analysis")
            print("   📊 Iniciando análisis de influenciadores...")
            
            ingested_data = self.load_ingested_data()
            posts = ingested_data.get("posts", [])
            comments = ingested_data.get("comments", [])

            if not comments:
                error_msg = "No comments found for analysis"
                logger.warning(error_msg)
                errors.append(error_msg)
                print("   ⚠️  No se encontraron comentarios")
                
                return {
                    "metadata": {
                        "module": "Q5 Influenciadores",
                        "version": 2,
                        "description": "Influencers and key voices analysis with identity awareness (Máximo Rendimiento)",
                    },
                    "results": results,
                    "errors": errors,
                }

            # Group comments by post_url (RULE 1: Keep comment objects, not just text)
            comments_by_post = {}
            for comment in comments:
                post_url = comment.get("post_url")
                if post_url:
                    if post_url not in comments_by_post:
                        comments_by_post[post_url] = []
                    comments_by_post[post_url].append(comment)

            print(f"   📍 Publicaciones encontradas: {len(posts)}")
            print(f"   💬 Comentarios a analizar: {len(comments)}")
            logger.info(f"Processing {len(posts)} posts with {len(comments)} comments")

            # Global accumulator for influencers across all posts
            all_influencers = {}  # {username: {autoridad: [...], afinidad: [...], razon: "...", count: N}}
            post_count = 0
            
            for idx, post in enumerate(posts, 1):
                post_url = post.get("post_url")
                if not post_url or post_url not in comments_by_post:
                    continue

                post_comments = comments_by_post[post_url]
                if not post_comments:
                    continue

                try:
                    # RULE 1: IDENTITY AWARENESS - Enrich comments with username
                    enriched_text = self._enrich_comments_with_identity(post_comments)

                    total_posts = len([p for p in posts if p.get('post_url') in comments_by_post])
                    print(f"   ⏳ Analizando publicación {idx}/{total_posts}...", end="", flush=True)
                    logger.info(f"Analyzing post {post_count + 1}/{total_posts}: {post_url[:50]}...")

                    # Call OpenAI with resilience (3 retries, 15s wait)
                    influencers_raw = await self._call_openai_for_influencers(enriched_text)

                    # RULE 3: STRICT TYPING - Clean and validate scores
                    influencers_cleaned = []
                    for influencer in influencers_raw:
                        try:
                            cleaned = self._clean_influencer_scores(influencer)
                            influencers_cleaned.append(cleaned)
                            
                            # Accumulate for global ranking
                            username = cleaned.get('username', 'unknown')
                            if username not in all_influencers:
                                all_influencers[username] = {
                                    'autoridad_scores': [],
                                    'afinidad_scores': [],
                                    'evidencias': [],
                                    'razones': []
                                }
                            
                            all_influencers[username]['autoridad_scores'].append(cleaned.get('autoridad', 0.0))
                            all_influencers[username]['afinidad_scores'].append(cleaned.get('afinidad', 50.0))
                            if cleaned.get('evidencia'):
                                all_influencers[username]['evidencias'].append(cleaned.get('evidencia'))
                            if cleaned.get('razon'):
                                all_influencers[username]['razones'].append(cleaned.get('razon'))
                                
                        except Exception as e:
                            logger.error(f"Error cleaning influencer data: {str(e)}", exc_info=True)
                            continue

                    # Build result for this post
                    post_analysis = {
                        "post_url": post_url,
                        "num_comentarios": len(post_comments),
                        "influenciadores": influencers_cleaned,
                    }

                    results["analisis_influenciadores"].append(post_analysis)
                    post_count += 1
                    print(f" ✓")
                    logger.info(f"Successfully analyzed post, found {len(influencers_cleaned)} influencers")

                except Exception as e:
                    error_msg = f"Error analyzing post {post_url}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
                    print(f" ✗")
                    continue

            # Calculate global influencer ranking
            if all_influencers:
                for username, data in all_influencers.items():
                    avg_autoridad = sum(data['autoridad_scores']) / len(data['autoridad_scores']) if data['autoridad_scores'] else 0.0
                    avg_afinidad = sum(data['afinidad_scores']) / len(data['afinidad_scores']) if data['afinidad_scores'] else 50.0
                    
                    # Get most common reason
                    razon = data['razones'][0] if data['razones'] else "No reason provided"
                    
                    # Get most representative comment evidence
                    comentario_evidencia = data['evidencias'][0] if data['evidencias'] else "No comments"
                    
                    # Calculate score de centralidad (normalize to 0-1 based on mentions)
                    mention_count = len(data['autoridad_scores'])
                    score_centralidad = round(min(mention_count / 12.0, 1.0), 3)  # 12 posts max
                    
                    # Determine polaridad_dominante based on afinidad
                    # afinidad: 0-25 Detractor, 25-75 Neutral, 75-100 Promotor
                    if avg_afinidad < 25:
                        polaridad_dominante = "Detractor"
                    elif avg_afinidad < 75:
                        polaridad_dominante = "Neutral"
                    else:
                        polaridad_dominante = "Promotor"
                    
                    # Calculate alcance (network reach based on mentions and authority)
                    alcance = round(mention_count * (avg_autoridad / 100.0), 1) if avg_autoridad > 0 else 0.0
                    
                    # Calculate sentimiento (afinidad normalized to -1 to 1)
                    sentimiento = round((avg_afinidad - 50.0) / 50.0, 2)
                    
                    results["influenciadores_globales"].append({
                        "username": username,
                        "autoridad_promedio": round(avg_autoridad, 2),
                        "afinidad_promedio": round(avg_afinidad, 2),
                        "menciones": mention_count,
                        "razon": razon,
                        # FRONTEND REQUIRED FIELDS
                        "score_centralidad": score_centralidad,
                        "polaridad_dominante": polaridad_dominante,
                        "alcance": alcance,
                        "sentimiento": sentimiento,
                        "comentario_evidencia": comentario_evidencia[:500],  # Truncate to 500 chars
                    })
                
                # Sort by score_centralidad descending (highest impact first)
                results["influenciadores_globales"].sort(
                    key=lambda x: x['score_centralidad'],
                    reverse=True
                )
                
                # FRONTEND COMPATIBILITY: Also add as top_influenciadores_detallado
                results["top_influenciadores_detallado"] = results["influenciadores_globales"]
                
                print(f"   ✅ Análisis completado: {post_count} publicaciones analizadas, {len(all_influencers)} influenciadores identificados")
                logger.info(f"Q5 Analysis complete: {post_count} posts analyzed, {len(all_influencers)} global influencers identified")
            else:
                print("   ⚠️  No influencers data available")
                logger.warning("No influencers identified in any posts")

        except Exception as e:
            fatal_error = f"Fatal error in Q5 analysis: {str(e)}"
            logger.error(fatal_error, exc_info=True)
            errors.append(fatal_error)
            print(f"   ❌ Error fatal: {fatal_error}")

        return {
            "metadata": {
                "module": "Q5 Influenciadores",
                "version": 2,
                "description": "Influencers and key voices analysis with identity awareness (Máximo Rendimiento)",
            },
            "results": results,
            "errors": errors,
        }

