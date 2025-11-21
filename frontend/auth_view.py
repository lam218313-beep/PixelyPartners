"""
Authentication view for Pixely Partners Frontend
"""

import streamlit as st
from api_client import APIClient, init_session_state, logout


def display_login():
    """Display login form."""
    st.title("🔐 Pixely Partners - Login")
    
    st.markdown("""
    ### Bienvenido al Dashboard de Análisis
    
    Ingresa tus credenciales para acceder a los insights de tu marca.
    """)
    
    with st.form("login_form"):
        username = st.text_input("Usuario", placeholder="tu@email.com")
        password = st.text_input("Contraseña", type="password")
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
                
                # Get user's first ficha cliente
                if "ficha_cliente_id" in auth_data:
                    st.session_state.ficha_cliente_id = auth_data["ficha_cliente_id"]
                    
                    # Get ficha details
                    ficha = client.get_ficha_cliente(auth_data["ficha_cliente_id"])
                    if ficha:
                        st.session_state.ficha_cliente_name = ficha.get("nombre_cliente", "Cliente")
                
                st.success("✅ Inicio de sesión exitoso")
                st.rerun()
                
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Error inesperado: {e}")


def display_logout_button():
    """Display logout button in sidebar."""
    if st.sidebar.button("🚪 Cerrar Sesión"):
        logout()
        st.rerun()


def display_user_info():
    """Display user info in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Usuario")
    
    user_email = st.session_state.get("user_email", "N/A")
    st.sidebar.text(f"Email: {user_email}")
    
    ficha_name = st.session_state.get("ficha_cliente_name", "N/A")
    st.sidebar.text(f"Cliente: {ficha_name}")
    
    display_logout_button()
