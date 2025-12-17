"""
Pixely Partners - Google Sheets Integration Module (Multi-Client)

This module handles data ingestion from Google Sheets for multiple clients.
Each client has their own config.json in orchestrator/inputs/Cliente_XX/
It detects new posts based on timestamp comparison and returns only incremental data.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)


class ClientConfig:
    """Represents configuration for a single client."""
    
    def __init__(self, config_path: str):
        """
        Load client configuration from config.json
        
        Args:
            config_path: Path to client's config.json file
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.client_id = config['client_id']
        self.client_name = config['client_name']
        self.google_sheets_url = config.get('google_sheets_url', '')
        self.spreadsheet_id = config['google_sheets_spreadsheet_id']
        self.credentials_path = config.get('credentials_path', '/app/credentials.json')
        self.enabled = config.get('enabled', True)
        self.config_dir = str(Path(config_path).parent)
    
    def __repr__(self):
        return f"ClientConfig(name={self.client_name}, id={self.client_id}, enabled={self.enabled})"


def load_all_clients(inputs_dir: str = "/app/orchestrator/inputs") -> List[ClientConfig]:
    """
    Load all client configurations from inputs directory.
    
    Args:
        inputs_dir: Path to orchestrator/inputs directory
    
    Returns:
        List of ClientConfig objects for enabled clients
    """
    clients = []
    inputs_path = Path(inputs_dir)
    
    if not inputs_path.exists():
        logger.warning(f"Inputs directory not found: {inputs_dir}")
        return clients
    
    # Iterate over all subdirectories (Cliente_01, Cliente_02, etc.)
    for client_dir in sorted(inputs_path.iterdir()):
        if not client_dir.is_dir():
            continue
        
        config_file = client_dir / "config.json"
        if not config_file.exists():
            logger.warning(f"config.json not found in {client_dir.name}, skipping")
            continue
        
        try:
            config = ClientConfig(str(config_file))
            
            if not config.enabled:
                logger.info(f"Client {config.client_name} is disabled, skipping")
                continue
            
            clients.append(config)
            logger.info(f"Loaded client: {config.client_name} (ID: {config.client_id})")
        
        except Exception as e:
            logger.error(f"Failed to load config from {client_dir.name}: {e}")
            continue
    
    logger.info(f"Loaded {len(clients)} enabled clients")
    return clients


