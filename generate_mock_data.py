#!/usr/bin/env python3
"""
Generate realistic mock data for all Q1-Q10 JSON files
Used for frontend testing before orchestrator analysis implementation
"""
import json
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "orchestrator" / "outputs"

# ============================================================================
# Q1 - EMOCIONES (Plutchik Model)
# ============================================================================
Q1_DATA = {
    "metadata": {
        "module": "Q1 Emociones",
        "version": 1,
        "description": "Emotional analysis of audience using Plutchik model"
    },
    "results": {
        "resumen_global_emociones": {
            "alegria": 0.68,
            "confianza": 0.72,
            "sorpresa": 0.45,
            "anticipacion": 0.58,
            "miedo": 0.18,
            "disgusto": 0.14,
            "ira": 0.12,
            "tristeza": 0.25
        },
        "analisis_por_publicacion": [
            {
                "post_url": "https://instagram.com/p/producto-nuevo-2024/",
                "emociones": {
                    "alegria": 0.85,
                    "confianza": 0.78,
                    "sorpresa": 0.72,
                    "anticipacion": 0.68,
                    "miedo": 0.05,
                    "disgusto": 0.03,
                    "ira": 0.02,
                    "tristeza": 0.08
                },
                "resumen_emocional": "Post genera emociones muy positivas: la audiencia expresa entusiasmo, confianza en el producto nuevo y anticipación por sus beneficios.",
                "sentimiento_dominante": "Positivo"
            },
            {
                "post_url": "https://instagram.com/p/oferta-especial-nov/",
                "emociones": {
                    "alegria": 0.82,
                    "confianza": 0.68,
                    "sorpresa": 0.65,
                    "anticipacion": 0.75,
                    "miedo": 0.08,
                    "disgusto": 0.05,
                    "ira": 0.03,
                    "tristeza": 0.12
                },
                "resumen_emocional": "Las ofertas generan sorpresa positiva y anticipación. Audiencia expresa alegría pero con algo de preocupación por disponibilidad limitada.",
                "sentimiento_dominante": "Positivo"
            },
            {
                "post_url": "https://instagram.com/p/servicio-al-cliente/",
                "emociones": {
                    "alegria": 0.55,
                    "confianza": 0.62,
                    "sorpresa": 0.35,
                    "anticipacion": 0.42,
                    "miedo": 0.22,
                    "disgusto": 0.18,
                    "ira": 0.25,
                    "tristeza": 0.35
                },
                "resumen_emocional": "Post sobre servicio al cliente genera reacciones mixtas: algunos expresan confianza, pero otros muestran frustración y enojo por respuestas lentas.",
                "sentimiento_dominante": "Neutral/Mixto"
            },
            {
                "post_url": "https://instagram.com/p/problema-producto-reportado/",
                "emociones": {
                    "alegria": 0.25,
                    "confianza": 0.35,
                    "sorpresa": 0.48,
                    "anticipacion": 0.32,
                    "miedo": 0.42,
                    "disgusto": 0.38,
                    "ira": 0.52,
                    "tristeza": 0.45
                },
                "resumen_emocional": "Post negativo: audiencia expresa ira por defectos del producto, disgusto por falta de solución rápida, y miedo a repetir la experiencia negativa.",
                "sentimiento_dominante": "Negativo"
            },
            {
                "post_url": "https://instagram.com/p/sustentabilidad-iniciativa/",
                "emociones": {
                    "alegria": 0.72,
                    "confianza": 0.78,
                    "sorpresa": 0.58,
                    "anticipacion": 0.68,
                    "miedo": 0.12,
                    "disgusto": 0.08,
                    "ira": 0.05,
                    "tristeza": 0.15
                },
                "resumen_emocional": "Post sobre iniciativas de sostenibilidad genera alegría y confianza. Audiencia aprecia el compromiso ambiental de la marca.",
                "sentimiento_dominante": "Positivo"
            },
            {
                "post_url": "https://instagram.com/p/evento-comunitario/",
                "emociones": {
                    "alegria": 0.88,
                    "confianza": 0.82,
                    "sorpresa": 0.62,
                    "anticipacion": 0.75,
                    "miedo": 0.02,
                    "disgusto": 0.01,
                    "ira": 0.01,
                    "tristeza": 0.05
                },
                "resumen_emocional": "Evento comunitario genera máxima alegría y entusiasmo. Audiencia expresa confianza en la marca y anticipación por futuras actividades.",
                "sentimiento_dominante": "Muy Positivo"
            },
            {
                "post_url": "https://instagram.com/p/cambio-precio-upd/",
                "emociones": {
                    "alegria": 0.35,
                    "confianza": 0.42,
                    "sorpresa": 0.78,
                    "anticipacion": 0.38,
                    "miedo": 0.35,
                    "disgusto": 0.28,
                    "ira": 0.32,
                    "tristeza": 0.38
                },
                "resumen_emocional": "Anuncio de cambio de precio genera sorpresa negativa. Audiencia muestra miedo, disgusto y enojo por la decisión.",
                "sentimiento_dominante": "Negativo"
            },
            {
                "post_url": "https://instagram.com/p/testimonio-cliente-exito/",
                "emociones": {
                    "alegria": 0.82,
                    "confianza": 0.88,
                    "sorpresa": 0.55,
                    "anticipacion": 0.62,
                    "miedo": 0.08,
                    "disgusto": 0.04,
                    "ira": 0.02,
                    "tristeza": 0.10
                },
                "resumen_emocional": "Testimonio positivo de cliente genera alegría y confianza elevada. Audiencia se siente inspirada por el éxito del cliente.",
                "sentimiento_dominante": "Muy Positivo"
            }
        ]
    },
    "errors": []
}

