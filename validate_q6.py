#!/usr/bin/env python3
"""Validation script for Q6 Oportunidades implementation"""

import json
import os

def validate_q6():
    """Validate Q6 data structure and view implementation"""
    print("\n" + "="*60)
    print("🔍 Q6 Oportunidades - Validation Report")
    print("="*60)
    
    # 1. Validate JSON
    print("\n📋 Validating Q6 JSON...")
    try:
        with open("orchestrator/outputs/q6_oportunidades.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        results = data.get("results", {})
        oportunidades = results.get("lista_oportunidades", [])
        
        print(f"  ✓ JSON loaded successfully")
        print(f"  ✓ Found {len(oportunidades)} oportunidades")
        
        # Validate each opportunity
        required_fields = ["tema", "gap_score", "actividad_competitiva", 
                          "justificacion", "recomendacion_accion"]
        
        for idx, opp in enumerate(oportunidades, 1):
            missing = [f for f in required_fields if f not in opp]
            if missing:
                print(f"  ✗ Opportunity {idx} missing: {missing}")
                return False
            
            gap = opp.get("gap_score", 0)
            actividad = opp.get("actividad_competitiva", "")
            
            if not (0 <= gap <= 100):
                print(f"  ✗ Opportunity {idx} gap_score out of range: {gap}")
                return False
            
            if actividad not in ["Baja", "Media", "Alta"]:
                print(f"  ✗ Opportunity {idx} invalid actividad: {actividad}")
                return False
            
            print(f"  ✓ {idx}. {opp['tema'][:40]}... (Gap: {gap}, Actividad: {actividad})")
        
        # Validate summary
        resumen = results.get("resumen_global", {})
        print(f"\n  ✓ Resumen Global:")
        print(f"     - Total: {resumen.get('total_oportunidades')}")
        print(f"     - Promedio Gap: {resumen.get('promedio_gap_score'):.0f}")
        print(f"     - Críticas: {resumen.get('oportunidades_criticas')}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def validate_view():
    """Validate Q6 view Python syntax"""
    print("\n📋 Validating Q6 View...")
    try:
        with open("frontend/view_components/qual/q6_view.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        compile(code, "q6_view.py", "exec")
        print(f"  ✓ No syntax errors")
        
        # Check for required functions
        if "def get_priority_color" in code:
            print(f"  ✓ Priority color function defined")
        if "def get_actividad_numeric" in code:
            print(f"  ✓ Activity numeric function defined")
        if "Gráfico 1" in code and "Gráfico 2" in code and "Gráfico 3" in code:
            print(f"  ✓ All 3 charts implemented")
        
        return True
        
    except SyntaxError as e:
        print(f"  ✗ Syntax Error: {e}")
        return False

def analyze_priorities():
    """Analyze priority distribution"""
    print("\n📊 Analyzing Priority Distribution...")
    
    try:
        with open("orchestrator/outputs/q6_oportunidades.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        oportunidades = data.get("results", {}).get("lista_oportunidades", [])
        
        maxima = []
        media = []
        baja = []
        
        for opp in oportunidades:
            gap = opp.get("gap_score", 0)
            actividad = opp.get("actividad_competitiva", "")
            tema = opp.get("tema", "Unknown")
            
            if gap >= 80 and actividad == "Baja":
                maxima.append((tema, gap, actividad))
            elif gap >= 70 and actividad == "Media":
                media.append((tema, gap, actividad))
            else:
                baja.append((tema, gap, actividad))
        
        print(f"\n  🟢 MÁXIMA PRIORIDAD ({len(maxima)}):")
        for tema, gap, act in maxima:
            print(f"     - {tema[:40]}... (Gap: {gap}, {act} Competencia)")
        
        print(f"\n  🟡 MEDIA PRIORIDAD ({len(media)}):")
        for tema, gap, act in media:
            print(f"     - {tema[:40]}... (Gap: {gap}, {act} Competencia)")
        
        print(f"\n  🔴 BAJA PRIORIDAD ({len(baja)}):")
        for tema, gap, act in baja:
            print(f"     - {tema[:40]}... (Gap: {gap}, {act} Competencia)")
        
        # Show strategic insights
        print(f"\n  💡 Strategic Insights:")
        print(f"     - {len(maxima)}/5 oportunidades son 'quick wins' (MÁXIMA)")
        print(f"     - {len(baja)}/5 requieren estrategia diferenciada (BAJA)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 Pixely Partners Q6 - Complete Validation")
    print("="*60)
    
    all_pass = True
    all_pass &= validate_q6()
    all_pass &= validate_view()
    all_pass &= analyze_priorities()
    
    print("\n" + "="*60)
    if all_pass:
        print("✅ ALL Q6 VALIDATIONS PASSED")
        print("🎉 Strategic Prioritization Matrix is ready!")
    else:
        print("❌ VALIDATION FAILED")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
