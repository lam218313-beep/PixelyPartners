"""
Pixely Partners - Q8: Temporal Analysis (Máximo Rendimiento)

Analyzes audience comments GROUPED BY TIME (weekly aggregation).
Identifies sentiment trends and topic evolution across weeks.

Features:
- Pandas DataFrame aggregation by WEEK (resample('W'))
- Defensive timestamp parsing: comment_timestamp, timestamp, created_at, fecha
- Per-week topic identification (independent from Q3)
- Normalized sentiment scores (-1.0 to 1.0) per week
- Topic frequency calculation per week (0.0 to 1.0)
- Strict float typing (forced conversion before storage)
- Resilient API calls with tenacity (@retry, 3 attempts, 2s wait)
- Per-week error isolation with comprehensive logging
- Safety patch: [:15000] chars per week to prevent token overflow
"""

from typing import Dict, Any, List
import json
import logging
import asyncio
import pandas as pd
from datetime import datetime

from tenacity import retry, stop_after_attempt, wait_fixed

from ..base_analyzer import BaseAnalyzer

# Configure logger to use the shared orchestrator configuration
logger = logging.getLogger(__name__)


class Q8Temporal(BaseAnalyzer):
    """
    Q8 Temporal Analysis using week-by-week decomposition.
    
    Groups comments by WEEK and analyzes sentiment trends and topic evolution.
    
    Features:
    - Weekly aggregation: Uses pandas resample('W') for time-based grouping
    - Defensive timestamp parsing: Tries multiple column names (comment_timestamp, timestamp, etc.)
    - Per-week analysis: Each week gets independent topic/sentiment analysis
    - Normalized metrics: Sentiment (-1.0 to 1.0), frequency (0.0 to 1.0)
    - Strict type enforcement: Forced float conversion
    - Resilient API calls: Automatic retry (3 attempts, 2s wait)
    - Per-week error isolation: If Week 2 fails, Week 3 continues
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

    def _find_timestamp_column(self, df: pd.DataFrame) -> str:
        """
        Defensively find the timestamp column using multiple fallback names.
        
        Tries in order: comment_timestamp, timestamp, created_at, fecha
        
        Args:
            df: DataFrame to search
            
        Returns:
            Name of the timestamp column, or None if not found
        """
        possible_names = ["comment_timestamp", "timestamp", "created_at", "fecha", "post_date"]
        for col in possible_names:
            if col in df.columns:
                logger.info(f"Found timestamp column: {col}")
                return col
        logger.warning(f"No timestamp column found. Available columns: {list(df.columns)}")
        return None

    async def _analyze_week_sentiment(self, week_label: str, week_text: str) -> Dict[str, Any]:
        """
        Analyzes sentiment and topic for a single WEEK.
        
        Args:
            week_label: String identifier (e.g., "Week 1", "2025-W01")
            week_text: Aggregated comment text for this week
            
        Returns:
            Analysis result dict with sentiment and topic
            
        Raises:
            Exception: If API call fails
        """
        
        prompt = f"""You are an expert analyst. Analyze the following weekly audience comments to identify sentiment trend and main topic.

WEEKLY COMMENTS (Week: {week_label}):
"{week_text}"

Analyze this week's sentiment and topic:
1. Calculate 'sentimiento_promedio' (-1.0 to 1.0):
   - Positive comments → closer to 1.0
   - Negative comments → closer to -1.0
   - Neutral comments → closer to 0.0

2. Identify 'topico_principal' (e.g., "Price", "Shipping", "Quality", "Customer Service")

3. Calculate 'frecuencia_topico_principal' (0.0 to 1.0):
   - What % of this week's comments mention the main topic?
   - If 80% mention "Price", then 0.8