# ============================================================================
# Q2 - PERSONALIDAD (Aaker Framework)
# ============================================================================
Q2_DATA = {
    "metadata": {
        "module": "Q2 Personalidad de Marca",
        "version": 1,
        "description": "Brand personality analysis using Aaker framework (5 dimensions)"
    },
    "results": {
        "resumen_global_personalidad": {
            "sinceridad": 0.68,
            "emocion": 0.72,
            "competencia": 0.74,
            "sofisticacion": 0.62,
            "rudeza": 0.52
        },
        "analisis_por_publicacion": [
            {
                "post_url": "https://instagram.com/p/producto-nuevo-2024/",
                "rasgos_aaker": {
                    "sinceridad": 0.78,
                    "emocion": 0.82,
                    "competencia": 0.88,
                    "sofisticacion": 0.65,
                    "rudeza": 0.35
                },
                "resumen": "Marca presentada como innovadora y confiable. Audiencia percibe competencia técnica y emoción genuina.",
                "tono_percibido": "Profesional y accesible"
            },
            {
                "post_url": "https://instagram.com/p/oferta-especial-nov/",
                "rasgos_aaker": {
                    "sinceridad": 0.72,
                    "emocion": 0.88,
                    "competencia": 0.68,
                    "sofisticacion": 0.48,
                    "rudeza": 0.42
                },
                "resumen": "Marca proyecta emoción y entusiasmo en la oferta. Menos énfasis en sofisticación. Enfoque en conexión emocional.",
                "tono_percibido": "Cercana y amigable"
            },
            {
                "post_url": "https://instagram.com/p/servicio-al-cliente/",
                "rasgos_aaker": {
                    "sinceridad": 0.82,
                    "emocion": 0.62,
                    "competencia": 0.58,
                    "sofisticacion": 0.55,
                    "rudeza": 0.68
                },
                "resumen": "Audiencia percibe sinceridad en respuestas de SAC. Pero competencia cuestionada. Algunos comentarios ásperos.",
                "tono_percibido": "Intento honesto pero con fricciones"
            },
            {
                "post_url": "https://instagram.com/p/problema-producto-reportado/",
                "rasgos_aaker": {
                    "sinceridad": 0.58,
                    "emocion": 0.38,
                    "competencia": 0.32,
                    "sofisticacion": 0.28,
                    "rudeza": 0.85
                },
                "resumen": "Crisis de reputación. Audiencia cuestiona sinceridad. Competencia severamente dañada. Tono muy áspero.",
                "tono_percibido": "Defensiva y sin control"
            },
            {
                "post_url": "https://instagram.com/p/sustentabilidad-iniciativa/",
                "rasgos_aaker": {
                    "sinceridad": 0.85,
                    "emocion": 0.78,
                    "competencia": 0.82,
                    "sofisticacion": 0.75,
                    "rudeza": 0.28
                },
                "resumen": "Marca presentada como sincera, sofisticada y comprometida. Audiencia ve competencia y valores alineados.",
                "tono_percibido": "Líder responsable y visionario"
            },
            {
                "post_url": "https://instagram.com/p/evento-comunitario/",
                "rasgos_aaker": {
                    "sinceridad": 0.88,
                    "emocion": 0.92,
                    "competencia": 0.75,
                    "sofisticacion": 0.68,
                    "rudeza": 0.18
                },
                "resumen": "Pico de conexión emocional y sinceridad. Marca vista como genuina y de corazón.",
                "tono_percibido": "Auténtica y generosa"
            },
            {
                "post_url": "https://instagram.com/p/cambio-precio-upd/",
                "rasgos_aaker": {
                    "sinceridad": 0.45,
                    "emocion": 0.35,
                    "competencia": 0.52,
                    "sofisticacion": 0.42,
                    "rudeza": 0.72
                },
                "resumen": "Cambio de precio daña percepción de sinceridad. Audiencia ve falta de empatía.",
                "tono_percibido": "Oportunista y desconectada"
            },
            {
                "post_url": "https://instagram.com/p/testimonio-cliente-exito/",
                "rasgos_aaker": {
                    "sinceridad": 0.82,
                    "emocion": 0.85,
                    "competencia": 0.88,
                    "sofisticacion": 0.72,
                    "rudeza": 0.25
                },
                "resumen": "Testimonio restaura confianza y sinceridad. Marca proyecta competencia e emoción auténtica.",
                "tono_percibido": "Confiable y ganadora"
            }
        ]
    },
    "errors": []
}

