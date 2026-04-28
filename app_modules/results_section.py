"""Results rendering and export UI."""

from io import BytesIO

import pandas as pd
import streamlit as st

from app_modules.config import DISPLAY_RESULT_COLUMNS
from app_modules.processing import build_display_results_df


def _has_non_empty_value(value: object) -> bool:
    """Return True when value is neither NA nor an empty/whitespace string."""
    if pd.isna(value):
        return False

    if str(value).strip() == "":
        return False

    return True


def render_results_section(full_results_df: pd.DataFrame) -> None:
    """Render summary metrics, filters, table, and export controls."""
    results_df = full_results_df

    results_df.rename(columns={"casId": "CAS RN", "SMILES": "SMILES", "column_names": "Chemical names", "formula": "Formula"}, inplace=True)
    if len(results_df) == 0:
        st.warning("⚠️ No results to display. The dataframe is empty.")
        return

    st.markdown(
        """
        <div class="process-step">
            <h3>Step 3: Explore Results</h3>
            <p>Review classifications and download your data</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📊 Summary Dashboard")

    total_count = len(results_df)
    metrics = [("Total Chemicals", total_count, "🧪")]

    if "SMILES" in results_df.columns:
        valid_smiles_count = int(results_df["SMILES"].apply(_has_non_empty_value).sum())
        metrics.append(("Valid SMILES", f"{valid_smiles_count}/{total_count}", "🧬"))
    else:
        metrics.append(("Valid SMILES", "N/A", "🧬"))

    fcc_status_col = "is Food Contact Chemical"
    fcc_tier_col = "Tier of FCCprio"

    if fcc_status_col in results_df.columns:
        food_contact_count = int(results_df[fcc_status_col].apply(_has_non_empty_value).sum())
        metrics.append(("Food Contact", f"{food_contact_count}/{total_count}", "🗄️"))

    if fcc_tier_col in results_df.columns:
        fcc_tier_count = int(results_df[fcc_tier_col].apply(_has_non_empty_value).sum())
        metrics.append(("FCCprio Tier", f"{fcc_tier_count}/{total_count}", "🎯"))

    if "Groups of concern" in results_df.columns:
        groups_count = int(results_df["Groups of concern"].apply(_has_non_empty_value).sum())
        metrics.append(("With Groups", f"{groups_count}/{total_count}", "🔬"))

    cols = st.columns(len(metrics))
    for col, (label, value, icon) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #667eea; margin: 0.5rem 0;">{value}</div>
                    <div class="metric-card-label" style="font-size: 0.85rem;">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Detailed Results Table")

    with st.expander("🔍 Filter Options", expanded=False):
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            if fcc_status_col in results_df.columns:
                fcc_filter = st.multiselect(
                    "Filter by FCC Status",
                    options=results_df[fcc_status_col].unique(),
                    default=None,
                )
                if fcc_filter:
                    results_df = results_df[results_df[fcc_status_col].isin(fcc_filter)]

        with filter_col2:
            if fcc_tier_col in results_df.columns:
                tier_filter = st.multiselect(
                    "Filter by FCCprio Tier",
                    options=sorted([t for t in results_df[fcc_tier_col].unique() if t != ""]),
                    default=None,
                )
                if tier_filter:
                    results_df = results_df[results_df[fcc_tier_col].isin(tier_filter)]

        with filter_col3:
            if "Groups of concern" in results_df.columns:
                groups_concern = results_df["Groups of concern"].str.split(",").explode().unique()

                group_col1, group_col2 = st.columns([3, 1])
                with group_col1:
                    group_filter = st.multiselect(
                        "Filter by Groups of Concern",
                        options=sorted([g.strip() for g in groups_concern if g and str(g).strip() != ""]),
                        default=None,
                        key="groups_multiselect",
                    )

                with group_col2:
                    if len(group_filter) > 1:
                        st.markdown("<br>", unsafe_allow_html=True)
                        logic_operator = st.radio(
                            "Logic",
                            options=["OR", "AND"],
                            index=0,
                            label_visibility="collapsed",
                            key="logic_operator",
                            help="OR: Match any selected group | AND: Match all selected groups",
                        )
                    else:
                        logic_operator = "OR"

                if group_filter:
                    if logic_operator == "OR":
                        filter_func = lambda x: any(g.strip() in str(x) for g in group_filter)
                    else:
                        filter_func = lambda x: all(g.strip() in str(x) for g in group_filter)

                    results_df = results_df[results_df["Groups of concern"].apply(filter_func)]

    display_results_df = build_display_results_df(results_df, DISPLAY_RESULT_COLUMNS)
    st.dataframe(display_results_df, use_container_width=True)

    st.markdown("### 💾 Export Results")
    identifier_cols = ["CAS RN", "SMILES", "Chemical names", "Formula"]
    enrichment_cols = ["is Food Contact Chemical", "Tier of FCCprio", "Groups of concern"]

    col_order = []
    col_order.extend([c for c in identifier_cols if c in full_results_df.columns])
    col_order.extend([c for c in enrichment_cols if c in full_results_df.columns])
    col_order.extend([c for c in full_results_df.columns if c not in col_order])

    export_results_df = full_results_df[col_order]

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        csv = export_results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"fcc_grouping_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_results_df.to_excel(writer, index=False, sheet_name="Results")

        st.download_button(
            label="📥 Download Excel",
            data=buffer.getvalue(),
            file_name=f"fcc_grouping_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col3:
        if st.button("🔄 Start New Analysis", use_container_width=True):
            st.session_state.results_df = None
            st.session_state.cas_input_text = ""
            st.rerun()
