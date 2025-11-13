#!/usr/bin/env python3
"""
Quick validation script to verify all mock data files are properly formatted
and contain expected structure
"""
import json
import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "orchestrator" / "outputs"

def validate_file(filename, expected_keys):
    """Validate a JSON file has expected structure"""
    filepath = OUTPUT_DIR / filename
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check metadata
        if "metadata" not in data:
            return f"❌ Missing 'metadata' key"
        
        if "results" not in data:
            return f"❌ Missing 'results' key"
        
        # Check expected keys
        results = data.get("results", {})
        for key in expected_keys:
            if key not in results:
                return f"❌ Missing expected key: {key}"
        
        # Count posts if applicable
        if "analisis_por_publicacion" in results:
            posts = results["analisis_por_publicacion"]
            if isinstance(posts, list):
                post_count = len(posts)
                return f"✅ Valid ({post_count} posts)"
            else:
                return f"✅ Valid (structure OK)"
        
        return "✅ Valid"
        
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON: {e}"
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    print("=" * 70)
    print("VALIDATING MOCK DATA FILES")
    print("=" * 70)
    print()
    
    validations = {
        "q1_emociones.json": ["resumen_global_emociones", "analisis_por_publicacion"],
        "q2_personalidad.json": ["resumen_global_personalidad", "analisis_por_publicacion"],
        "q3_topicos.json": ["topicos_principales", "analisis_por_publicacion"],
        "q4_marcos_narrativos.json": ["analisis_agregado", "marcos_principales", "analisis_por_publicacion"],
        "q5_influenciadores.json": ["influenciadores_principales", "metricas_globales"],
        "q6_oportunidades.json": ["oportunidades_principales", "total_oportunidades"],
        "q7_sentimiento_detallado.json": ["distribucion_sentimiento", "evolucion_temporal"],
        "q8_temporal.json": ["evolucion_metricas"],
        "q9_recomendaciones.json": ["recomendaciones", "total"],
        "q10_resumen_ejecutivo.json": ["kpis_principales", "hallazgos_clave"],
    }
    
    all_valid = True
    for filename, expected_keys in validations.items():
        result = validate_file(filename, expected_keys)
        status = "✅" if "✅" in result else "❌"
        print(f"{filename:<35} {result}")
        if "❌" in result:
            all_valid = False
    
    print()
    print("=" * 70)
    if all_valid:
        print("✅ ALL MOCK DATA FILES VALIDATED SUCCESSFULLY")
        print()
        print("Next steps:")
        print("  1. Open http://0.0.0.0:8501 in browser")
        print("  2. Test interactive selectors and filters")
        print("  3. Verify gráficos render with varied data")
        sys.exit(0)
    else:
        print("❌ SOME FILES HAVE ISSUES - CHECK ABOVE")
        sys.exit(1)
