#!/bin/bash
# Entry point for orchestrator container
# Executes analysis immediately on startup, then starts cron for scheduled runs

set -e

echo "========================================"
echo "Pixely Partners - Orchestrator Starting"
echo "========================================"

# Wait for API to be ready
echo "[Startup] Waiting for API to be ready..."
sleep 10

# Run analysis immediately on container startup (with better error handling)
echo "[Startup] Running initial analysis..."
cd /app
if python -m orchestrator; then
    echo "[Startup] ✅ Initial analysis completed successfully"
else
    echo "[Warning] ⚠️ Initial analysis failed (API may still be starting)"
    echo "[Info] Scheduled runs will retry automatically at 6:00 AM daily"
fi

echo "[Startup] Starting cron daemon for scheduled runs (6:00 AM daily)"

# Start cron in foreground to keep container running
exec cron -f
