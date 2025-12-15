"""
Input validation utilities for MCP scripts.

Provides consistent validation across all scripts
to ensure proper input formats and file existence.
"""

from pathlib import Path
from typing import List, Optional


def validate_pdb_file(file_path: Path) -> None:
    """
    Validate PDB file exists and has correct extension.

    Args:
        file_path: Path to PDB file

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file doesn't have .pdb extension
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDB file not found: {file_path}")

    if not file_path.suffix.lower() == '.pdb':
        raise ValueError(f"Input file must be a PDB file, got: {file_path.suffix}")


def validate_inputs(input_file: Path) -> None:
    """
    Validate general input files.

    Args:
        input_file: Path to input file

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")


def validate_sequences(sequences: Optional[List[str]]) -> None:
    """
    Validate protein sequences.

    Args:
        sequences: List of protein sequences to validate

    Raises:
        ValueError: If sequences are invalid
    """
    if not sequences:
        raise ValueError("At least one sequence must be provided")

    for i, seq in enumerate(sequences):
        if not seq:
            raise ValueError(f"Sequence {i+1} is empty")

        # Basic protein sequence validation
        valid_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
        invalid_chars = set(seq.upper()) - valid_amino_acids
        if invalid_chars:
            raise ValueError(f"Sequence {i+1} contains invalid amino acids: {invalid_chars}")


def validate_model_type(model_type: str) -> None:
    """
    Validate model type selection.

    Args:
        model_type: Model type string

    Raises:
        ValueError: If model type is not supported
    """
    valid_models = {"protein_mpnn", "ligand_mpnn", "soluble_mpnn"}
    if model_type not in valid_models:
        raise ValueError(f"Invalid model type: {model_type}. Must be one of {valid_models}")


def validate_temperature(temperature: float) -> None:
    """
    Validate temperature parameter.

    Args:
        temperature: Sampling temperature

    Raises:
        ValueError: If temperature is invalid
    """
    if not 0.0 <= temperature <= 2.0:
        raise ValueError(f"Temperature must be between 0.0 and 2.0, got: {temperature}")


def validate_num_sequences(num_sequences: int) -> None:
    """
    Validate number of sequences parameter.

    Args:
        num_sequences: Number of sequences to generate

    Raises:
        ValueError: If number is invalid
    """
    if num_sequences < 1:
        raise ValueError(f"Number of sequences must be >= 1, got: {num_sequences}")

    if num_sequences > 1000:
        raise ValueError(f"Number of sequences should be <= 1000 for reasonable runtime, got: {num_sequences}")


def validate_residue_list(residue_list: List[str], context: str = "residues") -> None:
    """
    Validate residue identifier list.

    Args:
        residue_list: List of residue identifiers (e.g., ["C1", "C2"])
        context: Context for error messages

    Raises:
        ValueError: If residue identifiers are invalid
    """
    if not residue_list:
        return  # Empty list is valid

    for residue in residue_list:
        if not residue:
            raise ValueError(f"Empty {context} identifier found")

        # Basic format check - should start with chain letter
        if len(residue) < 2 or not residue[0].isalpha():
            raise ValueError(f"Invalid {context} identifier: {residue}. Expected format like 'C1', 'A25', etc.")