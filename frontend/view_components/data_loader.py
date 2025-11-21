"""
Helper functions for loading analysis data from session state.
Used by view components to access API data.
"""

import streamlit as st
from typing import Optional, Dict, Any


def get_analysis_data(module_key: str) -> Optional[Dict[str, Any]]:
    """
    Get analysis data for a specific module from session state.
    
    Args:
        module_key: Module key (e.g., "q1_emociones", "q2_personalidad")
    
    Returns:
        Analysis data dict or None if not available
    """
    insights = st.session_state.get("current_insights")
    if not insights:
        return None
    
    return insights.get(module_key)


def load_q1_data() -> Optional[Dict[str, Any]]:
    """Load Q1 emotions data from API."""
    return get_analysis_data("q1_emociones")


def load_q2_data() -> Optional[Dict[str, Any]]:
    """Load Q2 personality data from API."""
    return get_analysis_data("q2_personalidad")


def load_q3_data() -> Optional[Dict[str, Any]]:
    """Load Q3 topics data from API."""
    return get_analysis_data("q3_topicos")


def load_q4_data() -> Optional[Dict[str, Any]]:
    """Load Q4 narrative frames data from API."""
    return get_analysis_data("q4_marcos_narrativos")


def load_q5_data() -> Optional[Dict[str, Any]]:
    """Load Q5 influencers data from API."""
    return get_analysis_data("q5_influenciadores")


def load_q6_data() -> Optional[Dict[str, Any]]:
    """Load Q6 opportunities data from API."""
    return get_analysis_data("q6_oportunidades")


def load_q7_data() -> Optional[Dict[str, Any]]:
    """Load Q7 detailed sentiment data from API."""
    return get_analysis_data("q7_sentimiento")


def load_q8_data() -> Optional[Dict[str, Any]]:
    """Load Q8 temporal data from API."""
    return get_analysis_data("q8_temporal")


def load_q9_data() -> Optional[Dict[str, Any]]:
    """Load Q9 recommendations data from API."""
    return get_analysis_data("q9_recomendaciones")


def load_q10_data() -> Optional[Dict[str, Any]]:
    """Load Q10 executive summary data from API."""
    return get_analysis_data("q10_resumen")
