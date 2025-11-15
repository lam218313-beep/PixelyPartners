"""
Pixely Partners - Orchestrator Main Entry Point

This module orchestrates the execution of all qualitative analysis modules (Q1-Q10).
It manages:
- Loading analysis modules dynamically
- Executing analyses asynchronously
- Saving results to JSON files
- Logging and error handling
"""

import os
import json
import asyncio
import re
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Import all analysis modules
from orchestrator.analysis_modules.q1_emociones import Q1Emociones
from orchestrator.analysis_modules.q2_personalidad import Q2Personalidad
from orchestrator.analysis_modules.q3_topicos import Q3Topicos
from orchestrator.analysis_modules.q4_marcos_narrativos import Q4MarcosNarrativos
from orchestrator.analysis_modules.q5_influenciadores import Q5Influenciadores
from orchestrator.analysis_modules.q6_oportunidades import Q6Oportunidades
from orchestrator.analysis_modules.q7_sentimiento_detallado import Q7SentimientoDetallado
from orchestrator.analysis_modules.q8_temporal import Q8Temporal
from orchestrator.analysis_modules.q9_recomendaciones import Q9Recomendaciones
from orchestrator.analysis_modules.q10_resumen_ejecutivo import Q10ResumenEjecutivo


# Configuration
script_dir = os.path.dirname(__file__)
log_file_path = os.path.join(script_dir, "outputs", "orchestrator_debug.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Analysis modules registry
ANALYSIS_MODULES = {
    "Q1": Q1Emociones,
    "Q2": Q2Personalidad,
    "Q3": Q3Topicos,
    "Q4": Q4MarcosNarrativos,
    "Q5": Q5Influenciadores,
    "Q6": Q6Oportunidades,
    "Q7": Q7SentimientoDetallado,
    "Q8": Q8Temporal,
    "Q9": Q9Recomendaciones,
    "Q10": Q10ResumenEjecutivo,
}

# Load environment variables
dotenv_path = os.path.join(script_dir, "..", ".env")
load_dotenv(dotenv_path=dotenv_path)


async def analyze_data(config: Dict[str, Any], module_to_run: str = "all"):
    """
    Main orchestrator function.
    
    Executes specified analysis modules and saves results to JSON files.
    
    Args:
        config: Configuration dict containing outputs_dir, API keys, etc.
        module_to_run: "all", "Q1", "Q2", etc. Defaults to "all".
    """
    try:
        print("\n" + "="*80)
        print("🚀 PIXELY PARTNERS - ORCHESTRATOR INICIADO")
        print("="*80)
        logging.info("Starting analysis engine...")

        # Initialize OpenAI client
        openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Set default outputs directory
        default_outputs_dir = os.path.join(script_dir, "outputs")
        if isinstance(config, dict):
            config.setdefault("outputs_dir", default_outputs_dir)
        else:
            config = {"outputs_dir": default_outputs_dir}

        # Determine which modules to execute
        modules_to_execute = []
        if module_to_run.lower() == "all":
            modules_to_execute = list(ANALYSIS_MODULES.keys())
            print(f"\n📊 Módulos a ejecutar: {', '.join(modules_to_execute)}\n")
            logging.info(f"Will execute all modules: {modules_to_execute}")
        elif module_to_run.upper() in ANALYSIS_MODULES:
            modules_to_execute = [module_to_run.upper()]
            print(f"\n📊 Módulo a ejecutar: {module_to_run.upper()}\n")
        else:
            error_msg = f"Error: Module '{module_to_run}' not recognized. Available: {list(ANALYSIS_MODULES.keys())}"
            print(f"❌ {error_msg}")
            logging.error(error_msg)
            return

        # Execute each module
        total_modules = len(modules_to_execute)
        for idx, module_name in enumerate(modules_to_execute, 1):
            try:
                print(f"\n[{idx}/{total_modules}] 🔄 Ejecutando {module_name}...")
                logging.info(f"--- Executing Module {module_name} ---")

                # Instantiate and run analyzer
                analyzer_class = ANALYSIS_MODULES[module_name]
                analyzer_instance = analyzer_class(openai_client, config)
                result = await analyzer_instance.analyze()

                # Generate output filename from class name
                class_name_raw = analyzer_class.__name__
                class_name_base = re.sub(r"^Q\d+", "", class_name_raw)
                class_name_suffix = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name_base).lower()
                output_filename = f"{module_name.lower()}_{class_name_suffix}.json"
                output_path = os.path.join(script_dir, "outputs", output_filename)

                # Save result to file
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)

                # Extract error count
                errors = result.get("errors", [])
                error_count = len(errors)
                
                # Extract result count
                results = result.get("results", {})
                if "analisis_por_publicacion" in results:
                    analysis_count = len(results["analisis_por_publicacion"])
                    print(f"   ✅ {module_name} completado: {analysis_count} análisis realizados", end="")
                    if error_count > 0:
                        print(f" ({error_count} errores)")
                    else:
                        print()
                else:
                    print(f"   ✅ {module_name} completado")

                logging.info(f"Module {module_name} completed. Saved to {output_path}")

            except Exception as e:
                error_msg = f"ERROR in Module {module_name}: {e}"
                print(f"   ❌ {error_msg}")
                logging.error(error_msg, exc_info=True)
                # Write error result to file
                error_result = {"error": f"Module {module_name} failed: {str(e)}"}
                output_filename = f"{module_name.lower()}_error.json"
                output_path = os.path.join(script_dir, "outputs", output_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(error_result, f, indent=4, ensure_ascii=False)

        print("\n" + "="*80)
        print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("="*80 + "\n")
        logging.info("Analysis engine completed.")

    except Exception as e:
        error_msg = f"Unexpected error in analysis engine: {e}"
        print(f"\n❌ {error_msg}\n")
        logging.error(error_msg, exc_info=True)


if __name__ == "__main__":
    # Run specific module or all
    asyncio.run(analyze_data(config={}, module_to_run="all"))
