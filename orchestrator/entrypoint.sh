#!/bin/bash
# Entry point for orchestrator container
# Allows running specific modules or all

# Default to running all modules
MODULE=${1:-all}

cd /app
python -m orchestrator.analyze "$MODULE"
