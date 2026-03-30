"""Data processing and grouping pipeline helpers."""

from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from rdkit import Chem

from constants import FPPS_SET, REDUCED_FPPS
from fccgroup import ChemicalGrouper, ColumnMapping, GroupingConfig


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
            smarts_fingerprints=REDUCED_FPPS.keys(),
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
        column_name for column_name in ["is Food Contact Chemical", "Tier of FCCprio", "Groups of concern"]
        if column_name in results_df.columns
    ]
    if fallback_columns:
        return results_df[fallback_columns].copy()

    return results_df.copy()


def _canonicalize_smiles(smiles: str) -> Optional[str]:
    """Canonicalize SMILES with RDKit."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True)
    except Exception:
        return None


def _to_bool(value: object) -> bool:
    """Best-effort conversion from lookup values to boolean."""
    if pd.isna(value):
        return False
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return True
    if text in {"0", "false", "no", "n", ""}:
        return False
    return False


def _build_fcc_lookups_from_smiles_lookup(lookup_df: pd.DataFrame) -> Tuple[Dict[str, str], Dict[str, bool], Dict[str, str], Dict[str, bool]]:
    """Build CAS and SMILES lookup maps for FCC tier and FCC status."""
    required = {"casId", "Tier of FCCprio"}
    if not required.issubset(lookup_df.columns):
        return {}, {}, {}, {}

    work_df = lookup_df.copy()
    work_df["cas_norm"] = work_df["casId"].astype(str).str.strip()

    if "canonical_SMILES" in work_df.columns:
        work_df["smiles_norm"] = work_df["canonical_SMILES"].astype(str).str.strip()
    elif "SMILES" in work_df.columns:
        work_df["smiles_norm"] = work_df["SMILES"].astype(str).apply(_canonicalize_smiles).fillna("")
    else:
        work_df["smiles_norm"] = ""

    if {"inFCCdb", "inFCCmigex"}.issubset(work_df.columns):
        work_df["fcc_flag"] = work_df["inFCCdb"].apply(_to_bool) | work_df["inFCCmigex"].apply(_to_bool)
    else:
        work_df["fcc_flag"] = True

    def first_non_empty(values: pd.Series) -> str:
        for value in values:
            if pd.notna(value) and str(value).strip() != "":
                return str(value).strip()
        return ""

    cas_df = work_df[work_df["cas_norm"] != ""]
    cas_tier_lookup = cas_df.groupby("cas_norm")["Tier of FCCprio"].apply(first_non_empty).to_dict()
    cas_fcc_lookup = cas_df.groupby("cas_norm")["fcc_flag"].any().to_dict()

    smiles_df = work_df[work_df["smiles_norm"] != ""]
    smiles_tier_lookup = smiles_df.groupby("smiles_norm")["Tier of FCCprio"].apply(first_non_empty).to_dict()
    smiles_fcc_lookup = smiles_df.groupby("smiles_norm")["fcc_flag"].any().to_dict()

    return cas_tier_lookup, cas_fcc_lookup, smiles_tier_lookup, smiles_fcc_lookup


def run_grouping_pipeline(analysis_df: pd.DataFrame, mapping_payload: Dict[str, object], grouping_methods: List[str]) -> pd.DataFrame:
    """Run full grouping + enrichment pipeline for current analysis dataframe."""
    methods_signature = tuple(sorted(str(method).lower() for method in grouping_methods))
    df_signature = dataframe_signature(analysis_df)
    grouper_sig = (df_signature, methods_signature, mapping_signature(mapping_payload))

    if st.session_state.grouper_signature != grouper_sig or st.session_state.grouper_instance is None:
        st.session_state.grouper_instance = initialize_grouper(
            _df=analysis_df,
            df_signature=df_signature,
            methods=methods_signature,
            mapping_payload=mapping_payload,
        )
        st.session_state.grouper_signature = grouper_sig

    results_df = st.session_state.grouper_instance.group_chemicals()

    smiles_lookup_df = load_smiles_lookup()
    if smiles_lookup_df is not None:
        cas_tier_lookup, cas_fcc_lookup, smiles_tier_lookup, smiles_fcc_lookup = _build_fcc_lookups_from_smiles_lookup(smiles_lookup_df)
    else:
        cas_tier_lookup, cas_fcc_lookup, smiles_tier_lookup, smiles_fcc_lookup = {}, {}, {}, {}

    results_df["is Food Contact Chemical"] = ""
    results_df["Tier of FCCprio"] = ""

    if "casId" in results_df.columns:
        cas_norm = results_df["casId"].astype(str).str.strip()
        results_df["is Food Contact Chemical"] = cas_norm.map(lambda x: "Yes" if cas_fcc_lookup.get(x, False) else "No")
        results_df["Tier of FCCprio"] = cas_norm.map(cas_tier_lookup).fillna("")

    if "SMILES" in results_df.columns:
        canonical_smiles = results_df["SMILES"].astype(str).apply(_canonicalize_smiles)
        unresolved_mask = results_df["Tier of FCCprio"].astype(str).str.strip() == ""

        smiles_tier_series = canonical_smiles.map(smiles_tier_lookup).fillna("")
        smiles_fcc_series = canonical_smiles.map(lambda x: "Yes" if smiles_fcc_lookup.get(x, False) else "No")

        results_df.loc[unresolved_mask, "Tier of FCCprio"] = smiles_tier_series[unresolved_mask]

        unresolved_fcc_mask = (results_df["is Food Contact Chemical"].astype(str).str.strip() == "") | (
            results_df["is Food Contact Chemical"].astype(str).str.strip() == "No"
        )
        results_df.loc[unresolved_fcc_mask, "is Food Contact Chemical"] = smiles_fcc_series[unresolved_fcc_mask]

    if "Chemical groups" in results_df.columns:
        results_df["Groups of concern"] = results_df.apply(
            lambda row: ",".join(
                [
                    group.strip()
                    for group in row["Chemical groups"].split(",")
                    if group.strip() in FPPS_SET and FPPS_SET[group.strip()]
                ]
            ),
            axis=1,
        )
    else:
        results_df["Groups of concern"] = ""

    return results_df
