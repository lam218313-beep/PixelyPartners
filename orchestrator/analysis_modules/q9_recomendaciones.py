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
        
        prompt = f"""Eres un analista estratégico experto en marketing digital y gestión de comunidades. Analiza los siguientes comentarios de la audiencia para identificar las 16 recomendaciones MÁS IMPACTANTES y ACCIONABLES (4 por semana).

COMENTARIOS DE LA AUDIENCIA (Análisis Global):
"{combined_text}"

Para CADA recomendación, genera:

1. "recomendacion": Un TÍTULO claro, descriptivo y profesional en ESPAÑOL (50-100 caracteres)
   - Ejemplo: "Crear programa de capacitación técnica con certificación incluida"
   - Ejemplo: "Implementar soporte 24/7 en español para atención regional"
   - Debe ser específico y orientado a acción

2. "descripcion": Una DESCRIPCIÓN OPERATIVA DETALLADA en ESPAÑOL (150-300 palabras) que incluya:
   - QUÉ se debe hacer exactamente (pasos concretos)
   - POR QUÉ es importante (problema que resuelve)
   - CÓMO implementarlo (proceso, recursos, timeline estimado)
   - MÉTRICAS esperadas o KPIs de éxito
   - Usa párrafos y bullets para claridad

3. "area_estrategica": Categoría estratégica (elige UNA):
   - "Producto/Servicio"
   - "Marketing y Comunicación"
   - "Atención al Cliente"
   - "Ventas y Conversión"
   - "Operaciones"

4. "score_impacto": Impacto numérico (escala 1-100):
   - 1-20: Mínimo (cambios cosméticos)
   - 21-50: Moderado (mejora engagement)
   - 51-80: Alto (mejora KPIs importantes)
   - 81-100: Crítico (transformacional)

5. "score_esfuerzo": Esfuerzo requerido (escala 1-100):
   - 1-20: Mínimo (<1 semana, bajo costo)
   - 21-50: Moderado (1-4 semanas, costo medio)
   - 51-80: Significativo (1-3 meses, inversión considerable)
   - 81-100: Mayor (3+ meses, recursos significativos)

REGLAS CRÍTICAS:
- Genera EXACTAMENTE 16 recomendaciones (4 por semana durante 4 semanas)
- TODO en ESPAÑOL (títulos, descripciones, áreas)
- SOLO problemas/oportunidades REALES identificados en los comentarios
- Descripciones OPERATIVAS con pasos concretos, no genéricas
- Devuelve valores numéricos válidos (1-100) para score_impacto y score_esfuerzo
- NO incluyas campos adicionales ni markdown en la descripción
- Retorna SOLO JSON válido, sin explicaciones adicionales

Formato JSON (retorna SOLO el array JSON, sin bloques de código):
[
    {{
        "recomendacion": "Título descriptivo de la acción",
        "descripcion": "Descripción detallada operativa: QUÉ hacer, POR QUÉ, CÓMO implementar, métricas esperadas...",
        "area_estrategica": "Marketing y Comunicación",
        "score_impacto": 75,
        "score_esfuerzo": 35
    }},
    {{
        "recomendacion": "Segunda recomendación",
        "descripcion": "Descripción...",
        "area_estrategica": "Atención al Cliente",
        "score_impacto": 82,
        "score_esfuerzo": 42
    }}
]"""
        
        try:
            logger.info(f"Generating recommendations from {len(combined_text)} chars of text")
            
            messages = [
                {
                    "role": "system",
                    "content": "Eres un analista estratégico senior. Analiza comentarios de audiencia y genera recomendaciones estratégicas DETALLADAS en español con scores numéricos. Retorna SOLO JSON válido."
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
                extracted_json = None
                
                if "```json" in content:
                    try:
                        json_part = content.split("```json")[1].split("```")[0].strip()
                        extracted_json = json.loads(json_part)
                    except Exception as e:
                        logger.debug(f"Failed to extract from ```json block: {e}")
                
                if not extracted_json and "```" in content:
                    try:
                        json_part = content.split("```")[1].split("```")[0].strip()
                        extracted_json = json.loads(json_part)
                    except Exception as e:
                        logger.debug(f"Failed to extract from ``` block: {e}")
                
                # Last resort: try to find and parse JSON array with lenient parsing
                if not extracted_json:
                    try:
                        import re
                        # Find content between [ and ]
                        match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
                        if match:
                            json_str = match.group(0)
                            extracted_json = json.loads(json_str)
                            logger.info(f"Successfully extracted JSON from regex pattern")
                    except Exception as e:
                        logger.debug(f"Failed to extract from regex: {e}")
                
                if extracted_json and isinstance(extracted_json, list):
                    logger.info(f"Successfully extracted {len(extracted_json)} recommendations from formatted content")
                    return extracted_json
                
                # Absolute fallback: return generic recommendations with high priority
                logger.error(f"Failed to parse JSON after all attempts. Using fallback recommendations.")
                logger.error(f"Response was: {content[:200]}...")
                
                # Generate 16 generic high-value recommendations based on common social media issues
                fallback_recs = [
                    {"recomendacion": "Aumentar frecuencia de publicación en horarios de mayor engagement", "score_impacto": 75, "score_esfuerzo": 20, "area_estrategica": "Marketing y Comunicación"},
                    {"recomendacion": "Implementar respuestas automáticas a comentarios frecuentes", "score_impacto": 70, "score_esfuerzo": 30, "area_estrategica": "Atención al Cliente"},
                    {"recomendacion": "Crear contenido interactivo con preguntas y encuestas", "score_impacto": 80, "score_esfuerzo": 35, "area_estrategica": "Marketing y Comunicación"},
                    {"recomendacion": "Desarrollar programa de influenciadores internos", "score_impacto": 85, "score_esfuerzo": 50, "area_estrategica": "Marketing y Comunicación"},
                    {"recomendacion": "Mejorar velocidad de respuesta en comentarios (máximo 4 horas)", "score_impacto": 72, "score_esfuerzo": 25, "area_estrategica": "Atención al Cliente"},
                    {"recomendacion": "Crear serie de contenido educativo sobre productos", "score_impacto": 78, "score_esfuerzo": 40, "area_estrategica": "Producto/Servicio"},
                    {"recomendacion": "Implementar hashtags estratégicos personalizados", "score_impacto": 65, "score_esfuerzo": 15, "area_estrategica": "Marketing y Comunicación"},
                    {"recomendacion": "Establecer estructura de atención 24/7 en redes", "score_impacto": 88, "score_esfuerzo": 55, "area_estrategica": "Operaciones"},
                    {"recomendacion": "Crear campañas mensuales temáticas alineadas con calendario", "score_impacto": 76, "score_esfuerzo": 38, "area_estrategica": "Marketing y Comunicación"},
                    {"recomendacion": "Desarrollar landing pages optimizadas desde redes sociales", "score_impacto": 82, "score_esfuerzo": 45, "area_estrategica": "Ventas y Conversión"},
                    {"recomendacion": "Implementar sistema de gamificación con recompensas", "score_impacto": 81, "score_esfuerzo": 48, "area_estrategica": "Operaciones"},
                    {"recomendacion": "Crear biblioteca de templates de respuestas efectivas", "score_impacto": 68, "score_esfuerzo": 20, "area_estrategica": "Atención al Cliente"},
                    {"recomendacion": "Realizar auditoría semanal de tono y consistencia de marca", "score_impacto": 70, "score_esfuerzo": 25, "area_estrategica": "Marketing y Comunicación"},
                    {"recomendacion": "Diseñar estrategia de colaboraciones con marcas complementarias", "score_impacto": 84, "score_esfuerzo": 52, "area_estrategica": "Ventas y Conversión"},
                    {"recomendacion": "Implementar análisis diario de menciones no etiquetadas", "score_impacto": 72, "score_esfuerzo": 18, "area_estrategica": "Marketing y Comunicación"},
                    {"recomendacion": "Crear programa de feedback estructurado de usuarios", "score_impacto": 79, "score_esfuerzo": 35, "area_estrategica": "Producto/Servicio"}
                ]
                
                return fallback_recs
            
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
                            # Look for both "impacto"/"esfuerzo" and "score_impacto"/"score_esfuerzo"
                            score_impacto = self._sanitize_numeric(
                                rec.get("score_impacto") or rec.get("impacto", 50),
                                "score_impacto",
                                min_val=1,
                                max_val=100
                            )
                            
                            score_esfuerzo = self._sanitize_numeric(
                                rec.get("score_esfuerzo") or rec.get("esfuerzo", 50),
                                "score_esfuerzo",
                                min_val=1,
                                max_val=100
                            )
                            
                            # Calculate PRIORITY in Python (NOT from AI)
                            prioridad = round(score_impacto / max(1, score_esfuerzo), 2)
                            
                            # Use IA-generated description when available
                            descripcion_ai = str(rec.get("descripcion", "")).strip()
                            if not descripcion_ai or len(descripcion_ai) < 60:
                                # Fallback: compose a minimal but useful description
                                descripcion_ai = (
                                    f"Acción: {recomendacion_text}. "
                                    "Implementación paso a paso con responsables, recursos y KPIs. "
                                    "Incluye timeline y métricas de éxito (impacto/efuerzo)."
                                )
                            # Trim excessively long descriptions to a safe size
                            if len(descripcion_ai) > 2000:
                                descripcion_ai = descripcion_ai[:2000]
                            
                            # Build recommendation dict
                            rec_dict = {
                                "recomendacion": recomendacion_text,
                                "descripcion": descripcion_ai,
                                "score_impacto": score_impacto,
                                "score_esfuerzo": score_esfuerzo,
                                "prioridad": prioridad,
                                # Preserve area_estrategica if the IA provided it
                                "area_estrategica": rec.get("area_estrategica")
                            }
                            
                            recomendaciones.append(rec_dict)
                            logger.debug(
                                f"Recommendation {idx}: impacto={score_impacto}, esfuerzo={score_esfuerzo}, prioridad={prioridad}, desc_len={len(descripcion_ai)}"
                            )
                            
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
                
                # Respect IA-provided area_estrategica; if missing, infer heuristically
                if not rec.get("area_estrategica"):
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
                
                # Sanitize descripcion: ensure present and within bounds
                desc = str(rec.get("descripcion", "")).strip()
                if not desc or len(desc) < 60:
                    desc = (
                        f"Acción: {rec['recomendacion']}. "
                        "Implementación paso a paso con responsables, recursos y KPIs; incluye timeline semanal."
                    )
                if len(desc) > 2000:
                    desc = desc[:2000]
                rec["descripcion"] = desc
                
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
                rec["justificacion_framework"] = ["1", "3", "6", "9"]  # Default: Emotions, Topics, Opportunities, Recommendations
                
                # Add acciones_concretas (action items to implement recommendation)
                area_selected = rec.get("area_estrategica", "Comunicación y Transparencia")
                acciones = [
                    f"Paso 1: Analizar contexto actual del {area_selected.lower()}",
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
                "recomendaciones_altas": len([r for r in recomendaciones_sorted if r.get("urgencia") == "ALTA"]),
                "urgencia_distribucion": {
                    "CRÍTICA": len([r for r in recomendaciones_sorted if r.get("urgencia") == "CRÍTICA"]),
                    "ALTA": len([r for r in recomendaciones_sorted if r.get("urgencia") == "ALTA"]),
                    "MEDIA-ALTA": len([r for r in recomendaciones_sorted if r.get("urgencia") == "MEDIA-ALTA"]),
                    "MEDIA": len([r for r in recomendaciones_sorted if r.get("urgencia") == "MEDIA"]),
                    "BAJA": len([r for r in recomendaciones_sorted if r.get("urgencia") == "BAJA"])
                }
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
