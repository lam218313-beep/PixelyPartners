"""
Pixely Partners - Frontend Output Directory Resolver

Utility to locate and resolve the orchestrator outputs directory
from the frontend, supporting multiple configuration methods:
1. Environment variable PIXELY_OUTPUTS_DIR
2. Container mount path
3. Relative path from this script
"""

import os


def get_outputs_dir() -> str:
    """
    Resolve the orchestrator outputs directory.
    
    Priority order:
    1. Environment variable PIXELY_OUTPUTS_DIR
    2. Container path /app/orchestrator/outputs
    3. Relative path from this script location
    
    Returns:
        Path to the outputs directory containing JSON analysis results.
    """
    # Check environment variable first
    env_outputs = os.environ.get("PIXELY_OUTPUTS_DIR")
    if env_outputs and os.path.isdir(env_outputs):
        return env_outputs

    # Check container mount path
    container_path = "/app/orchestrator/outputs"
    if os.path.isdir(container_path):
        return container_path

    # Fallback: relative path from this script
    script_dir = os.path.dirname(__file__)
    # Navigate to project root, then to orchestrator/outputs
    relative_path = os.path.join(script_dir, "..", "..", "orchestrator", "outputs")
    resolved_path = os.path.abspath(relative_path)

    return resolved_path
