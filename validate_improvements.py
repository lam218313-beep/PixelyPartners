#!/usr/bin/env python3
"""Quick validation script for Q4 & Q5 improvements"""

import json
import os
import sys

def validate_q5_json():
    """Validate Q5 influenciadores.json structure"""
    print("\n📋 Validating Q5 Influenciadores JSON...")
    
    try:
        with open("orchestrator/outputs/q5_influenciadores.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        results = data.get("results", {})
        top_inf = results.get("top_influenciadores_detallado", [])
        
        required_fields = ["username", "score_centralidad", "polaridad_dominante", 
                          "sentimiento", "alcance", "comentario_evidencia"]
        
        print(f"  ✓ JSON loaded successfully")
        print(f"  ✓ Found {len(top_inf)} detailed influencers")
        
        for idx, inf in enumerate(top_inf):
            missing = [f for f in required_fields if f not in inf]
            if missing:
                print(f"  ✗ Influencer {idx} missing fields: {missing}")
                return False
        
        print(f"  ✓ All {len(top_inf)} influencers have required fields")
        
        # Check polaridad types
        polaridades = set(inf.get("polaridad_dominante") for inf in top_inf)
        print(f"  ✓ Polaridad types found: {sorted(polaridades)}")
        
        # Check resumen_polaridad
        resumen = results.get("resumen_polaridad", {})
        print(f"  ✓ Resumen Polaridad: {resumen}")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def validate_q4_json():
    """Validate Q4 marcos narrativos.json structure"""
    print("\n📋 Validating Q4 Marcos Narrativos JSON...")
    
    try:
        with open("orchestrator/outputs/q4_marcos_narrativos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        results = data.get("results", {})
        evolucion = results.get("evolucion_temporal", [])
        
        print(f"  ✓ JSON loaded successfully")
        print(f"  ✓ Found {len(evolucion)} temporal periods")
        
        for idx, period in enumerate(evolucion):
            semana = period.get("semana") or period.get("periodo")
            marcos = period.get("marcos_distribucion", {})
            
            if not marcos:
                print(f"  ✗ Period {idx} missing marcos_distribucion")
                return False
            
            total = sum(marcos.values())
            if not (0.99 <= total <= 1.01):
                print(f"  ✗ Period {idx} marcos don't sum to 1.0 (got {total})")
                return False
        
        print(f"  ✓ All {len(evolucion)} periods have valid marcos_distribucion")
        print(f"  ✓ All periods' marcos sum to 1.0")
        
        # Show trend
        if len(evolucion) >= 2:
            first_pos = evolucion[0]["marcos_distribucion"]["Positivo"]
            last_pos = evolucion[-1]["marcos_distribucion"]["Positivo"]
            change = ((last_pos - first_pos) / first_pos) * 100
            trend = "📈 UP" if change > 0 else "📉 DOWN"
            print(f"  ✓ Positivo trend: {first_pos:.2%} → {last_pos:.2%} ({trend} {abs(change):.1f}%)")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def validate_view_files():
    """Validate Python view files have no syntax errors"""
    print("\n📋 Validating Python view files...")
    
    files = [
        "frontend/view_components/qual/q4_view.py",
        "frontend/view_components/qual/q5_view.py"
    ]
    
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
            compile(code, filepath, "exec")
            print(f"  ✓ {os.path.basename(filepath)} - No syntax errors")
        except SyntaxError as e:
            print(f"  ✗ {os.path.basename(filepath)} - Syntax Error: {e}")
            return False
    
    return True

def main():
    """Run all validations"""
    print("\n" + "="*60)
    print("🔍 Pixely Partners - Session Improvements Validation")
    print("="*60)
    
    all_pass = True
    
    all_pass &= validate_q5_json()
    all_pass &= validate_q4_json()
    all_pass &= validate_view_files()
    
    print("\n" + "="*60)
    if all_pass:
        print("✅ ALL VALIDATIONS PASSED")
        print("🎉 Q4 and Q5 improvements are ready for deployment!")
    else:
        print("❌ VALIDATION FAILED - See errors above")
        sys.exit(1)
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
