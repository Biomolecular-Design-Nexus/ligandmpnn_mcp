#!/usr/bin/env python3
"""Simple test for MCP server tools."""

import sys
from pathlib import Path

# Add paths
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR / "src"))

def test_validate_pdb():
    """Test PDB validation tool."""
    print("Testing validate_pdb_structure tool...")

    # Import the direct function from server module
    import server

    # Test with example PDB file
    example_file = SCRIPT_DIR / "examples" / "data" / "4GYT.pdb"

    if example_file.exists():
        result = server.validate_pdb_structure(str(example_file))
        print(f"Validation result: {result}")
        return result.get("status") == "success"
    else:
        print(f"Example file not found: {example_file}")
        return False

def test_list_examples():
    """Test list example structures tool."""
    print("Testing list_example_structures tool...")

    import server

    result = server.list_example_structures()
    print(f"Examples result: {result}")
    return result.get("status") == "success"

def test_job_management():
    """Test job management tools."""
    print("Testing job management...")

    import server

    result = server.list_jobs()
    print(f"List jobs result: {result}")
    return result.get("status") == "success"

if __name__ == "__main__":
    print("=== Testing MCP Server Tools ===")

    tests = [
        ("List Examples", test_list_examples),
        ("Validate PDB", test_validate_pdb),
        ("Job Management", test_job_management),
    ]

    passed = 0
    for name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {name}: PASSED")
                passed += 1
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")

    print(f"\nResults: {passed}/{len(tests)} tests passed")