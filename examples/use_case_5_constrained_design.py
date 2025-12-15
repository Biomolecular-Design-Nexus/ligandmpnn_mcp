#!/usr/bin/env python3
"""
Use Case 5: Constrained Protein Design

This script demonstrates scaffold-based sequence generation with constraints.
It supports fixing specific residues, redesigning only certain regions,
applying amino acid biases, and enforcing symmetry constraints.

Example usage:
python examples/use_case_5_constrained_design.py --input examples/data/1BC8.pdb --output ./outputs/constrained_design --fixed_residues "C1 C2 C3"
"""

import argparse
import os
import sys
import json
import tempfile
from pathlib import Path

# Add the repo directory to the path so we can import modules
repo_path = Path(__file__).parent.parent / "repo" / "LigandMPNN"
sys.path.insert(0, str(repo_path))

def run_constrained_design(input_pdb, output_dir="./outputs/constrained_design", seed=111,
                          temperature=0.1, num_sequences=3, model_type="ligand_mpnn",
                          fixed_residues="", redesigned_residues="", omit_AA="",
                          bias_AA="", bias_AA_per_residue=None, omit_AA_per_residue=None,
                          chains_to_design="", homo_oligomer=False):
    """
    Run constrained protein sequence design

    Args:
        input_pdb: Path to input PDB file
        output_dir: Directory to save outputs
        seed: Random seed for reproducibility
        temperature: Sampling temperature
        num_sequences: Number of sequences to generate
        model_type: Model to use (protein_mpnn, ligand_mpnn, etc.)
        fixed_residues: Space-separated residues to keep fixed (e.g., "C1 C2 C3")
        redesigned_residues: Space-separated residues to redesign (others fixed)
        omit_AA: Amino acids to globally avoid (e.g., "CDFGH")
        bias_AA: Global amino acid biases (e.g., "A:2.0,P:-1.0")
        bias_AA_per_residue: Dict of per-residue biases
        omit_AA_per_residue: Dict of per-residue omissions
        chains_to_design: Specific chains to design (e.g., "A,B")
        homo_oligomer: Whether to design as homooligomer with symmetry
    """

    # Import the main run module
    from run import main as run_main

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Handle JSON files for per-residue constraints
    bias_AA_per_residue_file = ""
    omit_AA_per_residue_file = ""

    if bias_AA_per_residue:
        bias_file_path = os.path.join(output_dir, "temp_bias_per_residue.json")
        with open(bias_file_path, 'w') as f:
            json.dump(bias_AA_per_residue, f)
        bias_AA_per_residue_file = bias_file_path

    if omit_AA_per_residue:
        omit_file_path = os.path.join(output_dir, "temp_omit_per_residue.json")
        with open(omit_file_path, 'w') as f:
            json.dump(omit_AA_per_residue, f)
        omit_AA_per_residue_file = omit_file_path

    # Set up arguments as if passed from command line
    class Args:
        def __init__(self):
            self.seed = seed
            self.pdb_path = str(input_pdb)
            self.out_folder = str(output_dir)
            self.temperature = temperature
            self.model_type = model_type
            self.batch_size = 1
            self.number_of_batches = num_sequences
            self.verbose = 1
            self.save_stats = 0
            # Constraint parameters
            self.fixed_residues = fixed_residues
            self.redesigned_residues = redesigned_residues
            self.omit_AA = omit_AA
            self.bias_AA = bias_AA
            self.bias_AA_per_residue = bias_AA_per_residue_file
            self.omit_AA_per_residue = omit_AA_per_residue_file
            self.chains_to_design = chains_to_design
            self.homo_oligomer = 1 if homo_oligomer else 0
            # Model checkpoints
            self.checkpoint_protein_mpnn = "./repo/LigandMPNN/model_params/proteinmpnn_v_48_020.pt"
            self.checkpoint_ligand_mpnn = "./repo/LigandMPNN/model_params/ligandmpnn_v_32_020_25.pt"
            self.checkpoint_soluble_mpnn = "./repo/LigandMPNN/model_params/solublempnn_v_48_020.pt"
            self.checkpoint_global_label_membrane_mpnn = "./repo/LigandMPNN/model_params/global_label_membrane_mpnn_v_48_020.pt"
            self.checkpoint_per_residue_label_membrane_mpnn = "./repo/LigandMPNN/model_params/per_residue_label_membrane_mpnn_v_48_020.pt"
            # Set defaults for unused parameters
            self.parse_these_chains_only = ""
            self.symmetry_residues = ""
            self.symmetry_weights = ""
            self.file_ending = ""
            self.zero_indexed = 0
            self.ligand_mpnn_use_atom_context = 1
            self.ligand_mpnn_use_side_chain_context = 0
            self.global_transmembrane_label = 0
            self.transmembrane_buried = ""
            self.transmembrane_interface = ""
            self.fasta_seq_separation = ":"
            self.pdb_path_multi = ""
            self.fixed_residues_multi = ""
            self.redesigned_residues_multi = ""
            self.omit_AA_per_residue_multi = ""
            self.bias_AA_per_residue_multi = ""
            self.ligand_mpnn_cutoff_for_score = 8.0
            self.pack_side_chains = 0
            self.pack_with_ligand_context = 0
            self.repack_everything = 0
            self.number_of_packs_per_design = 0
            self.checkpoint_path_sc = ""
            self.parse_atoms_with_zero_occupancy = 0

    # Create args object and run
    args = Args()

    print(f"Running constrained design using {model_type} on {input_pdb}")
    print(f"Output directory: {output_dir}")
    print(f"Generating {num_sequences} sequences with temperature {temperature}")
    if fixed_residues:
        print(f"Fixed residues: {fixed_residues}")
    if redesigned_residues:
        print(f"Redesigned residues: {redesigned_residues}")
    if omit_AA:
        print(f"Omitted amino acids: {omit_AA}")
    if bias_AA:
        print(f"Global biases: {bias_AA}")
    if chains_to_design:
        print(f"Chains to design: {chains_to_design}")
    if homo_oligomer:
        print("Homooligomer design with automatic symmetry")

    try:
        run_main(args)
        print(f"✅ Constrained design completed successfully! Check {output_dir} for results.")
        return True
    except Exception as e:
        print(f"❌ Error during constrained design: {e}")
        return False
    finally:
        # Clean up temporary files
        if bias_AA_per_residue and os.path.exists(bias_file_path):
            os.remove(bias_file_path)
        if omit_AA_per_residue and os.path.exists(omit_file_path):
            os.remove(omit_file_path)

