import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("Testing orchestrator execution...", file=sys.stderr)

# Test 1: Basic imports
try:
    from orchestrator.base_analyzer import BaseAnalyzer
    print("✅ BaseAnalyzer import OK", file=sys.stderr)
except Exception as e:
    print(f"❌ BaseAnalyzer import FAILED: {e}", file=sys.stderr)

# Test 2: Q1 module import
try:
    from orchestrator.analysis_modules.q1_emociones import Q1Emociones
    print("✅ Q1Emociones import OK", file=sys.stderr)
except Exception as e:
    print(f"❌ Q1Emociones import FAILED: {e}", file=sys.stderr)

# Test 3: Check ingested_data.json exists
data_file = os.path.join(current_dir, "orchestrator", "outputs", "ingested_data.json")
if os.path.exists(data_file):
    print(f"✅ ingested_data.json found at {data_file}", file=sys.stderr)
    with open(data_file, 'r') as f:
        import json
        data = json.load(f)
        posts = data.get('posts', [])
        comments = data.get('comments', [])
        print(f"   - Posts: {len(posts)}", file=sys.stderr)
        print(f"   - Comments: {len(comments)}", file=sys.stderr)
else:
    print(f"❌ ingested_data.json NOT found at {data_file}", file=sys.stderr)

# Test 4: Try to execute analyze
print("Running analyze_data()...", file=sys.stderr)
import asyncio
from orchestrator.analyze import analyze_data

asyncio.run(analyze_data(config={}, module_to_run="Q1"))
print("✅ analyze_data() completed", file=sys.stderr)

# Test 5: Check output files
output_dir = os.path.join(current_dir, "orchestrator", "outputs")
print(f"Output files in {output_dir}:", file=sys.stderr)
if os.path.exists(output_dir):
    for file in os.listdir(output_dir):
        fpath = os.path.join(output_dir, file)
        size = os.path.getsize(fpath)
        print(f"  - {file} ({size} bytes)", file=sys.stderr)
