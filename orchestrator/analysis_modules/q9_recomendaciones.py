"""
Pixely Partners - Q9: Strategic Recommendations (Máximo Rendimiento)

Generates 5-10 strategic, actionable recommendations based on:
- Recurring problems identified across comments
- Explicit user suggestions
- Sentiment trends and engagement patterns

Features:
- Global analysis: Combines ALL comments for holistic insights
- Numeric scoring: Impacto (1-100) and Esfuerzo (1-100)
- Backend calculation: Prioridad = Impacto / Esfuerzo (Python, not AI)
- Safety patch: Text truncation [:15000] to prevent token overflow
- Resilient API: tenacity with 3 attempts, 15s wait (analysis is heavy)
- Per-recommendation error isolation
- Sorted by priority (descending) for user convenience
"""

from typing import Dict, Any, List
import json
import logging
import asyncio

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

# Configure logger to use the shared orchestrator configuration
logger = logging.getLogger(__name__)


class Q9Recomendaciones(BaseAnalyzer):
    """
    Q9 Strategic Recommendations using global analysis.
    
    Analyzes ALL comments to identify recurring problems and generate
    5-10 strategic, prioritized recommendations.
    
    Features:
    - Global Aggregation: All comments combined for complete context
    - Numeric Scoring: Impacto (1-100) and Esfuerzo (1-100)
    - Backend Priority: Calculated as Impacto / Esfuerzo in Python
    - Token Safety: Text truncated to 15000 chars
    - Resilient: @retry with 15s wait for heavy analysis
    - Pre-sorted: By priority (descending)
    """

    def _get_model_params(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generates API parameters compatible with GPT-5-mini and other models.
        
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
            pass
        else:
            # Legacy models support temperature and max_tokens
            params["temperature"] = 0.7
            params["max_tokens"] = 1000
            
        return params

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
    async def _generate_recommendations(self, combined_text: str) -> List[Dict[str, Any]]:
        """
        Generates 5-10 strategic recommendations from combined text with automatic retry logic.
        
        Heavy analysis task: Waits 15s between retries (not 2s) to allow API recovery.
        
        Args:
            combined_text: Aggregated comment text (already truncated to 15000 chars)
            
        Returns:
            List of recommendation dicts with recomendacion, impacto, esfuerzo
            
        Raises:
            Exception: If all 3 retry attempts fail
        """
        
        prompt = f"""You are a strategic analyst. Analyze the following audience comments to identify the 5-10 MOST IMPACTFUL and ACTIONABLE recommendations.

AUDIENCE COMMENTS (Global Analysis):
"{combined_text}"

For EACH recommendation, identify:
1. "recomendacion": A clear, specific action (e.g., "Increase posting frequency on design tips to 3x/week")
2. "impacto": How much impact this recommendation would have (1-100 scale):
   - 1-20: Minimal impact (cosmetic changes)
   - 21-50: Moderate impact (could improve engagement)
   - 51-80: High impact (major improvement expected)
   - 81-100: Critical/Transformational (would significantly move KPIs)
3. "esfuerzo": How much effort/resources this requires to implement (1-100 scale):
   - 1-20: Minimal effort (can start immediately, <1 hour)
   - 21-50: Moderate effort (1-2 weeks of work)
   - 51-80: Significant effort (1-3 months of work)
   - 81-100: Major effort (3+ months, significant resources)

IMPORTANT RULES:
- Generate 5-10 recommendations (not more, not less)
- ONLY focus on problems identified in the comments and explicit user suggestions
- Ignore generic advice; focus on THIS audience's specific pain points
- Return ONLY valid JSON array with recomendacion, impacto, esfuerzo (NO prioridad)

Example format:
[
    {{"recomendacion": "...", "impacto": 85, "esfuerzo": 20}},
    {{"recomendacion": "...", "impacto": 72, "esfuerzo": 45}}
]"""
        
        try:
            logger.info(f"Generating recommendations from {len(combined_text)} chars of text")
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a strategic analyst. Analyze comments and generate numbered recommendations with numeric impact/effort scores (1-100). Return ONLY valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            params = self._get_model_params(messages)
            logger.debug(f"API params: model={params.get('model')}, temperature={params.get('temperature')}")
            
            logger.debug(f"Calling chat.completions.create...")
            response = await self.openai_client.chat.completions.create(**params)
            content = response.choices[0].message.content.strip()
            logger.debug(f"Response received: {len(content)} chars")
            
            # Try to parse JSON from response
            try:
                logger.debug(f"Parsing JSON from response...")
                data = json.loads(content)
                logger.info(f"Successfully parsed {len(data)} recommendations from API")
                return data
            except json.JSONDecodeError as je:
                logger.warning(f"JSON parse failed, trying to extract from markdown")
                # If JSON parsing fails, try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_part = content.split("```json")[1].split("```")[0].strip()
                    data = json.loads(json_part)
                elif "```" in content:
                    json_part = content.split("```")[1].split("```")[0].strip()
                    data = json.loads(json_part)
                else:
                    raise json.JSONDecodeError("Could not extract JSON from response", content, 0)
                logger.info(f"Successfully extracted {len(data)} recommendations from markdown")
                return data
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def _sanitize_numeric(self, value: Any, key: str, min_val: int = 1, max_val: int = 100) -> float:
        """
        Sanitize and clamp a numeric value to range [1-100].
        
        CRITICAL: Forced float conversion + range validation.
        
        Args:
            value: Raw value from AI (could be string, int, float, or None)
            key: Key name for logging
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Clamped float value
        """
        try:
            val = float(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid numeric value for '{key}': {value} (type: {type(value).__name__}). Using default 50")
            val = 50.0
        
        # Clamp to range [1-100]
        val = max(min_val, min(max_val, val))
        return round(val, 2)

    async def analyze(self) -> Dict[str, Any]:
        """
        Execute Q9 Strategic Recommendations analysis.
        
        Global analysis: Combines ALL comments to identify recurring problems
        and generate 5-10 prioritized strategic recommendations.
        
        Returns:
            Dictionary with metadata, recommendations (pre-sorted by priority), and errors
        """
        errors = []
        recomendaciones = []
        
        try:
            logger.info("Starting Q9 Strategic Recommendations Analysis")
            
            comments = self.get_comments_data()
            
            logger.info(f"Processing {len(comments)} comments for recommendation generation")
            print(f"   📊 Iniciando análisis de recomendaciones estratégicas...")
            
            if not comments:
                errors.append("No comments found for recommendation analysis")
                logger.warning("No comments found")
                return {
                    "metadata": {
                        "module": "Q9 Recomendaciones",
                        "version": 3,
                        "description": "Strategic recommendations with numeric scoring (Máximo Rendimiento)"
                    },
                    "results": {
                        "recomendaciones": []
                    },
                    "errors": errors
                }
            
            # Combine ALL comments into single text (GLOBAL analysis)
            combined_text = " ".join([
                str(c.get("comment_text", ""))
                for c in comments
                if c.get("comment_text") and str(c.get("comment_text")).strip()
            ])
            
            if not combined_text.strip():
                errors.append("No valid comment text found")
                logger.error("No valid comment text")
                return {
                    "metadata": {
                        "module": "Q9 Recomendaciones",
                        "version": 3,
                        "description": "Strategic recommendations with numeric scoring (Máximo Rendimiento)"
                    },
                    "results": {
                        "recomendaciones": []
                    },
                    "errors": errors
                }
            
            logger.info(f"Combined text: {len(combined_text)} chars")
            print(f"   ✓ {len(comments)} comentarios agregados")
            
            # SAFETY PATCH: Truncate to 15000 chars to prevent token overflow
            safe_text = combined_text[:15000]
            logger.info(f"Safe text (after truncation): {len(safe_text)} chars")
            print(f"   📍 Texto para análisis: {len(safe_text)} caracteres")
            
            # Call OpenAI for recommendations
            try:
                logger.info("Calling OpenAI for recommendation generation...")
                print(f"   ⏳ Generando recomendaciones... ", end="", flush=True)
                
                ai_recommendations = await self._generate_recommendations(safe_text)
                
                if not ai_recommendations:
                    errors.append("API returned empty recommendation list")
                    logger.error("Empty recommendation list from API")
                    print("✗ (empty)", flush=True)
                else:
                    logger.info(f"API returned {len(ai_recommendations)} recommendations")
                    print(f"✓ ({len(ai_recommendations)} recomendaciones)", flush=True)
                    
                    # Process each recommendation
                    for idx, rec in enumerate(ai_recommendations, 1):
                        try:
                            logger.debug(f"Processing recommendation {idx}/{len(ai_recommendations)}: {rec.get('recomendacion', '')[:50]}...")
                            
                            # Extract text
                            recomendacion_text = str(rec.get("recomendacion", "Unknown")).strip()[:200]
                            
                            # Sanitize NUMERIC values (STRICT TYPING)
                            score_impacto = self._sanitize_numeric(
                                rec.get("impacto", 50),
                                "impacto",
                                min_val=1,
                                max_val=100
                            )
                            
                            score_esfuerzo = self._sanitize_numeric(
                                rec.get("esfuerzo", 50),
                                "esfuerzo",
                                min_val=1,
                                max_val=100
                            )
                            
                            # Calculate PRIORITY in Python (NOT from AI)
                            # prioridad = score_impacto / score_esfuerzo, with score_esfuerzo min 1 (already guaranteed by range)
                            prioridad = round(score_impacto / max(1, score_esfuerzo), 2)
                            
                            # Build recommendation dict
                            rec_dict = {
                                "recomendacion": recomendacion_text,
                                "score_impacto": score_impacto,
                                "score_esfuerzo": score_esfuerzo,
                                "prioridad": prioridad
                            }
                            
                            recomendaciones.append(rec_dict)
                            logger.debug(f"Recommendation {idx}: score_impacto={score_impacto}, score_esfuerzo={score_esfuerzo}, prioridad={prioridad}")
                            
                        except Exception as rec_error:
                            logger.error(f"Error processing recommendation {idx}: {str(rec_error)}", exc_info=True)
                            errors.append(f"Error processing recommendation {idx}: {str(rec_error)}")
                            # Continue with next recommendation (error isolation)
                            continue
                    
            except Exception as api_error:
                logger.error(f"API Error: {type(api_error).__name__}: {str(api_error)}", exc_info=True)
                errors.append(f"API error during recommendation generation: {str(api_error)}")
                print("✗", flush=True)
            
            # SORT by priority (DESCENDING) - Most important first
            recomendaciones_sorted = sorted(
                recomendaciones,
                key=lambda x: x['prioridad'],
                reverse=True
            )
            
            # Add missing fields to each recommendation for frontend compatibility
            for i, rec in enumerate(recomendaciones_sorted, 1):
                # Add ID
                rec["id"] = i
                
                # Determine area_estrategica based on recommendation text (simple heuristic)
                rec_text_lower = rec["recomendacion"].lower()
                areas = {
                    'Comunicación y Transparencia': ['comunicación', 'mensaje', 'claridad', 'transparencia'],
                    'Contenido y Educación': ['contenido', 'educación', 'publicar', 'crear'],
                    'Influenciadores y Advocacy': ['influenciador', 'ambassador', 'advocacy'],
                    'Engagement y Comunidad': ['engagement', 'comunidad', 'interacción', 'comentarios'],
                    'Tono y Narrativa': ['tono', 'narrativa', 'voz', 'estilo'],
                    'Innovación de Producto': ['producto', 'innovación', 'feature', 'desarrollo'],
                    'Oportunidades de Mercado': ['mercado', 'oportunidad', 'demanda', 'segmento']
                }
                
                area_asignada = 'Comunicación y Transparencia'
                for area, keywords in areas.items():
                    if any(kw in rec_text_lower for kw in keywords):
                        area_asignada = area
                        break
                
                rec["area_estrategica"] = area_asignada
                
                # Add descripcion (from recomendacion text, first 150 chars)
                rec["descripcion"] = rec["recomendacion"][:150] + ("..." if len(rec["recomendacion"]) > 150 else "")
                
                # Determine urgencia based on score_impacto/score_esfuerzo ratio
                prioridad_val = rec["prioridad"]
                if prioridad_val >= 2.0:
                    urgencia = "CRÍTICA"
                elif prioridad_val >= 1.5:
                    urgencia = "ALTA"
                elif prioridad_val >= 1.0:
                    urgencia = "MEDIA-ALTA"
                elif prioridad_val >= 0.5:
                    urgencia = "MEDIA"
                else:
                    urgencia = "BAJA"
                
                rec["urgencia"] = urgencia
                
                # Build justificacion_framework as array of Q references
                # Based on score_impacto, reference relevant Qs
                rec["justificacion_framework"] = ["1", "3", "6", "9"]  # Default: Emotions, Topics, Opportunities, Recommendations
                
                # Add acciones_concretas (action items to implement recommendation)
                acciones = [
                    f"Paso 1: Analizar contexto actual del {area_asignada.lower()}",
                    f"Paso 2: Implementar: {rec['recomendacion'][:80]}",
                    f"Paso 3: Medir impacto en siguientes 2 semanas",
                    f"Paso 4: Ajustar según resultados (target: impacto ≥ {rec['score_impacto']}/100)"
                ]
                rec["acciones_concretas"] = acciones
            
            # Build resumen_global
            resumen_global = {
                "total_recomendaciones": len(recomendaciones_sorted),
                "score_impacto_promedio": round(
                    sum(r.get("score_impacto", 0) for r in recomendaciones_sorted) / max(len(recomendaciones_sorted), 1), 1
                ),
                "score_esfuerzo_promedio": round(
                    sum(r.get("score_esfuerzo", 0) for r in recomendaciones_sorted) / max(len(recomendaciones_sorted), 1), 1
                ),
                "recomendaciones_criticas": len([r for r in recomendaciones_sorted if r.get("urgencia") == "CRÍTICA"]),
                "recomendaciones_altas": len([r for r in recomendaciones_sorted if r.get("urgencia") == "ALTA"])
            }
            
            logger.info(f"Q9 analysis completed. {len(recomendaciones_sorted)} recommendations generated and sorted")
            print(f"   ✅ Análisis completado: {len(recomendaciones_sorted)} recomendaciones generadas")
            
        except Exception as e:
            logger.error(f"Critical error in Q9 analysis: {str(e)}", exc_info=True)
            errors.append(f"Critical error: {str(e)}")
            print(f"   ❌ Error fatal: {str(e)}")
        
        return {
            "metadata": {
                "module": "Q9 Recomendaciones",
                "version": 4,
                "description": "Strategic recommendations with area, urgency, and framework justification"
            },
            "results": {
                "lista_recomendaciones": recomendaciones_sorted,
                "resumen_global": resumen_global
            },
            "errors": errors
        }
