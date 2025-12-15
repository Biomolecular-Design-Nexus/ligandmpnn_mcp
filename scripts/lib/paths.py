"""
Path configuration utilities for MCP scripts.

Centralizes path management to make scripts more portable
and easier to maintain.
"""

from pathlib import Path
from typing import Dict, Union


def setup_paths(script_path: Path) -> Dict[str, Union[Path, Dict[str, Path]]]:
    """
    Set up standard paths relative to script location.

    Args:
        script_path: Path to the calling script (usually __file__)

    Returns:
        Dict containing all standard paths
    """
    script_dir = Path(script_path).parent
    mcp_root = script_dir.parent

    return {
        "script_dir": script_dir,
        "mcp_root": mcp_root,
        "repo": mcp_root / "repo" / "LigandMPNN",
        "configs": mcp_root / "configs",
        "results": mcp_root / "results",
        "examples_data": mcp_root / "examples" / "data",
        "models": {
            "proteinmpnn": mcp_root / "repo" / "LigandMPNN" / "model_params" / "proteinmpnn_v_48_020.pt",
            "ligandmpnn": mcp_root / "repo" / "LigandMPNN" / "model_params" / "ligandmpnn_v_32_020_25.pt",
            "solublempnn": mcp_root / "repo" / "LigandMPNN" / "model_params" / "solublempnn_v_48_020.pt",
            "global_label_membrane": mcp_root / "repo" / "LigandMPNN" / "model_params" / "global_label_membrane_mpnn_v_48_020.pt",
            "per_residue_label_membrane": mcp_root / "repo" / "LigandMPNN" / "model_params" / "per_residue_label_membrane_mpnn_v_48_020.pt"
        }
    }


# Standard paths for use in scripts
PATHS = setup_paths(__file__)


def get_model_path(model_type: str, paths: Dict[str, Union[Path, Dict[str, Path]]] = None) -> Path:
    """
    Get path to model file based on model type.

    Args:
        model_type: Type of model ('protein_mpnn', 'ligand_mpnn', etc.)
        paths: Paths dict (uses PATHS if not provided)

    Returns:
        Path to model file

    Raises:
        ValueError: If model type is not recognized
    """
    if paths is None:
        paths = PATHS

    models = paths["models"]

    if model_type == "protein_mpnn":
        return models["proteinmpnn"]
    elif model_type == "ligand_mpnn":
        return models["ligandmpnn"]
    elif model_type == "soluble_mpnn":
        return models["solublempnn"]
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def get_config_path(config_name: str, paths: Dict[str, Union[Path, Dict[str, Path]]] = None) -> Path:
    """
    Get path to configuration file.

    Args:
        config_name: Name of config (without .json extension)
        paths: Paths dict (uses PATHS if not provided)

    Returns:
        Path to config file
    """
    if paths is None:
        paths = PATHS

    return paths["configs"] / f"{config_name}.json"


def get_results_path(subdir: str = None, paths: Dict[str, Union[Path, Dict[str, Path]]] = None) -> Path:
    """
    Get path to results directory or subdirectory.

    Args:
        subdir: Optional subdirectory name
        paths: Paths dict (uses PATHS if not provided)

    Returns:
        Path to results directory
    """
    if paths is None:
        paths = PATHS

    base = paths["results"]
    return base / subdir if subdir else base


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, creating if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        The path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path