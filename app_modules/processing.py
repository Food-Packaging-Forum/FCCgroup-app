"""Data processing and grouping pipeline helpers."""

from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import streamlit as st
from rdkit import Chem

from fccgroup import ChemicalGrouper, ColumnMapping, GroupingConfig
from fccgroup.constants import MULTIINDEX_IDENTIFIER_LABEL, MULTIINDEX_STRUCTURAL_LABEL
from app_modules.config import (
    CANONICAL_SMILES_COLUMN,
    CAS_COLUMN_INPUT,
    FCC_LOOKUP_PATH,
    FOOD_CONTACT_CHEMICAL_COLUMN,
    GROUPS_OF_CONCERN_COLUMN,
    HAZARD_COLUMN,
    IN_FCCDB_COLUMN,
    IN_FCCMIGEX_COLUMN,
    NOT_AN_FCC_LABEL,
    SMILES_COLUMN_INPUT,
    TIER_OF_FCCPRIO_COLUMN,
)


@st.cache_data
def load_fcc_lookup_df() -> Optional[pd.DataFrame]:
    """Load the preprocessed FCC lookup table, or None when it hasn't been generated yet.

    One row per (casId, canonical_SMILES) pair, covering the whole FCC universe:
    entries without a chemical structure are kept with an empty canonical_SMILES
    so a CAS-only chemical is still identifiable.
    """
    try:
        return pd.read_csv(FCC_LOOKUP_PATH, sep="\t", dtype={CAS_COLUMN_INPUT: str})
    except FileNotFoundError:
        return None


@st.cache_data
def load_fcc_cas_records() -> Dict[str, Dict[str, str]]:
    """Index FCC records by CAS across the whole universe."""
    return _build_fcc_records(load_fcc_lookup_df(), CAS_COLUMN_INPUT)


@st.cache_data
def load_fcc_smiles_records() -> Dict[str, Dict[str, str]]:
    """Index FCC records by canonical SMILES, for structural matching."""
    return _build_fcc_records(load_fcc_lookup_df(), CANONICAL_SMILES_COLUMN)


@st.cache_resource
def initialize_grouper(
    _df: pd.DataFrame,
    df_signature: Tuple[object, ...],
    methods: Tuple[str, ...],
    mapping_payload: Dict[str, object],
) -> ChemicalGrouper:
    """Initialize grouper with cache over full initialization signature."""
    with st.spinner("🔄 Initializing chemical grouper..."):
        column_mapping = ColumnMapping(
            cas=mapping_payload.get("cas"),
            smiles=mapping_payload.get("smiles"),
            name_columns=mapping_payload.get("name_columns", []),
            formula=mapping_payload.get("formula"),
        )
        config = GroupingConfig(
            methods=list(methods),
            column_mapping=column_mapping,
        )
        return ChemicalGrouper(df=_df, grouping_config=config)


def mapping_signature(mapping_payload: Dict[str, object]) -> Tuple[Tuple[str, object], ...]:
    """Build stable signature from mapping payload content."""
    normalized = []
    for key in sorted(mapping_payload.keys()):
        value = mapping_payload[key]
        if isinstance(value, list):
            normalized.append((key, tuple(value)))
        else:
            normalized.append((key, value))
    return tuple(normalized)


def dataframe_signature(df: pd.DataFrame) -> Tuple[object, ...]:
    """Build content-aware dataframe signature for cache invalidation."""
    if df is None:
        return ("none",)

    hash_value = int(pd.util.hash_pandas_object(df.astype(str), index=True).sum()) if len(df) > 0 else 0
    return (
        tuple(df.columns.tolist()),
        tuple(df.dtypes.astype(str).tolist()),
        len(df),
        hash_value,
    )


def build_display_results_df(results_df: pd.DataFrame, display_columns: List[str]) -> pd.DataFrame:
    """Build display dataframe from preferred output columns."""
    available_columns = [column_name for column_name in display_columns if column_name in results_df.columns]
    if available_columns:
        return results_df[available_columns].copy()

    fallback_columns = [
        column_name for column_name in [FOOD_CONTACT_CHEMICAL_COLUMN, TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN, GROUPS_OF_CONCERN_COLUMN]
        if column_name in results_df.columns
    ]
    if fallback_columns:
        return results_df[fallback_columns].copy()

    return results_df.copy()


def _make_unique_column_name(base_name: str, existing_names: Set[str]) -> str:
    """Ensure flattened column names stay unique and deterministic."""
    candidate = base_name
    suffix = 2
    while candidate in existing_names:
        candidate = f"{base_name} ({suffix})"
        suffix += 1
    return candidate


def _flatten_results_columns(results_df: pd.DataFrame) -> pd.DataFrame:
    """Flatten fccgroup MultiIndex output while preserving child column labels."""
    flattened_columns: List[str] = []
    seen: Set[str] = set()

    for column in results_df.columns:
        parent = str(column[0]).strip() if len(column) > 0 and pd.notna(column[0]) else ""
        child = str(column[1]).strip() if len(column) > 1 and pd.notna(column[1]) else ""

        if parent in {MULTIINDEX_IDENTIFIER_LABEL, MULTIINDEX_STRUCTURAL_LABEL} and child:
            base_name = child
        elif child:
            base_name = f"{parent} | {child}" if parent else child
        else:
            base_name = parent or "column"

        unique_name = _make_unique_column_name(base_name, seen)
        seen.add(unique_name)
        flattened_columns.append(unique_name)

    flattened_df = results_df.copy()
    flattened_df.columns = flattened_columns
    return flattened_df


