"""
Pixely Partners - Google Sheets Integration Module

This module handles data ingestion from Google Sheets for each client.
It detects new posts based on timestamp comparison and returns only incremental data.
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)


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
                        logger.warning(f"Post {post.get('post_url')} missing timestamp, skipping")
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
            
            # Filter comments by post_url
            filtered_comments = [
                comment for comment in all_comments 
                if comment.get('post_url') in post_urls
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


async def fetch_incremental_data(
    spreadsheet_id: str,
    last_analysis_timestamp: Optional[datetime] = None,
    credentials_path: str = "/app/credentials.json"
) -> Dict[str, List[Dict]]:
    """
    High-level function to fetch incremental data from Google Sheets.
    
    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        last_analysis_timestamp: Timestamp of last analysis
        credentials_path: Path to Google credentials JSON
    
    Returns:
        Dictionary with 'posts' and 'comments' keys
    """
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
    
    async def test():
        # Example: Fetch data for a client
        spreadsheet_id = os.environ.get("GOOGLE_SHEETS_CLIENT_1_SPREADSHEET_ID")
        last_timestamp = datetime(2025, 11, 1)  # Example: November 1, 2025
        
        data = await fetch_incremental_data(spreadsheet_id, last_timestamp)
        print(f"New posts: {len(data['posts'])}")
        print(f"New comments: {len(data['comments'])}")
    
    asyncio.run(test())
