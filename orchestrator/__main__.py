"""
Orchestrator main entry point - allows running as module with incremental analysis
"""

import sys
import os
import asyncio
import logging
import httpx
from datetime import datetime
from typing import Optional
from .analyze import analyze_data
from .ingest_utils import fetch_incremental_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def authenticate_orchestrator(api_base_url: str) -> str:
    """
    Authenticate orchestrator with API and get JWT token.
    
    Args:
        api_base_url: Base URL of the API (e.g., http://api:8000)
    
    Returns:
        JWT access token
    """
    orchestrator_user = os.environ.get("ORCHESTRATOR_USER", "admin")
    orchestrator_password = os.environ.get("ORCHESTRATOR_PASSWORD", "secure_password")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{api_base_url}/token",
                data={
                    "username": orchestrator_user,
                    "password": orchestrator_password
                },
                timeout=30.0
            )
            response.raise_for_status()
            token_data = response.json()
            logger.info("✅ Orchestrator authenticated successfully")
            return token_data["access_token"]
        except Exception as e:
            logger.error(f"❌ Failed to authenticate orchestrator: {e}")
            raise


async def get_last_analysis_timestamp(
    api_base_url: str,
    token: str,
    ficha_cliente_id: str
) -> Optional[datetime]:
    """
    Get the timestamp of the last analysis execution from API.
    
    Args:
        api_base_url: Base URL of the API
        token: JWT access token
        ficha_cliente_id: UUID of the ficha cliente
    
    Returns:
        datetime of last analysis or None if never executed
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{api_base_url}/fichas_cliente/{ficha_cliente_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            ficha_data = response.json()
            
            last_timestamp_str = ficha_data.get("last_analysis_timestamp")
            if last_timestamp_str:
                last_timestamp = datetime.fromisoformat(last_timestamp_str.replace('Z', '+00:00'))
                logger.info(f"📅 Last analysis timestamp: {last_timestamp}")
                return last_timestamp
            else:
                logger.info("🆕 No previous analysis found. This is the first run.")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get last analysis timestamp: {e}")
            return None


async def update_last_analysis_timestamp(
    api_base_url: str,
    token: str,
    ficha_cliente_id: str
) -> bool:
    """
    Update the last_analysis_timestamp field in API after successful analysis.
    
    Args:
        api_base_url: Base URL of the API
        token: JWT access token
        ficha_cliente_id: UUID of the ficha cliente
    
    Returns:
        True if successful, False otherwise
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{api_base_url}/fichas_cliente/{ficha_cliente_id}/last_analysis_timestamp",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            logger.info("✅ Updated last_analysis_timestamp in database")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update last_analysis_timestamp: {e}")
            return False


async def main():
    """
    Main orchestrator entry point with incremental analysis logic.
    
    Flow:
    1. Authenticate with API
    2. Get last_analysis_timestamp from FichaCliente
    3. Fetch new posts from Google Sheets (created_at > last_timestamp)
    4. If no new posts → Skip analysis
    5. If new posts → Execute Q1-Q10 analysis
    6. Update last_analysis_timestamp after success
    """
    logger.info("="*80)
    logger.info("🚀 PIXELY PARTNERS - ORCHESTRATOR INICIADO")
    logger.info("="*80)
    
    # Get configuration from environment
    api_base_url = os.environ.get("API_BASE_URL", "http://api:8000")
    ficha_cliente_id = os.environ.get("FICHA_CLIENTE_ID")
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
    
    # Validate required environment variables
    if not ficha_cliente_id:
        logger.error("❌ FICHA_CLIENTE_ID environment variable not set")
        return
    
    if not spreadsheet_id:
        logger.error("❌ GOOGLE_SHEETS_SPREADSHEET_ID environment variable not set")
        return
    
    try:
        # Step 1: Authenticate
        token = await authenticate_orchestrator(api_base_url)
        
        # Step 2: Get last analysis timestamp
        last_timestamp = await get_last_analysis_timestamp(
            api_base_url, 
            token, 
            ficha_cliente_id
        )
        
        # Step 3: Fetch new posts from Google Sheets
        logger.info("📊 Fetching data from Google Sheets...")
        incremental_data = await fetch_incremental_data(
            spreadsheet_id=spreadsheet_id,
            last_analysis_timestamp=last_timestamp,
            credentials_path=os.environ.get("GOOGLE_CREDENTIALS_PATH", "/app/credentials.json")
        )
        
        new_posts = incremental_data["posts"]
        new_comments = incremental_data["comments"]
        
        # Step 4: Decision - Skip if no new data
        if len(new_posts) == 0:
            logger.info("⏸️  No new posts found. Skipping analysis.")
            logger.info(f"Last analysis was at: {last_timestamp or 'Never'}")
            return
        
        logger.info(f"✅ Found {len(new_posts)} new posts and {len(new_comments)} comments")
        logger.info("🔄 Starting analysis modules (Q1-Q10)...")
        
        # Step 5: Execute analysis with new data only
        module_to_run = sys.argv[1] if len(sys.argv) > 1 else "all"
        
        config = {
            "new_posts": new_posts,
            "new_comments": new_comments,
            "ficha_cliente_id": ficha_cliente_id,
            "incremental_mode": True
        }
        
        await analyze_data(config=config, module_to_run=module_to_run)
        
        # Step 6: Update last_analysis_timestamp
        logger.info("📝 Updating last_analysis_timestamp...")
        await update_last_analysis_timestamp(api_base_url, token, ficha_cliente_id)
        
        logger.info("="*80)
        logger.info("✅ ORCHESTRATOR EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("="*80)
    
    except Exception as e:
        logger.error(f"❌ Orchestrator execution failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
