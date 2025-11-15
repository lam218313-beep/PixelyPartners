"""
Pixely Partners - Q10: Executive Summary with Strategic Roadmap

Synthesizes Q1-Q9 analysis into executive dashboard with:
- Critical alert identification
- Key findings (5-7 main insights)
- Strategic implications
- General summary
- Key metrics (KPIs)
- Action roadmap by urgency level
"""

from typing import Dict, Any, List
import json
import logging
import os
from pathlib import Path

from ..base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class Q10ResumenEjecutivo(BaseAnalyzer):
    """
    Executive Summary that synthesizes Q1-Q9 analysis into strategic dashboard.
    
    Generates:
    - alerta_prioritaria: Most critical finding in red
    - hallazgos_clave: 5-7 key insights with context
    - implicaciones_estrategicas: Strategic business implications
    - resumen_general: Overall executive summary (3-5 sentences)
    - kpis_principales: Key metrics from Q1-Q9
    - urgencias_por_prioridad: Action items grouped by timeline
    """
    
    def _load_q_results(self, q_number: int) -> Dict[str, Any]:
        """
        Load previous Q results from JSON file.
        
        Args:
            q_number: Question number (1-9)
            
        Returns:
            Results dict or empty dict if not found
        """
        try:
            outputs_dir = self.load_ingested_data_path.parent
            json_file = outputs_dir / f"q{q_number}_*.json"
            
            # Try exact match
            exact_file = None
            for pattern in [f"q{q_number}_*.json", f"q{q_number}.json"]:
                candidates = list(Path(outputs_dir).glob(pattern))
                if candidates:
                    exact_file = candidates[0]
                    break
            
            if not exact_file or not exact_file.exists():
                logger.warning(f"Q{q_number} file not found in {outputs_dir}")
                return {}
            
            with open(exact_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("results", {})
        except Exception as e:
            logger.warning(f"Error loading Q{q_number}: {str(e)}")
            return {}
    
    def _extract_kpis(self) -> Dict[str, Any]:
        """Extract KPIs from Q1-Q9 results."""
        kpis = {}
        
        try:
            # Q1 - Emociones
            q1 = self._load_q_results(1)
            if q1:
                emocion_dominante = q1.get("emocion_dominante", {})
                if emocion_dominante:
                    kpis["emocion_dominante"] = emocion_dominante.get("emocion", "N/A")
                    kpis["emocion_porcentaje"] = round(emocion_dominante.get("porcentaje", 0) * 100, 1)
            
            # Q2 - Personalidad
            q2 = self._load_q_results(2)
            if q2:
                personalidad = q2.get("personalidad_dominante", {})
                if personalidad:
                    kpis["personalidad_marca"] = personalidad.get("tipo", "N/A")
            
            # Q7 - Sentimiento
            q7 = self._load_q_results(7)
            if q7:
                agg = q7.get("analisis_agregado", {})
                if agg:
                    kpis["sentimiento_positivo_pct"] = round(agg.get("Positivo", 0) * 100, 1)
                    kpis["sentimiento_negativo_pct"] = round(agg.get("Negativo", 0) * 100, 1)
                    kpis["ambivalencia_pct"] = round(agg.get("Mixto", 0) * 100, 1)
            
            # Q8 - Temporal
            q8 = self._load_q_results(8)
            if q8:
                resumen = q8.get("resumen_global", {})
                if resumen:
                    kpis["tendencia_temporal"] = resumen.get("tendencia", "Estable")
                    kpis["anomalias_detectadas"] = resumen.get("total_anomalias", 0)
            
            # Q3 - Temas
            q3 = self._load_q_results(3)
            if q3:
                temas = q3.get("temas_principales", [])
                if temas and len(temas) > 0:
                    kpis["tema_principal"] = temas[0].get("tema", "N/A")
            
            # Q5 - Influenciadores
            q5 = self._load_q_results(5)
            if q5:
                influenciadores = q5.get("influenciadores_principales", [])
                if influenciadores:
                    kpis["influenciadores_identificados"] = len(influenciadores)
            
            # Q6 - Oportunidades
            q6 = self._load_q_results(6)
            if q6:
                oportunidades = q6.get("oportunidades", [])
                if oportunidades:
                    kpis["oportunidades_identifi cadas"] = len(oportunidades)
            
            # Q9 - Recomendaciones
            q9 = self._load_q_results(9)
            if q9:
                resumen_q9 = q9.get("resumen_global", {})
                if resumen_q9:
                    kpis["recomendaciones_criticas"] = resumen_q9.get("recomendaciones_criticas", 0)
                    kpis["recomendaciones_altas"] = resumen_q9.get("recomendaciones_altas", 0)
        
        except Exception as e:
            logger.error(f"Error extracting KPIs: {str(e)}")
        
        return kpis
    
    def _generate_hallazgos_clave(self) -> List[str]:
        """Generate 5-7 key findings from Q1-Q9."""
        hallazgos = []
        
        try:
            # Load all Q results
            q1 = self._load_q_results(1)
            q2 = self._load_q_results(2)
            q3 = self._load_q_results(3)
            q5 = self._load_q_results(5)
            q6 = self._load_q_results(6)
            q7 = self._load_q_results(7)
            q8 = self._load_q_results(8)
            q9 = self._load_q_results(9)
            
            # Hallazgo 1: Emoción dominante
            if q1:
                emocion = q1.get("emocion_dominante", {})
                if emocion:
                    hallazgos.append(
                        f"La emoción dominante es {emocion.get('emocion', 'N/A')} ({round(emocion.get('porcentaje', 0)*100, 0):.0f}%), "
                        f"indicando que la audiencia es principalmente {emocion.get('descripcion', 'engaged')}"
                    )
            
            # Hallazgo 2: Tema principal
            if q3:
                temas = q3.get("temas_principales", [])
                if temas and len(temas) > 0:
                    hallazgos.append(
                        f"El tema más discutido es '{temas[0].get('tema', 'N/A')}', "
                        f"presente en {round(temas[0].get('porcentaje', 0)*100, 0):.0f}% de la conversación"
                    )
            
            # Hallazgo 3: Sentimiento
            if q7:
                agg = q7.get("analisis_agregado", {})
                if agg:
                    pos = round(agg.get("Positivo", 0)*100, 0)
                    neg = round(agg.get("Negativo", 0)*100, 0)
                    hallazgos.append(
                        f"El sentimiento es {pos:.0f}% positivo vs {neg:.0f}% negativo, "
                        f"con {round(agg.get('Mixto', 0)*100, 0):.0f}% ambivalencia (posible confusión en mensajería)"
                    )
            
            # Hallazgo 4: Oportunidades
            if q6:
                opors = q6.get("oportunidades", [])
                if opors:
                    hallazgos.append(
                        f"Se identificaron {len(opors)} oportunidades de mercado, "
                        f"con demanda insatisfecha en: {', '.join([o.get('oportunidad', 'N/A')[:30] for o in opors[:2]])}"
                    )
            
            # Hallazgo 5: Influenciadores
            if q5:
                infs = q5.get("influenciadores_principales", [])
                if infs:
                    hallazgos.append(
                        f"Los influenciadores clave son: {', '.join([i.get('usuario', 'N/A')[:20] for i in infs[:2]])}, "
                        f"con potencial de amplificación"
                    )
            
            # Hallazgo 6: Tendencia temporal
            if q8:
                res = q8.get("resumen_global", {})
                if res:
                    tendencia = res.get("tendencia", "Estable")
                    anomalias = res.get("total_anomalias", 0)
                    hallazgos.append(
                        f"La tendencia temporal es {tendencia}, con {anomalias} anomalías significativas detectadas "
                        f"(cambios >25% semana a semana)"
                    )
            
            # Hallazgo 7: Recomendaciones críticas
            if q9:
                res = q9.get("resumen_global", {})
                if res:
                    criticas = res.get("recomendaciones_criticas", 0)
                    if criticas > 0:
                        hallazgos.append(
                            f"Se identificaron {criticas} recomendación(es) CRÍTICA(S) que requieren "
                            f"acción inmediata en los próximos 48 horas"
                        )
        
        except Exception as e:
            logger.error(f"Error generating hallazgos: {str(e)}")
        
        # Ensure at least 5 hallazgos
        while len(hallazgos) < 5:
            hallazgos.append("Análisis en progreso.")
        
        return hallazgos[:7]
    
    def _generate_implicaciones_estrategicas(self) -> str:
        """Generate strategic business implications."""
        try:
            q7 = self._load_q_results(7)
            q6 = self._load_q_results(6)
            q8 = self._load_q_results(8)
            q9 = self._load_q_results(9)
            
            implications = []
            
            # Implicación 1: Sentimiento → Product/Marketing
            if q7:
                agg = q7.get("analisis_agregado", {})
                pos = agg.get("Positivo", 0)
                mixto = agg.get("Mixto", 0)
                
                if pos > 0.7:
                    implications.append(
                        "OPORTUNIDAD: Alto sentimiento positivo indica buena salud de marca. "
                        "Enfoque: Amplificar mensajes, expandir audiencia, monetizar advocacy."
                    )
                elif mixto > 0.3:
                    implications.append(
                        "RIESGO: Alta ambivalencia sugiere confusión en mensajería o producto. "
                        "Enfoque: Clarificar posicionamiento, auditar experiencia de cliente, comunicación transparente."
                    )
            
            # Implicación 2: Oportunidades → Roadmap
            if q6:
                opors = q6.get("oportunidades", [])
                if opors:
                    implications.append(
                        f"ESTRATEGIA DE CRECIMIENTO: {len(opors)} oportunidades de mercado identificadas. "
                        "Recomendación: Priorizar 2-3 para próximo trimestre con validación de mercado."
                    )
            
            # Implicación 3: Anomalías temporales → Eventos
            if q8:
                resumen = q8.get("resumen_global", {})
                anomalias = resumen.get("total_anomalias", 0)
                if anomalias > 2:
                    implications.append(
                        f"INESTABILIDAD: {anomalias} cambios abruptos detectados. "
                        "Investigar: ¿eventos externos?, ¿problemas de producto?, ¿crisis de PR?"
                    )
            
            # Implicación 4: Recomendaciones → Acción
            if q9:
                lista = q9.get("lista_recomendaciones", [])
                criticas = [r for r in lista if r.get("urgencia") == "CRÍTICA"]
                if criticas:
                    implications.append(
                        f"ACCIÓN INMEDIATA REQUERIDA: {len(criticas)} recomendación(es) crítica(s). "
                        f"Timeline: Implementar en 48h-1 semana máximo."
                    )
            
            # Implicación 5: Viabilidad general
            implications.append(
                "VIABILIDAD: Basado en análisis de Q1-Q9, hay POTENCIAL DE CRECIMIENTO pero requiere "
                "EJECUCIÓN DISCIPLINADA de recomendaciones priorizadas."
            )
            
            return " ".join(implications) if implications else "Análisis de implicaciones en progreso."
        
        except Exception as e:
            logger.error(f"Error generating implications: {str(e)}")
            return "Error al generar implicaciones estratégicas."
    
    def _generate_urgencias_por_prioridad(self) -> Dict[str, List[str]]:
        """Generate action items grouped by urgency/timeline."""
        urgencias = {
            "48_horas": [],
            "semana_1": [],
            "semanas_2_3": [],
            "no_urgente": []
        }
        
        try:
            q9 = self._load_q_results(9)
            if q9:
                recs = q9.get("lista_recomendaciones", [])
                
                for rec in recs:
                    texto = rec.get("recomendacion", "")[:100]
                    urgencia = rec.get("urgencia", "MEDIA")
                    
                    if urgencia == "CRÍTICA":
                        urgencias["48_horas"].append(f"🔴 {texto}")
                    elif urgencia == "ALTA":
                        urgencias["semana_1"].append(f"🟠 {texto}")
                    elif urgencia == "MEDIA-ALTA" or urgencia == "MEDIA":
                        urgencias["semanas_2_3"].append(f"🟡 {texto}")
                    else:
                        urgencias["no_urgente"].append(f"🟢 {texto}")
        
        except Exception as e:
            logger.error(f"Error generating urgencias: {str(e)}")
        
        return urgencias
    
    async def analyze(self) -> Dict[str, Any]:
        """
        Execute executive summary synthesis from Q1-Q9.
        
        Returns:
            Dictionary with complete executive dashboard
        """
        errors = []
        
        try:
            logger.info("Starting Q10 Executive Summary synthesis")
            print("   📊 Generando resumen ejecutivo...")
            
            # Extract all KPIs
            kpis_principales = self._extract_kpis()
            logger.info(f"Extracted {len(kpis_principales)} KPIs")
            print(f"   ✓ KPIs extraídos: {len(kpis_principales)}")
            
            # Generate hallazgos
            hallazgos_clave = self._generate_hallazgos_clave()
            logger.info(f"Generated {len(hallazgos_clave)} key findings")
            print(f"   ✓ {len(hallazgos_clave)} hallazgos clave generados")
            
            # Generate strategic implications
            implicaciones = self._generate_implicaciones_estrategicas()
            logger.info("Generated strategic implications")
            print("   ✓ Implicaciones estratégicas generadas")
            
            # Generate urgency roadmap
            urgencias = self._generate_urgencias_por_prioridad()
            logger.info(f"Generated {len(urgencias)} urgency categories")
            print(f"   ✓ Roadmap de urgencias generado")
            
            # Determine alert (first hallazgo critical)
            alerta = hallazgos_clave[0] if hallazgos_clave else "Estado de análisis pendiente"
            
            # Generate general summary
            tendencia = kpis_principales.get("tendencia_temporal", "Estable")
            tendencia_text = "Mejora Esperada" if tendencia == "Mejora" else "Monitoreo Requerido"
            emocion = kpis_principales.get("emocion_dominante", "N/A")
            sentimiento_pct = kpis_principales.get("sentimiento_positivo_pct", 0)
            
            resumen_general = (
                f"Análisis integral de Q1-Q9 completado. "
                f"Se identificaron {len(hallazgos_clave)} hallazgos clave con {len(urgencias.get('48_horas', []))} "
                f"acciones críticas para ejecutar en 48 horas. "
                f"Tendencia general: {tendencia_text}. "
                f"KPI Principal: {emocion} con {sentimiento_pct}% sentimiento positivo."
            )
            
            logger.info("Q10 executive summary synthesis completed")
            print("   ✅ Resumen ejecutivo completado")
            
        except Exception as e:
            logger.error(f"Critical error in Q10 analysis: {str(e)}", exc_info=True)
            errors.append(f"Critical error: {str(e)}")
            print(f"   ❌ Error fatal: {str(e)}")
        
        return {
            "metadata": {
                "module": "Q10 Resumen Ejecutivo",
                "version": 2,
                "description": "Executive summary synthesizing Q1-Q9 analysis with strategic roadmap"
            },
            "results": {
                "alerta_prioritaria": alerta,
                "hallazgos_clave": hallazgos_clave,
                "implicaciones_estrategicas": implicaciones,
                "resumen_general": resumen_general,
                "kpis_principales": kpis_principales,
                "urgencias_por_prioridad": urgencias
            },
            "errors": errors
        }

