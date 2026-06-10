"""Workflow explanation UI content."""

import textwrap

import streamlit as st

_WORKFLOW_TABS = [
    {"key": "fcc_id",    "icon": "🔎", "label": "FCC Identification"},
    {"key": "fcc_prio",  "icon": "🔬", "label": "FCCprio Prioritization"},
    {"key": "struct_grp","icon": "🎯", "label": "Structural Grouping"},
]

_TAB_CONTENT = {
    "fcc_id": {
        "title": "FCC Identification",
        "description": (
            "Determine whether each input chemical is a food contact chemical (FCC) "
            "by matching it against FPF's curated databases."
        ),
        "color": "#255aa7",
        "sections": [
            {
                "heading": "Purpose",
                "body": "Match input chemicals against the FCCdb and FCCmigex databases to determine FCC status.",
                "list": [],
            },
            {
                "heading": "Process",
                "body": "",
                "list": [
                    "FCCdb lookup by CAS (12,285 chemicals)",
                    "FCCmigex lookup by CAS (5,294 chemicals)",
                    "Assign FCC status when matched in either database",
                    "Record source database for traceability",
                ],
            },
            {
                "heading": "Output",
                "body": "Binary FCC status flag and source database information for each chemical.",
                "list": [],
            },
        ],
        "links": [
            {"label": "FCCdb Publication", "icon": "fas fa-file-invoice", "url": "https://www.sciencedirect.com/science/article/pii/S0160412020321802"},
            {"label": "FCCmigex Publication", "icon": "fas fa-file-invoice", "url": "https://doi.org/10.1080/10408398.2022.2067828"},
        ],
    },
    "fcc_prio": {
        "title": "FCCprio Prioritization",
        "description": (
            "Assign evidence-based priority tiers to food contact chemicals based on "
            "integrated hazard and exposure signals from the FCCprio framework."
        ),
        "color": "#255aa7",
        "sections": [
            {
                "heading": "Purpose",
                "body": "Rank FCCs by risk relevance so assessors can focus limited resources on the highest-priority chemicals.",
                "list": [],
            },
            {
                "heading": "Process",
                "body": "",
                "list": [
                    "Look up each FCC in the FCCprio dataset",
                    "Retrieve hazard and exposure tier assignments",
                    "Combine signals into a single priority tier (1–4)",
                    "Return full prioritization metadata",
                ],
            },
            {
                "heading": "Output",
                "body": "FCCprio tier (1 = highest priority) and associated prioritization metadata per chemical.",
                "list": [],
            },
        ],
        "links": [
            {"label": "FCCprio Data (Zenodo)", "icon": "fas fa-database", "url": "https://doi.org/10.5281/zenodo.14881617"},
        ],
    },
    "struct_grp": {
        "title": "Structural Grouping",
        "description": (
            "Group chemicals by molecular structure to support read-across analysis "
            "and systematic hazard prediction."
        ),
        "color": "#255aa7",
        "sections": [
            {
                "heading": "Purpose",
                "body": "Cluster chemicals sharing structural motifs so that hazard data can be read across within each group.",
                "list": [],
            },
            {
                "heading": "Process",
                "body": "",
                "list": [
                    "Validate input SMILES or resolve from CAS via PubChem",
                    "Apply SMARTS patterns in parallel (SMARTS method)",
                    "Compare against curated lists (LISTS method)",
                    "Run identifier regex searches (REGEX method)",
                    "Compile group membership outputs",
                ],
            },
            {
                "heading": "Output",
                "body": "Structural group labels and per-pattern match details for downstream read-across.",
                "list": [],
            },
        ],
        "links": [
            {"label": "FCCgroup on PyPI", "icon": "fas fa-cube", "url": "https://pypi.org/project/fccgroup/"},
        ],
    },
}


