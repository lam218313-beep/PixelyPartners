"""
Pixely Partners - Base Analyzer (API-First Architecture)

This module provides the abstract base class for all qualitative analysis modules (Q1-Q10).
All data comes from config (Google Sheets) and results are sent directly to API (database).
No local JSON files are used - everything is stored in PostgreSQL.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import os
import httpx
import logging

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """
    Abstract base class for all qualitative analysis modules (Q1-Q10).
    
    API-First Architecture:
    - Data comes from config["new_posts"] and config["new_comments"] (Google Sheets)
    - Results are sent directly to API endpoints (saved to PostgreSQL)
    - No local file I/O except for configuration
    
    Required config keys:
    - new_posts: List of post dictionaries from Google Sheets
    - new_comments: List of comment dictionaries from Google Sheets
    - ficha_cliente_id: UUID of the client (for API calls)
    - api_base_url: Base URL of the API (optional, default from env)
    - api_token: JWT token for API authentication (optional, fetched if needed)
    """

    def __init__(self, openai_client: Any, config: Dict[str, Any]):
        """
        Initialize the analyzer.
        
        Args:
            openai_client: AsyncOpenAI client instance for LLM calls.
            config: Configuration dictionary with new_posts, new_comments, ficha_cliente_id
        """
        self.openai_client = openai_client
        self.config = config
        
        # Model name is configurable via environment or config
        self.model_name = os.environ.get("OPENAI_MODEL") or self.config.get("openai_model") or "gpt-5-nano"
        
        # API configuration
        self.api_base_url = self.config.get("api_base_url") or os.environ.get("API_BASE_URL", "http://api:8000")
        self.api_token = self.config.get("api_token")
        self.ficha_cliente_id = self.config.get("ficha_cliente_id")

    def get_posts_data(self) -> List[Dict[str, Any]]:
        """
        Get posts data from config (comes from Google Sheets via ingest_utils).
        
        Returns:
            List of post dictionaries with keys: link, platform, created_at, content, likes, etc.
            
        Raises:
            KeyError: If new_posts is not in config
        """
        if "new_posts" not in self.config:
            raise KeyError("Config missing 'new_posts'. Ensure fetch_incremental_data_for_client() was called.")
        
        return self.config["new_posts"]

    def get_comments_data(self) -> List[Dict[str, Any]]:
        """
        Get comments data from config (comes from Google Sheets via ingest_utils).
        
        Returns:
            List of comment dictionaries with keys: link, comment_text, ownerUsername, created_at, likes
            
        Raises:
            KeyError: If new_comments is not in config
        """
        if "new_comments" not in self.config:
            raise KeyError("Config missing 'new_comments'. Ensure fetch_incremental_data_for_client() was called.")
        
        return self.config["new_comments"]

    def get_comments_for_post(self, post_link: str) -> List[Dict[str, Any]]:
        """
        Filter comments that belong to a specific post.
        
        Args:
            post_link: The 'link' field of the post (URL)
            
        Returns:
            List of comments matching the post link
        """
        all_comments = self.get_comments_data()
        return [c for c in all_comments if c.get("link") == post_link]

    async def save_results_to_api(self, module_name: str, results: Dict[str, Any]) -> bool:
        """
        Send analysis results to API for storage in PostgreSQL.
        
        Args:
            module_name: Module identifier (e.g., "Q1", "Q2", etc.)
            results: Analysis results dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ficha_cliente_id:
            logger.error(f"{module_name}: Cannot save results - missing ficha_cliente_id in config")
            return False
        
        if not self.api_token:
            logger.error(f"{module_name}: Cannot save results - missing api_token in config")
            return False
        
        try:
            endpoint = f"{self.api_base_url}/analysis_results"
            payload = {
                "ficha_cliente_id": self.ficha_cliente_id,
                "module_name": module_name,
                "results": results
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"{module_name}: Results saved to API successfully")
                return True
                
        except Exception as e:
            logger.error(f"{module_name}: Failed to save results to API: {e}")
            return False

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

