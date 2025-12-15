#!/usr/bin/env python3
"""
Script: sequence_scoring.py
Description: Protein sequence likelihood calculation using ProteinMPNN/LigandMPNN

Original Use Case: examples/use_case_3_sequence_scoring.py
Dependencies Removed: Simplified Args class structure, externalized configuration

Usage:
    python scripts/sequence_scoring.py --input <input_file> --output <output_file>

Example:
    python scripts/sequence_scoring.py --input examples/data/1BC8.pdb --output results/scoring.pt --sequences "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import os
import sys
import json
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "seed": 111,
    "model_type": "ligand_mpnn",
    "batch_size": 1,
    "number_of_batches": 1,
    "verbose": 1,
    "ligand_mpnn_cutoff_for_score": 8.0,
    "ligand_mpnn_use_atom_context": 1,
    "ligand_mpnn_use_side_chain_context": 0,
    "homo_oligomer": 0,
    "zero_indexed": 0,
    "parse_atoms_with_zero_occupancy": 0,
    "autoregressive_score": 0,
    "use_sequence": 1,
    "single_aa_score": 1
}

# ==============================================================================
# Path Configuration
# ==============================================================================
SCRIPT_DIR = Path(__file__).parent
MCP_ROOT = SCRIPT_DIR.parent

PATHS = {
    "repo": MCP_ROOT / "repo" / "LigandMPNN",
    "models": {
        "proteinmpnn": MCP_ROOT / "repo" / "LigandMPNN" / "model_params" / "proteinmpnn_v_48_020.pt",
        "ligandmpnn": MCP_ROOT / "repo" / "LigandMPNN" / "model_params" / "ligandmpnn_v_32_020_25.pt",
        "solublempnn": MCP_ROOT / "repo" / "LigandMPNN" / "model_params" / "solublempnn_v_48_020.pt",
        "global_label_membrane": MCP_ROOT / "repo" / "LigandMPNN" / "model_params" / "global_label_membrane_mpnn_v_48_020.pt",
        "per_residue_label_membrane": MCP_ROOT / "repo" / "LigandMPNN" / "model_params" / "per_residue_label_membrane_mpnn_v_48_020.pt"
    },
    "examples_data": MCP_ROOT / "examples" / "data"
}

# ==============================================================================
# Repository Interface Functions
# ==============================================================================
def get_repo_scorer():
    """Lazy load repo score module to minimize startup time."""
    repo_path = PATHS["repo"]
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository not found at {repo_path}")

    sys.path.insert(0, str(repo_path))
    try:
        from score import main as score_main
        return score_main
    except ImportError as e:
        raise ImportError(f"Failed to import repo score module: {e}")

def create_args_object(
    input_pdb: Path,
    output_file: Path,
    sequences: Optional[List[str]] = None,
    config: Optional[Dict[str, Any]] = None
):
    """Create Args object for repo function call."""
    config = {**DEFAULT_CONFIG, **(config or {})}

    class Args:
        def __init__(self):
            # Basic parameters
            self.seed = config["seed"]
            self.pdb_path = str(input_pdb)
            self.out_folder = str(output_file.parent)
            self.model_type = config["model_type"]
            self.batch_size = config["batch_size"]
            self.number_of_batches = config["number_of_batches"]
            self.verbose = config["verbose"]

            # Model checkpoints
            self.checkpoint_protein_mpnn = str(PATHS["models"]["proteinmpnn"])
            self.checkpoint_ligand_mpnn = str(PATHS["models"]["ligandmpnn"])
            self.checkpoint_soluble_mpnn = str(PATHS["models"]["solublempnn"])
            self.checkpoint_global_label_membrane_mpnn = str(PATHS["models"]["global_label_membrane"])
            self.checkpoint_per_residue_label_membrane_mpnn = str(PATHS["models"]["per_residue_label_membrane"])

            # Scoring-specific parameters
            self.autoregressive_score = config["autoregressive_score"]
            self.use_sequence = config["use_sequence"]
            self.single_aa_score = config["single_aa_score"]

            # Sequence to score (if provided)
            if sequences:
                self.fasta_seq = sequences[0] if len(sequences) == 1 else "/".join(sequences)
            else:
                self.fasta_seq = ""

            # Default empty/zero parameters (required by score.py)
            self.pdb_path_multi = ""
            self.fixed_residues = ""
            self.fixed_residues_multi = ""
            self.redesigned_residues = ""
            self.redesigned_residues_multi = ""
            self.symmetry_residues = ""
            self.homo_oligomer = config["homo_oligomer"]
            self.file_ending = ""
            self.zero_indexed = config["zero_indexed"]
            self.ligand_mpnn_cutoff_for_score = config["ligand_mpnn_cutoff_for_score"]
            self.ligand_mpnn_use_atom_context = config["ligand_mpnn_use_atom_context"]
            self.ligand_mpnn_use_side_chain_context = config["ligand_mpnn_use_side_chain_context"]
            self.parse_atoms_with_zero_occupancy = config["parse_atoms_with_zero_occupancy"]

            # Additional required parameters for score.py
            self.chains_to_design = ""
            self.parse_these_chains_only = ""
            self.global_transmembrane_label = 0
            self.transmembrane_buried = ""
            self.transmembrane_interface = ""

    return Args()

# ==============================================================================
# Utility Functions
# ==============================================================================
def load_config(config_file: Path) -> dict:
    """Load configuration from JSON file."""
    with open(config_file) as f:
        return json.load(f)

def validate_inputs(input_file: Path) -> None:
    """Validate input files exist."""
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if not input_file.suffix.lower() == '.pdb':
        raise ValueError(f"Input file must be a PDB file, got: {input_file.suffix}")

def parse_sequences(sequences_input: str) -> List[str]:
    """Parse sequences from string input."""
    if not sequences_input:
        return []

    # Handle both "/" and "," as separators
    if "/" in sequences_input:
        return [seq.strip() for seq in sequences_input.split("/")]
    elif "," in sequences_input:
        return [seq.strip() for seq in sequences_input.split(",")]
    else:
        return [sequences_input.strip()]

def collect_outputs(output_file: Path) -> Dict[str, Any]:
    """Collect generated output files and metadata."""
    outputs = {
        "score_file": None,
        "score_size": 0,
        "metadata": {}
    }

    if output_file.exists():
        outputs["score_file"] = str(output_file)
        outputs["score_size"] = output_file.stat().st_size

    outputs["metadata"] = {
        "output_file": str(output_file),
        "file_exists": output_file.exists(),
        "file_size_bytes": outputs["score_size"]
    }

    return outputs

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_sequence_scoring(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    sequences: Optional[Union[str, List[str]]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate protein sequence likelihood scores using ProteinMPNN/LigandMPNN.

    Args:
        input_file: Path to input PDB file
        output_file: Path to save output scores (optional, .pt file)
        sequences: Sequence(s) to score (string or list of strings)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Score files and metadata
            - output_file: Path to output file
            - success: Boolean indicating success
            - metadata: Execution metadata

    Example:
        >>> result = run_sequence_scoring("examples/data/1BC8.pdb",
        ...                              sequences="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG")
        >>> print(result['metadata']['file_size_bytes'])
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Parse sequences
    if isinstance(sequences, str):
        sequences_list = parse_sequences(sequences)
    elif isinstance(sequences, list):
        sequences_list = sequences
    else:
        sequences_list = []

    # Set output file
    if output_file:
        output_path = Path(output_file)
    else:
        # Default to input filename with .pt extension
        output_path = SCRIPT_DIR.parent / "results" / "scoring" / f"{input_file.stem}.pt"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Validate inputs
    validate_inputs(input_file)

    if not sequences_list:
        raise ValueError("At least one sequence must be provided for scoring")

    # Create args and get repo scorer
    args = create_args_object(input_file, output_path, sequences_list, config)
    score_main = get_repo_scorer()

    try:
        # Run sequence scoring
        print(f"Running sequence scoring on {input_file}")
        print(f"Model type: {config['model_type']}")
        print(f"Output file: {output_path}")
        print(f"Scoring {len(sequences_list)} sequence(s)")

        if len(sequences_list) <= 3:  # Show sequences if not too many
            for i, seq in enumerate(sequences_list, 1):
                print(f"Sequence {i}: {seq[:50]}{'...' if len(seq) > 50 else ''}")

        score_main(args)

        # Collect outputs
        result = collect_outputs(output_path)

        print(f"✅ Scoring completed successfully!")
        print(f"Score file: {output_path} ({result['score_size']} bytes)")

        return {
            "result": result,
            "output_file": str(output_path),
            "success": True,
            "metadata": {
                "input_file": str(input_file),
                "config": config,
                "num_sequences": len(sequences_list),
                "sequences": sequences_list if len(sequences_list) <= 5 else f"{len(sequences_list)} sequences",
                **result["metadata"]
            }
        }

    except Exception as e:
        print(f"❌ Error during scoring: {e}")
        return {
            "result": None,
            "output_file": str(output_path),
            "success": False,
            "metadata": {
                "input_file": str(input_file),
                "config": config,
                "error": str(e)
            }
        }

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True, help='Input PDB file path')
    parser.add_argument('--output', '-o', help='Output file path (.pt file)')
    parser.add_argument('--config', '-c', help='Config file (JSON)')
    parser.add_argument('--sequences', '-s', required=True,
                       help='Sequences to score (separated by "/" or ",")')
    parser.add_argument('--model_type', choices=['protein_mpnn', 'ligand_mpnn', 'soluble_mpnn'],
                       help='Model type (overrides config)')
    parser.add_argument('--seed', type=int, help='Random seed (overrides config)')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        config = load_config(Path(args.config))

    # Override config with CLI args
    kwargs = {}
    if args.model_type is not None:
        kwargs['model_type'] = args.model_type
    if args.seed is not None:
        kwargs['seed'] = args.seed

    # Run
    result = run_sequence_scoring(
        input_file=args.input,
        output_file=args.output,
        sequences=args.sequences,
        config=config,
        **kwargs
    )

    if result['success']:
        print(f"✅ Success: Scores saved to {result['output_file']}")
        return 0
    else:
        print(f"❌ Failed: {result['metadata'].get('error', 'Unknown error')}")
        return 1

if __name__ == '__main__':
    exit(main())