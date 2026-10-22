"""FCC priority groups page: browse the FCC universe by priority group."""

import re
from typing import Dict

import pandas as pd
import streamlit as st

from fccgroup.constants import IMPORTANT_GROUPS, PRIORITY_GROUPS_CONCERN

from app_modules.config import (
    CAS_COLUMN_INPUT,
    CAS_MAIN_UNIVERSE_COLUMN,
    FCC_UNIVERSE_PATH,
    FOOD_CONTACT_CHEMICAL_COLUMN,
    HAZARD_COLUMN,
    IMPORTANT_GROUP_UNIVERSE_COLUMN,
    IMPORTANT_GROUPS_COLUMN,
    IN_FCCDB_COLUMN,
    IN_FCCMIGEX_COLUMN,
    NOT_AN_FCC_LABEL,
    PRIORITY_GROUP_UNIVERSE_COLUMN,
    PRIORITY_GROUPS_COLUMN,
    SMILES_COLUMN_INPUT,
    TIER_OF_FCCPRIO_COLUMN,
)
from app_modules.results_section import render_results_section
from app_modules.styles import apply_group_button_styles

SELECTED_GROUP_KEY = "priority_group_selected"
BUTTONS_PER_ROW = 4
# Keyed widgets in the results section; their state must not outlive the selected group.
RESULTS_WIDGET_KEYS = ("groups_multiselect", "logic_operator", "download_scope_selector")

# Important groups that are not priority groups, in fccgroup's order.
OTHER_IMPORTANT_GROUPS = [g for g in dict.fromkeys(IMPORTANT_GROUPS) if g not in PRIORITY_GROUPS_CONCERN]
ALL_GROUPS = [*PRIORITY_GROUPS_CONCERN, *OTHER_IMPORTANT_GROUPS]

# Longest first so a name that contains another one (or a comma) wins the match.
_GROUP_PATTERN = re.compile(
    "|".join(re.escape(group) for group in sorted(ALL_GROUPS, key=len, reverse=True))
)


def _fcc_status(in_fccdb: bool, in_fccmigex: bool) -> str:
    """FCC status label in the wording the results table expects."""
    if in_fccdb and in_fccmigex:
        return "In FCCdb and FCCmigex"
    if in_fccdb:
        return "In FCCdb"
    if in_fccmigex:
        return "In FCCmigex"
    return NOT_AN_FCC_LABEL


def _split_groups(value: object) -> frozenset:
    """Groups listed in a comma-separated cell.

    Some group names contain commas themselves, so the cell is matched against
    the known names instead of being split on commas.
    """
    return frozenset(_GROUP_PATTERN.findall(value)) if isinstance(value, str) else frozenset()


@st.cache_data(show_spinner="Loading FCC universe...")
def load_group_universe() -> pd.DataFrame:
    """One row per chemical of the FCC universe, shaped like analysis results.

    Rows sharing a `casId main` describe the same chemical, so only one is kept and
    its main CAS is shown as the CAS. Chemicals without any group are kept.
    """
    universe_df = pd.read_excel(FCC_UNIVERSE_PATH, dtype={CAS_COLUMN_INPUT: str, CAS_MAIN_UNIVERSE_COLUMN: str})
    universe_df = universe_df.drop_duplicates(subset=CAS_MAIN_UNIVERSE_COLUMN).reset_index(drop=True)

    in_fccdb = pd.to_numeric(universe_df[IN_FCCDB_COLUMN], errors="coerce").fillna(0) > 0
    in_fccmigex = pd.to_numeric(universe_df[IN_FCCMIGEX_COLUMN], errors="coerce").fillna(0) > 0

    results_df = pd.DataFrame({
        CAS_COLUMN_INPUT: universe_df[CAS_MAIN_UNIVERSE_COLUMN],
        SMILES_COLUMN_INPUT: universe_df[SMILES_COLUMN_INPUT].fillna(""),
        FOOD_CONTACT_CHEMICAL_COLUMN: [_fcc_status(db, migex) for db, migex in zip(in_fccdb, in_fccmigex)],
        TIER_OF_FCCPRIO_COLUMN: universe_df[TIER_OF_FCCPRIO_COLUMN].fillna(""),
        HAZARD_COLUMN: universe_df[HAZARD_COLUMN].fillna(""),
        IMPORTANT_GROUPS_COLUMN: universe_df[IMPORTANT_GROUP_UNIVERSE_COLUMN].fillna(""),
        PRIORITY_GROUPS_COLUMN: universe_df[PRIORITY_GROUP_UNIVERSE_COLUMN].fillna(""),
    })
    results_df["_groups"] = [
        _split_groups(important) | _split_groups(priority)
        for important, priority in zip(results_df[IMPORTANT_GROUPS_COLUMN], results_df[PRIORITY_GROUPS_COLUMN])
    ]
    return results_df


def _group_counts(universe_df: pd.DataFrame) -> Dict[str, int]:
    """Chemicals per group."""
    counts = {group: 0 for group in ALL_GROUPS}
    for groups in universe_df["_groups"]:
        for group in groups:
            counts[group] += 1
    return counts


def _reset_results_widgets() -> None:
    for key in RESULTS_WIDGET_KEYS:
        st.session_state.pop(key, None)


def _select_group(group: str) -> None:
    """Button callback: select a group, or deselect it when it is already active."""
    _reset_results_widgets()
    st.session_state[SELECTED_GROUP_KEY] = None if st.session_state.get(SELECTED_GROUP_KEY) == group else group


def _clear_selection() -> None:
    _reset_results_widgets()
    st.session_state[SELECTED_GROUP_KEY] = None


def render_priority_groups_page() -> None:
    """Render the group buttons and, for the selected group, the standard results section."""
    st.markdown(
        """
        <h2 class="workflow-section-title">
            <span class="highlight">Select an FCC Group</span>
        </h2>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p>Click a group to list only the chemicals of the FCC universe that belong to it. "
        "Click the active group again to show every chemical, including those without an assigned group.</p>",
        unsafe_allow_html=True,
    )

    apply_group_button_styles()

    universe_df = load_group_universe()
    counts = _group_counts(universe_df)
    selected = st.session_state.get(SELECTED_GROUP_KEY)

    for heading, groups in (("Priority groups", PRIORITY_GROUPS_CONCERN), ("Other important groups", OTHER_IMPORTANT_GROUPS)):
        st.markdown(f'<p class="group-buttons-title">{heading}</p>', unsafe_allow_html=True)
        for start in range(0, len(groups), BUTTONS_PER_ROW):
            for col, group in zip(st.columns(BUTTONS_PER_ROW), groups[start:start + BUTTONS_PER_ROW]):
                col.button(
                    f"{group} ({counts[group]})",
                    key=f"priority_group_button_{group}",
                    type="primary" if group == selected else "secondary",
                    use_container_width=True,
                    on_click=_select_group,
                    args=(group,),
                )

    # Without a selection the table lists every chemical of the universe.
    group_df = universe_df
    if selected is not None:
        group_df = universe_df[universe_df["_groups"].map(lambda row_groups: selected in row_groups)]
    render_results_section(
        group_df.drop(columns="_groups").reset_index(drop=True),
        on_clear=_clear_selection,
        title="Explore Results",
    )
