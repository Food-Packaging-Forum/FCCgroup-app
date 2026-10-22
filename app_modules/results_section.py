"""Results rendering and export UI."""

import base64
from html import escape
from io import BytesIO
from typing import Callable, Optional

import pandas as pd
import streamlit as st
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

from app_modules.config import DISPLAY_RESULT_COLUMNS
from app_modules.processing import build_display_results_df
from app_modules.config import CHEMICAL_NAMES_COLUMN, FOOD_CONTACT_CHEMICAL_COLUMN, FORMULA_COLUMN, RENAME_DICT, TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN, GROUP_COLUMNS, CAS_COLUMN, SMILES_COLUMN

RESULTS_TABLE_KEY = "results_table"
STRUCTURE_IMAGE_SIZE = (420, 320)


def _fcc_status_to_tags(value: object) -> list:
    """Convert an FCC status string into read-only tags for ListColumn display."""
    text = str(value).lower()
    tags = []
    if "fccdb" in text:
        tags.append("FCCdb")
    if "fccmigex" in text:
        tags.append("FCCmigex")
    if "not an fcc" in text:
        tags.append("Not an FCC")
    return tags


def _has_non_empty_value(value: object) -> bool:
    """Return True when value is neither NA nor an empty/whitespace string."""
    if pd.isna(value):
        return False

    if str(value).strip() == "":
        return False

    if str(value).strip().lower() == "no data":
        return False

    return True


def _row_group_sets(df: pd.DataFrame, group_columns: list) -> pd.Series:
    """Per row, the set of groups listed in any of the group columns."""
    def to_set(row) -> frozenset:
        groups = set()
        for value in row:
            if _has_non_empty_value(value) and str(value).strip().upper() != "NA":
                groups.update(g.strip() for g in str(value).split(",") if g.strip())
        return frozenset(groups)

    return df[group_columns].apply(to_set, axis=1)


