#!/usr/bin/env python3
"""
Use Case 1: Basic Protein Sequence Design with ProteinMPNN

This script demonstrates scaffold-based protein sequence generation using ProteinMPNN.
Given a protein backbone structure (PDB), it generates new sequences that fold into
the same structure while maintaining structural integrity.

Example usage:
python examples/use_case_1_protein_design.py --input examples/data/1BC8.pdb --output ./outputs/protein_design
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

# Add the repo directory to the path so we can import modules
repo_path = Path(__file__).parent.parent / "repo" / "LigandMPNN"
sys.path.insert(0, str(repo_path))

def run_protein_design(input_pdb, output_dir="./outputs/protein_design", seed=111, temperature=0.1, num_sequences=3, model_type="protein_mpnn"):
    """
    Run protein sequence design using ProteinMPNN

    Args:
        input_pdb: Path to input PDB file
        output_dir: Directory to save outputs
        seed: Random seed for reproducibility
        temperature: Sampling temperature (higher = more diversity)
        num_sequences: Number of sequences to generate
        model_type: Type of model to use
    """

    # Import the main run module
    from run import main as run_main

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

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
            self.checkpoint_protein_mpnn = "./repo/LigandMPNN/model_params/proteinmpnn_v_48_020.pt"
            self.checkpoint_ligand_mpnn = "./repo/LigandMPNN/model_params/ligandmpnn_v_32_020_25.pt"
            self.checkpoint_soluble_mpnn = "./repo/LigandMPNN/model_params/solublempnn_v_48_020.pt"
            self.checkpoint_global_label_membrane_mpnn = "./repo/LigandMPNN/model_params/global_label_membrane_mpnn_v_48_020.pt"
            self.checkpoint_per_residue_label_membrane_mpnn = "./repo/LigandMPNN/model_params/per_residue_label_membrane_mpnn_v_48_020.pt"
            # Set defaults for unused parameters
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
            self.homo_oligomer = 0
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

    print(f"Running ProteinMPNN design on {input_pdb}")
    print(f"Model type: {model_type}")
    print(f"Output directory: {output_dir}")
    print(f"Generating {num_sequences} sequences with temperature {temperature}")

    try:
        run_main(args)
        print(f"✅ Design completed successfully! Check {output_dir} for results.")
        return True
    except Exception as e:
        print(f"❌ Error during design: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Protein sequence design using ProteinMPNN")
    parser.add_argument("--input", "-i", required=True, help="Input PDB file")
    parser.add_argument("--output", "-o", default="./outputs/protein_design",
                       help="Output directory (default: ./outputs/protein_design)")
    parser.add_argument("--seed", type=int, default=111,
                       help="Random seed (default: 111)")
    parser.add_argument("--temperature", "-t", type=float, default=0.1,
                       help="Sampling temperature (default: 0.1)")
    parser.add_argument("--num_sequences", "-n", type=int, default=3,
                       help="Number of sequences to generate (default: 3)")
    parser.add_argument("--model_type", default="protein_mpnn",
                       choices=["protein_mpnn", "ligand_mpnn", "soluble_mpnn"],
                       help="Model type (default: protein_mpnn)")

    args = parser.parse_args()

    # Verify input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file {args.input} not found")
        sys.exit(1)

    # Run the design
    success = run_protein_design(
        input_pdb=args.input,
        output_dir=args.output,
        seed=args.seed,
        temperature=args.temperature,
        num_sequences=args.num_sequences,
        model_type=args.model_type
    )

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()