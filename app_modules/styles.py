"""Styling and top-level page chrome."""

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from utils import _svg_as_data_uri


GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&family=Poppins:wght@600;700;800&display=swap');

    :root {
        --fpf-blue: #255aa7;
        --fpf-dark-blue: #2c3e61;
        --fpf-soft-blue: #d9e7f8;
        --fpf-light-gray: #eef1f5;
        --fpf-border: #cfd8e3;
        --fpf-text: #1f2a37;
        --fpf-muted: #556070;
        --fpf-gradient: #255aa7;
        --fpf-shadow: 0 6px 16px rgba(37, 90, 167, 0.28);
        --fpf-shadow-strong: 0 8px 18px rgba(37, 90, 167, 0.36);
    }

    html, body, [class*="css"] {
        font-family: 'Open Sans', 'Segoe UI', sans-serif;
        color: var(--fpf-text);
    }

    h1, h2, h3, h4, h5, h6,
    .highlight {
        font-family: 'Poppins', 'Segoe UI', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.6rem;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }

    .main-header img {
        height: 60px;
        width: auto;
        display: inline-block;
    }

    .main-header .highlight {
        background: var(--fpf-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #000000;
        margin-bottom: 1rem;
    }

    .st-key-start_analysis_button button {
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        min-height: 3rem;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
        font-weight: 700;
        letter-spacing: 0.01em;
        box-shadow: 0 10px 24px rgba(37, 90, 167, 0.34);
    }

    .st-key-start_analysis_button button:not(:disabled):hover {
        transform: scale(1.03);
        box-shadow: 0 12px 28px rgba(37, 90, 167, 0.42);
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
    }

    .st-key-start_analysis_button button:disabled {
        cursor: not-allowed;
        pointer-events: auto;
    }

    /* Unblock Streamlit's inner container chain so full-width elements can escape.
       stMain is intentionally excluded — it is the scroll container. */
    .block-container,
    div[data-testid="stVerticalBlock"],
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="element-container"],
    div[data-testid="stMarkdownContainer"] {
        overflow: visible !important;
    }

    .section-gradient-divider {
        position: relative;
        left: 50%;
        transform: translateX(-50%);
        width: 100vw;
        height: 4rem;
        background: linear-gradient(to bottom, transparent 0%, #F8F8F8 100%);
        margin: 0.5rem 0 4rem 0;
        pointer-events: none;
        display: block;
    }

    .metric-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }

    @media (max-width: 640px) {
        .metric-cards-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    .metric-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }

    @media (max-width: 640px) {
        .metric-cards-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    .metric-card {
        background: var(--secondary-background-color);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.15);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }

    .metric-card-label {
        color: var(--fpf-muted);
    }

    .metric-card-icon {
        font-size: 1.5rem;
        margin-bottom: 0.35rem;
    }

    .metric-card-value {
        font-family: 'Poppins', 'Segoe UI', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--fpf-dark-blue);
        margin-bottom: 0.2rem;
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

    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #e5e7eb, transparent);
    }

    .workflow-section-title {
        font-size: 2.8rem;
        font-weight: 700;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
        margin: 2rem 0 2.5rem 0;
        padding: 1rem 0;
        margin: 0.5rem 0 0rem 0;
    }

    .workflow-section-title .highlight {
        background: var(--fpf-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .workflow-subsection-title {
        font-size: 1.8rem;
        font-weight: 700;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
        margin: 2.5rem 0 2rem 0;
        padding: 0.5rem 0;
    }

    .workflow-subsection-title .highlight {
        background: var(--fpf-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ======================================================
       Dark-mode overrides
       Uses both [data-theme="dark"] (for Streamlit's own toggle)
       and @media (prefers-color-scheme: dark) (for system preference)
       to ensure maximum compatibility across Streamlit versions.
       ====================================================== */

    [data-theme="dark"] .subtitle { color: #c9d5e2; }
    @media (prefers-color-scheme: dark) { .subtitle { color: #c9d5e2; } }

    [data-theme="dark"] .metric-card {
        background: color-mix(in srgb, var(--secondary-background-color) 100%, white 18%);
        border-color: rgba(255, 255, 255, 0.12);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: color-mix(in srgb, var(--secondary-background-color) 100%, white 18%);
            border-color: rgba(255, 255, 255, 0.12);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }
    }

    [data-theme="dark"] .metric-card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05); }
    @media (prefers-color-scheme: dark) { .metric-card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05); } }

    [data-theme="dark"] .metric-card-label { color: #9ca3af; }
    @media (prefers-color-scheme: dark) { .metric-card-label { color: #9ca3af; } }

    [data-theme="dark"] .streamlit-expanderHeader { background-color: rgba(255, 255, 255, 0.05); }
    @media (prefers-color-scheme: dark) { .streamlit-expanderHeader { background-color: rgba(255, 255, 255, 0.05); } }

    [data-theme="dark"] hr {
        background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.1), transparent);
    }
    @media (prefers-color-scheme: dark) {
        hr {
            background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.1), transparent);
        }
    }

    [data-theme="dark"] .section-gradient-divider {
        background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.18) 100%);
    }
    @media (prefers-color-scheme: dark) {
        .section-gradient-divider {
            background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.18) 100%);
        }
    }

    /* Download buttons need explicit transition — they render as .stDownloadButton, not .stButton,
       so the global .stButton > button transition rule does not reach them. */
    .st-key-download_csv_button button,
    .st-key-download_excel_button button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease !important;
    }

    /* wf_tab buttons: ensure 0.3s transition wins over Streamlit's built-in shorter default */
    [class*="st-key-wf_tab_"] button {
        transition: all 0.3s ease !important;
    }

    /* Clear and download buttons — hover: zoom + shadow, no background change */
    .st-key-new_analysis_manual_button button:hover,
    .st-key-new_analysis_upload_button button:hover,
    .st-key-clear_data_results_button button:hover,
    .st-key-download_csv_button button:hover,
    .st-key-download_excel_button button:hover {
        transform: scale(1.03);
        box-shadow: var(--fpf-shadow);
        background: var(--background-color);
    }

    /* Hide sidebar and its toggle completely */
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* Sample data button — matches main workflow button style */
    .st-key-sample_data_button button {
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        min-height: 2.6rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        box-shadow: var(--fpf-shadow);
    }

    .st-key-sample_data_button button:hover {
        transform: scale(1.03);
        box-shadow: var(--fpf-shadow-strong);
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
    }

    .st-key-sample_data_button button:focus-visible {
        outline: 3px solid rgba(37, 90, 167, 0.35);
        outline-offset: 1px;
    }

    /* Grouping config panel */
    .st-key-grouping_config_panel {
        background: rgba(37, 90, 167, 0.06);
        border: 1px solid var(--fpf-border);
        border-radius: 12px;
        padding: 0.75rem 1.25rem 0.5rem;
        margin: 0 0 1.25rem 0;
    }

    [data-theme="dark"] .st-key-grouping_config_panel {
        background: rgba(37, 90, 167, 0.1);
        border-color: rgba(37, 90, 167, 0.3);
    }

    /* Page footer */
    .page-footer {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 2rem;
        padding: 0.5rem 0 1rem 0;
        flex-wrap: wrap;
    }

    .page-footer img.fpf-logo {
        height: 36px;
        width: auto;
    }

    .page-footer-license {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .page-footer-text {
        font-size: 0.85rem;
        color: var(--fpf-muted);
    }

    .workflow-section-boxes {
        display: flex;
        gap: 1rem;
        align-items: stretch;
        margin: 0.5rem 0 1rem 0;
    }

    .workflow-section-box {
        flex: 1;
        display: flex;
        flex-direction: column;
    }

    /* Download buttons need explicit transition — they render as .stDownloadButton, not .stButton,
       so the global .stButton > button transition rule does not reach them. */
    .st-key-download_csv_button button,
    .st-key-download_excel_button button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease !important;
    }

    /* wf_tab buttons: ensure 0.3s transition wins over Streamlit's built-in shorter default */
    [class*="st-key-wf_tab_"] button {
        transition: all 0.3s ease !important;
    }

    /* Clear and download buttons — hover: zoom + shadow, no background change */
    .st-key-new_analysis_manual_button button:hover,
    .st-key-new_analysis_upload_button button:hover,
    .st-key-clear_data_results_button button:hover,
    .st-key-download_csv_button button:hover,
    .st-key-download_excel_button button:hover {
        transform: scale(1.03);
        box-shadow: var(--fpf-shadow);
        background: var(--background-color);
    }

    /* Hide sidebar and its toggle completely */
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* Sample data button — matches main workflow button style */
    .st-key-sample_data_button button {
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        min-height: 2.6rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        box-shadow: var(--fpf-shadow);
    }

    .st-key-sample_data_button button:hover {
        transform: scale(1.03);
        box-shadow: var(--fpf-shadow-strong);
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
    }

    .st-key-sample_data_button button:focus-visible {
        outline: 3px solid rgba(37, 90, 167, 0.35);
        outline-offset: 1px;
    }

    /* Main workflow button */
    .st-key-main_workflow_button button {
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        min-height: 2.6rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        box-shadow: var(--fpf-shadow);
    }

    .st-key-main_workflow_button button:hover {
        transform: scale(1.03);
        box-shadow: var(--fpf-shadow-strong);
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
    }

    .st-key-main_workflow_button button:focus-visible {
        outline: 3px solid rgba(37, 90, 167, 0.35);
        outline-offset: 1px;
    }

    /* Grouping config panel */
    .st-key-grouping_config_panel {
        background: rgba(37, 90, 167, 0.06);
        border: 1px solid var(--fpf-border);
        border-radius: 12px;
        padding: 0.75rem 1.25rem 0.5rem;
        margin: 0 0 1.25rem 0;
    }

    [data-theme="dark"] .st-key-grouping_config_panel {
        background: rgba(37, 90, 167, 0.1);
        border-color: rgba(37, 90, 167, 0.3);
    }

    /* Page footer */
    .page-footer {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 2rem;
        padding: 0.5rem 0 1rem 0;
        flex-wrap: wrap;
    }

    .page-footer img.fpf-logo {
        height: 36px;
        width: auto;
    }

    .page-footer-license {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .page-footer-text {
        font-size: 0.85rem;
        color: var(--fpf-muted);
    }

    @media (max-width: 768px) {
        .main-header {
            font-size: 2.2rem;
            padding: 0.5rem 0;
        }

        .workflow-section-boxes {
            flex-direction: column;
        }
    }
</style>
"""


# NOTE: This must run as a real <script> via st.components.v1.html (an iframe),
# NOT st.markdown — Streamlit strips <script> tags from markdown, so the head
# injection never executes there. From inside the iframe we target the PARENT
# document's <head> (same origin), which is the actual page browsers read for
# the manifest and apple-touch-icon.
PWA_HEAD = """
<script>
(function () {
  var doc = window.parent.document;
  function addHead(tag, attrs) {
    var sel = tag + '[' + (attrs.rel ? 'rel="' + attrs.rel + '"' : 'href="' + attrs.href + '"') + ']';
    if (doc.querySelector(sel)) return;
    var el = doc.createElement(tag);
    Object.keys(attrs).forEach(function(k) { el.setAttribute(k, attrs[k]); });
    doc.head.appendChild(el);
  }
  function addMeta(name, content) {
    if (doc.querySelector('meta[name="' + name + '"]')) return;
    var el = doc.createElement('meta');
    el.name = name; el.content = content;
    doc.head.appendChild(el);
  }
  addHead('link', { rel: 'manifest',         href: '/app/static/manifest.json' });
  addHead('link', { rel: 'apple-touch-icon', href: '/app/static/apple-touch-icon.png' });
  addMeta('mobile-web-app-capable',            'yes');
  addMeta('apple-mobile-web-app-capable',      'yes');
  addMeta('apple-mobile-web-app-status-bar-style', 'default');
  addMeta('apple-mobile-web-app-title',        'FCCgroup');
  addMeta('theme-color',                       '#255aa7');
})();
</script>
"""


def apply_global_styles() -> None:
    """Apply shared CSS styles and PWA meta tags for the app."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    # Inject PWA head tags via a zero-height iframe component so the <script>
    # actually executes (st.markdown would strip it).
    components.html(PWA_HEAD, height=0, width=0)


def render_page_header(active_page: str = "main") -> tuple[bool, bool]:
    """Render app title and nav tabs. Returns (go_to_workflow, go_to_analysis)."""
    image_path = Path(__file__).resolve().parents[1] / "static" / "FCCgroup_logo_signet.svg"
    image_src = _svg_as_data_uri(image_path)

    st.markdown(
        f'<h1 class="main-header"><img src="{image_src}" alt="FCCgroup logo"><span class="highlight">FCCgroup</span></h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="subtitle">Identify and classify Food Contact Chemicals using FPF\'s integrated databases and structural analysis</p>',
        unsafe_allow_html=True,
    )

    on_workflow = active_page == "workflow"
    analysis_bg = "#255aa7" if not on_workflow else "transparent"
    analysis_color = "#ffffff" if not on_workflow else "inherit"
    analysis_border = "none" if not on_workflow else "1px solid rgba(128,128,128,0.4)"
    workflow_bg = "#255aa7" if on_workflow else "transparent"
    workflow_color = "#ffffff" if on_workflow else "inherit"
    workflow_border = "none" if on_workflow else "1px solid rgba(128,128,128,0.4)"

    st.markdown(
        f"""
        <style>
        .st-key-nav_analysis_button button {{
            background: {analysis_bg}; color: {analysis_color}; border: {analysis_border};
            border-radius: 12px; font-weight: 700; min-height: 2.4rem;
        }}
        .st-key-nav_analysis_button button:hover {{
            background: {analysis_bg}; color: {analysis_color}; border: {analysis_border};
            transform: scale(1.03); box-shadow: var(--fpf-shadow);
        }}
        .st-key-nav_workflow_button button {{
            background: {workflow_bg}; color: {workflow_color}; border: {workflow_border};
            border-radius: 12px; font-weight: 700; min-width: 148px;
        }}
        .st-key-nav_workflow_button button:hover {{
            background: {workflow_bg}; color: {workflow_color}; border: {workflow_border};
            transform: scale(1.03); box-shadow: var(--fpf-shadow);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        col_a, col_w = st.columns(2)
        with col_a:
            go_to_analysis = st.button("🔬 Analysis", key="nav_analysis_button", use_container_width=True)
        with col_w:
            go_to_workflow = st.button("📖 Detailed Workflow", key="nav_workflow_button", use_container_width=True)

    return go_to_workflow, go_to_analysis


def render_footer() -> None:
    """Render horizontal footer with logo and license."""
    fpf_logo_path = Path(__file__).resolve().parents[1] / "assets" / "fpf_logo_RGB_vector_SVG.svg"
    fpf_logo_src = _svg_as_data_uri(fpf_logo_path)

    st.markdown("---")
    st.markdown(
        f"""
        <div class="page-footer">
            <img src="{fpf_logo_src}" class="fpf-logo" alt="Food Packaging Forum">
            <div class="page-footer-license">
                <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" style="line-height:0;">
                    <img src="https://licensebuttons.net/l/by/4.0/88x31.png" alt="CC BY 4.0">
                </a>
                <span class="page-footer-text">© 2026 Food Packaging Forum — CC BY 4.0</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_mode_button_styles(is_manual_mode: bool) -> None:
    """Style the mode selector buttons according to selected mode."""
    is_upload_mode = not is_manual_mode

    manual_background = "#255aa7" if is_manual_mode else "transparent"
    manual_color = "#ffffff" if is_manual_mode else "inherit"
    manual_border = "none" if is_manual_mode else "1px solid rgba(128, 128, 128, 0.4)"
    manual_shadow = "0 6px 16px rgba(37, 90, 167, 0.28)" if is_manual_mode else "0 2px 8px rgba(0, 0, 0, 0.08)"

    upload_background = "#255aa7" if is_upload_mode else "transparent"
    upload_color = "#ffffff" if is_upload_mode else "inherit"
    upload_border = "none" if is_upload_mode else "1px solid rgba(128, 128, 128, 0.4)"
    upload_shadow = "0 6px 16px rgba(37, 90, 167, 0.28)" if is_upload_mode else "0 2px 8px rgba(0, 0, 0, 0.08)"

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

        .st-key-mode_manual_button button:hover {{
            background: {manual_background};
            color: {manual_color};
            border: {manual_border};
            box-shadow: var(--fpf-shadow-strong);
            transform: scale(1.03);
        }}

        .st-key-mode_upload_button button {{
            background: {upload_background};
            color: {upload_color};
            border: {upload_border};
            box-shadow: {upload_shadow};
        }}

        .st-key-mode_upload_button button:hover {{
            background: {upload_background};
            color: {upload_color};
            border: {upload_border};
            box-shadow: var(--fpf-shadow-strong);
            transform: scale(1.03);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
