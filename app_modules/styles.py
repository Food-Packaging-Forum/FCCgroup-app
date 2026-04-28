"""Styling and top-level page chrome."""

import streamlit as st


GLOBAL_CSS = """
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }

    .main-header .highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sidebar-main-header {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }

    .sidebar-main-header .highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 2rem;
    }

    .st-key-sidebar_workflow_button button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        min-height: 2.6rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
    }

    .st-key-sidebar_workflow_button button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(102, 126, 234, 0.38);
        filter: saturate(1.1);
    }

    .st-key-sidebar_workflow_button button:focus-visible {
        outline: 3px solid rgba(118, 75, 162, 0.35);
        outline-offset: 1px;
    }

    .card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }

    .process-step {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }

    .process-step:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
    }

    .process-step h3 {
        margin: 0;
        font-size: 1.3rem;
        font-weight: 600;
    }

    .process-step p {
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        opacity: 0.95;
    }

    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 1.2rem;
        margin: 0 0 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
    }

    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
    }

    .warning-box {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);
    }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }

    .metric-card-label {
        color: #6c757d;
    }

    .timeline-item {
        position: relative;
        padding-left: 2.5rem;
        padding-bottom: 2rem;
        border-left: 3px solid #e5e7eb;
    }

    .timeline-item:last-child {
        border-left: none;
    }

    .timeline-icon {
        position: absolute;
        left: -1rem;
        top: 0;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader {
        background-color: rgba(0, 0, 0, 0.03);
        border-radius: 10px;
        font-weight: 600;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }

    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #e5e7eb, transparent);
    }

    .workflow-card {
        margin: .5rem 0;
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: left;
        min-height: 150px;
        position: relative;
        transition: transform 0.3s ease;
        display: flex;
        flex-direction: column;
    }

    .workflow-card:hover {
        transform: translateY(-4px);
    }

    .workflow-card .brief-description {
        margin: 0.4rem 0;
        font-size: 0.9rem;
        opacity: 0.95;
        transition: opacity 0.3s ease;
        flex-grow: 1;
    }

    .workflow-card:hover .brief-description {
        opacity: 0.85;
    }

    .workflow-card .details-block {
        max-height: 0;
        opacity: 0;
        overflow: hidden;
        transition: max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1), 
                    opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1),
                    margin-top 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        margin-top: 0;
        flex-grow: 1;
    }

    .workflow-card .details-block > * {
        transition: opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .workflow-card:hover .details-block {
        max-height: 400px;
        opacity: 1;
        margin-top: 0.75rem;
        padding-top: 0.75rem;
    }

    .workflow-card .details-block p {
        margin: 0.5rem 0 0.25rem;
        font-size: 0.9rem;
        opacity: 0.95;
    }

    .workflow-card .details-block ul {
        margin: 0.25rem 0 0.5rem;
        padding-left: 1.1rem;
        font-size: 0.85rem;
        opacity: 0.9;
        line-height: 1.35;
    }

    @media (hover: none) {
        .workflow-card .details-block {
            max-height: 400px;
            opacity: 1;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
        }
    }

    .workflow-intro {
        background: rgba(102, 126, 234, 0.08);
        border-left: 4px solid #667eea;
        padding: 2rem;
        margin: 1.5rem 0 2rem 0;
        border-radius: 12px;
        font-size: 1rem;
        line-height: 1.6;
        transition: all 0.3s ease;
    }

    .workflow-intro:hover {
        border-left-color: #764ba2;
        background: rgba(102, 126, 234, 0.13);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }

    .use-case-item {
        background: rgba(0, 0, 0, 0.03);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .use-case-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        transform: scaleY(0);
        transform-origin: center;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .use-case-item:hover {
        transform: translateX(4px);
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        background: rgba(102, 126, 234, 0.07);
    }

    .use-case-item:hover::before {
        transform: scaleY(1);
    }

    .use-case-title {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
        letter-spacing: 0.3px;
    }

    .use-case-description {
        font-size: 0.95rem;
        line-height: 1.5;
        opacity: 0.8;
    }

    .workflow-section-title {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin: 2rem 0 2.5rem 0;
        padding: 1rem 0;
    }

    .workflow-section-title .highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .workflow-subsection-title {
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
        margin: 2.5rem 0 2rem 0;
        padding: 0.5rem 0;
    }

    .workflow-subsection-title .highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .workflow-button {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        text-decoration: none !important;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
        margin-top: 1rem;
        display: inline-block;
        margin-right: 0.5rem;
    }

    .workflow-button:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-decoration: none !important;
        color: white;
    }

    .workflow-button:visited {
        text-decoration: none !important;
        color: white;
    }

    .workflow-button-container {
        max-height: 0;
        opacity: 0;
        overflow: visible;
        transition: max-height 0.3s ease, opacity 0.3s ease;
        margin-top: 0;
    }

    .workflow-card:hover .workflow-button-container {
        max-height: 150px;
        opacity: 1;
        margin-top: 1.2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }

    @media (hover: none) {
        .workflow-card .workflow-button-container {
            max-height: 150px;
            opacity: 1;
            margin-top: 1.2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }
    }

    /* ======================================================
       Dark-mode overrides
       Uses both [data-theme="dark"] (for Streamlit's own toggle)
       and @media (prefers-color-scheme: dark) (for system preference)
       to ensure maximum compatibility across Streamlit versions.
       ====================================================== */

    [data-theme="dark"] .subtitle { color: #9ca3af; }
    @media (prefers-color-scheme: dark) { .subtitle { color: #9ca3af; } }

    [data-theme="dark"] .card {
        background: #1e2130;
        border-color: rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    @media (prefers-color-scheme: dark) {
        .card {
            background: #1e2130;
            border-color: rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
    }

    [data-theme="dark"] .card:hover { box-shadow: 0 8px 15px rgba(0, 0, 0, 0.35); }
    @media (prefers-color-scheme: dark) { .card:hover { box-shadow: 0 8px 15px rgba(0, 0, 0, 0.35); } }

    [data-theme="dark"] .metric-card {
        background: #1e2130;
        border-color: rgba(255, 255, 255, 0.08);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: #1e2130;
            border-color: rgba(255, 255, 255, 0.08);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
    }

    [data-theme="dark"] .metric-card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4); }
    @media (prefers-color-scheme: dark) { .metric-card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4); } }

    [data-theme="dark"] .metric-card-label { color: #9ca3af; }
    @media (prefers-color-scheme: dark) { .metric-card-label { color: #9ca3af; } }

    [data-theme="dark"] .streamlit-expanderHeader { background-color: rgba(255, 255, 255, 0.05); }
    @media (prefers-color-scheme: dark) { .streamlit-expanderHeader { background-color: rgba(255, 255, 255, 0.05); } }

    [data-theme="dark"] section[data-testid="stSidebar"] { background: none; }
    @media (prefers-color-scheme: dark) { section[data-testid="stSidebar"] { background: none; } }
</style>
"""


