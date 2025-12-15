# LigandMPNN MCP

> A comprehensive Model Control Protocol (MCP) server for protein design using LigandMPNN, providing both local script usage and AI assistant integration for scaffold-based protein sequence generation and likelihood calculation.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

LigandMPNN MCP provides access to state-of-the-art protein design algorithms through both standalone scripts and AI assistant integration. It supports scaffold-based protein sequence generation, ligand-aware design, sequence likelihood calculation, and constrained design with fixed residue positions.

### Features
- **Protein Sequence Design**: Generate novel protein sequences using ProteinMPNN and LigandMPNN
- **Ligand-Aware Design**: Design proteins optimized for ligand binding interactions
- **Sequence Scoring**: Calculate sequence likelihood and probability distributions
- **Constrained Design**: Design with fixed positions and amino acid constraints
- **Batch Processing**: Process multiple structures efficiently
- **Job Management**: Track long-running tasks with status monitoring
### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment
├── src/
│   ├── server.py           # MCP server
│   └── jobs/               # Job management system
├── scripts/
│   ├── protein_design.py   # Basic protein sequence design
│   ├── ligand_design.py    # Ligand-aware protein design
│   ├── sequence_scoring.py # Sequence likelihood calculation
│   ├── constrained_design.py # Constrained design with fixed residues
│   └── lib/                # Shared utilities
├── examples/
│   └── data/               # Demo PDB structures and configs
├── configs/                # Configuration files
└── repo/                   # Original LigandMPNN repository
```

---

## Installation

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- CUDA-capable GPU (optional, but recommended for performance)

### Step 1: Create Environment

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/ligandmpnn_mcp

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.10 -y
# or: conda create -p ./env python=3.10 -y

# Activate environment
mamba activate ./env
# or: conda activate ./env
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install MCP dependencies
pip install fastmcp loguru
```

### Step 3: Verify Installation

```bash
# Test imports
python -c "from src.server import mcp; print(f'Found {len(mcp.list_tools())} tools')"
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/protein_design.py` | Basic protein sequence design using ProteinMPNN | See below |
| `scripts/ligand_design.py` | Ligand-aware protein design using LigandMPNN | See below |
| `scripts/sequence_scoring.py` | Protein sequence likelihood calculation | See below |
| `scripts/constrained_design.py` | Constrained design with fixed/redesigned residues | See below |

### Script Examples

#### Basic Protein Design

```bash
# Activate environment
mamba activate ./env

# Run protein design
python scripts/protein_design.py \
  --input examples/data/1BC8.pdb \
  --output results/protein_design \
  --num_sequences 3 \
  --temperature 0.1
```

**Parameters:**
- `--input, -i`: Input PDB file (required)
- `--output, -o`: Output directory (default: results/)
- `--num_sequences, -n`: Number of sequences to generate (default: 3)
- `--temperature, -t`: Sampling temperature for diversity (default: 0.1)
- `--config, -c`: Configuration file (optional)

#### Ligand-Aware Design

```bash
python scripts/ligand_design.py \
  --input examples/data/1BC8.pdb \
  --output results/ligand_design \
  --num_sequences 3 \
  --use_atom_context
```

**Parameters:**
- `--use_atom_context`: Enable ligand atom context (recommended)
- `--use_side_chain_context`: Enable side chain context
- `--no_ligand_context`: Disable ligand context

#### Sequence Scoring

```bash
python scripts/sequence_scoring.py \
  --input examples/data/1BC8.pdb \
  --sequences "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG" \
  --output results/scoring.pt
```

**Parameters:**
- `--sequences`: Protein sequences to score (comma or slash separated)
- `--sequences_file`: FASTA file with sequences to score
- `--save_probs`: Save per-residue probabilities

#### Constrained Design

```bash
python scripts/constrained_design.py \
  --input examples/data/1BC8.pdb \
  --output results/constrained \
  --fixed_residues "C1 C2 C3" \
  --num_sequences 2
```

