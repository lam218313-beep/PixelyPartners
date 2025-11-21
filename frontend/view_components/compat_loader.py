"""
Compatibility layer for loading data from API or local files.
Provides backward compatibility during migration.
"""

import streamlit as st
import json
import os
from typing import Optional, Dict, Any


def load_from_api_or_file(
    api_loader_func,
    json_filename: str,
    module_name: str
) -> Optional[Dict[str, Any]]:
    """
    Try to load data from API first, fallback to local file if not available.
    
    Args:
        api_loader_func: Function to load from API
        json_filename: JSON filename for fallback
        module_name: Module name for error messages
    
    Returns:
        Data dict or None
    """
    # Try API first
    data = api_loader_func()
    if data is not None:
        return data
    
    # Fallback to local file (for development/backward compatibility)
    try:
        from .._outputs import get_outputs_dir
        outputs_dir = get_outputs_dir()
        json_path = os.path.join(outputs_dir, json_filename)
        
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    
    st.error(f"❌ No se encontraron datos de análisis {module_name}. Por favor ejecuta el análisis primero.")
    return None
