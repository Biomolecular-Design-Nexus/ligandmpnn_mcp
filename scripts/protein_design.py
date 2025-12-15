#!/usr/bin/env python3
"""
Script: protein_design.py
Description: Basic protein sequence design using ProteinMPNN

Original Use Case: examples/use_case_1_protein_design.py
Dependencies Removed: Simplified Args class structure, externalized configuration

Usage:
    python scripts/protein_design.py --input <input_file> --output <output_file>

Example:
    python scripts/protein_design.py --input examples/data/1BC8.pdb --output results/protein_design.csv
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import os
import sys
import json
from pathlib import Path
from typing import Union, Optional, Dict, Any

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "seed": 111,
    "temperature": 0.1,
    "model_type": "protein_mpnn",
    "batch_size": 1,
    "verbose": 1,
    "save_stats": 0,
    "ligand_mpnn_cutoff_for_score": 8.0,
    "pack_side_chains": 0,
    "pack_with_ligand_context": 0,
    "repack_everything": 0,
    "number_of_packs_per_design": 0,
    "ligand_mpnn_use_atom_context": 1,
    "ligand_mpnn_use_side_chain_context": 0,
    "global_transmembrane_label": 0,
    "homo_oligomer": 0,
    "zero_indexed": 0,
    "parse_atoms_with_zero_occupancy": 0
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
def get_repo_runner():
    """Lazy load repo run module to minimize startup time."""
    repo_path = PATHS["repo"]
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository not found at {repo_path}")

    sys.path.insert(0, str(repo_path))
    try:
        from run import main as run_main
        return run_main
    except ImportError as e:
        raise ImportError(f"Failed to import repo run module: {e}")

def create_args_object(
    input_pdb: Path,
    output_dir: Path,
    num_sequences: int = 3,
    config: Optional[Dict[str, Any]] = None
):
    """Create Args object for repo function call."""
    config = {**DEFAULT_CONFIG, **(config or {})}

    class Args:
        def __init__(self):
            # Basic parameters
            self.seed = config["seed"]
            self.pdb_path = str(input_pdb)
            self.out_folder = str(output_dir)
            self.temperature = config["temperature"]
            self.model_type = config["model_type"]
            self.batch_size = config["batch_size"]
            self.number_of_batches = num_sequences
            self.verbose = config["verbose"]
            self.save_stats = config["save_stats"]

            # Model checkpoints
            self.checkpoint_protein_mpnn = str(PATHS["models"]["proteinmpnn"])
            self.checkpoint_ligand_mpnn = str(PATHS["models"]["ligandmpnn"])
            self.checkpoint_soluble_mpnn = str(PATHS["models"]["solublempnn"])
            self.checkpoint_global_label_membrane_mpnn = str(PATHS["models"]["global_label_membrane"])
            self.checkpoint_per_residue_label_membrane_mpnn = str(PATHS["models"]["per_residue_label_membrane"])

            # Default empty/zero parameters
            self.fixed_residues = ""
            self.redesigned_residues = ""
            self.omit_AA = ""
            self.bias_AA = ""
            self.chains_to_design = ""
            self.parse_these_chains_only = ""
            self.bias_AA_per_residue = ""
            self.omit_AA_per_residue = ""
            self.symmetry_residues = ""
            self.symmetry_weights = ""
            self.homo_oligomer = config["homo_oligomer"]
            self.file_ending = ""
            self.zero_indexed = config["zero_indexed"]
            self.ligand_mpnn_use_atom_context = config["ligand_mpnn_use_atom_context"]
            self.ligand_mpnn_use_side_chain_context = config["ligand_mpnn_use_side_chain_context"]
            self.global_transmembrane_label = config["global_transmembrane_label"]
            self.transmembrane_buried = ""
            self.transmembrane_interface = ""
            self.fasta_seq_separation = ":"
            self.pdb_path_multi = ""
            self.fixed_residues_multi = ""
            self.redesigned_residues_multi = ""
            self.omit_AA_per_residue_multi = ""
            self.bias_AA_per_residue_multi = ""
            self.ligand_mpnn_cutoff_for_score = config["ligand_mpnn_cutoff_for_score"]
            self.pack_side_chains = config["pack_side_chains"]
            self.pack_with_ligand_context = config["pack_with_ligand_context"]
            self.repack_everything = config["repack_everything"]
            self.number_of_packs_per_design = config["number_of_packs_per_design"]
            self.checkpoint_path_sc = ""
            self.parse_atoms_with_zero_occupancy = config["parse_atoms_with_zero_occupancy"]

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

def collect_outputs(output_dir: Path) -> Dict[str, Any]:
    """Collect generated output files and metadata."""
    outputs = {
        "sequences": [],
        "backbones": [],
        "packed": [],
        "metadata": {}
    }

    # Look for output directories
    seqs_dir = output_dir / "seqs"
    backbones_dir = output_dir / "backbones"
    packed_dir = output_dir / "packed"

    if seqs_dir.exists():
        outputs["sequences"] = list(seqs_dir.glob("*.fa"))

    if backbones_dir.exists():
        outputs["backbones"] = list(backbones_dir.glob("*.pdb"))

    if packed_dir.exists():
        outputs["packed"] = list(packed_dir.glob("*.pdb"))

    outputs["metadata"] = {
        "total_sequences": len(outputs["sequences"]),
        "output_dir": str(output_dir),
        "has_backbones": len(outputs["backbones"]) > 0,
        "has_packed": len(outputs["packed"]) > 0
    }

    return outputs

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_protein_design(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    num_sequences: int = 3,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run basic protein sequence design using ProteinMPNN.

    Args:
        input_file: Path to input PDB file
        output_file: Path to save output directory (optional)
        num_sequences: Number of sequences to generate
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Generated sequences and metadata
            - output_dir: Path to output directory
            - success: Boolean indicating success
            - metadata: Execution metadata

    Example:
        >>> result = run_protein_design("examples/data/1BC8.pdb", num_sequences=5)
        >>> print(result['metadata']['total_sequences'])
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Set output directory
    if output_file:
        output_dir = Path(output_file)
    else:
        output_dir = SCRIPT_DIR.parent / "results" / "protein_design"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate inputs
    validate_inputs(input_file)

    # Create args and get repo runner
    args = create_args_object(input_file, output_dir, num_sequences, config)
    run_main = get_repo_runner()

    try:
        # Run protein design
        print(f"Running ProteinMPNN design on {input_file}")
        print(f"Model type: {config['model_type']}")
        print(f"Output directory: {output_dir}")
        print(f"Generating {num_sequences} sequences with temperature {config['temperature']}")

        run_main(args)

        # Collect outputs
        result = collect_outputs(output_dir)

        print(f"✅ Design completed successfully!")
        print(f"Generated {result['metadata']['total_sequences']} sequence files")

        return {
            "result": result,
            "output_dir": str(output_dir),
            "success": True,
            "metadata": {
                "input_file": str(input_file),
                "config": config,
                "num_sequences": num_sequences,
                **result["metadata"]
            }
        }

    except Exception as e:
        print(f"❌ Error during design: {e}")
        return {
            "result": None,
            "output_dir": str(output_dir),
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
    parser.add_argument('--output', '-o', help='Output directory path')
    parser.add_argument('--config', '-c', help='Config file (JSON)')
    parser.add_argument('--num_sequences', '-n', type=int, default=3,
                       help='Number of sequences to generate (default: 3)')
    parser.add_argument('--temperature', '-t', type=float,
                       help='Sampling temperature (overrides config)')
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
    if args.temperature is not None:
        kwargs['temperature'] = args.temperature
    if args.model_type is not None:
        kwargs['model_type'] = args.model_type
    if args.seed is not None:
        kwargs['seed'] = args.seed

    # Run
    result = run_protein_design(
        input_file=args.input,
        output_file=args.output,
        num_sequences=args.num_sequences,
        config=config,
        **kwargs
    )

    if result['success']:
        print(f"✅ Success: Results saved to {result['output_dir']}")
        return 0
    else:
        print(f"❌ Failed: {result['metadata'].get('error', 'Unknown error')}")
        return 1

if __name__ == '__main__':
    exit(main())