def _render_workflow_step_tabs() -> None:
    """Render three-step workflow as tab buttons with swappable content."""
    active = st.session_state.get("workflow_tab", "fcc_id")

    # Tab buttons
    cols = st.columns(3)
    for col, tab in zip(cols, _WORKFLOW_TABS):
        with col:
            if st.button(
                f"{tab['icon']} {tab['label']}",
                key=f"wf_tab_{tab['key']}",
                use_container_width=True,
            ):
                st.session_state.workflow_tab = tab["key"]
                st.rerun()

    # Dynamic CSS — highlight active tab button + white-button hover for publication links
    css_parts = []
    for tab in _WORKFLOW_TABS:
        is_active = tab["key"] == active
        bg = "#255aa7" if is_active else "transparent"
        color = "#ffffff" if is_active else "inherit"
        border = "none" if is_active else "1px solid rgba(128,128,128,0.4)"
        css_parts.append(
            f"""
            .st-key-wf_tab_{tab['key']} button {{
                background: {bg}; color: {color}; border: {border};
                border-radius: 12px; font-weight: 700; min-height: 2.6rem;
                transition: all 0.3s ease !important;
            }}
            .st-key-wf_tab_{tab['key']} button:hover {{
                background: {bg}; color: {color}; border: {border};
                transform: scale(1.03); box-shadow: var(--fpf-shadow);
            }}
            """
        )
    st.markdown(f"<style>{''.join(css_parts)}</style>", unsafe_allow_html=True)

    # Content for active tab
    content = _TAB_CONTENT[active]
    color = content["color"]

    st.markdown(
        f"""
        <div style="margin: 1.25rem 0 1.5rem 0;">
            <div style="font-size: 1.5rem; font-weight: 700; font-family: 'Poppins', sans-serif;
                        margin-bottom: 0.35rem; line-height: 1.2;">
                <span style="background: {color}; -webkit-background-clip: text;
                             -webkit-text-fill-color: transparent; background-clip: text;">
                    {content['title']}
                </span>
            </div>
            <div style="font-size: 0.97rem; color: #000000; line-height: 1.55;">{content['description']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Styled HTML link buttons for publications
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <style>
        .pub-link-btn {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.25rem;
            background: #ffffff;
            color: #1f2a37;
            border: 2px solid #dde8f8;
            border-radius: 12px;
            font-weight: 600;
            font-family: 'Open Sans', 'Segoe UI', sans-serif;
            text-decoration: none !important;
            transition: all 0.25s ease;
            cursor: pointer;
            min-width: 200px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        .pub-link-btn .pub-icon {
            width: 2.75rem;
            height: 2.75rem;
            border-radius: 50%;
            background: #255aa7;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            transition: background 0.25s ease;
        }
        .pub-link-btn .pub-icon i {
            font-size: 1.2rem;
            color: #ffffff;
            transition: color 0.25s ease;
        }
        .pub-link-btn .pub-text {
            font-size: 0.92rem;
            font-weight: 700;
            line-height: 1.3;
            white-space: normal;
            color: #1f2a37;
            transition: color 0.25s ease;
        }
        .pub-link-btn:hover {
            box-shadow: 0 4px 14px rgba(37,90,167,0.35);
            transform: translateY(-2px);
            text-decoration: none !important;
        }
        .pub-link-btn:hover .pub-icon {
            background: #d9e7f8;
        }
        .pub-link-btn:hover .pub-icon i {
            color: #2a5aa7;
        }
        .pub-link-btn:hover .pub-text {
            color: #2a5aa7;
        }
        .pub-link-btn:visited { text-decoration: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Section info boxes — single flex container guarantees equal heights
    box_parts = []
    for section in content["sections"]:
        list_html = ""
        if section["list"]:
            items = "".join(
                f"<li style='margin:0.3rem 0;font-size:0.9rem'>{item}</li>"
                for item in section["list"]
            )
            list_html = (
                "<ul style='margin:0.5rem 0 0 0;padding-left:1.2rem;line-height:1.6'>"
                + items + "</ul>"
            )
        body_html = (
            f"<p style='margin:0.5rem 0 0 0;font-size:0.9rem;line-height:1.55'>{section['body']}</p>"
            if section["body"] else ""
        )
        box_parts.append(
            "<div style='flex:1;display:flex;flex-direction:column'>"
            + f"<div style='background:linear-gradient(135deg,{color}12 0%,{color}04 100%);"
            + f"border-left:5px solid {color};border-radius:12px;"
            + "padding:1.25rem;flex:1;box-sizing:border-box'>"
            + f"<p style='font-weight:700;margin:0 0 0.4rem 0;font-size:1rem;"
            + f"font-family:Poppins,sans-serif;letter-spacing:0.02em'>"
            + f"{section['heading']}</p>"
            + body_html + list_html
            + "</div>"
            + "</div>"
        )
    st.markdown(
        "<div style='display:flex;gap:1rem;align-items:stretch;margin:0.5rem 0 1rem 0'>"
        + "".join(box_parts)
        + "</div>",
        unsafe_allow_html=True,
    )

    # Publication link buttons — pure HTML, centered flex layout
    if content["links"]:
        def _pub_btn(link: dict) -> str:
            icon = link["icon"]
            label = link["label"]
            url = link["url"]
            return (
                f"<a href='{url}' target='_blank' class='pub-link-btn'>"
                f"<span class='pub-icon'><i class='{icon}'></i></span>"
                f"<span class='pub-text'>{label}</span>"
                f"</a>"
            )
        links_html = "".join(_pub_btn(link) for link in content["links"])
        st.markdown(
            "<div style='display:flex;justify-content:center;gap:1rem;flex-wrap:wrap;margin:0.5rem 0 1rem 0'>"
            + links_html
            + "</div>",
            unsafe_allow_html=True,
        )


def display_workflow_explanation() -> None:
    """Display detailed workflow explanation."""

    st.markdown(
        """
        <div class="workflow-subsection-title">
            <span class="highlight">How to use this tool</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ui_steps = [
        {
            "number": "0",
            "title": "Navigation and configuration",
            "color": "#255aa7",
            "content": [
                "Click 📖 <strong>Detailed Workflow</strong> (top of the page) to open this page.",
                "Click 🔬 <strong>Analysis</strong> (top of this page) to return to the main analysis screen.",
            ] + [[
                "In <strong>Grouping Configuration</strong> (shown at the top in developer mode), choose one or more methods:",
                "<strong>SMARTS</strong>: structure-based grouping",
                "<strong>LISTS</strong>: list comparison grouping",
                "<strong>REGEX</strong>: name/identifier text pattern grouping",
                "If no method is selected, SMARTS is used by default."] if st.session_state.is_admin else []][0]
        },
        {
            "number": "1",
            "title": "Add your input data (Step 1)",
            "color": "#255aa7",
            "content": [
                "Choose <strong>Manual Entry</strong> for quick checks.",
                "Choose <strong>File Upload</strong> for Excel/CSV batches.",
                "In manual mode, choose <strong>CAS</strong> or <strong>SMILES</strong>, then paste one entry per line.",
                "You can click <strong>Try Sample Data</strong> to test the full flow instantly.",
                "In upload mode, set the header row, select the sheet (for Excel), then map columns.",
                "You are ready when the green <strong>Input Summary</strong> box appears.",
                "To clear your input and start over, simply refresh the page or click <strong>Clear Data</strong>."
            ]
        },
        {
            "number": "2",
            "title": "Run analysis (Step 2)",
            "color": "#255aa7",
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
            "title": "Explore results and export (Step 3)",
            "color": "#255aa7",
            "content": [
                "Read the <strong>Summary Dashboard</strong> first (total chemicals, valid structures, FCC status, tiers, groups).",
                "Open <strong>Filter Options</strong> to focus results by:"
                "<ul><li style=\"margin: 0.6rem 0;\">FCC status</li>"
                "<li style=\"margin: 0.6rem 0;\">FCCprio tier</li>"
                "<li style=\"margin: 0.6rem 0;\">Groups of concern</li></ul>",
                "For multiple groups of concern, choose:<ul><li><strong>OR</strong> to match any selected group</li>"
                "<li><strong>AND</strong> to require all selected groups</li></ul>",
                "Download final results as <strong>CSV</strong> or <strong>Excel</strong>.",
                "To clear your input and start over, simply refresh the page or click <strong>Clear Data</strong>."
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
                    box-shadow: 0 2px 8px rgba(44,62,97,0.08);
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
    st.markdown('<div class="section-gradient-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="workflow-subsection-title">
            <span class="highlight">Three-Step Process</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_workflow_step_tabs()

    st.markdown('<div class="section-gradient-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="workflow-subsection-title">
            <span class="highlight">Common Use Cases</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    use_cases = [
        ("Food Contact Screening", "Determine if chemicals are used in food contact materials"),
        ("Hazard Prioritization", "Identify high-priority chemicals for assessment"),
        ("Structural Read-Across", "Group chemicals by structural features for hazard prediction"),
        ("Research Analysis", "Systematic classification for publications and reports"),
        ("Regulatory Compliance", "Support safety assessments with integrated FPF data"),
    ]

    _COLOR = "#255aa7"
    use_cases_html = "".join(
        f"<div style='margin:0.75rem 0;'>"
        f"<div style='background:linear-gradient(135deg,{_COLOR}12 0%,{_COLOR}04 100%);"
        f"border-left:5px solid {_COLOR};border-radius:12px;padding:1.25rem;"
        f"font-size:0.95rem;line-height:1.55;'>"
        f"<p style='font-weight:700;margin:0 0 0.4rem 0;font-size:1rem;"
        f"font-family:Poppins,sans-serif;letter-spacing:0.02em;'>"
        f"{icon_title}</p>"
        f"{description}</div>"
        f"</div>"
        for icon_title, description in use_cases
    )
    st.markdown(use_cases_html, unsafe_allow_html=True)