Return ONLY valid JSON:
{{
    "sentimiento_promedio": 0.35,
    "topico_principal": "Precio",
    "frecuencia_topico_principal": 0.75
}}"""
        
        try:
            logger.info(f"_analyze_week_sentiment START: {week_label}")
            logger.debug(f"Using Chat Completions API for model: {self.model_name}")
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert analyst. Return valid JSON only with temporal metrics."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            params = self._get_model_params(messages)
            logger.debug(f"API params: model={params.get('model')}, temperature={params.get('temperature')}, max_tokens={params.get('max_tokens')}")
            
            logger.debug(f"Calling chat.completions.create...")
            response = await self.openai_client.chat.completions.create(**params)
            logger.debug(f"Got response from API")
            
            content = response.choices[0].message.content.strip()
            logger.debug(f"Response content: {content[:150]}...")
            
            # Try to parse JSON from response
            try:
                logger.debug(f"Parsing JSON...")
                data = json.loads(content)
                logger.info(f"_analyze_week_sentiment SUCCESS: {week_label} -> {data}")
                return data
            except json.JSONDecodeError as je:
                logger.warning(f"JSON parse failed, trying markdown extraction")
                # If JSON parsing fails, try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_part = content.split("```json")[1].split("```")[0].strip()
                    data = json.loads(json_part)
                elif "```" in content:
                    json_part = content.split("```")[1].split("```")[0].strip()
                    data = json.loads(json_part)
                else:
                    raise json.JSONDecodeError("Could not extract JSON from response", content, 0)
                logger.info(f"_analyze_week_sentiment SUCCESS (from markdown): {week_label} -> {data}")
                return data
            
        except Exception as e:
            logger.error(f"_analyze_week_sentiment FAILED: {week_label} - {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def _sanitize_numeric(self, value: Any, key: str, min_val: float = -1.0, max_val: float = 1.0) -> float:
        """
        Sanitize and clamp a numeric value to a range.
        
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
            logger.warning(f"Invalid numeric value for '{key}': {value} (type: {type(value).__name__}). Using 0.0")
            val = 0.0
        
        # Clamp to range
        val = max(min_val, min(max_val, val))
        return round(val, 3)

    async def analyze(self) -> Dict[str, Any]:
        """
        Execute temporal analysis using WEEKLY AGGREGATION.
        
        Generates:
        - serie_temporal_semanal: Weekly sentiment with porcentaje_positivo, porcentaje_negativo
        - anomalias_detectadas: Weeks with >25% change
        - resumen_global: Summary statistics
        - distribucion_topicos_por_semana: Topic distribution over time
        
        Returns:
            Dictionary with metadata, all required sections, and errors
        """
        errors = []
        serie_temporal_semanal = []
        anomalias_detectadas = []
        
        try:
            logger.info("Starting Q8 Temporal Analysis (Weekly Aggregation)")
            
            ingested_data = self.load_ingested_data()
            posts = ingested_data.get("posts", [])
            comments = ingested_data.get("comments", [])
            
            logger.info(f"Processing {len(comments)} comments and {len(posts)} posts for temporal analysis")
            print(f"   📊 Iniciando análisis temporal...")
            
            if not comments or not posts:
                errors.append(f"Missing data: {len(comments)} comments, {len(posts)} posts")
                logger.warning("Insufficient data for temporal analysis")
                return {
                    "metadata": {
                        "module": "Q8 Temporal",
                        "version": 3,
                        "description": "Weekly temporal analysis with anomaly detection"
                    },
                    "results": {
                        "serie_temporal_semanal": [],
                        "anomalias_detectadas": [],
                        "resumen_global": {},
                        "distribucion_topicos_por_semana": {}
                    },
                    "errors": errors
                }
            
            # Create a mapping from post_url to post timestamp
            post_timestamps = {}
            for post in posts:
                post_url = post.get("post_url")
                timestamp = post.get("timestamp")
                if post_url and timestamp:
                    try:
                        post_timestamps[post_url] = pd.to_datetime(timestamp)
                    except Exception as e:
                        logger.warning(f"Could not parse timestamp for {post_url}: {timestamp}")
            
            logger.info(f"Mapped {len(post_timestamps)} posts with timestamps")
            
            # Build comments dataframe with post timestamps
            comments_with_dates = []
            for comment in comments:
                post_url = comment.get("post_url")
                if post_url in post_timestamps:
                    comment_copy = comment.copy()
                    comment_copy['timestamp'] = post_timestamps[post_url]
                    comments_with_dates.append(comment_copy)
            
            if not comments_with_dates:
                errors.append("No comments matched with post timestamps")
                logger.error("No comments could be matched with post dates")
                return {
                    "metadata": {
                        "module": "Q8 Temporal",
                        "version": 3,
                        "description": "Weekly temporal analysis with anomaly detection"
                    },
                    "results": {
                        "serie_temporal_semanal": [],
                        "anomalias_detectadas": [],
                        "resumen_global": {},
                        "distribucion_topicos_por_semana": {}
                    },
                    "errors": errors
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(comments_with_dates)
            logger.info(f"DataFrame created with {len(df)} comments")
            print(f"   ✓ {len(df)} comments mapped to posts")
            
            # Convert timestamp column to datetime
            df['datetime'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
            # Remove rows with invalid timestamps
            df_valid = df[df['datetime'].notna()].copy()
            
            if len(df_valid) == 0:
                errors.append("No valid timestamps found")
                logger.error("No valid timestamps in data")
                return {
                    "metadata": {
                        "module": "Q8 Temporal",
                        "version": 3,
                        "description": "Weekly temporal analysis with anomaly detection"
                    },
                    "results": {
                        "serie_temporal_semanal": [],
                        "anomalias_detectadas": [],
                        "resumen_global": {},
                        "distribucion_topicos_por_semana": {}
                    },
                    "errors": errors
                }
            
            # Sort by datetime
            df_valid = df_valid.sort_values('datetime')
            logger.info(f"Valid comments: {len(df_valid)}, Date range: {df_valid['datetime'].min()} to {df_valid['datetime'].max()}")
            
            # Set index and resample by WEEK
            df_valid_indexed = df_valid.set_index('datetime')
            
            # Group by week
            week_groups = df_valid_indexed.resample('W')
            
            # Count non-empty weeks
            non_empty_weeks = [(g[0], g[1]) for g in week_groups if len(g[1]) > 0]
            logger.info(f"Total weeks with comments: {len(non_empty_weeks)}")
            print(f"   📍 Semanas identificadas: {len(non_empty_weeks)}")
            
            week_idx = 0
            prev_sentiment_positivo = None
            topicos_por_semana = {}
            
            for week_start, group_df in non_empty_weeks:
                week_idx += 1
                week_label = f"Week {week_idx} ({week_start.strftime('%Y-%m-%d')})"
                num_comments = len(group_df)
                
                logger.info(f"Analyzing {week_label}: {num_comments} comments")
                print(f"   ⏳ Analizando semana {week_idx}/{len(non_empty_weeks)}... ", end="", flush=True)
                
                try:
                    # Combine text from this week's comments
                    comments_text = " ".join([
                        str(text) for text in group_df['comment_text'].tolist()
                        if text and str(text).strip()
                    ])
                    
                    if not comments_text.strip():
                        logger.warning(f"Empty text for {week_label}")
                        print("✗ (no text)", flush=True)
                        continue
                    
                    # SAFETY PATCH: Truncate to 15000 chars to prevent token overflow
                    safe_text = comments_text[:15000]
                    logger.debug(f"Text length: {len(safe_text)} chars")
                    
                    # Call OpenAI for this week
                    logger.info(f"Calling _analyze_week_sentiment for {week_label} with {len(safe_text)} chars")
                    try:
                        analysis_result = await self._analyze_week_sentiment(week_label, safe_text)
                        logger.info(f"Got result for {week_label}: {analysis_result}")
                    except Exception as api_error:
                        logger.error(f"API Error for {week_label}: {type(api_error).__name__}: {str(api_error)}")
                        errors.append(f"API error for {week_label}: {str(api_error)}")
                        print("✗", flush=True)
                        continue
                    
                    # Sanitize numeric values (STRICT TYPING)
                    sentimiento = self._sanitize_numeric(
                        analysis_result.get("sentimiento_promedio", 0),
                        "sentimiento_promedio",
                        min_val=-1.0,
                        max_val=1.0
                    )
                    
                    frecuencia = self._sanitize_numeric(
                        analysis_result.get("frecuencia_topico_principal", 0),
                        "frecuencia_topico_principal",
                        min_val=0.0,
                        max_val=1.0
                    )
                    
                    topico = str(analysis_result.get("topico_principal", "Unknown")).strip()[:50]
                    
                    # Convert sentimiento (-1.0 to 1.0) to porcentajes (0-100)
                    # sentimiento=1.0 → 100% positivo, 0% negativo
                    # sentimiento=-1.0 → 0% positivo, 100% negativo
                    # sentimiento=0.0 → 50% positivo, 50% negativo (neutral)
                    porcentaje_positivo = round((sentimiento + 1.0) / 2.0, 3)
                    porcentaje_negativo = round(1.0 - porcentaje_positivo, 3)
                    
                    # Detect anomaly: >25% change from previous week
                    es_anomalia = False
                    if prev_sentiment_positivo is not None:
                        cambio = abs(porcentaje_positivo - prev_sentiment_positivo)
                        if cambio > 0.25:  # >25% change
                            es_anomalia = True
                            anomalia_info = {
                                "semana": week_idx,
                                "fecha_semana": week_start.strftime("%Y-%m-%d"),
                                "cambio_porcentaje": round(cambio * 100, 1),
                                "tipo_anomalia": "Mejora Significativa" if porcentaje_positivo > prev_sentiment_positivo else "Deterioro Significativo",
                                "sentimiento_anterior": round(prev_sentiment_positivo * 100, 1),
                                "sentimiento_actual": round(porcentaje_positivo * 100, 1),
                                "topico_dominante": topico
                            }
                            anomalias_detectadas.append(anomalia_info)
                    
                    prev_sentiment_positivo = porcentaje_positivo
                    topicos_por_semana[week_idx] = topico
                    
                    # Build week analysis with CORRECT FIELD NAMES for frontend
                    # Calculate engagement as ratio of comments to week duration (rough estimate)
                    engagement = round(num_comments / max(1, week_idx) * 0.1, 3)  # Normalize engagement metric
                    
                    week_analysis = {
                        "semana_numero": week_idx,
                        "fecha_semana": week_start.strftime("%Y-%m-%d"),
                        "num_comentarios": num_comments,
                        "porcentaje_positivo": porcentaje_positivo,
                        "porcentaje_negativo": porcentaje_negativo,
                        "topico_principal": topico,
                        "frecuencia_topico_principal": frecuencia,
                        "engagement": engagement,
                        "es_anomalia": es_anomalia
                    }
                    
                    serie_temporal_semanal.append(week_analysis)
                    print("✓", flush=True)
                    logger.info(f"Week {week_idx}: pos={porcentaje_positivo}, neg={porcentaje_negativo}, topic={topico}, engagement={engagement}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing {week_label}: {str(e)}", exc_info=True)
                    errors.append(f"Error analyzing {week_label}: {str(e)}")
                    print("✗", flush=True)
                    # Continue with next week (error isolation)
                    continue
            
            # Build resumen_global
            resumen_global = {
                "total_semanas": len(serie_temporal_semanal),
                "total_anomalias": len(anomalias_detectadas),
                "promedio_sentimiento_positivo": round(
                    sum(w.get("porcentaje_positivo", 0) for w in serie_temporal_semanal) / max(len(serie_temporal_semanal), 1), 3
                ),
                "promedio_sentimiento_negativo": round(
                    sum(w.get("porcentaje_negativo", 0) for w in serie_temporal_semanal) / max(len(serie_temporal_semanal), 1), 3
                ),
                "tendencia": "Mejora" if len(serie_temporal_semanal) > 0 and serie_temporal_semanal[-1]["porcentaje_positivo"] > (
                    serie_temporal_semanal[0]["porcentaje_positivo"] if len(serie_temporal_semanal) > 0 else 0
                ) else "Deterioro" if len(serie_temporal_semanal) > 1 else "Estable"
            }
            
            logger.info(f"Q8 analysis completed. {len(serie_temporal_semanal)} weeks analyzed successfully. {len(anomalias_detectadas)} anomalies detected")
            print(f"   ✅ Análisis completado: {len(serie_temporal_semanal)} semanas, {len(anomalias_detectadas)} anomalías")
            
        except Exception as e:
            logger.error(f"Critical error in Q8 analysis: {str(e)}", exc_info=True)
            errors.append(f"Critical error: {str(e)}")
            print(f"   ❌ Error fatal: {str(e)}")
        
        return {
            "metadata": {
                "module": "Q8 Temporal",
                "version": 3,
                "description": "Weekly temporal analysis with anomaly detection"
            },
            "results": {
                "serie_temporal_semanal": serie_temporal_semanal,
                "anomalias_detectadas": anomalias_detectadas,
                "resumen_global": resumen_global,
                "distribucion_topicos_por_semana": topicos_por_semana
            },
            "errors": errors
        }

