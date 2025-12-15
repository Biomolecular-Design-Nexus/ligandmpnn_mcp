#!/usr/bin/env python3
"""
MCP Server for LigandMPNN

Provides both synchronous and asynchronous (submit) APIs for protein design tools.
Fast operations (< 10 minutes) use sync API, longer operations use submit API.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import sys
import json

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("LigandMPNN")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)


@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)


@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)


@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)


@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Synchronous Tools (for fast operations < 10 min)
# ==============================================================================

@mcp.tool()
def simple_design(
    input_file: str,
    chains: Optional[str] = None,
    num_sequences: int = 3,
    temperature: float = 0.1,
    output_dir: Optional[str] = None
) -> dict:
    """
    Generate protein sequences for a given PDB structure using ProteinMPNN.

    Fast operation that completes in ~10 seconds. Use this for single structure design.

    Args:
        input_file: Path to input PDB file
        chains: Space-separated chain IDs to design (e.g., "A B")
        num_sequences: Number of sequences to generate (default: 3)
        temperature: Sampling temperature (default: 0.1)
        output_dir: Optional directory to save output files

    Returns:
        Dictionary with generated sequences and metadata
    """
    from protein_design import run_protein_design

    try:
        result = run_protein_design(
            input_file=input_file,
            output_file=output_dir,
            num_sequences=num_sequences,
            temperature=temperature,
            chains=chains
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        if hasattr(logger, 'error'):
            logger.error(f"simple_design failed: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
def sequence_scoring(
    input_file: str,
    fasta_sequences: Optional[str] = None,
    save_probs: bool = False,
    output_dir: Optional[str] = None
) -> dict:
    """
    Score protein sequences using ProteinMPNN likelihood calculation.

    Fast operation that completes in ~8 seconds. Use this for sequence evaluation.

    Args:
        input_file: Path to input PDB structure file
        fasta_sequences: Custom sequences to score (format: SEQ1/SEQ2)
        save_probs: Save per-residue probabilities
        output_dir: Optional directory to save output files

    Returns:
        Dictionary with sequence scores and analysis
    """
    from sequence_scoring import run_sequence_scoring

    try:
        # Parse sequences if provided
        sequences = None
        if fasta_sequences:
            sequences = [seq.strip() for seq in fasta_sequences.split("/") if seq.strip()]

        result = run_sequence_scoring(
            input_file=input_file,
            output_file=output_dir,
            sequences=sequences,
            save_probs=save_probs
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        if hasattr(logger, 'error'):
            logger.error(f"sequence_scoring failed: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
def constrained_design(
    input_file: str,
    chains_to_design: Optional[str] = None,
    fixed_positions: Optional[str] = None,
    num_sequences: int = 3,
    output_dir: Optional[str] = None
) -> dict:
    """
    Design proteins with constrained/fixed positions using ProteinMPNN.

    Fast operation for constrained design. Use this for position-specific constraints.

    Args:
        input_file: Path to input PDB file
        chains_to_design: Chains to design (e.g., "A B")
        fixed_positions: Fixed positions per chain (format: '1 2 3, 10 11 12')
        num_sequences: Number of sequences to generate
        output_dir: Optional directory to save output files

    Returns:
        Dictionary with constrained sequences and metadata
    """
    from constrained_design import run_constrained_design

    try:
        # Parse fixed positions
        fixed_residues = None
        if fixed_positions:
            # Split by commas for multiple chains, then by spaces for positions
            if ',' in fixed_positions:
                fixed_residues = [pos.strip().split() for pos in fixed_positions.split(',')]
            else:
                fixed_residues = fixed_positions.strip().split()

        result = run_constrained_design(
            input_file=input_file,
            output_file=output_dir,
            num_sequences=num_sequences,
            fixed_residues=fixed_residues
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        if hasattr(logger, 'error'):
            logger.error(f"constrained_design failed: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
def ca_only_design(
    input_file: str,
    chains: Optional[str] = None,
    model: str = "v_48_020",
    num_sequences: int = 3,
    output_dir: Optional[str] = None
) -> dict:
    """
    Design sequences using only carbon alpha atoms (backbone traces).

    Fast operation for CA-only design. Use this for backbone-only structures.

    Args:
        input_file: Path to input PDB file (full-atom or CA-only)
        chains: Chains to design using CA coordinates
        model: CA model version (v_48_002, v_48_010, v_48_020)
        num_sequences: Number of sequences to generate
        output_dir: Optional directory to save output files

    Returns:
        Dictionary with CA-designed sequences and metadata
    """
    from protein_design import run_protein_design

    try:
        # Configure for CA-only design
        ca_config = {
            "model_type": f"protein_mpnn_{model}",
            "ca_only": True
        }

        result = run_protein_design(
            input_file=input_file,
            output_file=output_dir,
            num_sequences=num_sequences,
            config=ca_config,
            chains=chains
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        if hasattr(logger, 'error'):
            logger.error(f"ca_only_design failed: {e}")
        return {"status": "error", "error": str(e)}

# ==============================================================================
# Submit Tools (for long-running operations > 10 min)
# ==============================================================================

@mcp.tool()
def submit_batch_design(
    input_dir: str,
    file_pattern: str = "*.pdb",
    chains: Optional[str] = None,
    num_sequences: int = 2,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch processing for multiple PDB files.

    This operation may take >10 minutes for large batches. Returns a job_id for tracking.

    Args:
        input_dir: Directory containing PDB files to process
        file_pattern: Pattern to match PDB files (default: "*.pdb")
        chains: Chains to design (empty = auto-detect)
        num_sequences: Number of sequences per structure
        output_dir: Directory for outputs
        job_name: Optional name for tracking

    Returns:
        Dictionary with job_id. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results
        - get_job_log(job_id) to see logs
    """
    # Create a batch script that processes multiple files
    script_path = str(SCRIPTS_DIR / "protein_design.py")

    # Find files matching pattern
    input_path = Path(input_dir)
    if not input_path.exists():
        return {"status": "error", "error": f"Input directory not found: {input_dir}"}

    files = list(input_path.glob(file_pattern))
    if not files:
        return {"status": "error", "error": f"No files matching pattern '{file_pattern}' in {input_dir}"}

    # Convert file list to comma-separated string for batch processing
    input_files = ",".join(str(f) for f in files)

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_files,
            "num_sequences": num_sequences,
            "chains": chains,
            "output_dir": output_dir
        },
        job_name=job_name or f"batch_{len(files)}_files"
    )


