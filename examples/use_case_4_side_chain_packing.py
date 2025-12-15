#!/usr/bin/env python3
"""
Use Case 4: Side Chain Packing with LigandMPNN

This script demonstrates side chain packing combined with sequence design.
It generates new sequences and then packs side chains considering ligand context,
providing complete structural models with optimized side chain conformations.

Example usage:
python examples/use_case_4_side_chain_packing.py --input examples/data/1BC8.pdb --output ./outputs/side_chain_packing
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

# Add the repo directory to the path so we can import modules
repo_path = Path(__file__).parent.parent / "repo" / "LigandMPNN"
sys.path.insert(0, str(repo_path))

def run_side_chain_packing(input_pdb, output_dir="./outputs/side_chain_packing", seed=111,
                          temperature=0.1, num_sequences=2, num_packs_per_design=4,
                          pack_with_ligand_context=True, repack_everything=False,
                          fixed_residues=""):
    """
    Run protein sequence design with side chain packing using LigandMPNN

    Args:
        input_pdb: Path to input PDB file
        output_dir: Directory to save outputs
        seed: Random seed for reproducibility
        temperature: Sampling temperature for sequence design
        num_sequences: Number of sequences to generate
        num_packs_per_design: Number of side chain packing samples per design
        pack_with_ligand_context: Whether to consider ligand atoms during packing
        repack_everything: Whether to repack all residues (including fixed ones)
        fixed_residues: Space-separated list of residues to fix (e.g., "C1 C2 C3")
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
            self.model_type = "ligand_mpnn"
            self.batch_size = 1
            self.number_of_batches = num_sequences
            self.verbose = 1
            self.save_stats = 0
            # Side chain packing parameters
            self.pack_side_chains = 1
            self.number_of_packs_per_design = num_packs_per_design
            self.pack_with_ligand_context = 1 if pack_with_ligand_context else 0
            self.repack_everything = 1 if repack_everything else 0
            self.fixed_residues = fixed_residues
            # Model checkpoints
            self.checkpoint_protein_mpnn = "./repo/LigandMPNN/model_params/proteinmpnn_v_48_020.pt"
            self.checkpoint_ligand_mpnn = "./repo/LigandMPNN/model_params/ligandmpnn_v_32_020_25.pt"
            self.checkpoint_soluble_mpnn = "./repo/LigandMPNN/model_params/solublempnn_v_48_020.pt"
            self.checkpoint_global_label_membrane_mpnn = "./repo/LigandMPNN/model_params/global_label_membrane_mpnn_v_48_020.pt"
            self.checkpoint_per_residue_label_membrane_mpnn = "./repo/LigandMPNN/model_params/per_residue_label_membrane_mpnn_v_48_020.pt"
            self.checkpoint_path_sc = "./repo/LigandMPNN/model_params/ligandmpnn_sc_v_32_002_16.pt"
            # Set defaults for unused parameters
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
            self.parse_atoms_with_zero_occupancy = 0
            self.sc_num_denoising_steps = 3
            self.sc_num_samples = 16
            self.packed_suffix = "_packed"
            self.force_hetatm = 0

    # Create args object and run
    args = Args()

    print(f"Running LigandMPNN with side chain packing on {input_pdb}")
    print(f"Output directory: {output_dir}")
    print(f"Generating {num_sequences} sequences with {num_packs_per_design} packing samples each")
    print(f"Pack with ligand context: {pack_with_ligand_context}")
    print(f"Repack everything: {repack_everything}")
    if fixed_residues:
        print(f"Fixed residues: {fixed_residues}")

    try:
        run_main(args)
        print(f"✅ Side chain packing completed successfully! Check {output_dir} for results.")
        print(f"   - Generated sequences: {output_dir}/seqs/")
        print(f"   - Packed structures: {output_dir}/backbones/")
        return True
    except Exception as e:
        print(f"❌ Error during side chain packing: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Protein sequence design with side chain packing")
    parser.add_argument("--input", "-i", required=True, help="Input PDB file")
    parser.add_argument("--output", "-o", default="./outputs/side_chain_packing",
                       help="Output directory (default: ./outputs/side_chain_packing)")
    parser.add_argument("--seed", type=int, default=111,
                       help="Random seed (default: 111)")
    parser.add_argument("--temperature", "-t", type=float, default=0.1,
                       help="Sampling temperature (default: 0.1)")
    parser.add_argument("--num_sequences", "-n", type=int, default=2,
                       help="Number of sequences to generate (default: 2)")
    parser.add_argument("--num_packs", type=int, default=4,
                       help="Number of packing samples per design (default: 4)")
    parser.add_argument("--no_ligand_context", action="store_true",
                       help="Don't use ligand context during side chain packing")
    parser.add_argument("--repack_everything", action="store_true",
                       help="Repack all residues (including fixed ones)")
    parser.add_argument("--fixed_residues", type=str, default="",
                       help="Space-separated list of residues to fix (e.g., 'C1 C2 C3')")

    args = parser.parse_args()

    # Verify input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file {args.input} not found")
        sys.exit(1)

    # Run the design with side chain packing
    success = run_side_chain_packing(
        input_pdb=args.input,
        output_dir=args.output,
        seed=args.seed,
        temperature=args.temperature,
        num_sequences=args.num_sequences,
        num_packs_per_design=args.num_packs,
        pack_with_ligand_context=not args.no_ligand_context,
        repack_everything=args.repack_everything,
        fixed_residues=args.fixed_residues
    )

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()