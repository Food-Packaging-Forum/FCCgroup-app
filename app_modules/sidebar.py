"""Sidebar rendering logic."""
import os
import streamlit as st
from fccgroup import GroupingMethod


def render_sidebar() -> bool:
    """Render sidebar content and grouping configuration controls."""
    open_workflow = False
    with st.sidebar:
        st.image("assets/FCCprio_logo_signet.svg", use_container_width=True)
        st.markdown('<h1 class="sidebar-main-header"><span class="highlight">FCC Grouping Tool</span></h1>', unsafe_allow_html=True)
        st.markdown("---")

        open_workflow = st.button(
            "📖 Explore Detailed Workflow",
            key="sidebar_workflow_button",
            use_container_width=True,
        )

        with st.expander("ℹ️ About This Tool", expanded=True):
            st.markdown(
                """
                **Workflow:**
                1. 🗄️ FCC Identification
                2. 🎯 FCCprio Prioritization
                3. 🔬 FCCgroup Structural Grouping
                """
            )

        with st.expander("📚 Data Sources"):
            st.markdown(
                """
                - **FCCdb** - 12,285 chemicals
                - **FCCmigex** - 5,294 chemicals
                - **FCCprio** - 4 Priority tiers
                - **FCCgroup** - Structural patterns
                """
            )

        with st.expander("📖 References"):
            st.markdown(
                """
                - [FCCdb Paper](https://www.sciencedirect.com/science/article/pii/S0160412020321802)
                - [FCCmigex Paper](https://doi.org/10.1080/10408398.2022.2067828)
                - [FCCprio Zenodo](https://doi.org/10.5281/zenodo.14881617)
                - [FCCgroup PyPI](https://pypi.org/project/fccgroup/)
                """
            )

        if st.session_state.is_admin:
            st.markdown("---")
            st.subheader("⚙️ Grouping Configuration")

            grouping_method_options = {
                GroupingMethod.SMARTS.value: "⚛️ SMARTS: Structural Patterns",
                GroupingMethod.LISTS.value: "📄 Lists: Comparison with lists",
                GroupingMethod.REGEX.value: "🆎 Regex: Search regex expressions on identifiers",
            }

            selected_methods = st.multiselect(
                "Select grouping methods:",
                options=list(grouping_method_options.keys()),
                default=st.session_state.grouping_methods,
                format_func=lambda x: grouping_method_options[x],
                key="grouping_method_selector",
                help="Choose between speed (patterns only) and comprehensiveness (all methods)",
            )

            if not selected_methods:
                st.warning("Select at least one grouping method. SMARTS will be used by default.")
                selected_methods = [GroupingMethod.SMARTS.value]

            st.session_state.grouping_methods = selected_methods

            st.info("**Active Methods:**\n- " + ", ".join(m.upper() for m in st.session_state.grouping_methods))
        else:
            if "grouping_methods" not in st.session_state:
                st.session_state.grouping_methods = [GroupingMethod.SMARTS.value]

        st.markdown("---")
        st.caption("© 2026 Food Packaging Forum")

    return open_workflow
