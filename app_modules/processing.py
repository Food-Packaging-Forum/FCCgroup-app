"""Data processing and grouping pipeline helpers."""

from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import streamlit as st
from rdkit import Chem

from fccgroup import ChemicalGrouper, ColumnMapping, GroupingConfig
from fccgroup.constants import MULTIINDEX_IDENTIFIER_LABEL, MULTIINDEX_STRUCTURAL_LABEL
from app_modules.config import CAS_COLUMN_INPUT, FOOD_CONTACT_CHEMICAL_COLUMN, GROUPS_OF_CONCERN_COLUMN, HAZARD_COLUMN, SMILES_COLUMN_INPUT, TIER_OF_FCCPRIO_COLUMN


@st.cache_data
def load_smiles_lookup():
    """Load preprocessed SMILES lookup table for fast enrichment."""
    lookup_path = "assets/smiles_lookup.tsv"
    try:
        lookup_df = pd.read_csv(lookup_path, sep="\t")
    except FileNotFoundError:
        return None
    return lookup_df


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


def _build_fcc_lookups_from_smiles_lookup(lookup_df: pd.DataFrame) -> Tuple[Dict[str, str], Dict[str, bool], Dict[str, str], Dict[str, bool]]:
    """Build CAS and SMILES lookup maps for FCC tier and FCC status."""
    work_df = lookup_df.copy()
    work_df["cas_norm"] = work_df[CAS_COLUMN_INPUT].astype(str).str.strip()

    if "canonical_SMILES" in work_df.columns:
        work_df["smiles_norm"] = work_df["canonical_SMILES"].astype(str).str.strip()
    elif "SMILES" in work_df.columns:
        work_df["smiles_norm"] = work_df["SMILES"].astype(str).apply(_canonicalize_smiles).fillna("")
    else:
        work_df["smiles_norm"] = ""

    work_df["fcc_flag"] = work_df.apply(
        lambda x: "In FCCdb and FCCmigex" if x["inFCCdb"] and x["inFCCmigex"] 
            else ("In FCCdb" if x["inFCCdb"] 
            else ("In FCCmigex" if x["inFCCmigex"] 
            else "Not a FCC")),
        axis=1
    )

    def first_non_empty(values: pd.Series) -> str:
        for value in values:
            if pd.notna(value) and str(value).strip() != "":
                return str(value).strip()
        return ""

    cas_df = work_df[work_df["cas_norm"] != ""]
    cas_tier_lookup = cas_df.groupby("cas_norm")["Tier of FCCprio"].apply(first_non_empty).to_dict()
    cas_hazard_lookup = cas_df.groupby("cas_norm")[HAZARD_COLUMN].apply(first_non_empty).to_dict()
    cas_fcc_lookup = cas_df.groupby("cas_norm")["fcc_flag"].apply(first_non_empty).to_dict()

    smiles_df = work_df[work_df["smiles_norm"] != ""]
    smiles_tier_lookup = smiles_df.groupby("smiles_norm")["Tier of FCCprio"].apply(first_non_empty).to_dict()
    smiles_hazard_lookup = smiles_df.groupby("smiles_norm")[HAZARD_COLUMN].apply(first_non_empty).to_dict()
    smiles_fcc_lookup = smiles_df.groupby("smiles_norm")["fcc_flag"].apply(first_non_empty).to_dict()

    return cas_tier_lookup, cas_fcc_lookup, cas_hazard_lookup, smiles_tier_lookup, smiles_fcc_lookup, smiles_hazard_lookup


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

    results_df = st.session_state.grouper_instance.group_chemicals(save=False)
    results_df = _flatten_results_columns(results_df)

    smiles_lookup_df = load_smiles_lookup()
    cas_tier_lookup, cas_fcc_lookup, cas_hazard_lookup, smiles_tier_lookup, smiles_fcc_lookup, smiles_hazard_lookup = _build_fcc_lookups_from_smiles_lookup(smiles_lookup_df)

    results_df[FOOD_CONTACT_CHEMICAL_COLUMN] = ""
    results_df[TIER_OF_FCCPRIO_COLUMN] = ""
    results_df[HAZARD_COLUMN] = ""

    if CAS_COLUMN_INPUT in results_df.columns:
        cas_norm = results_df[CAS_COLUMN_INPUT].astype(str).str.strip()
        results_df[FOOD_CONTACT_CHEMICAL_COLUMN] = cas_norm.map(lambda x: cas_fcc_lookup.get(x, "Not a FCC"))
        results_df[TIER_OF_FCCPRIO_COLUMN] = cas_norm.map(cas_tier_lookup).fillna("")
        results_df[HAZARD_COLUMN] = cas_norm.map(cas_hazard_lookup).fillna("")

    if SMILES_COLUMN_INPUT in results_df.columns:
        canonical_smiles = results_df[SMILES_COLUMN_INPUT].astype(str).apply(_canonicalize_smiles)
        unresolved_mask = results_df[TIER_OF_FCCPRIO_COLUMN].astype(str).str.strip() == ""

        smiles_tier_series = canonical_smiles.map(smiles_tier_lookup).fillna("")
        smiles_fcc_series = canonical_smiles.map(lambda x: smiles_fcc_lookup.get(x, "Not a FCC"))

        results_df.loc[unresolved_mask, TIER_OF_FCCPRIO_COLUMN] = smiles_tier_series[unresolved_mask]
        results_df.loc[unresolved_mask, HAZARD_COLUMN] = canonical_smiles.map(smiles_hazard_lookup).fillna("")[unresolved_mask]

        unresolved_fcc_mask = (results_df[FOOD_CONTACT_CHEMICAL_COLUMN].astype(str).str.strip() == "") | (
            results_df[FOOD_CONTACT_CHEMICAL_COLUMN].astype(str).str.strip() == "No"
        )
        results_df.loc[unresolved_fcc_mask, FOOD_CONTACT_CHEMICAL_COLUMN] = smiles_fcc_series[unresolved_fcc_mask]
    return results_df
