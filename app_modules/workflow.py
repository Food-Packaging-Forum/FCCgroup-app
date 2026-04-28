"""Workflow explanation UI content."""

import textwrap

import streamlit as st


def display_workflow_explanation() -> None:
    """Display detailed workflow explanation."""
    st.markdown(
        """
        <div class="workflow-section-title">
            📖 <span class="highlight">Detailed Workflow Information</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="workflow-intro">
        This tool implements a comprehensive chemical identification and grouping pipeline for Food Contact Chemicals (FCCs).
        The workflow integrates FPF's internal resources with structural analysis to systematically classify and prioritize chemicals.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="workflow-subsection-title">
            🧭 <span class="highlight">How The UI Works</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ui_steps = [
        {
            "number": "0",
            "emoji": "⚙️",
            "title": "Start from the sidebar",
            "color": "#667eea",
            "content": [
                "Click <strong>Explore Detailed Workflow</strong> to open this page.",
                "Click <strong>Back to Analysis</strong> (top of this page) to return to the main analysis screen.",
                "In <strong>Grouping Configuration</strong>, choose one or more methods:",
                "<strong>SMARTS</strong>: structure-based grouping",
                "<strong>LISTS</strong>: list comparison grouping",
                "<strong>REGEX</strong>: name/identifier text pattern grouping",
                "If no method is selected, SMARTS is used by default.",
            ]
        },
        {
            "number": "1",
            "emoji": "📥",
            "title": "Add your input data (Step 1)",
            "color": "#764ba2",
            "content": [
                "Choose <strong>Manual Entry</strong> for quick checks.",
                "Choose <strong>File Upload</strong> for Excel/CSV batches.",
                "In manual mode, choose <strong>CAS</strong> or <strong>SMILES</strong>, then paste one entry per line.",
                "You can click <strong>Try Sample Data</strong> to test the full flow instantly.",
                "In upload mode, set the header row, select the sheet (for Excel), then map columns.",
                "You are ready when the green <strong>Input Summary</strong> box appears.",
            ]
        },
        {
            "number": "2",
            "emoji": "🚀",
            "title": "Run analysis (Step 2)",
            "color": "#f5576c",
            "content": [
                "Click <strong>Start Analysis</strong>.",
                "The button stays disabled until valid input and at least one grouping method are available.",
                "Progress appears in three statuses:",
                "<strong>Step 1/3: Initializing</strong>",
                "<strong>Step 2/3: Processing rows</strong>",
                "<strong>Step 3/3: Finalizing results</strong>",
                "After success, the app opens the results section automatically.",
            ]
        },
        {
            "number": "3",
            "emoji": "📊",
            "title": "Explore results and export (Step 3)",
            "color": "#00f2fe",
            "content": [
                "Read the <strong>Summary Dashboard</strong> first (total chemicals, valid structures, FCC status, tiers, groups).",
                "Open <strong>Filter Options</strong> to focus results by:",
                "FCC status",
                "FCCprio tier",
                "Groups of concern",
                "For multiple groups of concern, choose:",
                "<strong>OR</strong> to match any selected group",
                "<strong>AND</strong> to require all selected groups",
                "Download final results as <strong>CSV</strong> or <strong>Excel</strong>.",
                "Click <strong>Start New Analysis</strong> to clear results and begin another run.",
            ]
        },
    ]

    cards_html = []
    for step in ui_steps:
        items_html = "".join([
            f'<li style="margin: 0.45rem 0;">{item}</li>' for item in step["content"]
        ])
        cards_html.append(
            f"""
            <div class="ui-step-card" style="
                background: linear-gradient(135deg, {step['color']}15 0%, {step['color']}05 100%);
                border-left: 5px solid {step['color']};
            ">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 2.5rem; margin-right: 1rem;">{step['emoji']}</div>
                    <div>
                        <div style="font-size: 0.85rem; font-weight: 600; color: {step['color']}; letter-spacing: 0.5px;">STEP {step['number']}</div>
                        <div style="font-size: 1.2rem; font-weight: 700;">{step['title']}</div>
                    </div>
                </div>
                <ul class="ui-step-list">
                    {items_html}
                </ul>
            </div>
            """
        )

    st.markdown(
        textwrap.dedent(
            f"""
            <style>
                .ui-step-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    gap: 1rem;
                    align-items: stretch;
                    grid-auto-rows: .2fr;
                }}
                .ui-step-card {{
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                    transition: all 0.3s ease;
                    height: 100%;
                    box-sizing: border-box;
                    display: flex;
                    flex-direction: column;
                }}
                .ui-step-list {{
                    color: inherit;
                    line-height: 1.6;
                    font-size: 0.95rem;
                    margin: 0;
                    padding-left: 1.2rem;
                    flex: 1;
                }}
                .ui-step-list li {{
                    margin: 0.45rem 0;
                }}
                @media (max-width: 900px) {{
                    .ui-step-grid {{
                        grid-template-columns: 1fr;
                        grid-auto-rows: auto;
                    }}
                }}
                [data-theme="dark"] .ui-step-card {{
                    box-shadow: 0 2px 8px rgba(0,0,0,0.35);
                }}
            </style>
            <div class="ui-step-grid">
                {''.join(cards_html)}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        textwrap.dedent(
            """
            <style>
                .common-blockers-box {
                    background: linear-gradient(135deg, #fff3cd 0%, #fff8e1 100%);
                    border-left: 5px solid #f59e0b;
                    border-radius: 12px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.15);
                }
                .common-blockers-title {
                    font-weight: 700;
                    color: #92400e;
                    margin-bottom: 0.5rem;
                }
                .common-blockers-body {
                    color: #b45309;
                    font-size: 0.95rem;
                    line-height: 1.6;
                }
                [data-theme="dark"] .common-blockers-box {
                    background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.08) 100%);
                    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);
                }
                [data-theme="dark"] .common-blockers-title {
                    color: #fbbf24;
                }
                [data-theme="dark"] .common-blockers-body {
                    color: #fcd34d;
                }
            </style>
            <div class="common-blockers-box">
                <div style="display: flex; align-items: flex-start; gap: 1rem;">
                    <div style="font-size: 1.8rem; flex-shrink: 0;">⚡</div>
                    <div>
                        <div class="common-blockers-title">Common blockers</div>
                        <div class="common-blockers-body">
                            Invalid identifier format, missing column mapping in upload mode, or trying to run without a selected grouping method.
                        </div>
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="workflow-subsection-title">
            🔄 <span class="highlight">Three-Step Process</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="workflow-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔎</div>
                <strong style="font-size: 1.2rem; display: block; margin-bottom: 0.6rem;">FCC Identification</strong>
                <p class="brief-description">
                    Match against FCCdb and FCCmigex databases to identify food contact chemicals.
                </p>
                <div class="details-block">
                    <p><strong>Purpose</strong></p>
                    <p>Determine whether a chemical is a food contact chemical based on FPF databases.</p>
                    <p style="margin-top: 0.65rem;"><strong>Process</strong></p>
                    <ul>
                        <li>FCCdb matching by CAS</li>
                        <li>FCCmigex matching by CAS</li>
                        <li>Assign FCC status if matched in either</li>
                    </ul>
                    <p style="margin-top: 0.65rem;"><strong>Output</strong></p>
                    <p>Binary FCC status and source information.</p>
                </div>
                <div class="workflow-button-container">
                    <a href="https://www.sciencedirect.com/science/article/pii/S0160412020321802" target="_blank" class="workflow-button">📄 FCCdb Paper</a>
                    <a href="https://doi.org/10.1080/10408398.2022.2067828" target="_blank" class="workflow-button">📄 FCCmigex Paper</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="workflow-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); box-shadow: 0 4px 10px rgba(245, 87, 108, 0.3);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔬</div>
                <strong style="font-size: 1.2rem; display: block; margin-bottom: 0.6rem;">FCCprio Prioritization</strong>
                <p class="brief-description">
                    Assign priority tiers based on hazard and exposure data.
                </p>
                <div class="details-block">
                    <p><strong>Purpose</strong></p>
                    <p>Prioritize food contact chemicals based on hazard and exposure signals.</p>
                    <p style="margin-top: 0.65rem;"><strong>Process</strong></p>
                    <ul>
                        <li>Match against FCCprio records</li>
                        <li>Assign priority tier</li>
                        <li>Return prioritization metadata</li>
                    </ul>
                    <p style="margin-top: 0.65rem;"><strong>Output</strong></p>
                    <p>FCCprio tier and prioritization metadata.</p>
                </div>
                <div class="workflow-button-container">
                    <a href="https://doi.org/10.5281/zenodo.14881617" target="_blank" class="workflow-button">📄 FCCprio Data</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="workflow-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); box-shadow: 0 4px 10px rgba(79, 172, 254, 0.3);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎯</div>
                <strong style="font-size: 1.2rem; display: block; margin-bottom: 0.6rem;">Structural Grouping</strong>
                <p class="brief-description">
                    Group by molecular structure using SMARTS patterns.
                </p>
                <div class="details-block">
                    <p><strong>Purpose</strong></p>
                    <p>Group chemicals by structural motifs to support read-across analysis.</p>
                    <p style="margin-top: 0.65rem;"><strong>Process</strong></p>
                    <ul>
                        <li>Validate or resolve SMILES</li>
                        <li>Apply SMARTS patterns in parallel</li>
                        <li>Compile group membership outputs</li>
                    </ul>
                    <p style="margin-top: 0.65rem;"><strong>Output</strong></p>
                    <p>Structural grouping labels and pattern-level matches.</p>
                </div>
                <div class="workflow-button-container">
                    <a href="https://pypi.org/project/fccgroup/" target="_blank" class="workflow-button">📄 FCCgroup PyPI</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        """
        <div class="workflow-subsection-title">
            🎯 <span class="highlight">Common Use Cases</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    use_cases = [
        ("🔍 Food Contact Screening", "Determine if chemicals are used in food contact materials"),
        ("⚠️ Risk Prioritization", "Identify high-priority chemicals for assessment"),
        ("🧬 Structural Read-Across", "Group chemicals by structural features for hazard prediction"),
        ("📊 Research Analysis", "Systematic classification for publications and reports"),
        ("📋 Regulatory Compliance", "Support safety assessments with integrated FPF data"),
    ]

    for icon_title, description in use_cases:
        st.markdown(
            f"""
            <div class="use-case-item">
                <div class="use-case-title">{icon_title}</div>
                <div class="use-case-description">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
