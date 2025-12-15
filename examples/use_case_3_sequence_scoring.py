#!/usr/bin/env python3
"""
Use Case 3: Sequence Scoring and Likelihood Calculation

This script demonstrates likelihood calculation for protein sequences given a structure.
It computes the log-likelihood of sequences under the ProteinMPNN/LigandMPNN model,
which is useful for evaluating sequence-structure compatibility and design quality.

Example usage:
python examples/use_case_3_sequence_scoring.py --input examples/data/1BC8.pdb --output ./outputs/scoring
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

# Add the repo directory to the path so we can import modules
repo_path = Path(__file__).parent.parent / "repo" / "LigandMPNN"
sys.path.insert(0, str(repo_path))

def run_sequence_scoring(input_pdb, output_dir="./outputs/scoring", seed=111, model_type="protein_mpnn",
                        sequences=None):
    """
    Score protein sequences using ProteinMPNN/LigandMPNN likelihood calculation

    Args:
        input_pdb: Path to input PDB file
        output_dir: Directory to save outputs
        seed: Random seed for reproducibility
        model_type: Type of model to use for scoring
        sequences: Optional custom sequences to score (if None, scores native sequence)
    """

    # Import the scoring module
    from score import main as score_main

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Set up arguments as if passed from command line
    class Args:
        def __init__(self):
            self.seed = seed
            self.pdb_path = str(input_pdb)
            self.out_folder = str(output_dir)
            self.model_type = model_type
            self.verbose = 1
            # Model checkpoints
            self.checkpoint_protein_mpnn = "./repo/LigandMPNN/model_params/proteinmpnn_v_48_020.pt"
            self.checkpoint_ligand_mpnn = "./repo/LigandMPNN/model_params/ligandmpnn_v_32_020_25.pt"
            self.checkpoint_soluble_mpnn = "./repo/LigandMPNN/model_params/solublempnn_v_48_020.pt"
            self.checkpoint_global_label_membrane_mpnn = "./repo/LigandMPNN/model_params/global_label_membrane_mpnn_v_48_020.pt"
            self.checkpoint_per_residue_label_membrane_mpnn = "./repo/LigandMPNN/model_params/per_residue_label_membrane_mpnn_v_48_020.pt"
            # Scoring specific parameters
            self.fasta_path = sequences if sequences else ""
            self.chains_to_design = ""
            self.parse_these_chains_only = ""
            self.ligand_mpnn_use_atom_context = 1
            self.ligand_mpnn_use_side_chain_context = 0
            self.global_transmembrane_label = 0
            self.transmembrane_buried = ""
            self.transmembrane_interface = ""
            self.ligand_mpnn_cutoff_for_score = 8.0
            self.parse_atoms_with_zero_occupancy = 0
            self.pdb_path_multi = ""
            self.fixed_residues = ""
            self.fixed_residues_multi = ""
            self.redesigned_residues = ""
            self.redesigned_residues_multi = ""
            self.symmetry_residues = ""
            self.homo_oligomer = 0
            self.file_ending = ""
            self.zero_indexed = 0
            self.batch_size = 1
            self.number_of_batches = 1
            self.autoregressive_score = 0
            self.use_sequence = 1
            self.single_aa_score = 1

    # Create args object and run
    args = Args()

    print(f"Scoring sequences using {model_type} on {input_pdb}")
    print(f"Output directory: {output_dir}")
    if sequences:
        print(f"Custom sequences file: {sequences}")
    else:
        print("Scoring native sequence from PDB")

    try:
        score_main(args)
        print(f"✅ Sequence scoring completed successfully! Check {output_dir} for results.")
        print(f"   - Scores will be saved as: {output_dir}/score_only/")
        return True
    except Exception as e:
        print(f"❌ Error during sequence scoring: {e}")
        return False

def create_custom_sequences_file(sequences, output_path):
    """
    Create a FASTA file with custom sequences for scoring

    Args:
        sequences: List of sequences or single sequence string
        output_path: Path where to save the FASTA file
    """
    if isinstance(sequences, str):
        sequences = [sequences]

    with open(output_path, 'w') as f:
        for i, seq in enumerate(sequences):
            f.write(f">sequence_{i+1}\n")
            f.write(f"{seq}\n")

    return output_path

def main():
    parser = argparse.ArgumentParser(description="Protein sequence scoring using ProteinMPNN/LigandMPNN")
    parser.add_argument("--input", "-i", required=True, help="Input PDB file")
    parser.add_argument("--output", "-o", default="./outputs/scoring",
                       help="Output directory (default: ./outputs/scoring)")
    parser.add_argument("--seed", type=int, default=111,
                       help="Random seed (default: 111)")
    parser.add_argument("--model_type", default="protein_mpnn",
                       choices=["protein_mpnn", "ligand_mpnn", "soluble_mpnn"],
                       help="Model type for scoring (default: protein_mpnn)")
    parser.add_argument("--sequences", type=str,
                       help="Custom sequences to score (comma-separated)")
    parser.add_argument("--sequences_file", type=str,
                       help="FASTA file with sequences to score")

    args = parser.parse_args()

    # Verify input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file {args.input} not found")
        sys.exit(1)

    sequences_file = None
    if args.sequences:
        # Create temporary FASTA file for custom sequences
        sequences_list = [s.strip() for s in args.sequences.split(',')]
        temp_path = os.path.join(args.output, "temp_sequences.fasta")
        os.makedirs(args.output, exist_ok=True)
        sequences_file = create_custom_sequences_file(sequences_list, temp_path)
        print(f"Created temporary sequences file: {sequences_file}")
    elif args.sequences_file:
        if not os.path.exists(args.sequences_file):
            print(f"❌ Error: Sequences file {args.sequences_file} not found")
            sys.exit(1)
        sequences_file = args.sequences_file

    # Run the scoring
    success = run_sequence_scoring(
        input_pdb=args.input,
        output_dir=args.output,
        seed=args.seed,
        model_type=args.model_type,
        sequences=sequences_file
    )

    # Clean up temporary file
    if args.sequences and sequences_file and os.path.exists(sequences_file):
        os.remove(sequences_file)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()