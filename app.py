"""Streamlit entry point for the FCC grouping web application."""

import sys
from pathlib import Path

import streamlit as st

from app_modules.input_section import render_input_section
from app_modules.processing import run_grouping_pipeline
from app_modules.results_section import render_results_section
from app_modules.state import initialize_session_state
from app_modules.styles import apply_global_styles, render_footer, render_page_header
from app_modules.workflow import display_workflow_explanation
from fccgroup import GroupingMethod

# Add src to path for local imports expected by project scripts.
sys.path.append(str(Path(__file__).parent / "src"))


st.set_page_config(
    page_title="FCCgroup",
    page_icon="assets/FCCgroup_logo_signet.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _render_process_section(analysis_df, input_summary_ready: bool) -> bool:
    """Render processing call-to-action and return button state."""
    st.markdown(
        """
        <div class="section-gradient-divider"></div>
        <h2 class="workflow-section-title">
            <span class="highlight">Step 2: Analyze Chemicals</span>
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p>When your input is ready, click <b>🚀 Start Analysis</b> to launch automated grouping.</p>',
        unsafe_allow_html=True,
    )
    col , _, _ = st.columns([2, 1, 1])
    with col:
        return st.button(
            "🚀 Start Analysis",
            type="primary",
            key="start_analysis_button",
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


def _render_grouping_config() -> None:
    """Render grouping method selector at the top of the main page (admin only)."""
    if not st.session_state.is_admin:
        return

    grouping_method_options = {
        GroupingMethod.SMARTS.value: "⚛️ SMARTS: Structural Patterns",
        GroupingMethod.LISTS.value: "📄 Lists: Comparison with lists",
        GroupingMethod.REGEX.value: "🆎 Regex: Search regex expressions on identifiers",
    }

    with st.container(key="grouping_config_panel"):
        st.markdown("**⚙️ Grouping Configuration**")

        selected_methods = st.multiselect(
            "Select grouping methods:",
            options=list(grouping_method_options.keys()),
            default=st.session_state.grouping_methods,
            format_func=lambda x: grouping_method_options[x],
            key="grouping_method_selector",
            help="Choose between speed (patterns only) and comprehensiveness (all methods)",
            label_visibility="collapsed",
        )

        if not selected_methods:
            st.warning("Select at least one grouping method. SMARTS will be used by default.")
            selected_methods = [GroupingMethod.SMARTS.value]

        st.session_state.grouping_methods = selected_methods
        st.info("**Active:** " + ", ".join(m.upper() for m in st.session_state.grouping_methods))


def main() -> None:
    """Main application orchestration."""
    apply_global_styles()
    initialize_session_state()
    go_to_workflow, go_to_analysis = render_page_header(st.session_state.active_page)

    if go_to_workflow:
        st.session_state.active_page = "workflow"
        st.rerun()
    if go_to_analysis:
        st.session_state.active_page = "main"
        st.rerun()

    if st.session_state.active_page == "workflow":
        display_workflow_explanation()
        render_footer()
        return

    _render_grouping_config()

    analysis_df, input_summary_ready, _, _, _ = render_input_section()

    process_button = _render_process_section(analysis_df=analysis_df, input_summary_ready=input_summary_ready)
    if process_button:
        _process_analysis(analysis_df)

    if st.session_state.results_df is not None:
        render_results_section(st.session_state.results_df)

    render_footer()


if __name__ == "__main__":
    main()
