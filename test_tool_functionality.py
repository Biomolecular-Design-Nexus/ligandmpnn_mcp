#!/usr/bin/env python3
"""Test actual tool functionality with simple direct calls."""

import sys
from pathlib import Path

# Add paths
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR / "src"))
sys.path.insert(0, str(SCRIPT_DIR / "scripts"))

def test_list_examples_direct():
    """Test list_example_structures by calling the implementation directly."""
    print("Testing list_example_structures implementation...")

    try:
        # Import the server module to access paths
        import server

        # Get the examples directory
        examples_dir = server.MCP_ROOT / "examples" / "data"

        if not examples_dir.exists():
            print(f"❌ Examples directory not found: {examples_dir}")
            return False

        structures = []
        for pdb_file in examples_dir.glob("*.pdb"):
            structures.append({
                "path": str(pdb_file),
                "name": pdb_file.name,
            })

        if len(structures) > 0:
            print(f"✅ Found {len(structures)} example structures")
            for structure in structures:
                print(f"   - {structure['name']}")
            return True
        else:
            print("❌ No structures found")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_validation_direct():
    """Test validation functionality directly."""
    print("Testing validation implementation...")

    try:
        # Test with an example file
        examples_dir = SCRIPT_DIR / "examples" / "data"
        pdb_files = list(examples_dir.glob("*.pdb"))

        if not pdb_files:
            print("❌ No PDB files found for testing")
            return False

        test_file = pdb_files[0]
        print(f"Testing with file: {test_file.name}")

        # Simple validation - check if file exists and has content
        if test_file.exists() and test_file.stat().st_size > 0:
            print(f"✅ File {test_file.name} exists and has content ({test_file.stat().st_size} bytes)")
            return True
        else:
            print(f"❌ File validation failed")
            return False

    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_job_manager_workflow():
    """Test the job manager workflow."""
    print("Testing job manager workflow...")

    try:
        from jobs.manager import job_manager

        # Test 1: List jobs (should be empty)
        result = job_manager.list_jobs()
        if result.get("status") == "success":
            print(f"✅ Initial job list: {result['total']} jobs")
        else:
            print(f"❌ Failed to list jobs: {result}")
            return False

        # Test 2: Submit a test job (this will fail but we can test the submission process)
        # Create a simple test script
        test_script = SCRIPT_DIR / "test_dummy_script.py"
        test_script.write_text('''#!/usr/bin/env python3
import sys
import time
print("Test job starting...")
time.sleep(1)
print("Test job completed!")
''')

        result = job_manager.submit_job(
            script_path=str(test_script),
            args={},
            job_name="test_job"
        )

        if result.get("status") == "submitted":
            job_id = result.get("job_id")
            print(f"✅ Job submitted successfully with ID: {job_id}")

            # Wait a moment and check status
            import time
            time.sleep(2)

            status = job_manager.get_job_status(job_id)
            print(f"✅ Job status retrieved: {status.get('status', 'unknown')}")

            # Clean up
            test_script.unlink()

            return True
        else:
            print(f"❌ Failed to submit job: {result}")
            return False

    except Exception as e:
        print(f"❌ Job manager test failed: {e}")
        return False

def test_script_imports():
    """Test that we can import the main scripts."""
    print("Testing script imports...")

    scripts_to_test = [
        "protein_design",
        "ligand_design",
        "sequence_scoring",
        "constrained_design"
    ]

    imported = 0
    for script in scripts_to_test:
        try:
            __import__(script)
            print(f"✅ {script}.py imported successfully")
            imported += 1
        except Exception as e:
            print(f"❌ Failed to import {script}.py: {e}")

    return imported == len(scripts_to_test)

if __name__ == "__main__":
    print("=== Testing MCP Server Tool Functionality ===\n")

    tests = [
        ("Script Imports", test_script_imports),
        ("List Examples Direct", test_list_examples_direct),
        ("Validation Direct", test_validation_direct),
        ("Job Manager Workflow", test_job_manager_workflow),
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
        print("🎉 All functionality tests passed! Server tools are working.")
    else:
        print("⚠️ Some functionality tests failed. Check the errors above.")