def parse_per_residue_dict(dict_str):
    """Parse per-residue dictionary from string format like 'C1:A:2.0,G:-1.0;C2:P:3.0' """
    if not dict_str:
        return None

    result = {}
    for residue_spec in dict_str.split(';'):
        parts = residue_spec.split(':')
        if len(parts) < 2:
            continue
        residue = parts[0]
        aa_specs = parts[1:]

        if residue not in result:
            result[residue] = {}

        # Parse AA:bias pairs
        for i in range(0, len(aa_specs), 2):
            if i + 1 < len(aa_specs):
                aa = aa_specs[i]
                bias = float(aa_specs[i + 1])
                result[residue][aa] = bias

    return result

def main():
    parser = argparse.ArgumentParser(description="Constrained protein sequence design")
    parser.add_argument("--input", "-i", required=True, help="Input PDB file")
    parser.add_argument("--output", "-o", default="./outputs/constrained_design",
                       help="Output directory (default: ./outputs/constrained_design)")
    parser.add_argument("--seed", type=int, default=111,
                       help="Random seed (default: 111)")
    parser.add_argument("--temperature", "-t", type=float, default=0.1,
                       help="Sampling temperature (default: 0.1)")
    parser.add_argument("--num_sequences", "-n", type=int, default=3,
                       help="Number of sequences to generate (default: 3)")
    parser.add_argument("--model_type", default="ligand_mpnn",
                       choices=["protein_mpnn", "ligand_mpnn", "soluble_mpnn"],
                       help="Model type (default: ligand_mpnn)")

    # Constraint options
    parser.add_argument("--fixed_residues", type=str, default="",
                       help="Space-separated residues to fix (e.g., 'C1 C2 C3')")
    parser.add_argument("--redesigned_residues", type=str, default="",
                       help="Space-separated residues to redesign (others fixed)")
    parser.add_argument("--omit_AA", type=str, default="",
                       help="Amino acids to globally avoid (e.g., 'CDFGH')")
    parser.add_argument("--bias_AA", type=str, default="",
                       help="Global amino acid biases (e.g., 'A:2.0,P:-1.0')")
    parser.add_argument("--chains_to_design", type=str, default="",
                       help="Specific chains to design (e.g., 'A,B')")
    parser.add_argument("--homo_oligomer", action="store_true",
                       help="Design as homooligomer with automatic symmetry")

    # Advanced per-residue constraints
    parser.add_argument("--bias_AA_per_residue", type=str, default="",
                       help="Per-residue biases (format: 'C1:A:2.0,G:-1.0;C2:P:3.0')")
    parser.add_argument("--omit_AA_per_residue", type=str, default="",
                       help="Per-residue omissions (format: 'C1:ACDEFG;C2:HIKLM')")

    args = parser.parse_args()

    # Verify input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file {args.input} not found")
        sys.exit(1)

    # Parse per-residue constraints
    bias_per_residue = parse_per_residue_dict(args.bias_AA_per_residue) if args.bias_AA_per_residue else None

    omit_per_residue = None
    if args.omit_AA_per_residue:
        omit_per_residue = {}
        for spec in args.omit_AA_per_residue.split(';'):
            parts = spec.split(':')
            if len(parts) == 2:
                omit_per_residue[parts[0]] = parts[1]

    # Run the constrained design
    success = run_constrained_design(
        input_pdb=args.input,
        output_dir=args.output,
        seed=args.seed,
        temperature=args.temperature,
        num_sequences=args.num_sequences,
        model_type=args.model_type,
        fixed_residues=args.fixed_residues,
        redesigned_residues=args.redesigned_residues,
        omit_AA=args.omit_AA,
        bias_AA=args.bias_AA,
        bias_AA_per_residue=bias_per_residue,
        omit_AA_per_residue=omit_per_residue,
        chains_to_design=args.chains_to_design,
        homo_oligomer=args.homo_oligomer
    )

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()