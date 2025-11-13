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
            logging.info(f"Will execute all modules: {modules_to_execute}")
        elif module_to_run.upper() in ANALYSIS_MODULES:
            modules_to_execute = [module_to_run.upper()]
        else:
            logging.error(
                f"Error: Module '{module_to_run}' not recognized. "
                f"Available: {list(ANALYSIS_MODULES.keys())}"
            )
            return

        # Execute each module
        for module_name in modules_to_execute:
            try:
                logging.info(f"--- Executing Module {module_name} ---")

                # Instantiate and run analyzer
                analyzer_class = ANALYSIS_MODULES[module_name]
                analyzer_instance = analyzer_class(openai_client, config)
                result = await analyzer_instance.analyze()

                # Generate output filename from class name
                # Convert Q1Emociones -> q1_emociones.json
                class_name_raw = analyzer_class.__name__
                # Remove Q prefix and numbers (e.g., Q1 from Q1Emociones)
                class_name_base = re.sub(r"^Q\d+", "", class_name_raw)
                # Convert CamelCase to snake_case
                class_name_suffix = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name_base).lower()
                output_filename = f"{module_name.lower()}_{class_name_suffix}.json"
                output_path = os.path.join(script_dir, "outputs", output_filename)

                # Save result to file
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)

                logging.info(f"Module {module_name} completed. Saved to {output_path}")

            except Exception as e:
                logging.error(f"ERROR in Module {module_name}: {e}")
                # Write error result to file
                error_result = {"error": f"Module {module_name} failed: {str(e)}"}
                output_filename = f"{module_name.lower()}_error.json"
                output_path = os.path.join(script_dir, "outputs", output_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(error_result, f, indent=4, ensure_ascii=False)

        logging.info("Analysis engine completed.")

    except Exception as e:
        logging.error(f"Unexpected error in analysis engine: {e}")


if __name__ == "__main__":
    # Run specific module or all
    asyncio.run(analyze_data(config={}, module_to_run="all"))
