import sys
import os
import asyncio
from datetime import datetime

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"\n{'='*70}", file=sys.stderr)
print(f"PIXELY PARTNERS - ORCHESTRATOR LOCAL TEST", file=sys.stderr)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", file=sys.stderr)
print(f"{'='*70}\n", file=sys.stderr)

# Import and run
from orchestrator.analyze import analyze_data

print("▶ Executing all Q1-Q10 analysis modules...", file=sys.stderr)
asyncio.run(analyze_data(config={}, module_to_run="all"))
print("✅ All modules completed\n", file=sys.stderr)

# Check output files
output_dir = os.path.join(current_dir, "orchestrator", "outputs")
output_files = [f for f in os.listdir(output_dir) if f.endswith('.json') and f != 'ingested_data.json']
output_files.sort()

print(f"{'='*70}", file=sys.stderr)
print(f"RESULTS - Generated {len(output_files)} analysis JSON files:", file=sys.stderr)
print(f"{'='*70}", file=sys.stderr)

for i, file in enumerate(output_files, 1):
    fpath = os.path.join(output_dir, file)
    size = os.path.getsize(fpath)
    print(f"{i:2d}. {file:45s} ({size:6d} bytes)", file=sys.stderr)

# Show sample from each file
print(f"\n{'='*70}", file=sys.stderr)
print("SAMPLE - First result from Q1 analysis:", file=sys.stderr)
print(f"{'='*70}\n", file=sys.stderr)

import json
q1_path = os.path.join(output_dir, "q1_emociones.json")
if os.path.exists(q1_path):
    with open(q1_path) as f:
        q1_data = json.load(f)
        if q1_data.get('results', {}).get('analisis_por_publicacion'):
            first_post = q1_data['results']['analisis_por_publicacion'][0]
            print(json.dumps(first_post, indent=2, ensure_ascii=False))

print(f"\n{'='*70}", file=sys.stderr)
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", file=sys.stderr)
print(f"{'='*70}\n", file=sys.stderr)
