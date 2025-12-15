"""
Shared library for LigandMPNN/ProteinMPNN MCP scripts.

This library contains common functions used across multiple scripts,
extracted and simplified to minimize dependencies.
"""

from .io import load_config, save_config
from .validation import validate_inputs, validate_pdb_file
from .repo_interface import get_repo_runner, get_repo_scorer, create_base_args
from .paths import PATHS, setup_paths

__all__ = [
    'load_config', 'save_config',
    'validate_inputs', 'validate_pdb_file',
    'get_repo_runner', 'get_repo_scorer', 'create_base_args',
    'PATHS', 'setup_paths'
]