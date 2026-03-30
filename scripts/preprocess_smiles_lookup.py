"""
SMILES Lookup Preprocessing Script

This script preprocesses the FCC database to create a SMILES-based lookup table.
It expands CX SMILES and other enumerable SMILES formats into all possible 
canonical SMILES representations, enabling fast matching during runtime.

Run this script whenever the FCC database is updated:
    python scripts/preprocess_smiles_lookup.py
"""

import sys
from pathlib import Path
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdMolEnumerator
import threading
from queue import Queue, Empty

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

try:
    from fccgroup.molecular.composition import align_bundle_coords
except ImportError:
    print("Warning: Could not import align_bundle_coords, using basic enumeration")
    align_bundle_coords = lambda x: x


def canonicalize_smiles(smiles: str) -> str:
    """Canonicalize a SMILES string using RDKit."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True)
    except:
        return None


def expand_smiles_to_molecules(smiles: str) -> list:
    """
    Expand a SMILES (including CX SMILES) into all possible canonical SMILES.
    
    Handles:
    - Enhanced stereochemistry (CX SMILES feature)
    - Mixtures
    - Variable attachment points
    - Any other RDKit-enumerable features
    
    Returns list of canonical SMILES strings.
    """
    canonical_smiles = []
    
    def enumerate_with_timeout(mol, result_queue, timeout=300):
        """Helper function to enumerate molecules with timeout (5 minutes default)."""
        try:
            enumerated_mols = list(rdMolEnumerator.Enumerate(mol))
            
            if len(enumerated_mols) > 1:
                # Multiple molecules enumerated (mixtures, stereo, etc.)
                for enumerated_mol in align_bundle_coords(enumerated_mols):
                    canonical = Chem.MolToSmiles(enumerated_mol, canonical=True)
                    result_queue.put(canonical)
            else:
                # Single molecule - just canonicalize
                canonical = Chem.MolToSmiles(mol, canonical=True)
                result_queue.put(canonical)
            result_queue.put(None)  # Signal completion
        except Exception as e:
            result_queue.put(None)  # Signal completion with error
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return []
        
        # Use threading with timeout to handle long-running enumerations
        result_queue = Queue()
        thread = threading.Thread(target=enumerate_with_timeout, args=(mol, result_queue, 300))
        thread.daemon = True
        thread.start()
        thread.join(timeout=300)  # 5 minutes timeout
        
        if thread.is_alive():
            # Timeout occurred - fall back to simple canonicalization
            print(f"    ⚠ Timeout during enumeration, using simple canonicalization")
            try:
                canonical = Chem.MolToSmiles(mol, canonical=True)
                canonical_smiles.append(canonical)
            except:
                pass
        else:
            # Collect results from queue
            while True:
                try:
                    result = result_queue.get_nowait()
                    if result is None:
                        break
                    canonical_smiles.append(result)
                except Empty:
                    break
            
    except Exception as e:
        pass
    
    return list(set(canonical_smiles))  # Remove duplicates


def create_smiles_lookup(input_path: Path, output_path: Path):
    """
    Create a SMILES lookup table from the FCC database.
    
    Args:
        input_path: Path to input Excel file (FCC database)
        output_path: Path to output TSV file (SMILES lookup table)
    """
    print(f"\n{'='*70}")
    print("SMILES Lookup Preprocessing")
    print(f"{'='*70}\n")
    
    # Load the FCC database
    print(f"Loading FCC database from: {input_path}")
    df = pd.read_excel(input_path)
    print(f"  ✓ Loaded {len(df)} entries\n")
    
    # Check for SMILES column
    if 'SMILES' not in df.columns:
        raise ValueError("Input file must contain a 'SMILES' column")
    
    # Prepare lookup records
    print("Expanding SMILES to canonical forms...")
    print(f"Processing {len(df)} entries (this may take a few minutes)...")
    print("⏱️  Note: Individual molecules timeout after 5 minutes and fall back to simple canonicalization\n")
    
    lookup_records = []
    expanded_count = 0
    total_expansions = 0
    failed_count = 0
    timeout_count = 0
    
    for idx, row in df.iterrows():
        if (idx + 1) % 100 == 0:
            print(f"  Progress: {idx + 1}/{len(df)} ({((idx + 1)/len(df)*100):.1f}%) | Timeouts: {timeout_count}")
        
        smiles = row.get('SMILES', '')
        if not smiles or pd.isna(smiles):
            continue
        
        # Expand the SMILES (handles both CX and regular SMILES)
        canonical_forms = expand_smiles_to_molecules(smiles)
        
        if len(canonical_forms) == 0:
            failed_count += 1
            continue
        
        if len(canonical_forms) > 1:
            expanded_count += 1
            total_expansions += len(canonical_forms)
        
        # Create a record for each canonical form
        for canonical in canonical_forms:
            lookup_record = row.to_dict()
            lookup_record['canonical_SMILES'] = canonical
            lookup_record['original_SMILES'] = smiles
            lookup_records.append(lookup_record)
    
    # Create lookup DataFrame
    lookup_df = pd.DataFrame(lookup_records)
    
    # Remove duplicates (keep first occurrence)
    initial_size = len(lookup_df)
    lookup_df = lookup_df.drop_duplicates(subset=['canonical_SMILES'], keep='first')
    duplicates_removed = initial_size - len(lookup_df)
    
    print(f"\n{'='*70}")
    print("Processing Summary:")
    print(f"{'='*70}")
    print(f"  • Original entries:                {len(df):,}")
    print(f"  • Failed to parse:                 {failed_count:,}")
    print(f"  • Expanded CX/enumerable SMILES:   {expanded_count:,}")
    print(f"  • Total canonical forms created:   {total_expansions:,}")
    print(f"  • Unique canonical SMILES:         {len(lookup_df):,}")
    print(f"  • Duplicates removed:              {duplicates_removed:,}")
    print(f"{'='*70}\n")
    
    # Save to TSV (tab-separated values format)
    print(f"Saving lookup table to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lookup_df.to_csv(output_path, index=False, sep='\t')
    
    # Report file size
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved successfully ({file_size_mb:.2f} MB)\n")
    
    return lookup_df


def main():
    """Main preprocessing function."""
    # Define paths relative to project root
    project_root = Path(__file__).parent.parent
    assets_path = project_root / "assets"
    
    # Input: FCC database (the one used in app.py)
    input_path = assets_path / "FCCuniverse_grouping_in.xlsx"
    
    # Output: SMILES lookup table
    output_path = assets_path / "smiles_lookup.tsv"
    
    # Check if input exists
    if not input_path.exists():
        print(f"❌ Error: Input file not found at {input_path}")
        print("\nPlease ensure the FCC database is available at:")
        print(f"  {input_path}")
        sys.exit(1)
    
    # Create lookup table
    try:
        lookup_df = create_smiles_lookup(input_path, output_path)
        print("✅ Preprocessing completed successfully!\n")
        
        # Display sample
        print("Sample of lookup table:")
        sample_cols = ['canonical_SMILES', 'original_SMILES']
        if 'casId' in lookup_df.columns:
            sample_cols.append('casId')
        print(lookup_df[sample_cols].head(10))
        print("\n")
        print("📋 Next steps:")
        print("  1. The lookup table is saved at:")
        print(f"     {output_path}")
        print("  2. The app will automatically load it when using SMILES input mode")
        
    except Exception as e:
        print(f"\n❌ Error during preprocessing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
