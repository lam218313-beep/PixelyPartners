"""
Authentication view for Pixely Partners Frontend
"""

import streamlit as st
from pathlib import Path
from api_client import APIClient, init_session_state, logout
from cookie_manager import CookieManager


def display_login():
    """Display login form."""
    
    # Logo before form
    logo_path = Path(__file__).parent / "assets" / "Logo Rosa SVG_Mesa de trabajo 1-01-01.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            import base64
            logo_data = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""<div class="login-logo">
                <img src="data:image/png;base64,{logo_data}" alt="Pixely Partners">
            </div>""",
            unsafe_allow_html=True
        )
    
    with st.form("login_form"):
        st.markdown("### Login")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        remember_me = st.checkbox("Recordarme (mantener sesión por 7 días)", value=True)
        submit = st.form_submit_button("Iniciar Sesión")
        
        if submit:
            if not username or not password:
                st.error("Por favor ingresa usuario y contraseña")
                return
            
            try:
                client = APIClient()
                auth_data = client.login(username, password)
                
                # Store in session state
                st.session_state.access_token = auth_data["access_token"]
                st.session_state.token_type = auth_data["token_type"]
                st.session_state.user_email = auth_data.get("user_email")
                st.session_state.tenant_id = auth_data.get("tenant_id")
                
                ficha_name = None
                # Get user's first ficha cliente
                if "ficha_cliente_id" in auth_data:
                    st.session_state.ficha_cliente_id = auth_data["ficha_cliente_id"]
                    
                    # Get ficha details
                    ficha = client.get_ficha_cliente(auth_data["ficha_cliente_id"])
                    if ficha:
                        ficha_name = ficha.get("nombre_cliente", "Cliente")
                        st.session_state.ficha_cliente_name = ficha_name
                
                # Save to cookie if "Remember Me" is checked
                if remember_me:
                    cookie_mgr = CookieManager()
                    cookie_mgr.save_auth_cookie(
                        access_token=auth_data["access_token"],
                        user_email=auth_data.get("user_email"),
                        tenant_id=auth_data.get("tenant_id"),
                        ficha_cliente_id=auth_data.get("ficha_cliente_id"),
                        ficha_cliente_name=ficha_name,
                        days=7
                    )
                
                st.success("✅ Inicio de sesión exitoso")
                st.rerun()
                
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Error inesperado: {e}")
    
    # Footer debajo del formulario
    st.markdown(
        """<div class="login-footer">
            Hecho para <span class="dikimro">DIKIMRO</span> ♥
        </div>""",
        unsafe_allow_html=True
    )


def display_logout_button():
    """Display logout button in sidebar."""
    if st.sidebar.button("🚪 Cerrar Sesión"):
        # Clear cookie
        cookie_mgr = CookieManager()
        cookie_mgr.clear_auth_cookie()
        
        # Clear session
        logout()
        st.rerun()


def display_user_info():
    """Display user info in sidebar."""
    
    # Logo in sidebar
    logo_path = Path(__file__).parent / "assets" / "Logo Rosa SVG_Mesa de trabajo 1-01-01.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            import base64
            logo_data = base64.b64encode(f.read()).decode()
        st.sidebar.markdown(
            f"""<div class="sidebar-logo">
                <img src="data:image/png;base64,{logo_data}" alt="Pixely Partners">
            </div>""",
            unsafe_allow_html=True
        )
    
    st.sidebar.markdown("---")
