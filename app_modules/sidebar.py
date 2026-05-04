"""Sidebar rendering logic."""
import os
import streamlit as st
from fccgroup import GroupingMethod
from utils import _svg_as_data_uri
from pathlib import Path


def render_sidebar() -> bool:
    """Render sidebar content and grouping configuration controls."""
    open_workflow = False
    with st.sidebar:
        image_path = Path(__file__).resolve().parents[1] / "assets" / "FCCprio_logo_signet.svg"
        image_src = _svg_as_data_uri(image_path)

        st.markdown(f'<h1 class="sidebar-main-header"><img src="{image_src}" alt="FCCprio logo"><span class="highlight">FCC Grouping Tool</span></h1>', unsafe_allow_html=True)
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

        with st.expander("⚖️ License"):
            st.markdown(
                """
                [![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

                **Creative Commons Attribution 4.0 International**

                Copyright (c) 2026 Food Packaging Forum

                This work is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
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
        st.image("assets/fpf_logo_RGB_vector_SVG.svg", width=200)
        st.caption("© 2026 Food Packaging Forum")
        st.markdown("""<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank"><img src="https://licensebuttons.net/l/by/4.0/88x31.png" alt="CC BY 4.0"></a>""", unsafe_allow_html=True)

    return open_workflow
