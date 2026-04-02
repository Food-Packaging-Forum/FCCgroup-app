"""Session-state helpers."""

import os

import streamlit as st
from fccgroup import GroupingMethod


def initialize_session_state() -> None:
    """Initialize all session-state keys used by the app."""
    defaults = {
        "results_df": None,
        "show_workflow": False,
        "active_page": "main",
        "cas_input_text": "",
        "uploaded_df": None,
        "input_type": "casId",
        "input_mode": "Manual Entry",
        "mapping_payload": {},
        "grouper_signature": None,
        "grouper_instance": None,
        "grouping_methods": [GroupingMethod.SMARTS.value],
        "is_admin": os.environ.get("IS_FCCGROUP_ADMIN", "").strip().lower() == "true",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
