# MCP Scripts

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported
2. **Self-Contained**: Functions inlined or isolated in shared library
3. **Configurable**: Parameters in config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts Overview

| Script | Description | Repo Dependent | Config | Status |
|--------|-------------|----------------|--------|---------|
| `protein_design.py` | Basic protein sequence design | Yes (model) | `configs/protein_design_config.json` | ✅ Tested |
| `ligand_design.py` | Protein-ligand complex design | Yes (model) | `configs/ligand_design_config.json` | ✅ Tested |
| `sequence_scoring.py` | Protein sequence likelihood scoring | Yes (model) | `configs/sequence_scoring_config.json` | ✅ Tested |
| `constrained_design.py` | Constrained design with fixed residues | Yes (model) | `configs/constrained_design_config.json` | ✅ Tested |

## Usage

### Environment Setup

```bash
# Activate environment (prefer mamba over conda)
mamba activate ./env  # or: conda activate ./env
```

### Basic Usage

```bash
# Run a script with minimal parameters
python scripts/protein_design.py --input examples/data/1BC8.pdb --output results/test_design --num_sequences 3

# Run with custom config
python scripts/protein_design.py --input FILE --output DIR --config configs/custom.json

# Run sequence scoring
python scripts/sequence_scoring.py --input examples/data/1BC8.pdb --output results/scores.pt --sequences "MKTVRQERLKSI..."

# Run constrained design
python scripts/constrained_design.py --input examples/data/1BC8.pdb --output results/constrained --fixed_residues "C1 C2 C3"
```

### Configuration Files

Each script can use configuration files to set default parameters:

```bash
python scripts/protein_design.py --input FILE --config configs/protein_design_config.json
```

## Script Details

### protein_design.py

**Purpose**: Basic protein sequence design using ProteinMPNN
**Main Function**: `run_protein_design(input_file, output_file=None, num_sequences=3, config=None, **kwargs)`

**Key Parameters**:
- `input_file`: Path to input PDB file
- `output_file`: Path to save output directory (optional)
- `num_sequences`: Number of sequences to generate (default: 3)
- `temperature`: Sampling temperature (default: 0.1)
- `model_type`: Model to use ('protein_mpnn', 'ligand_mpnn', 'soluble_mpnn')

**Outputs**: Generates sequence files in `{output_dir}/seqs/`, backbone files in `{output_dir}/backbones/`

### ligand_design.py

**Purpose**: Protein-ligand complex design using LigandMPNN
**Main Function**: `run_ligand_design(input_file, output_file=None, num_sequences=3, use_atom_context=True, use_side_chain_context=False, config=None, **kwargs)`

**Key Parameters**:
- `use_atom_context`: Whether to use ligand atoms as context (default: True)
- `use_side_chain_context`: Whether to use fixed residue side chain atoms (default: False)

**Outputs**: Similar to protein_design.py but with ligand context awareness

### sequence_scoring.py

**Purpose**: Calculate protein sequence likelihood scores
**Main Function**: `run_sequence_scoring(input_file, output_file=None, sequences=None, config=None, **kwargs)`

**Key Parameters**:
- `sequences`: Sequence(s) to score (string or list of strings)
- `model_type`: Model to use for scoring

**Outputs**: Generates PyTorch tensor file with likelihood scores

### constrained_design.py

**Purpose**: Constrained protein sequence design with fixed/redesigned residues
**Main Function**: `run_constrained_design(input_file, output_file=None, num_sequences=3, fixed_residues=None, redesigned_residues=None, config=None, **kwargs)`

**Key Parameters**:
- `fixed_residues`: Residues to keep fixed (e.g., "C1 C2 C3" or ["C1", "C2", "C3"])
- `redesigned_residues`: Residues to redesign (e.g., "C4 C5")

## Shared Library

Common functions are in `scripts/lib/`:

- `io.py`: File loading/saving, parsing functions (12 functions)
- `validation.py`: Input validation utilities (7 functions)
- `repo_interface.py`: Repository interface and lazy loading (5 functions)
- `paths.py`: Path management and configuration (6 functions)

**Total Functions**: 30 shared functions

### Using the Shared Library

```python
from scripts.lib import load_config, validate_pdb_file, get_repo_runner, PATHS

# Load configuration
config = load_config(Path("configs/custom.json"))

# Validate inputs
validate_pdb_file(Path("input.pdb"))

# Get repo interface
run_main = get_repo_runner()

# Use standard paths
model_path = PATHS["models"]["ligandmpnn"]
```

## Repository Dependencies

All scripts still depend on the repository for:
1. **Model files**: Pre-trained weights (~120MB total)
2. **Core algorithms**: LigandMPNN/ProteinMPNN model implementations
3. **Data processing**: Structure parsing and feature extraction

**Why Repository Dependencies Remain**:
- Model implementations are complex (thousands of lines)
- Pre-trained weights are required for functionality
- Inlining would create massive, unmaintainable scripts

**Dependency Isolation**:
- ✅ Lazy loading - repo only imported when functions are called
- ✅ Path abstraction - relative paths, not hardcoded
- ✅ Error handling - clear messages when repo unavailable
- ✅ Interface isolation - minimal repo surface area exposed

## For MCP Wrapping (Step 6)

Each script exports a main function that can be easily wrapped:

```python
# Example MCP tool wrapper
from scripts.protein_design import run_protein_design

@mcp.tool()
def design_protein_sequences(
    input_file: str,
    output_file: str = None,
    num_sequences: int = 3,
    temperature: float = 0.1
) -> dict:
    """Generate protein sequences from a PDB structure."""
    return run_protein_design(
        input_file=input_file,
        output_file=output_file,
        num_sequences=num_sequences,
        temperature=temperature
    )
```

## Testing

All scripts have been tested with example data:

```bash
# Test protein design
python scripts/protein_design.py --input examples/data/1BC8.pdb --output results/test_protein --num_sequences 1
# ✅ Generated 1 sequence files

# Test scoring
python scripts/sequence_scoring.py --input examples/data/1BC8.pdb --sequences "MKTVRQ..." --output results/test.pt
# ✅ Generated 271KB score file

# Test constrained design
python scripts/constrained_design.py --input examples/data/1BC8.pdb --fixed_residues "C1 C2 C3" --num_sequences 1
# ✅ Generated constrained sequences with C1,C2,C3 fixed

```

## Performance

- **Fast execution**: All scripts complete in 3-5 seconds for single sequences
- **Model loading**: Efficient lazy loading (~2 second model load time)
- **Memory usage**: Reasonable memory footprint for protein design tasks
- **Ligand parsing**: Successfully processes complex protein-ligand structures (406 atoms in test case)

## Error Handling

Scripts include comprehensive error handling:
- Input validation before processing
- Clear error messages for missing files/invalid parameters
- Graceful handling of repository dependencies
- Proper cleanup on failure