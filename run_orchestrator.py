#!/usr/bin/env python
"""
Entry point to run the orchestrator from the project root.
This script properly sets up the Python path and executes the analysis.
"""

import sys
import os

# Add current directory to Python path so relative imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import and run the orchestrator
if __name__ == "__main__":
    # Import the module which will execute if __name__ == "__main__"
    import orchestrator.analyze