def apply_global_styles() -> None:
    """Apply shared CSS styles for the app."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_page_header() -> None:
    """Render app title area."""
    st.markdown('<h1 class="main-header">🧪 <span class="highlight">FCC Grouping Tool</span></h1>', unsafe_allow_html=True)

    st.markdown(
        '<p class="subtitle">Identify and classify Food Contact Chemicals using FPF\'s integrated databases and structural analysis</p>',
        unsafe_allow_html=True,
    )


def apply_mode_button_styles(is_manual_mode: bool) -> None:
    """Style the mode selector buttons according to selected mode."""
    is_upload_mode = not is_manual_mode

    manual_background = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" if is_manual_mode else "transparent"
    manual_color = "#ffffff" if is_manual_mode else "inherit"
    manual_border = "none" if is_manual_mode else "1px solid rgba(128, 128, 128, 0.4)"
    manual_shadow = "0 6px 16px rgba(102, 126, 234, 0.28)" if is_manual_mode else "0 2px 8px rgba(0, 0, 0, 0.08)"

    upload_background = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" if is_upload_mode else "transparent"
    upload_color = "#ffffff" if is_upload_mode else "inherit"
    upload_border = "none" if is_upload_mode else "1px solid rgba(128, 128, 128, 0.4)"
    upload_shadow = "0 6px 16px rgba(102, 126, 234, 0.28)" if is_upload_mode else "0 2px 8px rgba(0, 0, 0, 0.08)"

    st.markdown(
        f"""
        <style>
        .st-key-mode_manual_button button,
        .st-key-mode_upload_button button {{
            min-height: 110px;
            border-radius: 16px;
            padding: 1rem 1.25rem;
            display: grid;
            grid-template-columns: 2.6rem 1fr;
            gap: 0.35rem;
            align-items: center;
        }}

        .st-key-mode_manual_button button p,
        .st-key-mode_upload_button button p {{
            white-space: pre-line;
            line-height: 1.35;
            font-size: 1rem;
            font-weight: 600;
            text-align: left;
        }}

        @media (max-width: 640px) {{
            .st-key-mode_manual_button button,
            .st-key-mode_upload_button button {{
                grid-template-columns: 1fr;
                gap: 0.25rem;
                justify-items: center;
                text-align: center;
                padding: 0.9rem 1rem;
            }}

            .st-key-mode_manual_button button p,
            .st-key-mode_upload_button button p {{
                text-align: center;
            }}
        }}

        .st-key-mode_manual_button button::before {{
            content: "✏️";
            font-size: 2rem;
            line-height: 1;
            text-align: center;
        }}

        .st-key-mode_upload_button button::before {{
            content: "📤";
            font-size: 2rem;
            line-height: 1;
            text-align: center;
        }}

        .st-key-mode_manual_button button {{
            background: {manual_background};
            color: {manual_color};
            border: {manual_border};
            box-shadow: {manual_shadow};
        }}

        .st-key-mode_upload_button button {{
            background: {upload_background};
            color: {upload_color};
            border: {upload_border};
            box-shadow: {upload_shadow};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
