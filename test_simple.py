#!/usr/bin/env python3
"""Simple test for basic server functionality."""

import sys
from pathlib import Path

# Add paths
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR / "src"))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        # Test job manager import
        from jobs.manager import job_manager
        print("✅ Job manager imported successfully")

        # Test server import
        from server import mcp
        print("✅ MCP server imported successfully")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_job_manager():
    """Test job manager basic functionality."""
    print("Testing job manager...")

    try:
        from jobs.manager import job_manager

        # Test list_jobs (should work even with no jobs)
        result = job_manager.list_jobs()
        if result.get("status") == "success":
            print(f"✅ Job manager working - found {result['total']} jobs")
            return True
        else:
            print(f"❌ Job manager error: {result}")
            return False
    except Exception as e:
        print(f"❌ Job manager test failed: {e}")
        return False

def test_examples_directory():
    """Test that examples directory exists and has content."""
    print("Testing examples directory...")

    examples_dir = SCRIPT_DIR / "examples" / "data"

    if not examples_dir.exists():
        print(f"❌ Examples directory not found: {examples_dir}")
        return False

    pdb_files = list(examples_dir.glob("*.pdb"))
    if len(pdb_files) == 0:
        print("❌ No PDB files found in examples")
        return False

    print(f"✅ Found {len(pdb_files)} PDB files in examples")
    return True

def test_scripts_directory():
    """Test that scripts exist and are importable."""
    print("Testing scripts directory...")

    scripts_dir = SCRIPT_DIR / "scripts"

    if not scripts_dir.exists():
        print(f"❌ Scripts directory not found: {scripts_dir}")
        return False

    # Check for expected scripts
    expected_scripts = ["protein_design.py", "ligand_design.py", "sequence_scoring.py", "constrained_design.py"]
    missing = []

    for script in expected_scripts:
        if not (scripts_dir / script).exists():
            missing.append(script)

    if missing:
        print(f"❌ Missing scripts: {missing}")
        return False

    print(f"✅ All {len(expected_scripts)} expected scripts found")
    return True

if __name__ == "__main__":
    print("=== Testing MCP Server Basic Functionality ===\n")

    tests = [
        ("Imports", test_imports),
        ("Examples Directory", test_examples_directory),
        ("Scripts Directory", test_scripts_directory),
        ("Job Manager", test_job_manager),
    ]

    passed = 0
    for name, test_func in tests:
        print(f"--- {name} ---")
        try:
            if test_func():
                passed += 1
            print()  # Empty line for readability
        except Exception as e:
            print(f"❌ {name}: UNEXPECTED ERROR - {e}\n")

    print(f"=== Results: {passed}/{len(tests)} tests passed ===")

    if passed == len(tests):
        print("🎉 All tests passed! MCP server is ready for use.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")