# ============================================================================
# Q3 - TOPICOS (Topic Modeling)
# ============================================================================
Q3_DATA = {
    "metadata": {
        "module": "Q3 Tópicos",
        "version": 1,
        "description": "Topic modeling and analysis of audience conversations"
    },
    "results": {
        "topicos_principales": [
            {"nombre": "Producto", "frecuencia": 0.35, "sentimiento_promedio": 0.62},
            {"nombre": "Experiencia de Compra", "frecuencia": 0.28, "sentimiento_promedio": 0.58},
            {"nombre": "Servicio al Cliente", "frecuencia": 0.18, "sentimiento_promedio": 0.48},
            {"nombre": "Sostenibilidad", "frecuencia": 0.12, "sentimiento_promedio": 0.75},
            {"nombre": "Precio/Valor", "frecuencia": 0.07, "sentimiento_promedio": 0.42}
        ],
        "analisis_por_publicacion": [
            {
                "post_url": "https://instagram.com/p/producto-nuevo-2024/",
                "topicos": {
                    "Producto": 0.65,
                    "Experiencia de Compra": 0.22,
                    "Servicio al Cliente": 0.08,
                    "Sostenibilidad": 0.04,
                    "Precio/Valor": 0.01
                },
                "sentimiento": 0.78,
                "resumen": "Conversación enfocada en características del nuevo producto. Sentimiento muy positivo."
            },
            {
                "post_url": "https://instagram.com/p/oferta-especial-nov/",
                "topicos": {
                    "Producto": 0.32,
                    "Experiencia de Compra": 0.48,
                    "Servicio al Cliente": 0.12,
                    "Sostenibilidad": 0.02,
                    "Precio/Valor": 0.06
                },
                "sentimiento": 0.72,
                "resumen": "Énfasis en proceso de compra y disponibilidad. Buen sentimiento general."
            },
            {
                "post_url": "https://instagram.com/p/servicio-al-cliente/",
                "topicos": {
                    "Producto": 0.18,
                    "Experiencia de Compra": 0.15,
                    "Servicio al Cliente": 0.62,
                    "Sostenibilidad": 0.01,
                    "Precio/Valor": 0.04
                },
                "sentimiento": 0.52,
                "resumen": "Mayoría de comentarios sobre calidad del SAC. Sentimiento mixto."
            },
            {
                "post_url": "https://instagram.com/p/problema-producto-reportado/",
                "topicos": {
                    "Producto": 0.52,
                    "Experiencia de Compra": 0.22,
                    "Servicio al Cliente": 0.18,
                    "Sostenibilidad": 0.01,
                    "Precio/Valor": 0.07
                },
                "sentimiento": 0.28,
                "resumen": "Discusión crítica sobre defectos del producto. Sentimiento negativo."
            },
            {
                "post_url": "https://instagram.com/p/sustentabilidad-iniciativa/",
                "topicos": {
                    "Producto": 0.15,
                    "Experiencia de Compra": 0.08,
                    "Servicio al Cliente": 0.02,
                    "Sostenibilidad": 0.72,
                    "Precio/Valor": 0.03
                },
                "sentimiento": 0.82,
                "resumen": "Conversación enfocada en compromiso ambiental. Muy positivo."
            },
            {
                "post_url": "https://instagram.com/p/evento-comunitario/",
                "topicos": {
                    "Producto": 0.28,
                    "Experiencia de Compra": 0.35,
                    "Servicio al Cliente": 0.12,
                    "Sostenibilidad": 0.18,
                    "Precio/Valor": 0.07
                },
                "sentimiento": 0.88,
                "resumen": "Experiencia positiva del evento. Mezcla de tópicos. Sentimiento muy positivo."
            },
            {
                "post_url": "https://instagram.com/p/cambio-precio-upd/",
                "topicos": {
                    "Producto": 0.18,
                    "Experiencia de Compra": 0.25,
                    "Servicio al Cliente": 0.08,
                    "Sostenibilidad": 0.01,
                    "Precio/Valor": 0.48
                },
                "sentimiento": 0.35,
                "resumen": "Críticas sobre cambio de precio. Poco sentimiento positivo."
            },
            {
                "post_url": "https://instagram.com/p/testimonio-cliente-exito/",
                "topicos": {
                    "Producto": 0.48,
                    "Experiencia de Compra": 0.28,
                    "Servicio al Cliente": 0.15,
                    "Sostenibilidad": 0.05,
                    "Precio/Valor": 0.04
                },
                "sentimiento": 0.85,
                "resumen": "Testimonio positivo enfocado en producto y resultados. Muy positivo."
            }
        ]
    },
    "errors": []
}