@st.cache_data(show_spinner=False, max_entries=500)
def _structure_svg(smiles: str) -> Optional[str]:
    """2D depiction of a SMILES as SVG, or None when RDKit cannot parse it."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None or rdMolDraw2D is None:
        return None
    drawer = rdMolDraw2D.MolDraw2DSVG(*STRUCTURE_IMAGE_SIZE)
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()


def _render_structure_panel(row: pd.Series) -> None:
    """Structure image of the selected row next to its identifiers and groups.

    Both cards are cells of one CSS grid so they always share the same height,
    independent of Streamlit's column markup.
    """
    smiles = row.get(SMILES_COLUMN)
    svg = _structure_svg(str(smiles).strip()) if _has_non_empty_value(smiles) else None
    if svg is not None:
        svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        image_html = f'<img class="structure-image" src="data:image/svg+xml;base64,{svg_b64}" alt="Chemical structure">'
    elif _has_non_empty_value(smiles):
        image_html = '<div class="structure-details-value">The SMILES of this chemical could not be drawn.</div>'
    else:
        image_html = '<div class="structure-details-value">No structure available: this chemical has no SMILES.</div>'

    detail_columns = [
        CHEMICAL_NAMES_COLUMN, CAS_COLUMN, FORMULA_COLUMN, SMILES_COLUMN,
        TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN, *GROUP_COLUMNS,
    ]
    fields = []
    for column in detail_columns:
        if column not in row.index or not _has_non_empty_value(row[column]) or str(row[column]).strip().upper() == "NA":
            continue
        value = str(row[column]).strip()
        if column in GROUP_COLUMNS:
            # One chip per group, like the tags in the results table.
            value_html = "".join(
                f'<span class="structure-details-chip">{escape(group.strip())}</span>'
                for group in value.split(",") if group.strip()
            )
        elif column == SMILES_COLUMN:
            value_html = f'<span class="structure-details-smiles">{escape(value)}</span>'
        else:
            value_html = escape(value)
        fields.append(
            f'<div class="structure-details-field"><div class="structure-details-label">{escape(column)}</div>'
            f'<div class="structure-details-value">{value_html}</div></div>'
        )
    body = "".join(fields) if fields else '<div class="structure-details-value">No details available.</div>'
    st.markdown(
        f'<div class="structure-panel"><div class="structure-card structure-image-card">{image_html}</div>'
        f'<div class="structure-card structure-details-card">{body}</div></div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    """CSV export, cached so unchanged tables are not re-serialized on every rerun."""
    return df.to_csv(index=False).encode("utf-8")


@st.cache_data(show_spinner=False)
def _to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Excel export, cached because writing a large table with openpyxl is slow."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")
    return buffer.getvalue()


def render_results_section(
    full_results_df: pd.DataFrame,
    on_clear: Optional[Callable[[], None]] = None,
    title: str = "Step 3: Explore Results",
) -> None:
    """Render summary metrics, filters, table, and export controls.

    `on_clear` replaces the default "Clear Data" behaviour (resetting the analysis
    results and input text) for pages whose results come from somewhere else.
    `title` replaces the step heading for pages that are not part of the analysis steps.
    """
    results_df = full_results_df.copy()
    results_df = results_df.rename(columns=RENAME_DICT)
    if len(results_df) == 0:
        st.warning("⚠️ No results to display. The dataframe is empty.")
        return

    st.markdown(
        f"""
        <div class="section-gradient-divider"></div>
        <h2 class="workflow-section-title">
            <span class="highlight">{title}</span>
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

    # Metrics are computed on identifiers deduplicated by CAS/SMILES so a chemical
    # repeated across several rows is only counted once; the table below keeps every row.
    identifier_columns = [col for col in (CAS_COLUMN, SMILES_COLUMN) if col in results_df.columns]
    metrics_df = results_df.drop_duplicates(subset=identifier_columns) if identifier_columns else results_df

    total_count = len(metrics_df)
    metrics = [("Total Chemicals", total_count, "🧪")]

    if SMILES_COLUMN in metrics_df.columns:
        valid_smiles_count = int(metrics_df[SMILES_COLUMN].apply(_has_non_empty_value).sum())
        metrics.append(("Valid SMILES", f"{valid_smiles_count}/{total_count}", "🧬"))
    else:
        metrics.append(("Valid SMILES", "N/A", "🧬"))

    if FOOD_CONTACT_CHEMICAL_COLUMN in metrics_df.columns:
        food_contact_count = int(metrics_df[FOOD_CONTACT_CHEMICAL_COLUMN].apply(lambda x: x!="Not an FCC").sum())
        metrics.append(("Food Contact", f"{food_contact_count}/{total_count}", "🗄️"))

    if TIER_OF_FCCPRIO_COLUMN in metrics_df.columns:
        fcc_tier_count = int(metrics_df[TIER_OF_FCCPRIO_COLUMN].apply(_has_non_empty_value).sum())
        metrics.append(("FCCprio Tier", f"{fcc_tier_count}/{total_count}", "🎯"))

    group_columns = [col for col in GROUP_COLUMNS if col in results_df.columns]
    if group_columns:
        # A chemical counts once when it has an important group, a priority group, or both.
        groups_count = int(metrics_df[group_columns].apply(lambda col: col.apply(_has_non_empty_value)).any(axis=1).sum())
        metrics.append(("With Groups", f"{groups_count}/{total_count}", "🔬"))
    na_fill_columns = [
        col for col in (TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN, *group_columns)
        if col in results_df.columns
    ]
    if na_fill_columns:
        results_df[na_fill_columns] = results_df[na_fill_columns].replace("", "NA")

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
                results_df = results_df[results_df[FOOD_CONTACT_CHEMICAL_COLUMN].isin(fcc_filter)]

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
        if group_columns:
            row_groups = _row_group_sets(results_df, group_columns)
            available_groups = sorted(set().union(*row_groups)) if len(row_groups) else []

            group_col1, group_col2 = st.columns([2, 1])
            with group_col1:
                group_filter = st.multiselect(
                    "Filter by group",
                    options=available_groups,
                    default=None,
                    key="groups_multiselect",
                    help=f"Matches a group listed in {' or '.join(group_columns)}, or across both combined.",
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
                        help="OR: Match any selected group | AND: Match all selected groups (across both columns)",
                    )
                else:
                    logic_operator = "OR"

            if group_filter:
                selected = set(group_filter)
                if logic_operator == "OR":
                    keep = row_groups.apply(lambda groups: bool(groups & selected))
                else:
                    keep = row_groups.apply(lambda groups: selected <= groups)

                results_df = results_df[keep]
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
                "Not an FCC",
            ],
            disabled=True,
            color = ["#0aaa99", "#f4ad20", "grey"],
        )

    table_event = st.dataframe(
        table_df,
        use_container_width=True,
        column_config=column_config,
        key=RESULTS_TABLE_KEY,
        on_select="rerun",
        selection_mode="single-row",
    )

    # Selected positions refer to table_df as passed in, whatever sorting the user applied;
    # a selection made before the filters changed may point past the end of the table.
    selected_rows = [i for i in table_event.selection.rows if i < len(display_results_df)]
    if selected_rows:
        _render_structure_panel(display_results_df.iloc[selected_rows[0]])
    else:
        st.caption("Select a row in the table (checkbox on the left) to see the chemical structure.")

    
    st.markdown(
        """
        <h3 class="workflow-subsection-title">
            <span class="highlight">Export Results</span>
        </h3>
        """,
        unsafe_allow_html=True,
    )
    identifier_cols = [CAS_COLUMN, SMILES_COLUMN, CHEMICAL_NAMES_COLUMN, FORMULA_COLUMN]
    enrichment_cols = [FOOD_CONTACT_CHEMICAL_COLUMN, TIER_OF_FCCPRIO_COLUMN, HAZARD_COLUMN, *GROUP_COLUMNS]

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
        csv = _to_csv_bytes(export_results_df)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"fcc_grouping_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_csv_button",
        )

    with col2:
        st.download_button(
            label="📥 Download Excel",
            data=_to_excel_bytes(export_results_df),
            file_name=f"fcc_grouping_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_excel_button",
        )

    with col3:
        if st.button("🔄 Clear Data", use_container_width=True, key="clear_data_results_button"):
            if on_clear is not None:
                on_clear()
            else:
                st.session_state.results_df = None
                st.session_state.cas_input_text = ""
            st.rerun()
