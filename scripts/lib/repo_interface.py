"""
Repository interface utilities for MCP scripts.

Handles lazy loading and interface to the LigandMPNN repository
to minimize startup time and isolate repo dependencies.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

from .paths import PATHS


def get_repo_runner() -> Callable:
    """
    Lazy load repo run module to minimize startup time.

    Returns:
        The run.main function from repo

    Raises:
        FileNotFoundError: If repository not found
        ImportError: If run module can't be imported
    """
    repo_path = PATHS["repo"]
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository not found at {repo_path}")

    sys.path.insert(0, str(repo_path))
    try:
        from run import main as run_main
        return run_main
    except ImportError as e:
        raise ImportError(f"Failed to import repo run module: {e}")


def get_repo_scorer() -> Callable:
    """
    Lazy load repo score module to minimize startup time.

    Returns:
        The score.main function from repo

    Raises:
        FileNotFoundError: If repository not found
        ImportError: If score module can't be imported
    """
    repo_path = PATHS["repo"]
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository not found at {repo_path}")

    sys.path.insert(0, str(repo_path))
    try:
        from score import main as score_main
        return score_main
    except ImportError as e:
        raise ImportError(f"Failed to import repo score module: {e}")


def create_base_args(
    input_pdb: Path,
    output_location: Path,
    config: Dict[str, Any],
    is_scoring: bool = False
) -> object:
    """
    Create base Args object with common parameters.

    Args:
        input_pdb: Path to input PDB file
        output_location: Output file/directory path
        config: Configuration dictionary
        is_scoring: Whether this is for scoring (vs design)

    Returns:
        Args object ready for repo functions
    """
    class Args:
        def __init__(self):
            # Basic parameters
            self.seed = config.get("seed", 111)
            self.pdb_path = str(input_pdb)
            self.verbose = config.get("verbose", 1)
            self.model_type = config.get("model_type", "ligand_mpnn")

            # Output handling
            if is_scoring:
                self.out_folder = str(output_location.parent)
            else:
                self.out_folder = str(output_location)

            # Model checkpoints
            models = PATHS["models"]
            self.checkpoint_protein_mpnn = str(models["proteinmpnn"])
            self.checkpoint_ligand_mpnn = str(models["ligandmpnn"])
            self.checkpoint_soluble_mpnn = str(models["solublempnn"])
            self.checkpoint_global_label_membrane_mpnn = str(models["global_label_membrane"])
            self.checkpoint_per_residue_label_membrane_mpnn = str(models["per_residue_label_membrane"])

            # Ligand context parameters
            self.ligand_mpnn_use_atom_context = config.get("ligand_mpnn_use_atom_context", 1)
            self.ligand_mpnn_use_side_chain_context = config.get("ligand_mpnn_use_side_chain_context", 0)
            self.ligand_mpnn_cutoff_for_score = config.get("ligand_mpnn_cutoff_for_score", 8.0)

            # Processing parameters
            self.batch_size = config.get("batch_size", 1)
            self.number_of_batches = config.get("number_of_batches", 1)

            # Design-specific parameters (not used in scoring)
            if not is_scoring:
                self.temperature = config.get("temperature", 0.1)
                self.save_stats = config.get("save_stats", 0)

            # Scoring-specific parameters
            if is_scoring:
                self.autoregressive_score = config.get("autoregressive_score", 0)
                self.use_sequence = config.get("use_sequence", 1)
                self.single_aa_score = config.get("single_aa_score", 1)

            # Constraint parameters
            self.fixed_residues = config.get("fixed_residues", "")
            self.redesigned_residues = config.get("redesigned_residues", "")
            self.omit_AA = config.get("omit_AA", "")
            self.bias_AA = config.get("bias_AA", "")
            self.chains_to_design = config.get("chains_to_design", "")
            self.parse_these_chains_only = config.get("parse_these_chains_only", "")
            self.bias_AA_per_residue = config.get("bias_AA_per_residue", "")
            self.omit_AA_per_residue = config.get("omit_AA_per_residue", "")
            self.symmetry_residues = config.get("symmetry_residues", "")
            self.symmetry_weights = config.get("symmetry_weights", "")

            # Packing parameters
            self.pack_side_chains = config.get("pack_side_chains", 0)
            self.pack_with_ligand_context = config.get("pack_with_ligand_context", 0)
            self.repack_everything = config.get("repack_everything", 0)
            self.number_of_packs_per_design = config.get("number_of_packs_per_design", 0)
            self.checkpoint_path_sc = config.get("checkpoint_path_sc", "")

            # Membrane parameters
            self.global_transmembrane_label = config.get("global_transmembrane_label", 0)
            self.transmembrane_buried = config.get("transmembrane_buried", "")
            self.transmembrane_interface = config.get("transmembrane_interface", "")

            # Advanced parameters
            self.homo_oligomer = config.get("homo_oligomer", 0)
            self.file_ending = config.get("file_ending", "")
            self.zero_indexed = config.get("zero_indexed", 0)
            self.parse_atoms_with_zero_occupancy = config.get("parse_atoms_with_zero_occupancy", 0)
            self.fasta_seq_separation = config.get("fasta_seq_separation", ":")

            # Multi-structure parameters
            self.pdb_path_multi = config.get("pdb_path_multi", "")
            self.fixed_residues_multi = config.get("fixed_residues_multi", "")
            self.redesigned_residues_multi = config.get("redesigned_residues_multi", "")
            self.omit_AA_per_residue_multi = config.get("omit_AA_per_residue_multi", "")
            self.bias_AA_per_residue_multi = config.get("bias_AA_per_residue_multi", "")

    return Args()


def add_sequence_to_args(args: object, sequences: List[str]) -> None:
    """
    Add sequence(s) to Args object for scoring.

    Args:
        args: Args object to modify
        sequences: List of sequences to add
    """
    if sequences:
        args.fasta_seq = sequences[0] if len(sequences) == 1 else "/".join(sequences)
    else:
        args.fasta_seq = ""


def add_constraints_to_args(
    args: object,
    fixed_residues: str = "",
    redesigned_residues: str = ""
) -> None:
    """
    Add constraint parameters to Args object.

    Args:
        args: Args object to modify
        fixed_residues: String of fixed residues
        redesigned_residues: String of redesigned residues
    """
    args.fixed_residues = fixed_residues
    args.redesigned_residues = redesigned_residues