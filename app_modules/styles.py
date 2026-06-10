"""Styling and top-level page chrome."""

import base64
from pathlib import Path

import streamlit as st
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

    .brand-banner {
        display: flex;
        justify-content: center;
        margin: 0 0 1rem 0;
    }

    .brand-banner img {
        max-height: 62px;
        object-fit: contain;
        width: auto;
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
        height: 40px;
        width: auto;
        display: inline-block;
    }

    .main-header .highlight {
        background: var(--fpf-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sidebar-main-header {
        font-size: 2rem;
        font-weight: 700;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }

    .sidebar-main-header img {
        width: 32px;
        height: auto;
        padding-right: 0.35rem;
        display: inline-block;
        vertical-align: middle;
    }

    .sidebar-main-header .highlight {
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

    .header-intro {
        max-width: 900px;
        margin: 0 auto 1.6rem auto;
        background: linear-gradient(180deg, rgba(37, 90, 167, 0.08) 0%, rgba(44, 62, 97, 0.04) 100%);
        border: 1px solid var(--fpf-border);
        border-left: 5px solid var(--fpf-blue);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        line-height: 1.55;
        font-size: 0.98rem;
        color: var(--fpf-text);
        box-shadow: 0 2px 6px rgba(44, 62, 97, 0.08);
    }

    .header-intro strong {
        color: var(--fpf-dark-blue);
        font-family: 'Poppins', 'Segoe UI', sans-serif;
        font-weight: 700;
    }

    .st-key-sidebar_workflow_button button {
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        min-height: 2.6rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        box-shadow: var(--fpf-shadow);
    }

    .st-key-sidebar_workflow_button button:hover {
        transform: scale(1.03);
        box-shadow: var(--fpf-shadow-strong);
        background: var(--fpf-gradient);
        color: #ffffff;
        border: none;
    }

    .st-key-sidebar_workflow_button button:focus-visible {
        outline: 3px solid rgba(37, 90, 167, 0.35);
        outline-offset: 1px;
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

    .cta-hint {
        text-align: center;
        margin-bottom: 0.65rem;
        color: var(--fpf-dark-blue);
        font-size: 0.96rem;
        font-weight: 600;
    }

    .card {
        background: var(--secondary-background-color);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin: 1.5rem 0;
        border: 1px solid rgba(128, 128, 128, 0.2);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
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

    .info-box {
        background: rgba(37, 90, 167, 0.1);
        border-left: 4px solid var(--fpf-blue);
        padding: 1.2rem;
        margin: 0 0 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(37, 90, 167, 0.1);
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
        background: rgba(44, 62, 97, 0.08);
        border-left: 4px solid var(--fpf-dark-blue);
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(44, 62, 97, 0.1);
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
        background: var(--fpf-gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(37, 90, 167, 0.4);
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
        background: rgba(37, 90, 167, 0.08);
        border-left: 4px solid var(--fpf-blue);
        padding: 2rem;
        margin: 1.5rem 0 2rem 0;
        border-radius: 12px;
        font-size: 1rem;
        line-height: 1.6;
        transition: all 0.3s ease;
    }

    .workflow-intro:hover {
        border-left-color: var(--fpf-dark-blue);
        background: rgba(37, 90, 167, 0.12);
        box-shadow: 0 4px 12px rgba(37, 90, 167, 0.15);
    }

    .use-case-item {
        background: rgba(0, 0, 0, 0.03);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
        background: linear-gradient(180deg, #255aa7 0%, #2c3e61 100%);
        transform: scaleY(0);
        transform-origin: center;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .use-case-item:hover {
        transform: translateX(4px);
        border-color: var(--fpf-blue);
        box-shadow: 0 4px 12px rgba(37, 90, 167, 0.15);
        background: rgba(37, 90, 167, 0.07);
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

    .workflow-card-prioritization {
        background: #2c3e61;
        box-shadow: 0 4px 10px rgba(31, 77, 144, 0.3);
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

    [data-theme="dark"] .subtitle { color: #c9d5e2; }
    @media (prefers-color-scheme: dark) { .subtitle { color: #c9d5e2; } }

    [data-theme="dark"] .card {
        background: color-mix(in srgb, var(--secondary-background-color) 100%, white 18%);
        border-color: rgba(255, 255, 255, 0.12);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    @media (prefers-color-scheme: dark) {
        .card {
            background: color-mix(in srgb, var(--secondary-background-color) 100%, white 18%);
            border-color: rgba(255, 255, 255, 0.12);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }
    }

    [data-theme="dark"] .card:hover { box-shadow: 0 8px 15px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05); }
    @media (prefers-color-scheme: dark) { .card:hover { box-shadow: 0 8px 15px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05); } }

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

    [data-theme="dark"] .timeline-item { border-left-color: rgba(255, 255, 255, 0.1); }
    @media (prefers-color-scheme: dark) { .timeline-item { border-left-color: rgba(255, 255, 255, 0.1); } }

    [data-theme="dark"] .use-case-item {
        background: rgba(255, 255, 255, 0.03);
        border-color: rgba(255, 255, 255, 0.09);
    }
    [data-theme="dark"] .use-case-item:hover {
        background: rgba(37, 90, 167, 0.1);
        border-color: rgba(37, 90, 167, 0.45);
        box-shadow: 0 4px 12px rgba(37, 90, 167, 0.12);
    }
    @media (prefers-color-scheme: dark) {
        .use-case-item {
            background: rgba(255, 255, 255, 0.03);
            border-color: rgba(255, 255, 255, 0.09);
        }
        .use-case-item:hover {
            background: rgba(37, 90, 167, 0.1);
            border-color: rgba(37, 90, 167, 0.45);
            box-shadow: 0 4px 12px rgba(37, 90, 167, 0.12);
        }
    }

    [data-theme="dark"] .workflow-intro {
        background: rgba(37, 90, 167, 0.1);
    }
    [data-theme="dark"] .workflow-intro:hover {
        background: rgba(37, 90, 167, 0.15);
        box-shadow: 0 4px 12px rgba(37, 90, 167, 0.12);
    }
    @media (prefers-color-scheme: dark) {
        .workflow-intro {
            background: rgba(37, 90, 167, 0.1);
        }
        .workflow-intro:hover {
            background: rgba(37, 90, 167, 0.15);
            box-shadow: 0 4px 12px rgba(37, 90, 167, 0.12);
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

    @media (max-width: 768px) {
        .main-header {
            font-size: 2.2rem;
            padding: 0.5rem 0;
        }

        .header-intro {
            padding: 0.9rem 1rem;
            font-size: 0.93rem;
        }

        .brand-banner img {
            max-height: 52px;
        }

        .workflow-section-boxes {
            flex-direction: column;
        }
    }
</style>
"""


def apply_global_styles() -> None:
    """Apply shared CSS styles for the app."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_page_header(active_page: str = "main") -> tuple[bool, bool]:
    """Render app title and nav tabs. Returns (go_to_workflow, go_to_analysis)."""
    image_path = Path(__file__).resolve().parents[1] / "assets" / "FCCprio_logo_signet.svg"
    image_src = _svg_as_data_uri(image_path)

    st.markdown(
        f'<h1 class="main-header"><img src="{image_src}" alt="FCCprio logo"><span class="highlight">FCCgroup</span></h1>',
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
