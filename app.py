"""Streamlit entry point for the FCC grouping web application."""

import sys
from pathlib import Path

import streamlit as st

from app_modules.input_section import render_input_section
from app_modules.processing import run_grouping_pipeline
from app_modules.results_section import render_results_section
from app_modules.sidebar import render_sidebar
from app_modules.state import initialize_session_state
from app_modules.styles import apply_global_styles, render_page_header
from app_modules.workflow import display_workflow_explanation

# Add src to path for local imports expected by project scripts.
sys.path.append(str(Path(__file__).parent / "src"))


st.set_page_config(
    page_title="FCC Chemical Grouping Tool",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _render_process_section(analysis_df, input_summary_ready: bool) -> bool:
    """Render processing call-to-action and return button state."""
    st.markdown(
        """
        <div class="process-step">
            <h3>Step 2: Analyze Chemicals</h3>
            <p>Run the comprehensive grouping pipeline</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        return st.button(
            "🚀 Start Analysis",
            type="primary",
            use_container_width=True,
            disabled=not input_summary_ready or not st.session_state.grouping_methods,
        )


def _process_analysis(analysis_df) -> None:
    """Execute grouping pipeline with progress feedback and error handling."""
    st.session_state.results_df = None
    if analysis_df.empty:
        st.error("⚠️ No valid entries found in the text input. Please check your input.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("🔄 Step 1/3: Initializing...")
        progress_bar.progress(10)

        mapping_payload = st.session_state.mapping_payload
        if not mapping_payload.get("cas") and not mapping_payload.get("smiles"):
            st.error("❌ Invalid identifiers. Provide at least one of CAS or SMILES so the library can resolve the input mode.")
            return

        status_text.text(f"🔄 Step 2/3: Processing {len(analysis_df)} rows...")
        progress_bar.progress(30)

        st.session_state.results_df = run_grouping_pipeline(
            analysis_df=analysis_df,
            mapping_payload=mapping_payload,
            grouping_methods=st.session_state.grouping_methods,
        )

        status_text.text("🔄 Step 3/3: Finalizing results...")
        progress_bar.progress(100)

        st.success(f"✅ Successfully analyzed {len(st.session_state.results_df)} chemicals!")
        if st.session_state.is_admin:
            st.balloons()
    except Exception as error:
        st.error(f"❌ Error during analysis: {str(error)}")
        st.exception(error)
    finally:
        status_text.empty()
        progress_bar.empty()


def main() -> None:
    """Main application orchestration."""
    apply_global_styles()
    initialize_session_state()
    open_workflow = render_sidebar()
    render_page_header()

    if open_workflow:
        st.session_state.active_page = "workflow"

    if st.session_state.active_page == "workflow":
        if st.button("← Back to Analysis", key="back_to_main_button"):
            st.session_state.active_page = "main"
            st.rerun()
        display_workflow_explanation()
        return

    analysis_df, input_summary_ready, _, _, _ = render_input_section()

    process_button = _render_process_section(analysis_df=analysis_df, input_summary_ready=input_summary_ready)
    if process_button:
        _process_analysis(analysis_df)

    if st.session_state.results_df is not None:
        render_results_section(st.session_state.results_df)


if __name__ == "__main__":
    main()