# ============================================================================
# Q4 - MARCOS NARRATIVOS (Narrative Frames - Entman Theory)
# ============================================================================
Q4_DATA = {
    "metadata": {
        "module": "Q4 Marcos Narrativos",
        "version": 1,
        "description": "Narrative framing analysis using Entman theory"
    },
    "results": {
        "analisis_agregado": {
            "Positivo": 0.55,
            "Negativo": 0.22,
            "Aspiracional": 0.18,
            "Neutral": 0.05
        },
        "marcos_principales": [
            {"nombre": "Positivo", "descripcion": "Frames que enfatizan beneficios y éxito", "prevalencia": 0.55},
            {"nombre": "Negativo", "descripcion": "Frames que critican problemas o limitaciones", "prevalencia": 0.22},
            {"nombre": "Aspiracional", "descripcion": "Frames que inspiran cambio positivo", "prevalencia": 0.18},
            {"nombre": "Neutral", "descripcion": "Frames informativos sin posicionamiento", "prevalencia": 0.05}
        ],
        "analisis_por_publicacion": [
            {
                "post_url": "https://instagram.com/p/producto-nuevo-2024/",
                "marcos_narrativos": {
                    "Positivo": 0.72,
                    "Negativo": 0.08,
                    "Aspiracional": 0.15,
                    "Neutral": 0.05
                },
                "marco_dominante": "Positivo",
                "ejemplos_narrativos": [
                    "Este nuevo producto es revolucionario para la industria",
                    "Finalmente tenemos la solución que esperábamos",
                    "La innovación que todos necesitábamos"
                ]
            },
            {
                "post_url": "https://instagram.com/p/oferta-especial-nov/",
                "marcos_narrativos": {
                    "Positivo": 0.62,
                    "Negativo": 0.12,
                    "Aspiracional": 0.20,
                    "Neutral": 0.06
                },
                "marco_dominante": "Positivo",
                "ejemplos_narrativos": [
                    "Oportunidad que no debo perder",
                    "Acceso a calidad a mejor precio",
                    "Momento perfecto para probar el producto"
                ]
            },
            {
                "post_url": "https://instagram.com/p/servicio-al-cliente/",
                "marcos_narrativos": {
                    "Positivo": 0.42,
                    "Negativo": 0.38,
                    "Aspiracional": 0.12,
                    "Neutral": 0.08
                },
                "marco_dominante": "Mixto",
                "ejemplos_narrativos": [
                    "Intenta ayudar pero es lento",
                    "Respuestas genéricas sin soluciones reales",
                    "Así no es cómo debe funcionar el servicio"
                ]
            },
            {
                "post_url": "https://instagram.com/p/problema-producto-reportado/",
                "marcos_narrativos": {
                    "Positivo": 0.15,
                    "Negativo": 0.72,
                    "Aspiracional": 0.08,
                    "Neutral": 0.05
                },
                "marco_dominante": "Negativo",
                "ejemplos_narrativos": [
                    "Producto defectuoso que no funciona como promete",
                    "Marca que no se hace responsable por errores",
                    "Decepcionar de manera sistemática"
                ]
            },
            {
                "post_url": "https://instagram.com/p/sustentabilidad-iniciativa/",
                "marcos_narrativos": {
                    "Positivo": 0.48,
                    "Negativo": 0.05,
                    "Aspiracional": 0.42,
                    "Neutral": 0.05
                },
                "marco_dominante": "Aspiracional",
                "ejemplos_narrativos": [
                    "Marca que construye un futuro más sostenible",
                    "Liderazgo en responsabilidad ambiental",
                    "Inspiración para cambio positivo en la industria"
                ]
            },
            {
                "post_url": "https://instagram.com/p/evento-comunitario/",
                "marcos_narrativos": {
                    "Positivo": 0.68,
                    "Negativo": 0.02,
                    "Aspiracional": 0.25,
                    "Neutral": 0.05
                },
                "marco_dominante": "Positivo + Aspiracional",
                "ejemplos_narrativos": [
                    "Marca que se conecta genuinamente con su comunidad",
                    "Humanidad corporativa en acción",
                    "El tipo de empresa que quiero apoyar"
                ]
            },
            {
                "post_url": "https://instagram.com/p/cambio-precio-upd/",
                "marcos_narrativos": {
                    "Positivo": 0.22,
                    "Negativo": 0.62,
                    "Aspiracional": 0.08,
                    "Neutral": 0.08
                },
                "marco_dominante": "Negativo",
                "ejemplos_narrativos": [
                    "Decisión unilateral que no considera al cliente",
                    "Precio inflado para maximizar ganancias",
                    "Señal de que la marca cambió para peor"
                ]
            },
            {
                "post_url": "https://instagram.com/p/testimonio-cliente-exito/",
                "marcos_narrativos": {
                    "Positivo": 0.78,
                    "Negativo": 0.05,
                    "Aspiracional": 0.12,
                    "Neutral": 0.05
                },
                "marco_dominante": "Positivo",
                "ejemplos_narrativos": [
                    "Transformación real en la vida del cliente",
                    "Producto que cumple exactamente lo que promete",
                    "Inversión que valió completamente la pena"
                ]
            }
        ]
    },
    "errors": []
}

