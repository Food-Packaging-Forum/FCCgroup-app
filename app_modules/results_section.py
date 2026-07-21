"""Results rendering and export UI."""

from io import BytesIO

import pandas as pd
import streamlit as st

from app_modules.config import DISPLAY_RESULT_COLUMNS
from app_modules.processing import build_display_results_df
from app_modules.config import CHEMICAL_NAMES_COLUMN, FOOD_CONTACT_CHEMICAL_COLUMN, FORMULA_COLUMN, RENAME_DICT, TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN, GROUPS_OF_CONCERN_COLUMN, CAS_COLUMN, SMILES_COLUMN


def _fcc_status_to_tags(value: object) -> list:
    """Convert an FCC status string into read-only tags for ListColumn display."""
    text = str(value).lower()
    tags = []
    if "fccdb" in text:
        tags.append("FCCdb")
    if "fccmigex" in text:
        tags.append("FCCmigex")
    if "not a fcc" in text:
        tags.append("Not a FCC")
    return tags


def _has_non_empty_value(value: object) -> bool:
    """Return True when value is neither NA nor an empty/whitespace string."""
    if pd.isna(value):
        return False

    if str(value).strip() == "":
        return False

    return True


def render_results_section(full_results_df: pd.DataFrame) -> None:
    """Render summary metrics, filters, table, and export controls."""
    results_df = full_results_df.copy()
    results_df = results_df.rename(columns=RENAME_DICT)
    if len(results_df) == 0:
        st.warning("⚠️ No results to display. The dataframe is empty.")
        return

    st.markdown(
        """
        <div class="section-gradient-divider"></div>
        <h2 class="workflow-section-title">
            <span class="highlight">Step 3: Explore Results</span>
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <h3 class="workflow-subsection-title">
            <span class="highlight">Summary Dashboard</span>
        </h3>
        """,
        unsafe_allow_html=True,
    )

    total_count = len(results_df)
    metrics = [("Total Chemicals", total_count, "🧪")]

    if SMILES_COLUMN in results_df.columns:
        valid_smiles_count = int(results_df[SMILES_COLUMN].apply(_has_non_empty_value).sum())
        metrics.append(("Valid SMILES", f"{valid_smiles_count}/{total_count}", "🧬"))
    else:
        metrics.append(("Valid SMILES", "N/A", "🧬"))

    if FOOD_CONTACT_CHEMICAL_COLUMN in results_df.columns:
        food_contact_count = int(results_df[FOOD_CONTACT_CHEMICAL_COLUMN].apply(lambda x: x!="Not a FCC").sum())
        metrics.append(("Food Contact", f"{food_contact_count}/{total_count}", "🗄️"))

    if TIER_OF_FCCPRIO_COLUMN in results_df.columns:
        fcc_tier_count = int(results_df[TIER_OF_FCCPRIO_COLUMN].apply(_has_non_empty_value).sum())
        metrics.append(("FCCprio Tier", f"{fcc_tier_count}/{total_count}", "🎯"))

    if GROUPS_OF_CONCERN_COLUMN in results_df.columns:
        groups_count = int(results_df[GROUPS_OF_CONCERN_COLUMN].apply(_has_non_empty_value).sum())
        metrics.append(("With Priority Groups", f"{groups_count}/{total_count}", "🔬"))
    print(results_df.columns)
    results_df[[TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN, GROUPS_OF_CONCERN_COLUMN]] = results_df[[TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN, GROUPS_OF_CONCERN_COLUMN]].replace("", "NA")

    unfiltered_results_df = results_df.copy()

    cards_html = "".join(
        f'<div class="metric-card">'
        f'<div class="metric-card-icon">{icon}</div>'
        f'<div class="metric-card-value">{value}</div>'
        f'<div class="metric-card-label">{label}</div>'
        f'</div>'
        for label, value, icon in metrics
    )
    st.markdown(
        f'<div class="metric-cards-grid">{cards_html}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <h3 class="workflow-subsection-title">
            <span class="highlight">Results Table</span>
        </h3>
        """,
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    with filter_col1:
        if FOOD_CONTACT_CHEMICAL_COLUMN in results_df.columns:
            fcc_filter = st.multiselect(
                f"Filter by {FOOD_CONTACT_CHEMICAL_COLUMN.replace('is ', '')}",
                options=results_df[FOOD_CONTACT_CHEMICAL_COLUMN].unique(),
                default=None,
            )
            if fcc_filter:
                results_df = results_df[results_df[FOOD_CONTACT_CHEMICAL_COLUMN].str.contains(fcc_filter)]

    with filter_col2:
        if TIER_OF_FCCPRIO_COLUMN in results_df.columns:
            tier_filter = st.multiselect(
                f"Filter by {TIER_OF_FCCPRIO_COLUMN}",
                options=sorted([t for t in results_df[TIER_OF_FCCPRIO_COLUMN].unique() if t != ""]),
                default=None,
            )
            if tier_filter:
                results_df = results_df[results_df[TIER_OF_FCCPRIO_COLUMN].isin(tier_filter)]

    with filter_col3:
        if HAZARD_COLUMN in results_df.columns:
            tier_filter = st.multiselect(
                f"Filter by {HAZARD_COLUMN}",
                options=sorted([t for t in results_df[HAZARD_COLUMN].str.split(", ").explode().unique()]),
                default=None,
            )
            if tier_filter:
                results_df = results_df[results_df[HAZARD_COLUMN].apply(lambda x: all(h in x.split(", ") for h in tier_filter))]

    with filter_col4:
        if GROUPS_OF_CONCERN_COLUMN in results_df.columns:
            groups_concern = results_df[GROUPS_OF_CONCERN_COLUMN].str.split(",").explode().unique()

            group_col1, group_col2 = st.columns([2, 1])
            with group_col1:
                group_filter = st.multiselect(
                    f"Filter by {GROUPS_OF_CONCERN_COLUMN}",
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

                results_df = results_df[results_df[GROUPS_OF_CONCERN_COLUMN].apply(filter_func)]
    display_results_df = build_display_results_df(results_df, DISPLAY_RESULT_COLUMNS)

    table_df = display_results_df.copy()
    column_config = {}
    if FOOD_CONTACT_CHEMICAL_COLUMN in table_df.columns:
        table_df[FOOD_CONTACT_CHEMICAL_COLUMN] = table_df[FOOD_CONTACT_CHEMICAL_COLUMN].apply(_fcc_status_to_tags)
        column_config[FOOD_CONTACT_CHEMICAL_COLUMN] = st.column_config.MultiselectColumn(
            FOOD_CONTACT_CHEMICAL_COLUMN,
            help="Databases listing this chemical as a food contact chemical (FCCdb, fccmigex).",
            accept_new_options=False,
            options=[
                "FCCdb",
                "FCCmigex",
                "Not a FCC",
            ],
            disabled=True,
            color = ["#0aaa99", "#f4ad20", "grey"],
        )

    st.dataframe(table_df, use_container_width=True, column_config=column_config)

    
    st.markdown(
        """
        <h3 class="workflow-subsection-title">
            <span class="highlight">Export Results</span>
        </h3>
        """,
        unsafe_allow_html=True,
    )
    identifier_cols = [CAS_COLUMN, SMILES_COLUMN, CHEMICAL_NAMES_COLUMN, FORMULA_COLUMN]
    enrichment_cols = [FOOD_CONTACT_CHEMICAL_COLUMN, TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN, GROUPS_OF_CONCERN_COLUMN]

    def _order_export_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
        col_order = []
        col_order.extend([c for c in identifier_cols if c in dataframe.columns])
        col_order.extend([c for c in enrichment_cols if c in dataframe.columns])
        col_order.extend([c for c in dataframe.columns if c not in col_order])
        return dataframe[col_order]

    DOWNLOAD_SCOPE_WHOLE = "Whole dataset (all columns)"
    DOWNLOAD_SCOPE_DISPLAYED = "Displayed results only (current filters and columns)"

    download_scope = st.selectbox(
        "What would you like to download?",
        options=[DOWNLOAD_SCOPE_DISPLAYED, DOWNLOAD_SCOPE_WHOLE],
        key="download_scope_selector",
        help=(
            "Displayed results only: exactly the rows and columns shown in the table above, "
            "including any active filters."
            "Whole dataset: every analyzed chemical with all available columns. "
        ),
    )

    if download_scope == DOWNLOAD_SCOPE_DISPLAYED:
        export_results_df = display_results_df.copy()
    else:
        export_results_df = _order_export_columns(unfiltered_results_df)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        csv = export_results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"fcc_grouping_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_csv_button",
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
            key="download_excel_button",
        )

    with col3:
        if st.button("🔄 Clear Data", use_container_width=True, key="clear_data_results_button"):
            st.session_state.results_df = None
            st.session_state.cas_input_text = ""
            st.rerun()
