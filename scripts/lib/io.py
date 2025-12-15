"""
I/O utility functions for MCP scripts.

These functions are extracted and simplified from repo code
to minimize dependencies and provide consistent file handling.
"""

import json
from pathlib import Path
from typing import Dict, Any, Union, List


def load_config(config_file: Path) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_file: Path to JSON config file

    Returns:
        Dict containing configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        JSONDecodeError: If config file is invalid JSON
    """
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file) as f:
        return json.load(f)


def save_config(config: Dict[str, Any], config_file: Path) -> None:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary to save
        config_file: Path to save config file
    """
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def parse_sequences(sequences_input: str) -> List[str]:
    """
    Parse sequences from string input.

    Handles multiple separators: "/" and ","

    Args:
        sequences_input: String containing sequences

    Returns:
        List of parsed sequences
    """
    if not sequences_input:
        return []

    # Handle both "/" and "," as separators
    if "/" in sequences_input:
        return [seq.strip() for seq in sequences_input.split("/")]
    elif "," in sequences_input:
        return [seq.strip() for seq in sequences_input.split(",")]
    else:
        return [sequences_input.strip()]


def parse_residue_list(residue_string: str) -> List[str]:
    """
    Parse residue specification string into list.

    Args:
        residue_string: String like "C1 C2 C3" or "C1,C2,C3"

    Returns:
        List of residue identifiers
    """
    if not residue_string:
        return []

    # Handle both space and comma separated
    if " " in residue_string:
        return [res.strip() for res in residue_string.split()]
    elif "," in residue_string:
        return [res.strip() for res in residue_string.split(",")]
    else:
        return [residue_string.strip()]


def format_residue_list(residue_list: List[str]) -> str:
    """
    Format residue list back to string.

    Args:
        residue_list: List of residue identifiers

    Returns:
        Space-separated string
    """
    return " ".join(residue_list)


def collect_design_outputs(output_dir: Path) -> Dict[str, Any]:
    """
    Collect generated output files from design runs.

    Args:
        output_dir: Directory to scan for outputs

    Returns:
        Dict with file lists and metadata
    """
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


def collect_scoring_outputs(output_file: Path) -> Dict[str, Any]:
    """
    Collect generated output files from scoring runs.

    Args:
        output_file: Expected output file path

    Returns:
        Dict with file info and metadata
    """
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