class GoogleSheetsIngestor:
    """
    Handles connection and data retrieval from Google Sheets.
    
    Each client has their own spreadsheet with two sheets:
    - "Posts": Contains social media posts with metadata
    - "Comments": Contains comments for each post
    """
    
    def __init__(self, credentials_path: str = "/app/credentials.json"):
        """
        Initialize Google Sheets client.
        
        Args:
            credentials_path: Path to Google service account credentials JSON
        """
        self.credentials_path = credentials_path
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using service account."""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, 
                scope
            )
            self.client = gspread.authorize(creds)
            logger.info("Successfully authenticated with Google Sheets API")
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {self.credentials_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise
    
    def fetch_new_posts(
        self, 
        spreadsheet_id: str, 
        last_analysis_timestamp: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Fetch posts from Google Sheets, filtering by timestamp.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            last_analysis_timestamp: Timestamp of last analysis. If None, fetch all posts.
        
        Returns:
            List of post dictionaries with new posts only
        """
        try:
            # Open spreadsheet and get Posts sheet
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            posts_sheet = spreadsheet.worksheet("Posts")
            
            # Get all records as list of dicts
            all_posts = posts_sheet.get_all_records()
            
            logger.info(f"Fetched {len(all_posts)} total posts from Google Sheets")
            
            # Debug: Log available columns from first post
            if all_posts:
                logger.info(f"Available columns in Posts sheet: {list(all_posts[0].keys())}")
            
            # If no last timestamp, return all posts
            if last_analysis_timestamp is None:
                logger.info("No last_analysis_timestamp provided. Returning all posts.")
                return all_posts
            
            # Filter posts by created_at > last_analysis_timestamp
            new_posts = []
            for post in all_posts:
                try:
                    # Try multiple possible column names for timestamp
                    post_date_str = post.get('created_at') or post.get('post_date') or post.get('timestamp')
                    
                    if not post_date_str:
                        logger.warning(f"Post {post.get('link')} missing timestamp, skipping")
                        continue
                    
                    # Parse timestamp (support multiple formats)
                    post_date = self._parse_timestamp(post_date_str)
                    
                    # Compare with last analysis timestamp
                    if post_date > last_analysis_timestamp:
                        new_posts.append(post)
                        logger.debug(f"New post detected: {post.get('post_url')} ({post_date})")
                
                except Exception as e:
                    logger.warning(f"Error processing post {post.get('post_url')}: {e}")
                    continue
            
            logger.info(f"Found {len(new_posts)} new posts since {last_analysis_timestamp}")
            return new_posts
        
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet 'Posts' not found in spreadsheet {spreadsheet_id}")
            raise
        except Exception as e:
            logger.error(f"Error fetching posts from Google Sheets: {e}")
            raise
    
    def fetch_comments_for_posts(
        self, 
        spreadsheet_id: str, 
        post_urls: List[str]
    ) -> List[Dict]:
        """
        Fetch comments for specific posts from Google Sheets.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            post_urls: List of post URLs to fetch comments for
        
        Returns:
            List of comment dictionaries
        """
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            comments_sheet = spreadsheet.worksheet("Comments")
            
            # Get all comments
            all_comments = comments_sheet.get_all_records()
            
            # Filter comments by link (post URL)
            filtered_comments = [
                comment for comment in all_comments 
                if comment.get('link') in post_urls
            ]
            
            logger.info(f"Fetched {len(filtered_comments)} comments for {len(post_urls)} posts")
            return filtered_comments
        
        except gspread.exceptions.WorksheetNotFound:
            logger.warning(f"Worksheet 'Comments' not found in spreadsheet {spreadsheet_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching comments from Google Sheets: {e}")
            return []
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse timestamp string with multiple format support.
        
        Args:
            timestamp_str: Timestamp string from Google Sheets
        
        Returns:
            datetime object
        """
        # Try ISO 8601 format first
        formats = [
            "%Y-%m-%dT%H:%M:%S",      # 2025-01-15T10:30:00
            "%Y-%m-%d %H:%M:%S",       # 2025-01-15 10:30:00
            "%d/%m/%Y %H:%M:%S",       # 15/01/2025 10:30:00
            "%d/%m/%Y",                # 15/01/2025
            "%Y-%m-%d",                # 2025-01-15
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, raise error
        raise ValueError(f"Could not parse timestamp: {timestamp_str}")


async def fetch_incremental_data_for_client(
    client_config: ClientConfig,
    last_analysis_timestamp: Optional[datetime] = None
) -> Dict[str, any]:
    """
    High-level function to fetch incremental data for a specific client.
    
    Args:
        client_config: ClientConfig object with spreadsheet ID and credentials
        last_analysis_timestamp: Timestamp of last analysis for this client
    
    Returns:
        Dictionary with 'client_id', 'client_name', 'posts', and 'comments' keys
    """
    ingestor = GoogleSheetsIngestor(client_config.credentials_path)
    
    # Fetch new posts
    new_posts = ingestor.fetch_new_posts(
        client_config.spreadsheet_id, 
        last_analysis_timestamp
    )
    
    # If no new posts, return empty
    if not new_posts:
        logger.info(f"No new posts for client {client_config.client_name}")
        return {
            "client_id": client_config.client_id,
            "client_name": client_config.client_name,
            "posts": [],
            "comments": []
        }
    
    # Fetch comments for new posts
    post_urls = [post.get('link') for post in new_posts if post.get('link')]
    comments = ingestor.fetch_comments_for_posts(client_config.spreadsheet_id, post_urls)
    
    return {
        "client_id": client_config.client_id,
        "client_name": client_config.client_name,
        "posts": new_posts,
        "comments": comments
    }


async def fetch_incremental_data_all_clients(
    inputs_dir: str = "/app/orchestrator/inputs"
) -> List[Dict]:
    """
    Fetch incremental data for all enabled clients.
    
    Args:
        inputs_dir: Path to orchestrator/inputs directory
    
    Returns:
        List of dictionaries, one per client with their incremental data
    """
    clients = load_all_clients(inputs_dir)
    
    if not clients:
        logger.warning("No enabled clients found")
        return []
    
    results = []
    for client in clients:
        try:
            # Note: last_analysis_timestamp would be fetched from API per client
            # For now, we'll handle that in __main__.py
            data = await fetch_incremental_data_for_client(client, last_analysis_timestamp=None)
            results.append(data)
        except Exception as e:
            logger.error(f"Failed to fetch data for client {client.client_name}: {e}")
            continue
    
    return results


async def fetch_incremental_data(
    spreadsheet_id: str,
    last_analysis_timestamp: Optional[datetime] = None,
    credentials_path: str = "/app/credentials.json"
) -> Dict[str, List[Dict]]:
    """
    Legacy function for backward compatibility.
    Fetch incremental data from Google Sheets for a single client.
    
    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        last_analysis_timestamp: Timestamp of last analysis
        credentials_path: Path to Google credentials JSON
    
    Returns:
        Dictionary with 'posts' and 'comments' keys
    """
    logger.warning("fetch_incremental_data() is deprecated. Use fetch_incremental_data_for_client() instead.")
    ingestor = GoogleSheetsIngestor(credentials_path)
    
    # Fetch new posts
    new_posts = ingestor.fetch_new_posts(spreadsheet_id, last_analysis_timestamp)
    
    # If no new posts, return empty
    if not new_posts:
        return {"posts": [], "comments": []}
    
    # Fetch comments for new posts
    post_urls = [post.get('post_url') for post in new_posts if post.get('post_url')]
    comments = ingestor.fetch_comments_for_posts(spreadsheet_id, post_urls)
    
    return {
        "posts": new_posts,
        "comments": comments
    }


# Example usage for testing
if __name__ == "__main__":
    import asyncio
    
    async def test_multi_client():
        # Test loading all clients
        clients = load_all_clients("/app/orchestrator/inputs")
        print(f"Found {len(clients)} enabled clients")
        
        for client in clients:
            print(f"\nClient: {client.client_name}")
            print(f"  ID: {client.client_id}")
            print(f"  Spreadsheet: {client.spreadsheet_id}")
            
            # Fetch data for this client
            data = await fetch_incremental_data_for_client(client, last_analysis_timestamp=None)
            print(f"  New posts: {len(data['posts'])}")
            print(f"  New comments: {len(data['comments'])}")
    
    asyncio.run(test_multi_client())

