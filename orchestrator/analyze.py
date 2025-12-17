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
import httpx
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

# Logging to stdout (Docker logs) instead of file
# All analysis results are saved to database via API
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
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
    Main orchestrator function - API-First Architecture.
    
    Executes specified analysis modules and sends results directly to API (PostgreSQL).
    No local JSON files are created - all data stored in database.
    
    Args:
        config: Configuration dict with new_posts, new_comments, ficha_cliente_id, api_token
        module_to_run: "all", "Q1", "Q2", etc. Defaults to "all".
    """
    try:
        print("\n" + "="*80)
        print("🚀 PIXELY PARTNERS - ORCHESTRATOR ANÁLISIS")
        print("="*80)
        logging.info("Starting analysis engine...")

        # Initialize OpenAI client
        openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Validate required config keys
        required_keys = ["new_posts", "new_comments", "ficha_cliente_id"]
        missing_keys = [k for k in required_keys if k not in config]
        if missing_keys:
            error_msg = f"Missing required config keys: {missing_keys}"
            print(f"❌ {error_msg}")
            logging.error(error_msg)
            return

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
        module_results = {}  # Store results for Q10
        
        for idx, module_name in enumerate(modules_to_execute, 1):
            try:
                print(f"\n[{idx}/{total_modules}] 🔄 Ejecutando {module_name}...")
                logging.info(f"--- Executing Module {module_name} ---")

                # For Q10, add previous results to config
                if module_name == "Q10":
                    for q_num in range(1, 10):
                        q_key = f"Q{q_num}"
                        if q_key in module_results:
                            config[f"q{q_num}_results"] = module_results[q_key]

                # Instantiate and run analyzer
                analyzer_class = ANALYSIS_MODULES[module_name]
                analyzer_instance = analyzer_class(openai_client, config)
                result = await analyzer_instance.analyze()

                # Store result for Q10
                module_results[module_name] = result

                # Send results to API (database)
                await analyzer_instance.save_results_to_api(module_name, result)

                # Auto-generate Hilos de Trabajo after Q9 is saved to API
                if module_name == "Q9":
                    try:
                        api_base_url = config.get("api_base_url", os.environ.get("API_BASE_URL", "http://api:8000"))
                        ficha_id = config.get("ficha_cliente_id")
                        api_token = config.get("api_token")
                        if api_base_url and ficha_id and api_token:
                            logging.info(f"Triggering task generation from Q9 for ficha {ficha_id}...")
                            async with httpx.AsyncClient() as client:
                                resp = await client.post(
                                    f"{api_base_url}/api/v1/fichas/{ficha_id}/tasks/generate-from-q9",
                                    headers={"Authorization": f"Bearer {api_token}"},
                                    timeout=60.0,
                                )
                                resp.raise_for_status()
                                data = resp.json()
                                created = data.get("tasks_created")
                                dist = data.get("distribution", {})
                                logging.info(
                                    f"Hilos de Trabajo generados automáticamente: {created} (Distribución: W1={dist.get('week_1')}, W2={dist.get('week_2')}, W3={dist.get('week_3')}, W4={dist.get('week_4')})"
                                )
                                print(f"   🧵 Hilos de Trabajo generados: {created} tareas (4/semana)")
                        else:
                            logging.warning("Skipping auto-generation of tasks: missing api_base_url, ficha_cliente_id, or api_token in config")
                    except Exception as gen_err:
                        logging.error(f"Failed to auto-generate tasks from Q9: {gen_err}", exc_info=True)
                        print("   ⚠️ No se pudieron generar los Hilos de Trabajo automáticamente")

                # Extract counts for console output
                errors = result.get("errors", [])
                error_count = len(errors)
                
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

                logging.info(f"Module {module_name} completed and saved to API")

            except Exception as e:
                error_msg = f"ERROR in Module {module_name}: {e}"
                print(f"   ❌ {error_msg}")
                logging.error(error_msg, exc_info=True)

        print("\n" + "="*80)
        print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("="*80 + "\n")
        logging.info("Analysis engine completed.")

    except Exception as e:
        error_msg = f"Unexpected error in analysis engine: {e}"
        print(f"\n❌ {error_msg}\n")
        logging.error(error_msg, exc_info=True)
        logging.error(error_msg, exc_info=True)


if __name__ == "__main__":
    # Run specific module or all
    asyncio.run(analyze_data(config={}, module_to_run="all"))
