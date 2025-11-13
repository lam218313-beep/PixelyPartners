import os
import json
import asyncio
import re
from dotenv import load_dotenv
import logging
from openai import AsyncOpenAI
from typing import Dict, Any

script_dir = os.path.dirname(__file__)
# Configure logging to a file within the mounted volume
log_file_path = os.path.join(script_dir, '..', '..', 'outputs', 'orchestrator_debug.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Importar Módulos de Análisis ---
# A medida que se creen nuevos módulos, se importarán aquí
from analysis_modules.q1_emociones import Q1Emociones
from analysis_modules.q2_personalidad import Q2Personalidad # Ejemplo futuro
from analysis_modules.q3_topicos import Q3Topicos # Añadir Q3Temas
from analysis_modules.q4_marcos_narrativos import Q4MarcosNarrativos
from analysis_modules.q6_oportunidades import Q6Oportunidades
# Q9 Recomendaciones
from analysis_modules.q9_recomendaciones import Q9Recomendaciones
from analysis_modules.q10_resumen_ejecutivo import Q10ResumenEjecutivo

# Cargar variables de entorno desde el archivo .env
dotenv_path = os.path.join(script_dir, '..', '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Configuración del Enrutador de Análisis ---
# Este diccionario mapea el nombre del módulo a su clase correspondiente.
# Para añadir un nuevo análisis, solo se necesita agregarlo a este diccionario.
ANALYSIS_MODULES = {
    "Q1": Q1Emociones,
    "Q2": Q2Personalidad, # Ejemplo para el futuro
    "Q3": Q3Topicos, # Añadir Q3Temas
    "Q4": Q4MarcosNarrativos,
    "Q6": Q6Oportunidades,
    "Q9": Q9Recomendaciones,
    "Q10": Q10ResumenEjecutivo
}

async def analyze_data(config: Dict[str, Any], module_to_run="all"):
    """
    Orquestador principal para el análisis de datos de redes sociales.
    Ejecuta los módulos de análisis especificados (ej. "Q1" o "all").
    """
    try:
        logging.info("Iniciando el motor de análisis...")
        openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY")) # Use OPENAI_API_KEY for OpenAI API key
        # Ensure analyzers use the same outputs directory as this orchestrator
        # Default outputs dir (relative to this script) -> pixely_stable/orchestrator/outputs
        default_outputs_dir = os.path.join(script_dir, '..', '..', 'outputs')
        # If caller didn't pass outputs_dir in config, set it so BaseAnalyzer.load_ingested_data can find files
        if isinstance(config, dict):
            config.setdefault('outputs_dir', default_outputs_dir)
        else:
            config = {'outputs_dir': default_outputs_dir}
        modules_to_execute = []
        if module_to_run.lower() == "all":
            modules_to_execute = ANALYSIS_MODULES.keys()
            logging.info(f"Se ejecutarán todos los módulos disponibles: {list(modules_to_execute)}")
        elif module_to_run.upper() in ANALYSIS_MODULES:
            modules_to_execute = [module_to_run.upper()]
        else:
            logging.error(f"Error: Módulo '{module_to_run}' no es reconocido. Módulos disponibles: {list(ANALYSIS_MODULES.keys())}")
            return

        for module_name in modules_to_execute:
            try:
                logging.info(f"--- Ejecutando Módulo {module_name} ---")
                
                analyzer_class = ANALYSIS_MODULES[module_name]
                analyzer_instance = analyzer_class(openai_client, config) # Pass openai_client and config
                result = await analyzer_instance.analyze()
                
                # Convención de nombres para el archivo de salida (ej. q1_emociones.json)
                # Convertir el nombre de la clase (p.ej. Q11Engagement) a snake_case removiendo
                # el prefijo Q\d+ para evitar nombres como q11_1_engagement.json
                class_name_raw = analyzer_class.__name__
                # Eliminar prefijo Q seguido de dígitos (Q1, Q11, etc.)
                class_name_base = re.sub(r'^Q\d+', '', class_name_raw)
                class_name_suffix = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name_base).lower()
                output_filename = f"{module_name.lower()}_{class_name_suffix}.json"
                output_path = os.path.join(script_dir, '..', '..', 'outputs', output_filename)
                
                logging.info(f"Attempting to save result for {module_name} to: {output_path}")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                logging.info(f"Módulo {module_name} ejecutado y resultado guardado en: {output_path}")

            except Exception as e:
                logging.error(f"ERROR en Módulo {module_name}: {e}")
                error_result = {"error": f"El módulo {module_name} no se pudo ejecutar: {e}"}
                output_filename = f"{module_name.lower()}_error.json"
                output_path = os.path.join(script_dir, '..', '..', 'outputs', output_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(error_result, f, indent=4, ensure_ascii=False)
                logging.info(f"Error del Módulo {module_name} registrado en: {output_path}")

        logging.info("\nMotor de análisis completado.")

    except Exception as e:
        logging.error(f"Ocurrió un error inesperado en el motor de análisis: {e}")

# This part is needed to run the async function
if __name__ == "__main__":
    asyncio.run(analyze_data(module_to_run="Q3"))