@mcp.tool()
def submit_large_design(
    input_file: str,
    chains: Optional[str] = None,
    num_sequences: int = 50,
    temperature: float = 0.1,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit large-scale sequence design for background processing.

    Use this for generating many sequences (>10) which may take longer.

    Args:
        input_file: Path to input PDB file
        chains: Space-separated chain IDs to design
        num_sequences: Number of sequences to generate (large number)
        temperature: Sampling temperature
        output_dir: Directory for outputs
        job_name: Optional name for tracking

    Returns:
        Dictionary with job_id for tracking the design job
    """
    script_path = str(SCRIPTS_DIR / "protein_design.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "chains": chains,
            "num_sequences": num_sequences,
            "temperature": temperature,
            "output_dir": output_dir
        },
        job_name=job_name or f"large_design_{num_sequences}_seqs"
    )

# ==============================================================================
# Validation and Utility Tools
# ==============================================================================

@mcp.tool()
def validate_pdb_structure(input_file: str) -> dict:
    """
    Validate a PDB structure for ProteinMPNN compatibility.

    Quick validation of PDB file format and chains.

    Args:
        input_file: Path to PDB file to validate

    Returns:
        Dictionary with validation results and structure info
    """
    from lib.validation import validate_pdb_file
    from lib.io import load_structure_info

    try:
        # Basic file validation
        validate_pdb_file(Path(input_file))

        # Get structure information
        info = load_structure_info(Path(input_file))

        return {
            "status": "success",
            "file_path": input_file,
            "valid": True,
            "chains": info.get("chains", []),
            "num_residues": info.get("num_residues", 0),
            "has_ligands": info.get("has_ligands", False),
            "structure_info": info
        }
    except FileNotFoundError:
        return {"status": "error", "error": f"File not found: {input_file}", "valid": False}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid PDB file: {e}", "valid": False}
    except Exception as e:
        return {"status": "error", "error": f"Validation failed: {e}", "valid": False}


@mcp.tool()
def list_example_structures() -> dict:
    """
    List available example PDB structures for testing.

    Returns paths to example structures included with ProteinMPNN.

    Returns:
        Dictionary with example structure paths and descriptions
    """
    examples_dir = MCP_ROOT / "examples" / "data"

    if not examples_dir.exists():
        return {"status": "error", "error": "Examples directory not found"}

    structures = []
    for pdb_file in examples_dir.glob("*.pdb"):
        # Try to get basic info about each structure
        try:
            from lib.io import load_structure_info
            info = load_structure_info(pdb_file)
            structures.append({
                "path": str(pdb_file),
                "name": pdb_file.name,
                "chains": info.get("chains", []),
                "num_residues": info.get("num_residues", 0),
                "has_ligands": info.get("has_ligands", False)
            })
        except:
            # Basic fallback info if parsing fails
            structures.append({
                "path": str(pdb_file),
                "name": pdb_file.name,
                "chains": "unknown",
                "num_residues": 0,
                "has_ligands": False
            })

    return {
        "status": "success",
        "examples_dir": str(examples_dir),
        "structures": structures,
        "total_structures": len(structures)
    }

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()