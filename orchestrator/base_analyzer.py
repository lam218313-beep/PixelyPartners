"""
Pixely Partners - Base Analyzer (Single-Client Native)

This module provides the abstract base class for all qualitative analysis modules (Q1-Q10).
The system is natively single-client: no competitor data, no multi-client branching.
All analyzers inherit from this class and implement the analyze() method.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import os


class BaseAnalyzer(ABC):
    """
    Abstract base class for all qualitative analysis modules (Q1-Q10).
    
    Provides:
    - Initialization with OpenAI client and config
    - Utility to load ingested_data.json
    - Standard output format with metadata, results, and error handling
    
    The system operates natively on client data only. No multi-client modes or competitor analysis.
    """

    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        """
        Initialize the analyzer.
        
        Args:
            openai_client: AsyncOpenAI client instance for LLM calls.
            config: Configuration dictionary containing outputs_dir and other settings.
        """
        self.openai_client = openai_client
        self.config = config
        # Default outputs directory relative to this script's location
        self.outputs_dir = self.config.get(
            "outputs_dir",
            os.path.join(os.path.dirname(__file__), "outputs")
        )
        # Model name is configurable via environment or config (fallback to gpt-5-nano)
        self.model_name = os.environ.get("OPENAI_MODEL") or self.config.get("openai_model") or "gpt-5-nano"

    def load_ingested_data(self) -> Dict[str, Any]:
        """
        Load and return the complete ingested data from ingested_data.json.
        
        Returns:
            Dict containing client_ficha, posts, and comments data.
            
        Raises:
            FileNotFoundError: If ingested_data.json is not found.
        """
        json_path = os.path.join(self.outputs_dir, "ingested_data.json")

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Ingested data file not found at: {json_path}")

        with open(json_path, "r", encoding="utf-8-sig") as f:
            ingested_data = json.load(f)

        return ingested_data

    @abstractmethod
    async def analyze(self) -> Dict[str, Any]:
        """
        Execute analysis logic specific to this module.
        
        Must be implemented by each analyzer subclass.
        
        Returns:
            Dictionary with structure:
            {
                "metadata": {
                    "module": "Q{N} {Name}",
                    "version": 1,
                    "description": "..."
                },
                "results": {...},  # Analysis-specific results
                "errors": [...]    # Any errors encountered during analysis
            }
        """
        pass
