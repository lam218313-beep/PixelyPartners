#!/usr/bin/env python
"""
Pixely Partners - Project Validation Script

Performs quick checks on project structure, syntax, and configuration.
Run this to verify everything is ready to go.
"""

import os
import sys
import json
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check(label: str, condition: bool, details: str = ""):
    """Print a check result."""
    status = f"{GREEN}✓{RESET}" if condition else f"{RED}✗{RESET}"
    msg = f"{status} {label}"
    if details:
        msg += f" ({details})"
    print(msg)
    return condition


def main():
    """Run validation checks."""
    print(f"\n{YELLOW}=== Pixely Partners Project Validation ==={RESET}\n")

    root = Path(__file__).parent
    all_pass = True

    # 1. Directory Structure
    print(f"{YELLOW}[DIRECTORIES]{RESET}")
    dirs_to_check = [
        "orchestrator",
        "orchestrator/analysis_modules",
        "orchestrator/outputs",
        "frontend",
        "frontend/view_components",
        "frontend/view_components/qual",
        "tests",
    ]
    for d in dirs_to_check:
        all_pass &= check(f"  {d}/", (root / d).is_dir())

    # 2. Core Python Files
    print(f"\n{YELLOW}[PYTHON FILES]{RESET}")
    files_to_check = [
        "orchestrator/base_analyzer.py",
        "orchestrator/analyze.py",
        "frontend/app.py",
        "frontend/view_components/_outputs.py",
        "tests/test_imports.py",
    ]
    for f in files_to_check:
        all_pass &= check(f"  {f}", (root / f).is_file())

    # 3. Analysis Modules (Q1-Q10)
    print(f"\n{YELLOW}[ANALYSIS MODULES]{RESET}")
    for i in range(1, 11):
        module_name = f"q{i}_*.py"
        module_files = list((root / "orchestrator/analysis_modules").glob(f"q{i}_*.py"))
        all_pass &= check(f"  Q{i}", len(module_files) > 0, f"{len(module_files)} file(s)")

    # 4. View Components (Q1-Q10)
    print(f"\n{YELLOW}[VIEW COMPONENTS]{RESET}")
    for i in range(1, 11):
        view_file = root / "frontend/view_components/qual" / f"q{i}_view.py"
        all_pass &= check(f"  Q{i} view", view_file.is_file())

    # 5. Configuration Files
    print(f"\n{YELLOW}[CONFIGURATION FILES]{RESET}")
    config_files = [
        "requirements.txt",
        ".env.example",
        "docker-compose.yml",
        "Dockerfile.orchestrator",
        "Dockerfile.frontend",
        ".gitignore",
    ]
    for f in config_files:
        all_pass &= check(f"  {f}", (root / f).is_file())

    # 6. Documentation
    print(f"\n{YELLOW}[DOCUMENTATION]{RESET}")
    docs = ["README.md", "QUICKSTART.md"]
    for f in docs:
        all_pass &= check(f"  {f}", (root / f).is_file())

    # 7. Example Data
    print(f"\n{YELLOW}[EXAMPLE DATA]{RESET}")
    ingested_file = root / "orchestrator/outputs/ingested_data.json"
    if ingested_file.is_file():
        try:
            with open(ingested_file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            posts_count = len(data.get("posts", []))
            all_pass &= check(f"  ingested_data.json", True, f"{posts_count} posts")
        except Exception as e:
            all_pass &= check(f"  ingested_data.json", False, f"Error: {e}")
    else:
        all_pass &= check(f"  ingested_data.json", False)

    # 8. Python Syntax Check
    print(f"\n{YELLOW}[PYTHON SYNTAX]{RESET}")
    import py_compile
    py_files = list(root.glob("orchestrator/**/*.py")) + list(root.glob("frontend/**/*.py")) + list(root.glob("tests/**/*.py"))
    syntax_pass = True
    for py_file in py_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            print(f"  {RED}✗{RESET} {py_file.relative_to(root)}: {e}")
            syntax_pass = False
    if syntax_pass:
        check(f"  All Python files", True, f"{len(py_files)} files validated")
    else:
        all_pass = False

    # 9. Environment Setup
    print(f"\n{YELLOW}[ENVIRONMENT SETUP]{RESET}")
    env_file = root / ".env"
    env_example = root / ".env.example"
    if env_file.is_file():
        check("  .env file", True)
    else:
        check("  .env file", False, f"Copy from .env.example")
        all_pass = False

    # Summary
    print(f"\n{YELLOW}=== Summary ==={RESET}")
    if all_pass:
        print(f"{GREEN}OK: All checks passed! Project is ready.{RESET}")
        print(f"\n{YELLOW}Next steps:{RESET}")
        print(f"  1. Create .env from .env.example (add OPENAI_API_KEY)")
        print(f"  2. Run: python orchestrator/analyze.py")
        print(f"  3. Run: streamlit run frontend/app.py")
        print(f"  Or use Docker: docker-compose up --build")
        return 0
    else:
        print(f"{RED}FAIL: Some checks failed. See above for details.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
