"""
Cookie management for persistent authentication
"""

import streamlit as st
import extra_streamlit_components as stx
from typing import Optional
import json
from datetime import datetime, timedelta


class CookieManager:
    """Manage authentication cookies for persistent login."""
    
    def __init__(self, cookie_name: str = "pixely_auth"):
        self.cookie_name = cookie_name
        self.cookie_manager = stx.CookieManager()
    
    def save_auth_cookie(
        self,
        access_token: str,
        user_email: str,
        tenant_id: str,
        ficha_cliente_id: Optional[str] = None,
        ficha_cliente_name: Optional[str] = None,
        days: int = 7
    ):
        """
        Save authentication data to cookie.
        
        Args:
            access_token: JWT token
            user_email: User email
            tenant_id: Tenant ID
            ficha_cliente_id: Client ficha ID
            ficha_cliente_name: Client ficha name
            days: Cookie expiration in days (default 7)
        """
        auth_data = {
            "access_token": access_token,
            "user_email": user_email,
            "tenant_id": tenant_id,
            "ficha_cliente_id": ficha_cliente_id,
            "ficha_cliente_name": ficha_cliente_name,
            "saved_at": datetime.now().isoformat()
        }
        
        # Calculate expiration
        expires_at = datetime.now() + timedelta(days=days)
        
        # Save to cookie
        self.cookie_manager.set(
            self.cookie_name,
            json.dumps(auth_data),
            expires_at=expires_at
        )
    
    def load_auth_cookie(self) -> Optional[dict]:
        """
        Load authentication data from cookie.
        
        Returns:
            Dict with auth data or None if not found/expired
        """
        try:
            cookie_value = self.cookie_manager.get(self.cookie_name)
            if not cookie_value:
                return None
            
            auth_data = json.loads(cookie_value)
            
            # Check if token is expired (JWT tokens expire in 30 min by default)
            saved_at = datetime.fromisoformat(auth_data.get("saved_at"))
            token_age = datetime.now() - saved_at
            
            # If saved more than 7 days ago, consider expired
            if token_age.days > 7:
                self.clear_auth_cookie()
                return None
            
            return auth_data
            
        except Exception as e:
            st.error(f"Error loading auth cookie: {e}")
            return None
    
    def clear_auth_cookie(self):
        """Clear authentication cookie."""
        self.cookie_manager.delete(self.cookie_name)
    
    def restore_session_from_cookie(self) -> bool:
        """
        Restore session state from cookie.
        
        Returns:
            True if session was restored, False otherwise
        """
        auth_data = self.load_auth_cookie()
        if not auth_data:
            return False
        
        # Restore session state
        st.session_state.access_token = auth_data.get("access_token")
        st.session_state.token_type = "bearer"
        st.session_state.user_email = auth_data.get("user_email")
        st.session_state.tenant_id = auth_data.get("tenant_id")
        st.session_state.ficha_cliente_id = auth_data.get("ficha_cliente_id")
        st.session_state.ficha_cliente_name = auth_data.get("ficha_cliente_name")
        
        return True