# ============================================================================
# Q5-Q10 - PLACEHOLDER DATA
# ============================================================================

Q5_DATA = {
    "metadata": {"module": "Q5 Influenciadores", "version": 1},
    "results": {
        "influenciadores_principales": [
            {"usuario": "@influencer_1", "alcance": 125000, "engagement_rate": 0.08, "sentimiento": 0.72},
            {"usuario": "@influencer_2", "alcance": 89000, "engagement_rate": 0.06, "sentimiento": 0.68},
            {"usuario": "@influencer_3", "alcance": 54000, "engagement_rate": 0.12, "sentimiento": 0.78}
        ],
        "metricas_globales": {
            "influenciadores_identificados": 45,
            "alcance_total": 2850000,
            "engagement_promedio": 0.074
        }
    },
    "errors": []
}

Q6_DATA = {
    "metadata": {"module": "Q6 Oportunidades", "version": 1},
    "results": {
        "oportunidades_principales": [
            {"tipo": "Engagement", "potencial": 0.82, "esfuerzo": "Bajo", "resumen": "Aumentar interacción en posts de video"},
            {"tipo": "Expansion", "potencial": 0.68, "esfuerzo": "Medio", "resumen": "Explorar nuevas categorías de producto"},
            {"tipo": "Retention", "potencial": 0.75, "esfuerzo": "Bajo", "resumen": "Programa de lealtad para clientes frecuentes"}
        ],
        "total_oportunidades": 12
    },
    "errors": []
}

