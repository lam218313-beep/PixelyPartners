"""
Orchestrator main entry point - Multi-Client Incremental Analysis
Processes all enabled clients from orchestrator/inputs/Cliente_XX/config.json
"""

import sys
import os
import asyncio
import logging
import httpx
from datetime import datetime
from typing import Optional
from .analyze import analyze_data
from .ingest_utils import load_all_clients, fetch_incremental_data_for_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def authenticate_orchestrator(api_base_url: str, max_retries: int = 5) -> str:
    """
    Authenticate orchestrator with API and get JWT token.
    Includes retry logic for API availability.
    
    Args:
        api_base_url: Base URL of the API (e.g., http://api:8000)
        max_retries: Maximum number of retry attempts
    
    Returns:
        JWT access token
    """
    orchestrator_user = os.environ.get("ORCHESTRATOR_USER", "admin")
    orchestrator_password = os.environ.get("ORCHESTRATOR_PASSWORD", "secure_password")
    
    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient() as client:
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
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            if attempt < max_retries:
                wait_time = attempt * 2  # Exponential backoff: 2s, 4s, 6s, 8s, 10s
                logger.warning(f"⏳ API not ready (attempt {attempt}/{max_retries}). Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"❌ Failed to connect to API after {max_retries} attempts")
                raise
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Authentication failed: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during authentication: {e}")
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


async def process_single_client(
    client_config,
    api_base_url: str,
    token: str,
    module_to_run: str = "all"
) -> bool:
    """
    Process a single client: fetch data, analyze if new posts, update timestamp.
    
    Args:
        client_config: ClientConfig object
        api_base_url: Base URL of the API
        token: JWT access token
        module_to_run: Which analysis module to run (default: "all")
    
    Returns:
        True if analysis was executed, False if skipped
    """
    logger.info("="*80)
    logger.info(f"📋 Processing Client: {client_config.client_name}")
    logger.info(f"   UUID: {client_config.client_id}")
    logger.info(f"   Spreadsheet ID: {client_config.spreadsheet_id}")
    logger.info("="*80)
    
    try:
        # Get last analysis timestamp for this client
        last_timestamp = await get_last_analysis_timestamp(
            api_base_url, 
            token, 
            client_config.client_id
        )
        
        # Fetch new posts from Google Sheets
        logger.info(f"📊 Fetching data from Google Sheets for {client_config.client_name}...")
        incremental_data = await fetch_incremental_data_for_client(
            client_config,
            last_analysis_timestamp=last_timestamp
        )
        
        new_posts = incremental_data["posts"]
        new_comments = incremental_data["comments"]
        
        # Decision - Skip if no new data
        if len(new_posts) == 0:
            logger.info(f"⏸️  No new posts found for {client_config.client_name}. Skipping analysis.")
            logger.info(f"   Last analysis was at: {last_timestamp or 'Never'}")
            return False
        
        logger.info(f"✅ Found {len(new_posts)} new posts and {len(new_comments)} comments")
        logger.info(f"🔄 Starting analysis modules (Q1-Q10) for {client_config.client_name}...")
        
        # Execute analysis with new data only
        config = {
            "new_posts": new_posts,
            "new_comments": new_comments,
            "ficha_cliente_id": client_config.client_id,
            "client_name": client_config.client_name,
            "api_base_url": api_base_url,
            "api_token": token,  # Pass JWT token for API calls
            "incremental_mode": True
        }
        
        await analyze_data(config=config, module_to_run=module_to_run)
        
        # Update last_analysis_timestamp
        logger.info(f"📝 Updating last_analysis_timestamp for {client_config.client_name}...")
        await update_last_analysis_timestamp(
            api_base_url, 
            token, 
            client_config.client_id
        )
        
        logger.info(f"✅ Analysis completed for {client_config.client_name}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to process client {client_config.client_name}: {e}", exc_info=True)
        return False


async def main():
    """
    Main orchestrator entry point - Multi-Client Processing.
    
    Flow:
    1. Authenticate with API
    2. Load all enabled clients from orchestrator/inputs/
    3. For each client:
       a. Get last_analysis_timestamp from FichaCliente
       b. Fetch new posts from client's Google Sheets
       c. If no new posts → Skip analysis
       d. If new posts → Execute Q1-Q10 analysis
       e. Update last_analysis_timestamp after success
    """
    logger.info("="*80)
    logger.info("🚀 PIXELY PARTNERS - ORCHESTRATOR INICIADO (MULTI-CLIENT)")
    logger.info("="*80)
    
    # Get configuration from environment
    api_base_url = os.environ.get("API_BASE_URL", "http://api:8000")
    inputs_dir = os.environ.get("ORCHESTRATOR_INPUTS_DIR", "/app/orchestrator/inputs")
    module_to_run = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    try:
        # Step 1: Authenticate
        logger.info("🔐 Authenticating with API...")
        token = await authenticate_orchestrator(api_base_url)
        
        # Step 2: Load all enabled clients
        logger.info(f"📂 Loading client configurations from {inputs_dir}...")
        clients = load_all_clients(inputs_dir)
        
        if not clients:
            logger.warning("⚠️  No enabled clients found. Nothing to process.")
            return
        
        logger.info(f"✅ Found {len(clients)} enabled clients")
        
        # Step 3: Process each client
        processed_count = 0
        skipped_count = 0
        failed_count = 0
        
        for client in clients:
            result = await process_single_client(
                client, 
                api_base_url, 
                token, 
                module_to_run
            )
            
            if result:
                processed_count += 1
            elif result is False:
                skipped_count += 1
            else:
                failed_count += 1
        
        # Summary
        logger.info("="*80)
        logger.info("📊 EXECUTION SUMMARY")
        logger.info(f"   ✅ Processed: {processed_count} clients")
        logger.info(f"   ⏸️  Skipped: {skipped_count} clients (no new data)")
        logger.info(f"   ❌ Failed: {failed_count} clients")
        logger.info("="*80)
        logger.info("✅ ORCHESTRATOR EXECUTION COMPLETED")
        logger.info("="*80)
    
    except Exception as e:
        logger.error(f"❌ Orchestrator execution failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
