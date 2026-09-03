"""
FCC Lookup Preprocessing Script

This script preprocesses the FCC database into the single lookup table the
app uses to decide whether a chemical is a food contact chemical.

The lookup is keyed by casId, since every FCC universe entry has one, but a
CAS can carry zero, one, or (for enumerable CX SMILES) several canonical
SMILES rows. Structure-less entries are kept with an empty canonical_SMILES
so they remain identifiable by CAS, and CAS lookups no longer silently miss
chemicals that lack a parseable structure.

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
from fccgroup.molecular.composition import align_bundle_coords


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


def create_fcc_lookup(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """
    Create the single FCC lookup table used by the app.

    One casId can carry zero structures (kept, so CAS-only chemicals are
    still identifiable), one structure, or - rarely, for enumerable CX
    SMILES - several canonical structures; each becomes its own row sharing
    the same casId and metadata. There is deliberately no separate
    CAS-keyed and SMILES-keyed file: splitting them previously meant the
    CAS table only covered chemicals that also had a parseable structure,
    silently losing every structure-less entry from CAS lookups.

    Args:
        df: The FCC database as loaded from the Excel workbook.
        output_path: Path to output TSV file (FCC lookup table).
    """
    if 'casId' not in df.columns:
        raise ValueError("Input file must contain a 'casId' column")
    if 'SMILES' not in df.columns:
        raise ValueError("Input file must contain a 'SMILES' column")

    print("Expanding SMILES to canonical forms...")
    print(f"Processing {len(df)} entries (this may take a few minutes)...")
    print("⏱️  Note: Individual molecules timeout after 5 minutes and fall back to simple canonicalization")
    print()

    work_df = df.copy()
    work_df['casId'] = work_df['casId'].astype(str).str.strip()
    work_df = work_df[~work_df['casId'].str.lower().isin(['', 'nan', 'none'])]

    metadata_columns = [col for col in ('inFCCdb', 'inFCCmigex', 'Hazard', 'Tier of FCCprio') if col in work_df.columns]

    lookup_records = []
    without_structure = 0
    expanded_count = 0
    total_expansions = 0
    failed_count = 0

    for idx, row in work_df.iterrows():
        if (idx + 1) % 100 == 0:
            print(f"  Progress: {idx + 1}/{len(df)} ({((idx + 1)/len(df)*100):.1f}%)")

        metadata = {col: row[col] for col in metadata_columns}
        smiles = row.get('SMILES', '')

        if not smiles or pd.isna(smiles):
            without_structure += 1
            lookup_records.append({'casId': row['casId'], 'canonical_SMILES': '', **metadata})
            continue

        canonical_forms = expand_smiles_to_molecules(smiles)
        if len(canonical_forms) == 0:
            failed_count += 1
            lookup_records.append({'casId': row['casId'], 'canonical_SMILES': '', **metadata})
            continue

        if len(canonical_forms) > 1:
            expanded_count += 1
            total_expansions += len(canonical_forms)

        for canonical in canonical_forms:
            lookup_records.append({'casId': row['casId'], 'canonical_SMILES': canonical, **metadata})

    lookup_df = pd.DataFrame(lookup_records)
    initial_size = len(lookup_df)
    lookup_df = lookup_df.drop_duplicates(keep='first')
    duplicates_removed = initial_size - len(lookup_df)

    print()
    print(f"{'='*70}")
    print("Processing Summary:")
    print(f"{'='*70}")
    print(f"  • Universe entries:                {len(df):,}")
    print(f"  • Entries without a structure:     {without_structure:,} (kept)")
    print(f"  • Failed to parse:                 {failed_count:,} (kept, structure-less)")
    print(f"  • Expanded CX/enumerable SMILES:   {expanded_count:,}")
    print(f"  • Total canonical forms created:   {total_expansions:,}")
    print(f"  • Unique CAS in lookup:            {lookup_df['casId'].nunique():,}")
    print(f"  • Lookup rows:                     {len(lookup_df):,}")
    print(f"  • Exact duplicate rows removed:    {duplicates_removed:,}")
    print(f"{'='*70}")
    print()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    lookup_df.to_csv(output_path, index=False, sep='\t')
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved to {output_path} ({file_size_mb:.2f} MB)")
    print()

    return lookup_df


def main():
    """Main preprocessing function."""
    # Define paths relative to project root
    project_root = Path(__file__).parent.parent
    assets_path = project_root / "assets"

    # Input: FCC database (the one used in app.py)
    input_path = assets_path / "FCCuniverse.xlsx"

    # Output: single lookup table covering the whole FCC universe
    output_path = assets_path / "fcc_lookup.tsv"

    # Check if input exists
    if not input_path.exists():
        print(f"❌ Error: Input file not found at {input_path}")
        print("Please ensure the FCC database is available at:")
        print(f"  {input_path}")
        sys.exit(1)

    # Create lookup table
    try:
        print()
        print(f"{'='*70}")
        print("FCC Lookup Preprocessing")
        print(f"{'='*70}")
        print()

        print(f"Loading FCC database from: {input_path}")
        df = pd.read_excel(input_path)
        print(f"  ✓ Loaded {len(df)} entries")
        print()

        lookup_df = create_fcc_lookup(df, output_path)
        print("✅ Preprocessing completed successfully!")
        print()

        # Display sample
        print("Sample of lookup table:")
        sample_cols = [col for col in ['casId', 'canonical_SMILES', 'inFCCdb', 'inFCCmigex'] if col in lookup_df.columns]
        print(lookup_df[sample_cols].head(10))
        print()
        print("📋 Next steps:")
        print("  1. The lookup table is saved at:")
        print(f"     {output_path}")
        print("  2. The app loads it automatically: CAS first, structure as fallback")

    except Exception as e:
        print(f"❌ Error during preprocessing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