**Parameters:**
- `--fixed_residues`: Residues to keep unchanged (space/comma separated)
- `--redesigned_residues`: Specific residues to redesign
- `--chains_to_design`: Specific chains to design

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name LigandMPNN
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add LigandMPNN -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "LigandMPNN": {
      "command": "/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/ligandmpnn_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/ligandmpnn_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from LigandMPNN?
```

#### Basic Protein Design
```
Use simple_design with input file @examples/data/1BC8.pdb and generate 5 sequences
```

#### Ligand-Aware Design
```
Run ligand_design on @examples/data/1BC8.pdb with ligand context enabled
```

#### Sequence Scoring
```
Score this sequence using @examples/data/1BC8.pdb as reference: "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
```

#### Constrained Design
```
Use constrained_design with @examples/data/1BC8.pdb, fixing residues 1, 2, and 3
```

#### Long-Running Tasks (Submit API)
```
Submit large design job for @examples/data/1BC8.pdb with 100 sequences
Then check the job status
```

#### Batch Processing
```
Process these files in batch:
- @examples/data/1BC8.pdb
- @examples/data/2GFB.pdb
- @examples/data/4GYT.pdb
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/1BC8.pdb` | Reference a specific PDB file |
| `@configs/default_config.json` | Reference a config file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "LigandMPNN": {
      "command": "/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/ligandmpnn_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/ligandmpnn_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available?
> Use simple_design with file examples/data/1BC8.pdb
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `simple_design` | Basic protein sequence design | `input_file`, `chains`, `num_sequences`, `temperature` |
| `sequence_scoring` | Score protein sequences | `input_file`, `fasta_sequences`, `save_probs` |
| `constrained_design` | Design with fixed/redesigned positions | `input_file`, `chains_to_design`, `fixed_positions`, `num_sequences` |
| `ca_only_design` | Design using only carbon alpha atoms | `input_file`, `chains`, `model`, `num_sequences` |
| `validate_pdb_structure` | Validate PDB file compatibility | `input_file` |
| `list_example_structures` | List available example structures | None |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_batch_design` | Batch processing multiple files | `input_dir`, `file_pattern`, `chains`, `num_sequences` |
| `submit_large_design` | Large-scale sequence generation | `input_file`, `chains`, `num_sequences`, `temperature` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs |

---

## Examples

### Example 1: Basic Protein Analysis

**Goal:** Analyze and redesign a protein structure

**Using Script:**
```bash
python scripts/protein_design.py \
  --input examples/data/1BC8.pdb \
  --output results/example1/ \
  --num_sequences 5
```

**Using MCP (in Claude Code):**
```
Use simple_design to process @examples/data/1BC8.pdb and generate 5 sequences, save results to results/example1/
```

**Expected Output:**
- Generated FASTA sequence files in `results/example1/seqs/`
- Backbone PDB files with new sequences
- Design statistics and metadata

### Example 2: Ligand-Aware Design

**Goal:** Design protein sequences optimized for ligand binding

**Using Script:**
```bash
python scripts/ligand_design.py \
  --input examples/data/1BC8.pdb \
  --output results/ligand_aware/ \
  --num_sequences 3 \
  --use_atom_context
```

**Using MCP (in Claude Code):**
```
Run ligand_design on @examples/data/1BC8.pdb with atom context enabled and generate 3 sequences
```

**Expected Output:**
- Ligand-aware designed sequences
- Optimized protein-ligand binding interfaces
- Confidence scores for ligand interactions

### Example 3: Sequence Scoring

**Goal:** Evaluate sequence likelihood for a given structure

**Using Script:**
```bash
python scripts/sequence_scoring.py \
  --input examples/data/1BC8.pdb \
  --sequences "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG" \
  --output results/scoring.pt
```

**Using MCP (in Claude Code):**
```
Score the sequence "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG" using @examples/data/1BC8.pdb as reference structure
```

**Expected Output:**
- PyTorch tensor file with likelihood scores
- Per-residue probability distributions
- Native sequence comparison scores

### Example 4: Constrained Design

**Goal:** Design with specific residues fixed in place

**Using Script:**
```bash
python scripts/constrained_design.py \
  --input examples/data/1BC8.pdb \
  --output results/constrained/ \
  --fixed_residues "C1 C2 C3" \
  --num_sequences 2
```

**Using MCP (in Claude Code):**
```
Use constrained_design with @examples/data/1BC8.pdb, keeping residues 1, 2, and 3 fixed, generate 2 sequences
```

**Expected Output:**
- Sequences with specified residues preserved
- Constraint satisfaction report
- Optimized variable regions

### Example 5: Batch Processing

**Goal:** Process multiple structures at once

**Using Script:**
```bash
for f in examples/data/*.pdb; do
  python scripts/protein_design.py --input "$f" --output results/batch/
done
```

**Using MCP (in Claude Code):**
```
Submit batch processing for all PDB files in @examples/data/ with 3 sequences each
```

**Expected Output:**
- Individual design results for each structure
- Batch processing status and logs
- Consolidated results directory

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With |
|------|-------------|----------|
| `1BC8.pdb` | Small protein-ligand complex (142KB, 93 residues) | All design tools |
| `2GFB.pdb` | Large protein structure with insertion codes (2.3MB) | Stress testing, batch |
| `4GYT.pdb` | Multi-chain protein complex (525KB) | Multi-chain design |
| `bias_AA_per_residue.json` | Per-residue amino acid bias configuration | Constrained design |
| `omit_AA_per_residue.json` | Per-residue amino acid omission rules | Constrained design |
| `pdb_ids.json` | Multi-structure processing configuration | Batch processing |

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `default_config.json` | Comprehensive default settings | 45 parameters |
| `protein_design_config.json` | Basic protein design settings | Model type, temperature, processing |
| `ligand_design_config.json` | Ligand-aware design settings | Ligand context, side chains |
| `sequence_scoring_config.json` | Sequence scoring settings | Model type, probability saving |
| `constrained_design_config.json` | Constrained design settings | Fixed residues, constraints |

### Config Example

```json
{
  "_description": "Basic protein design configuration",
  "model": {
    "model_type": "protein_mpnn",
    "temperature": 0.1,
    "seed": 111
  },
  "processing": {
    "batch_size": 1,
    "verbose": 1
  },
  "constraints": {
    "fixed_residues": "",
    "redesigned_residues": ""
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.10 -y
mamba activate ./env
pip install -r requirements.txt
```

**Problem:** Import errors
```bash
# Verify installation
python -c "from src.server import mcp"

# Check tool count
python -c "
import sys; sys.path.insert(0, 'src')
from server import mcp
import asyncio
print('Tools:', len(asyncio.run(mcp.get_tools())))
"
```

**Problem:** CUDA/PyTorch issues
```bash
# Check CUDA availability
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# Reinstall PyTorch if needed
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove LigandMPNN
claude mcp add LigandMPNN -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

**Problem:** Tools not working
```bash
# Test server directly
python -c "
import sys; sys.path.insert(0, 'src')
from server import mcp
import asyncio
tools = asyncio.run(mcp.get_tools())
print('Available tools:', list(tools.keys()))
"
```

**Problem:** Path issues
```bash
# Verify paths exist
ls -la examples/data/
ls -la scripts/
ls -la configs/

# Check current directory
pwd
# Should be: /home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/ligandmpnn_mcp
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job log
cat jobs/<job_id>/job.log
```

**Problem:** Job failed
```
Use get_job_log with job_id "<job_id>" and tail 100 to see error details
```

**Problem:** Out of memory
- Reduce `num_sequences` parameter
- Use smaller protein structures for testing
- Ensure sufficient RAM available

### Script Issues

**Problem:** Repository not found
```bash
# Verify repo directory exists
ls -la repo/

# Check repo structure
ls -la repo/LigandMPNN/
```

**Problem:** Model files missing
```bash
# Check for model files
find repo/ -name "*.pt" -type f

# Re-download if necessary
cd repo && git pull
```

**Problem:** Permission errors
```bash
# Fix permissions
chmod +x scripts/*.py
chmod -R 755 env/
```

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Run integration tests
python tests/integration_tests.py

# Test individual tools
python -c "from src.server import list_example_structures; print(list_example_structures())"
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
fastmcp dev src/server.py

# Or run directly
python src/server.py
```

### Performance Monitoring

```bash
# Monitor GPU usage
nvidia-smi

# Monitor job status
python -c "from src.jobs.manager import job_manager; print(job_manager.list_jobs())"
```

---

## Performance Characteristics

| Operation Type | Typical Runtime | Memory Usage | Concurrency |
|---------------|-----------------|--------------|-------------|
| Single design (1-10 seqs) | 5-15 seconds | ~1GB | Up to 4 concurrent |
| Batch design (10+ files) | 10-60 minutes | ~1-2GB | 1 at a time |
| Sequence scoring | 3-8 seconds | ~0.5GB | Up to 8 concurrent |
| Validation | <1 second | ~10MB | Unlimited |

---

## License

This project is based on [LigandMPNN](https://github.com/dauparas/LigandMPNN) and maintains the same MIT license.

## Credits

Based on [LigandMPNN](https://github.com/dauparas/LigandMPNN) by Dauparas et al.
- Original Paper: [Robust deep learning–based protein sequence design using ProteinMPNN](https://www.science.org/doi/10.1126/science.add2187)
- LigandMPNN Paper: [Atomic context-conditioned protein sequence design using LigandMPNN](https://www.biorxiv.org/content/10.1101/2023.12.13.571462v1)

MCP Integration developed for the Claude Code ecosystem.