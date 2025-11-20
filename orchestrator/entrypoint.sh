#!/bin/bash
# Entry point for orchestrator container
# Executes analysis immediately on startup, then starts cron for scheduled runs

set -e

echo "========================================"
echo "Pixely Partners - Orchestrator Starting"
echo "========================================"

# Run analysis immediately on container startup
echo "[Startup] Running initial analysis..."
cd /app
python -m orchestrator || echo "[Warning] Initial analysis failed, but continuing..."

echo "[Startup] Initial analysis complete"
echo "[Startup] Starting cron daemon for scheduled runs (6:00 AM daily)"

# Start cron in foreground to keep container running
exec cron -f
