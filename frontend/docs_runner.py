"""Docs runner: import legacy `docs/*.py` view modules and expose their display functions in Streamlit.

This module discovers Python files under the repo `docs/` folder, imports them as `docs.<mod>` and
looks for callables whose name starts with `display_`. It then shows a selector and calls the chosen
display function inside the Streamlit app.
"""
from __future__ import annotations

import importlib
import inspect
import pkgutil
import streamlit as st  # type: ignore
import os
from typing import Callable, Dict, List


def discover_docs_displayables() -> Dict[str, Callable]:
    """Discover display callables in modules under the `docs` package.

    Returns a mapping label -> callable.
    """
    results: Dict[str, Callable] = {}

    # Ensure docs is importable
    try:
        import docs  # type: ignore
    except Exception:
        st.error("No se encontró el paquete 'docs' en el path. Asegúrate de que /docs está presente in the repo.")
        return results

    # Iterate over modules in docs package
    pkg = docs  # type: ignore
    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        full_name = f"docs.{name}"
        try:
            mod = importlib.import_module(full_name)
        except Exception as e:
            # Don't raise; show a warning and continue
            st.warning(f"No se pudo importar {full_name}: {e}")
            continue

        # Find callables that look like "display_..."
        for attr_name, attr in inspect.getmembers(mod, inspect.isfunction):
            if attr_name.startswith("display_"):
                label = f"{name}::{attr_name}"
                results[label] = attr

    return results


def run_docs_runner():
    st.sidebar.header("Legacy docs plots")
    displayables = discover_docs_displayables()
    if not displayables:
        st.info("No se encontraron visualizadores en 'docs/'.")
        return

    choice = st.sidebar.selectbox("Selecciona vista (docs)", list(displayables.keys()))
    func = displayables.get(choice)
    if func:
        try:
            func()
        except Exception as e:
            st.error(f"Error al ejecutar la vista seleccionada: {e}")


if __name__ == "__main__":
    run_docs_runner()
