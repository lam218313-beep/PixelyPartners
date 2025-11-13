"""
Orchestrator main entry point - allows running as module
"""

import sys
import asyncio
from .analyze import analyze_data

if __name__ == "__main__":
    # Get module name from command line argument (default: "all")
    module_to_run = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    # Run the orchestrator
    asyncio.run(analyze_data(config={}, module_to_run=module_to_run))
