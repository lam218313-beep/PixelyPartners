"""
Style Loader for Pixely Partners Frontend
Loads external CSS files and applies them to Streamlit app
"""

import streamlit as st
from pathlib import Path


def load_css_file(css_filename):
    """
    Load an external CSS file and inject it into Streamlit.
    
    Args:
        css_filename (str): Name of the CSS file in the assets folder
    """
    css_path = Path(__file__).parent / "assets" / css_filename
    
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found: {css_filename}")


def load_particles_background():
    """Load particles animation background."""
    js_path = Path(__file__).parent / "assets" / "particles.js"
    
    if js_path.exists():
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
            st.markdown(f"<script>{js_content}</script>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Particles JS file not found")


def load_all_styles():
    """Load all custom styles for the application."""
    st.markdown("""
    <style>
    body, .stApp, .main {
        background: radial-gradient(ellipse at center, #1a0a15 0%, #000000 70%) !important;
        min-height: 100vh !important;
        height: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    load_css_file("header_footer.css")
    load_css_file("sidebar_styles.css")
    load_css_file("glassmorphism.css")
    load_particles_background()


def load_login_styles():
    """Load styles specifically for login page."""
    load_css_file("login_styles.css")
    load_css_file("header_footer.css")
    load_css_file("glassmorphism.css")
    load_particles_background()


def load_dashboard_styles():
    """Load styles specifically for dashboard pages."""
    st.markdown("""
    <style>
    body, .stApp, .main {
        background: radial-gradient(ellipse at center, #1a0a15 0%, #000000 70%) !important;
        min-height: 100vh !important;
        height: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    load_css_file("sidebar_styles.css")
    load_css_file("header_footer.css")
    load_css_file("glassmorphism.css")
    load_particles_background()