def _canonicalize_smiles(smiles: str) -> Optional[str]:
    """Canonicalize SMILES with RDKit."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True)
    except Exception:
        return None


def _first_non_empty(values) -> str:
    """Return the first value that is neither NA nor blank, else an empty string."""
    for value in values:
        if pd.notna(value) and str(value).strip() != "":
            return str(value).strip()
    return ""


def _fcc_status_label(in_fccdb: bool, in_fccmigex: bool) -> str:
    """Name the source database(s) an entry belongs to.

    A blank flag never counts as membership, so entries carrying neither flag
    stay non-FCCs rather than being reported as present in both databases.
    """
    if in_fccdb and in_fccmigex:
        return "In FCCdb and FCCmigex"
    if in_fccdb:
        return "In FCCdb"
    if in_fccmigex:
        return "In FCCmigex"
    return NOT_AN_FCC_LABEL


def _build_fcc_records(lookup_df: Optional[pd.DataFrame], key_column: str) -> Dict[str, Dict[str, str]]:
    """Index one FCC record per identifier so status, tier and hazard stay in sync."""
    if lookup_df is None or key_column not in lookup_df.columns:
        return {}

    work_df = lookup_df.copy()
    work_df["_key"] = work_df[key_column].astype(str).str.strip()
    work_df = work_df[~work_df["_key"].str.lower().isin(["", "nan", "none"])]

    for flag_column in (IN_FCCDB_COLUMN, IN_FCCMIGEX_COLUMN):
        if flag_column in work_df.columns:
            work_df[flag_column] = pd.to_numeric(work_df[flag_column], errors="coerce").fillna(0) > 0
        else:
            work_df[flag_column] = False

    for value_column in (TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN):
        if value_column not in work_df.columns:
            work_df[value_column] = ""

    # An identifier listed more than once is present in a database when any of its rows says so.
    grouped = work_df.groupby("_key", sort=False).agg(
        in_fccdb=(IN_FCCDB_COLUMN, "any"),
        in_fccmigex=(IN_FCCMIGEX_COLUMN, "any"),
        tier=(TIER_OF_FCCPRIO_COLUMN, _first_non_empty),
        hazard=(HAZARD_COLUMN, _first_non_empty),
    )

    return {
        key: {
            "status": _fcc_status_label(bool(row.in_fccdb), bool(row.in_fccmigex)),
            "tier": row.tier,
            "hazard": row.hazard,
        }
        for key, row in zip(grouped.index, grouped.itertuples(index=False))
    }


def _identifier_keys(results_df: pd.DataFrame, column_name: str, canonicalize: bool) -> List[Optional[str]]:
    """Extract normalized lookup keys for one identifier column, or Nones when absent."""
    if column_name not in results_df.columns:
        return [None] * len(results_df)

    values = results_df[column_name].astype(str).str.strip()
    if canonicalize:
        return [_canonicalize_smiles(value) if value else None for value in values]
    return [value if value and value.lower() not in {"nan", "none"} else None for value in values]


def _assign_fcc_columns(results_df: pd.DataFrame, cas_is_primary: bool) -> pd.DataFrame:
    """Resolve FCC status, tier and hazard for every row.

    The identifier the user actually supplied decides first: a CAS is a valid
    identifier even for chemicals that have no structure, so it must not be
    overruled by — or lost to — structural matching. The other identifier is
    only consulted when the primary one finds nothing.
    """
    cas_records = load_fcc_cas_records()
    smiles_records = load_fcc_smiles_records()

    cas_keys = _identifier_keys(results_df, CAS_COLUMN_INPUT, canonicalize=False)
    smiles_keys = _identifier_keys(results_df, SMILES_COLUMN_INPUT, canonicalize=True)

    statuses: List[str] = []
    tiers: List[str] = []
    hazards: List[str] = []

    for cas_key, smiles_key in zip(cas_keys, smiles_keys):
        cas_record = cas_records.get(cas_key) if cas_key else None
        smiles_record = smiles_records.get(smiles_key) if smiles_key else None

        ordered = [cas_record, smiles_record] if cas_is_primary else [smiles_record, cas_record]
        matches = [record for record in ordered if record]

        statuses.append(matches[0]["status"] if matches else NOT_AN_FCC_LABEL)
        tiers.append(_first_non_empty(record["tier"] for record in matches))
        hazards.append(_first_non_empty(record["hazard"] for record in matches))

    results_df[FOOD_CONTACT_CHEMICAL_COLUMN] = statuses
    results_df[TIER_OF_FCCPRIO_COLUMN] = tiers
    results_df[HAZARD_COLUMN] = hazards
    return results_df


def run_grouping_pipeline(analysis_df: pd.DataFrame, mapping_payload: Dict[str, object], grouping_methods: List[str]) -> pd.DataFrame:
    """Run full grouping + enrichment pipeline for current analysis dataframe."""
    methods_signature = tuple(sorted(str(method).lower() for method in grouping_methods))
    df_signature = dataframe_signature(analysis_df)
    grouper_sig = (df_signature, methods_signature, mapping_signature(mapping_payload))

    if st.session_state.grouper_signature != grouper_sig or st.session_state.grouper_instance is None:
        st.session_state.grouper_instance = initialize_grouper(
            _df=analysis_df.iloc[:1000],
            df_signature=df_signature,
            methods=methods_signature,
            mapping_payload=mapping_payload,
        )
        st.session_state.grouper_signature = grouper_sig

    results_df = st.session_state.grouper_instance.group_chemicals(save=False, verbose=True)
    results_df = _flatten_results_columns(results_df)

    if not load_fcc_cas_records() and not load_fcc_smiles_records():
        st.warning(
            "⚠️ FCC lookup tables are missing. Run "
            "`python scripts/preprocess_smiles_lookup.py` to generate them; "
            "until then no chemical can be identified as an FCC."
        )

    return _assign_fcc_columns(results_df, cas_is_primary=bool(mapping_payload.get("cas")))