Q7_DATA = {
    "metadata": {"module": "Q7 Sentimiento Detallado", "version": 1},
    "results": {
        "distribucion_sentimiento": {
            "muy_positivo": 0.28,
            "positivo": 0.35,
            "neutral": 0.18,
            "negativo": 0.15,
            "muy_negativo": 0.04
        },
        "evolucion_temporal": [
            {"periodo": "Semana 1", "sentimiento": 0.58},
            {"periodo": "Semana 2", "sentimiento": 0.62},
            {"periodo": "Semana 3", "sentimiento": 0.65},
            {"periodo": "Semana 4", "sentimiento": 0.60}
        ]
    },
    "errors": []
}

Q8_DATA = {
    "metadata": {"module": "Q8 Análisis Temporal", "version": 1},
    "results": {
        "evolucion_metricas": [
            {"fecha": "2024-01-01", "menciones": 145, "engagement": 890, "sentimiento": 0.62},
            {"fecha": "2024-01-08", "menciones": 167, "engagement": 1020, "sentimiento": 0.65},
            {"fecha": "2024-01-15", "menciones": 189, "engagement": 1150, "sentimiento": 0.68},
            {"fecha": "2024-01-22", "menciones": 201, "engagement": 1280, "sentimiento": 0.65}
        ]
    },
    "errors": []
}

Q9_DATA = {
    "metadata": {"module": "Q9 Recomendaciones", "version": 1},
    "results": {
        "recomendaciones": [
            {"prioridad": "Alta", "accion": "Mejorar tiempo de respuesta SAC", "impacto": 0.85},
            {"prioridad": "Alta", "accion": "Expandir línea de productos sostenibles", "impacto": 0.78},
            {"prioridad": "Media", "accion": "Crear contenido de educación del cliente", "impacto": 0.62},
            {"prioridad": "Media", "accion": "Fortalecer programa de referidos", "impacto": 0.58}
        ],
        "total": 4
    },
    "errors": []
}

Q10_DATA = {
    "metadata": {"module": "Q10 Resumen Ejecutivo", "version": 1},
    "results": {
        "kpis_principales": {
            "volumen_menciones": 1802,
            "sentiment_score": 0.64,
            "engagement_rate": 0.078,
            "share_of_voice": 0.42
        },
        "hallazgos_clave": [
            "Marca percibida positivamente en 63% de menciones",
            "Sostenibilidad es diferenciador clave (+15% engagement)",
            "Oportunidad crítica: mejorar respuesta SAC (trending negativo)",
            "Eventos comunitarios generan máxima lealtad"
        ],
        "recomendacion_general": "Invertir en sostenibilidad y experiencia del cliente mientras se resuelve rápidamente los temas de SAC"
    },
    "errors": []
}

# ============================================================================
# Write all files
# ============================================================================

def write_json(filename, data):
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✓ Created {filename}")

if __name__ == "__main__":
    print("Generating realistic mock data for Q1-Q10...")
    print()
    
    write_json("q1_emociones.json", Q1_DATA)
    write_json("q2_personalidad.json", Q2_DATA)
    write_json("q3_topicos.json", Q3_DATA)
    write_json("q4_marcos_narrativos.json", Q4_DATA)
    write_json("q5_influenciadores.json", Q5_DATA)
    write_json("q6_oportunidades.json", Q6_DATA)
    write_json("q7_sentimiento_detallado.json", Q7_DATA)
    write_json("q8_temporal.json", Q8_DATA)
    write_json("q9_recomendaciones.json", Q9_DATA)
    write_json("q10_resumen_ejecutivo.json", Q10_DATA)
    
    print()
    print("✓ All mock data files generated successfully!")
