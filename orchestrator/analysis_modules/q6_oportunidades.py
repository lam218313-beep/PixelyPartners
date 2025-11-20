"""
Pixely Partners - Q6: Strategic Opportunities Analysis (Máximo Rendimiento)

Identifies market opportunities from audience comments using a DEMAND vs. IMPACT matrix.
NO competitive analysis (only client's own data).

KEY PIVOT: The matrix redefines the axes to be 100% individual:
- gap_score (Eje X): Demand/Frequency - How often is this mentioned?
- competencia_score (Eje Y): Impact/Urgency - How much does it hurt without it?

This approach:
1. Keeps the frontend-compatible key names (gap_score, competencia_score)
2. Uses only the client's own data (no invented competitive data)
3. Provides actionable insights: High Demand + High Impact = GOLD

Features:
- Global Analysis: Combines all comments for strategic overview
- Text Truncation: Applies [:15000] safety patch to prevent token overflow
- Strict Float Typing: All scores sanitized to float for Plotly
- Resiliency: @retry with tenacity + comprehensive logging
- Correct Schema: Returns "oportunidades" key with frontend-compatible fields
"""

from typing import Dict, Any, List
import json
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class Q6Oportunidades(BaseAnalyzer):
    """
    Q6 Strategic Opportunities Analysis (Demand vs. Impact Matrix).
    
    Analyzes client's own data (no competitive analysis) to identify opportunities
    based on two 100% individual metrics:
    - gap_score (Demand): How frequently mentioned
    - competencia_score (Impact): How much pain it causes
    
    CRITICAL GUARANTEE: All numeric scores are strictly float type,
    preventing frontend Plotly graph collapse.
    """

    def _sanitize_score(self, value: Any, field_name: str = "score", default: float = 0.0) -> float:
        """
        RULE: STRICT FLOAT TYPING
        
        Converts any value to float [0, 100] with comprehensive fallback.
        Handles AI quirks: "85.0", "90%", "Alto", etc.
        
        Args:
            value: Raw value from LLM
            field_name: Field name for logging
            default: Default if conversion fails
            
        Returns:
            Clean float [0, 100]
        """
        if isinstance(value, (int, float)):
            try:
                result = float(value)
                return float(max(0.0, min(100.0, result)))
            except (ValueError, TypeError):
                logger.warning(f"{field_name}: Failed to convert number {value}, using default {default}")
                return default

        if isinstance(value, str):
            try:
                cleaned = value.replace('%', '').replace('/100', '').strip().lower()
                
                # Handle qualitative mappings
                qualitative_map = {
                    'muy bajo': 10.0, 'bajo': 25.0, 'low': 25.0, 'baja': 25.0,
                    'medio': 50.0, 'media': 50.0, 'medium': 50.0,
                    'alto': 75.0, 'muy alto': 90.0, 'high': 75.0, 'alta': 75.0,
                }
                
                if cleaned in qualitative_map:
                    return qualitative_map[cleaned]
                
                # Try numeric
                result = float(cleaned)
                return float(max(0.0, min(100.0, result)))
            except (ValueError, TypeError):
                logger.warning(f"{field_name}: Failed to parse string '{value}', using default {default}")
                return default
        
        logger.warning(f"{field_name}: Unsupported type {type(value)}, using default {default}")
        return default

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
    async def _call_openai_for_opportunities(self, combined_text: str) -> List[Dict[str, Any]]:
        """
        RULE: RESILIENCY
        
        Resilient call to identify opportunities from combined comments.
        Uses @retry for automatic recovery from transient failures.
        
        Args:
            combined_text: All comments combined (already truncated to 15000 chars)
            
        Returns:
            List of opportunity objects with oportunidad, gap_score, competencia_score, etc.
            
        Raises:
            Exception: If all 3 retry attempts fail
        """
        prompt = f"""You are an expert in market opportunity analysis. Your task is to analyze audience feedback and identify strategic opportunities.

CRITICAL INSTRUCTION: Do NOT analyze competitors. You only have access to THIS CLIENT'S comments. Work with what you have.

MATRIX DEFINITION (This is how the data will be visualized):
- **gap_score (Eje X: Demanda/Frecuencia)**: 0-100 scale.
  * How many people mention this? How often? (Frequency metric)
  * 0-30: Rarely mentioned (1-2 comments)
  * 30-60: Sometimes mentioned (3-5 comments)
  * 60-100: Frequently mentioned (6+ comments or very emphatic tone)

- **competencia_score (Eje Y: Impacto/Urgencia)**: 0-100 scale.
  * How much PAIN/URGENCY if we don't fix this? (Intensity metric)
  * 0-30: "Nice to have" (polite suggestions)
  * 30-60: "Would be helpful" (clear need)
  * 60-100: "CRITICAL" or "This is killing us" (severe pain points)

ANALYSIS RULES:
1. Identify distinct opportunities/themes from the comments
2. For each, count frequency (gap_score)
3. For each, assess pain intensity (competencia_score)
4. Focus on high-frequency OR high-pain items (or both)
5. Ignore spam, generic praise, and off-topic comments

EXAMPLE:
Comments:
- "We need faster invoice delivery" (User A)
- "Invoice speed is a nightmare" (User B)
- "Better invoicing would save us hours" (User C)
→ Opportunity: "Faster Invoice Delivery"
→ gap_score: 75 (mentioned by 3 users, emphatic tone)
→ competencia_score: 80 (described as "nightmare", saves "hours")

CLIENT COMMENTS (This is all you can analyze):
{combined_text}

Return ONLY valid JSON array. Each object must have these exact fields:
[
  {{
    "oportunidad": "<opportunity name>",
    "gap_score": <integer 0-100>,
    "competencia_score": <integer 0-100>,
    "detalle": "<brief explanation of the opportunity>",
    "accion": "<recommended action>"
  }},
  ...
]

STRICT RULES:
- gap_score and competencia_score MUST be integers (not strings)
- Return at least 3-5 opportunities if valid ones exist
- Sort by gap_score descending (highest demand first)
- If comments are too sparse, return []
"""

        try:
            # Use Responses API for GPT-5 models
            if self.model_name and "gpt-5" in self.model_name:
                logger.debug(f"Using Responses API for model: {self.model_name}")
                
                reasoning_effort = "minimal" if any(x in self.model_name for x in ["mini", "nano"]) else "low"
                
                response = await self.openai_client.responses.create(
                    model=self.model_name,
                    input=prompt,
                    reasoning={"effort": reasoning_effort},
                    text={"verbosity": "low"}
                )
                response_text = response.output_text.strip()
            else:
                # Fallback to Chat Completions API
                logger.debug(f"Using Chat Completions API for model: {self.model_name}")
                params = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                }
                if not any(x in self.model_name for x in ["gpt-5", "o1"]):
                    params["temperature"] = 0.7
                    params["max_tokens"] = 2000

                response = await self.openai_client.chat.completions.create(**params)
                response_text = response.choices[0].message.content.strip()
            
            # Parse JSON with fallback
            try:
                opportunities_list = json.loads(response_text)
                if not isinstance(opportunities_list, list):
                    logger.warning(f"Response is not a list: {type(opportunities_list)}")
                    return []
                return opportunities_list
            except json.JSONDecodeError:
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
            logger.error(f"Error calling OpenAI API for opportunities: {str(e)}", exc_info=True)
            raise

    async def analyze(self) -> Dict[str, Any]:
        """
        Execute Q6 opportunities analysis: Demand vs. Impact matrix (client-only data).
        
        Returns:
            {
                "metadata": {...},
                "results": {
                    "oportunidades": [
                        {
                            "oportunidad": "...",
                            "gap_score": float,
                            "competencia_score": float,
                            "detalle": "...",
                            "accion": "..."
                        }
                    ]
                },
                "errors": [...]
            }
        """
        errors = []
        results = {
            "oportunidades": [],
        }

        try:
            logger.info("Starting Q6 Opportunities Analysis")
            print("   🔍 Iniciando análisis de oportunidades (Demanda vs. Impacto)...")
            
            comments = self.get_comments_data()

            if not comments:
                error_msg = "No comments found for analysis"
                logger.warning(error_msg)
                errors.append(error_msg)
                print("   ⚠️  No se encontraron comentarios")
                
                return {
                    "metadata": {
                        "module": "Q6 Oportunidades",
                        "version": 2,
                        "description": "Demand vs. Impact opportunities analysis - Client data only (Máximo Rendimiento)",
                    },
                    "results": results,
                    "errors": errors,
                }

            # RULE: GLOBAL ANALYSIS
            # Combine all comments (this is one single analysis, not per-post)
            combined_text = "\n".join([
                f"[{c.get('ownerUsername', 'anon')}]: {c.get('comment_text', '')}"
                for c in comments if c.get('comment_text', '').strip()
            ])

            # RULE: SAFETY PATCH - TRUNCATE TO PREVENT TOKEN OVERFLOW
            # 15,000 characters = ~3,500 tokens (rough estimate)
            # This keeps us well within the context window
            safe_text = combined_text[:15000]
            
            print(f"   📍 Comentarios a analizar: {len(comments)}")
            logger.info(f"Processing {len(comments)} comments for opportunity analysis (truncated to {len(safe_text)} chars)")

            # Call OpenAI for opportunities
            opportunities_raw = await self._call_openai_for_opportunities(safe_text)
            logger.info(f"OpenAI returned {len(opportunities_raw)} opportunities")

            # RULE: STRICT FLOAT TYPING - Sanitize all numeric fields
            opportunities_cleaned = []
            
            for opp in opportunities_raw:
                try:
                    gap_score = self._sanitize_score(opp.get("gap_score", 0), "gap_score")
                    competencia_score = self._sanitize_score(opp.get("competencia_score", 0), "competencia_score")
                    
                    # Convert competencia_score (0-1) to categorical for frontend
                    if competencia_score < 0.33:
                        actividad_competitiva = "Baja"
                    elif competencia_score < 0.67:
                        actividad_competitiva = "Media"
                    else:
                        actividad_competitiva = "Alta"
                    
                    cleaned_opp = {
                        "oportunidad": str(opp.get("oportunidad", "Unknown")).strip()[:150],
                        "tema": str(opp.get("oportunidad", "Unknown")).strip()[:150],  # FRONTEND REQUIRED - alias for oportunidad
                        "gap_score": gap_score,
                        "competencia_score": competencia_score,
                        "actividad_competitiva": actividad_competitiva,  # FRONTEND REQUIRED
                        "detalle": str(opp.get("detalle", "")).strip()[:300],
                        "justificacion": str(opp.get("detalle", "")).strip()[:300],  # FRONTEND REQUIRED - alias for detalle
                        "accion": str(opp.get("accion", "")).strip()[:300],
                        "recomendacion_accion": str(opp.get("accion", "")).strip()[:300],  # FRONTEND REQUIRED - alias for accion
                    }
                    
                    logger.debug(
                        f"Cleaned opportunity: {cleaned_opp['oportunidad']}\n"
                        f"  gap_score: {cleaned_opp['gap_score']} (type: {type(cleaned_opp['gap_score']).__name__})\n"
                        f"  competencia_score: {cleaned_opp['competencia_score']} (type: {type(cleaned_opp['competencia_score']).__name__})\n"
                        f"  actividad_competitiva: {cleaned_opp['actividad_competitiva']}"
                    )
                    opportunities_cleaned.append(cleaned_opp)
                    
                except Exception as e:
                    logger.error(f"Error cleaning opportunity data: {str(e)}", exc_info=True)
                    continue

            # Sort by gap_score descending (highest demand first)
            opportunities_cleaned.sort(key=lambda x: x['gap_score'], reverse=True)
            results["oportunidades"] = opportunities_cleaned
            
            # FRONTEND COMPATIBILITY: Also add as lista_oportunidades
            results["lista_oportunidades"] = opportunities_cleaned
            
            # Calculate summary statistics for frontend
            if opportunities_cleaned:
                gap_scores = [opp['gap_score'] for opp in opportunities_cleaned]
                promedio_gap = sum(gap_scores) / len(gap_scores) if gap_scores else 0
                oportunidades_criticas = sum(1 for opp in opportunities_cleaned 
                                            if opp['gap_score'] >= 80 and opp['actividad_competitiva'] == 'Baja')
                
                results["resumen_global"] = {
                    "promedio_gap_score": round(promedio_gap, 1),
                    "oportunidades_criticas": oportunidades_criticas,
                    "total_oportunidades": len(opportunities_cleaned),
                }

            print(f"   ✅ Análisis completado: {len(opportunities_cleaned)} oportunidades identificadas")
            logger.info(f"Q6 Analysis complete: {len(opportunities_cleaned)} opportunities identified")

        except Exception as e:
            fatal_error = f"Fatal error in Q6 analysis: {str(e)}"
            logger.error(fatal_error, exc_info=True)
            errors.append(fatal_error)
            print(f"   ❌ Error fatal: {fatal_error}")

        return {
            "metadata": {
                "module": "Q6 Oportunidades",
                "version": 2,
                "description": "Demand vs. Impact opportunities analysis - Client data only (Máximo Rendimiento)",
            },
            "results": results,
            "errors": errors,
        }

