"""Input and column-mapping UI section."""

from typing import List, Tuple

import pandas as pd
import streamlit as st

from app_modules.config import MAPPING_FIELD_LABELS, build_default_mapping_payload
from app_modules.styles import apply_mode_button_styles


def _reset_for_new_analysis() -> None:
    """Reset input and results state while preserving input mode and method settings."""
    st.session_state.cas_input_text = ""
    st.session_state.text_area_counter = st.session_state.get("text_area_counter", 0) + 1
    st.session_state.uploaded_df = None
    st.session_state.results_df = None
    st.session_state.mapping_payload = {}
    st.session_state.file_upload_counter = st.session_state.get("file_upload_counter", 0) + 1
    for key in ["_upload_sheet_names", "_upload_sheet_names_key", "_upload_parse_key"]:
        if key in st.session_state:
            del st.session_state[key]


def _render_manual_entry() -> List[str]:
    """Render manual CAS/SMILES entry mode and return unique values."""
    input_type_options = {
        "CAS": "casId",
        "SMILES": "SMILES",
    }
    input_type = st.radio(
        "Input Type:",
        options=["CAS", "SMILES"],
        index=0 if st.session_state.input_type == "casId" else 1,
        horizontal=True,
        key="input_type_radio",
        help="Choose between CAS Registry Numbers or SMILES notation",
    )
    st.session_state.input_type = input_type_options[input_type]

    input_label = "CAS Registry Numbers" if st.session_state.input_type == "casId" else "SMILES Notation"
    if st.session_state.input_type == "casId":
        placeholder_text = "80-05-7\n538-23-8\n70546-25-7\n..."
        help_text = "Enter one CAS ID per line."
        tips_html = """
        **💡 Manual Entry Tips**\n
        - One CAS per line\n
        - Format: 123-45-6\n
        """
    else:
        placeholder_text = "CC(C)(C1=CC=C(O)C=C1)C1=CC=C(O)C=C1\nCCCCCCCC(=O)OCC(COC(=O)CCCCCCC)OC(=O)CCCCCCC\n..."
        help_text = "Enter one SMILES string per line."
        tips_html = """
        **💡 Manual Entry Tips**\n
        - One SMILES per line\n
        - Use standard SMILES notation\n
        """

    # Counter-based key forces a fresh widget (with new value=) when sample data or reset is triggered,
    # avoiding the StreamlitAPIException from modifying widget state after instantiation.
    cas_input = st.text_area(
        input_label,
        value=st.session_state.cas_input_text,
        height=220,
        placeholder=placeholder_text,
        help=help_text,
        label_visibility="collapsed",
        key=f"manual_input_textarea_{st.session_state.get('text_area_counter', 0)}",
    )
    st.session_state.cas_input_text = cas_input

    has_manual_input = bool(cas_input.strip())

    # Slide-in animation fires when the container enters the DOM (first keystroke).
    st.markdown(
        """
        <style>
        .st-key-new_analysis_manual_container {
            animation: slideInFromRight 0.4s ease-out;
        }
        @keyframes slideInFromRight {
            from { opacity: 0; transform: translateX(24px); }
            to { opacity: 1; transform: translateX(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Tips on the left, button area on the right — horizontally aligned in one row.
    tips_col, btn_area = st.columns([1, 1])
    with tips_col:
        st.info(tips_html)
    with btn_area:
        # Single button centered in the btn_area; both buttons fill it equally when data is present.
        if has_manual_input:
            sub_try, sub_new = st.columns(2)
            with sub_new:
                with st.container(key="new_analysis_manual_container"):
                    if st.button("🔄 Clear Data", use_container_width=True, key="new_analysis_manual_button"):
                        _reset_for_new_analysis()
                        st.rerun()
        else:
            _, sub_try, _ = st.columns([1, 4, 1])

        with sub_try:
            if st.button("📝 Try Sample Data", use_container_width=True, key="sample_data_button"):
                if st.session_state.input_type == "casId":
                    sample = "80-05-7\n538-23-8\n70546-25-7\n68134-22-5\n128-37-0\n50-00-0"
                else:
                    sample = "CC(C)(C1=CC=C(O)C=C1)C1=CC=C(O)C=C1\nCCCCCCCC(=O)OCC(COC(=O)CCCCCCC)OC(=O)CCCCCCC\nCCN(CC)C1=CC2=C(C=C1)C(C#N)=C(C1=NC3=C(S1)C=CC=C3)C(=O)O2\nCC(=O)C(N=NC1=CC=CC=C1C(F)(F)F)C(=O)NC1=CC2=C(NC(=O)N2)C=C1\nCC1=CC(=C(O)C(=C1)C(C)(C)C)C(C)(C)C\nC=O"
                st.session_state.cas_input_text = sample
                st.session_state.text_area_counter = st.session_state.get("text_area_counter", 0) + 1
                st.rerun()

    manual_input_values = [line.strip() for line in st.session_state.cas_input_text.split("\n") if line.strip()]
    return list(dict.fromkeys(manual_input_values))


def _render_file_upload() -> None:
    """Render file uploader and persist uploaded dataframe in session state."""
    st.markdown("**📤 Upload a File for Column-Based Analysis**")
    st.caption("Uploaded files are analyzed directly. Use column mapping below to tell the library which columns correspond to the identifiers and metadata you want to provide.")

    uploaded_file = st.file_uploader(
        "Upload Excel or CSV",
        type=["xlsx", "xls", "csv"],
        help="Upload a table containing your chemical identifiers and optional metadata columns.",
        label_visibility="collapsed",
        key=f"file_uploader_{st.session_state.get('file_upload_counter', 0)}",
    )

    if uploaded_file is None:
        return

    if st.button("🔄 Clear Data", key="new_analysis_upload_button"):
        _reset_for_new_analysis()
        st.rerun()

    try:
        row_col = st.number_input("Row number containing headers:", min_value=1, max_value=11, value=1, step=1, key="header_row_input")

        sheet_name = None
        if not uploaded_file.name.endswith(".csv"):
            # Cache sheet names separately — reading them is cheap but still avoids redundant I/O.
            file_id = (uploaded_file.name, uploaded_file.size)
            if st.session_state.get("_upload_sheet_names_key") != file_id:
                uploaded_file.seek(0)
                st.session_state._upload_sheet_names = pd.ExcelFile(uploaded_file).sheet_names
                st.session_state._upload_sheet_names_key = file_id
            sheet_name = st.selectbox("Sheet name:", options=st.session_state._upload_sheet_names, key="sheet_selector")

        # Only re-parse the file when the file itself or its parsing parameters change.
        parse_key = (uploaded_file.name, uploaded_file.size, row_col, sheet_name)
        if st.session_state.get("_upload_parse_key") != parse_key:
            uploaded_file.seek(0)
            if uploaded_file.name.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file, header=row_col - 1)
            else:
                df_upload = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=row_col - 1)
            st.session_state.uploaded_df = df_upload
            st.session_state._upload_parse_key = parse_key

        df_upload = st.session_state.uploaded_df
        st.success(f"✅ Uploaded dataset with {len(df_upload)} rows and {len(df_upload.columns)} columns.")
        st.dataframe(df_upload.head(5), use_container_width=True)
    except Exception as error:
        st.error(f"❌ Error reading file. The supported files are as of now: Excel (.xlsx, .xls) and CSV (.csv). Details: {str(error)}.")


def _render_column_mapping(analysis_df: pd.DataFrame) -> None:
    """Render mapping controls for uploaded data."""
    default_mapping = build_default_mapping_payload(st.session_state.input_type)
    existing_mapping = st.session_state.mapping_payload
    mapping_base = {
        key: existing_mapping.get(key, value)
        for key, value in default_mapping.items()
    }

    st.markdown("### 🗺️ Column Mapping")
    st.caption("Map only the columns you want to provide from your uploaded file. Some methods depend on specific identifiers, so incomplete mappings can fail during processing.")
    st.info(
        "Minimum guidance by method:\n"
        "- SMARTS: map SMILES.\n"
        "- LISTS: map CAS.\n"
        "- REGEX: map at least one name field.\n"
        "- Combined methods: provide the union of required columns."
    )

    default_selected_fields = [
        field for field, value in mapping_base.items()
        if (field == "name_columns" and value) or (field != "name_columns" and value is not None)
    ]
    selected_mapping_fields = st.multiselect(
        "Identifiers to map",
        options=list(MAPPING_FIELD_LABELS.keys()),
        default=default_selected_fields,
        format_func=lambda field: MAPPING_FIELD_LABELS[field],
        key="selected_mapping_fields",
        help="Type in the selector to filter identifiers. Each column selector below also supports search.",
    )

    mapping_columns = [None] + list(analysis_df.columns)
    mapping_payload = {
        "cas": None,
        "smiles": None,
        "name_columns": [],
        "formula": None,
    }

    for field in selected_mapping_fields:
        if field == "name_columns":
            mapping_payload[field] = st.multiselect(
                MAPPING_FIELD_LABELS[field],
                options=list(analysis_df.columns),
                default=[col for col in mapping_base.get(field, []) if col in analysis_df.columns],
                key=f"mapping_{field}",
                help="Type to filter available columns.",
            )
            continue

        current_value = mapping_base.get(field)
        mapping_payload[field] = st.selectbox(
            MAPPING_FIELD_LABELS[field],
            options=mapping_columns,
            index=mapping_columns.index(current_value) if current_value in mapping_columns else 0,
            key=f"mapping_{field}",
            help="Type to filter available columns.",
        )

    st.session_state.mapping_payload = mapping_payload


def render_input_section() -> Tuple[pd.DataFrame, bool, int, str, List[str]]:
    """Render full input section and return analysis dataframe + input summary details."""
    st.markdown(
        """
        <h2 class="workflow-section-title">
            <span class="highlight">Step 1: Add Input Data</span>
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.info("⚠️ For optimization reasons, the number of entries is limited to **1,000**. Larger datasets may impact performance.")

    apply_mode_button_styles(st.session_state.input_mode == "Manual Entry")

    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        if st.button(
            "Manual Entry\nPaste CAS or SMILES directly for quick checks",
            key="mode_manual_button",
            use_container_width=True,
        ):
            st.session_state.input_mode = "Manual Entry"
            st.rerun()
    with mode_col2:
        if st.button(
            "File Upload\nUpload Excel or CSV and map your columns",
            key="mode_upload_button",
            use_container_width=True,
        ):
            st.session_state.input_mode = "File Upload"
            st.rerun()

    manual_input_values: List[str] = []

    if st.session_state.input_mode == "Manual Entry":
        manual_input_values = _render_manual_entry()

    if st.session_state.input_mode == "File Upload":
        _render_file_upload()

    uploaded_df_available = st.session_state.uploaded_df is not None
    using_uploaded_input = st.session_state.input_mode == "File Upload" and uploaded_df_available

    if using_uploaded_input:
        analysis_df = st.session_state.uploaded_df.copy()
        _render_column_mapping(analysis_df)
    else:
        analysis_df = pd.DataFrame({st.session_state.input_type: manual_input_values})
        st.session_state.mapping_payload = build_default_mapping_payload(st.session_state.input_type)

    input_summary_ready = False
    input_summary_count = 0
    input_summary_label = "entries"
    input_summary_preview: List[str] = []

    if st.session_state.input_mode == "Manual Entry":
        if manual_input_values:
            input_summary_ready = True
            input_summary_count = len(manual_input_values)
            input_summary_label = "CAS ID(s)" if st.session_state.input_type == "casId" else "SMILES string(s)"
            input_summary_preview = manual_input_values[:3]
    elif using_uploaded_input:
        mapped_columns: List[str] = []
        for field, value in st.session_state.mapping_payload.items():
            if field == "name_columns":
                mapped_columns.extend([col for col in value if col in analysis_df.columns])
            elif value in analysis_df.columns:
                mapped_columns.append(value)

        mapped_columns = list(dict.fromkeys(mapped_columns))
        if mapped_columns:
            analysis_df = analysis_df[mapped_columns]
            preview_source = mapped_columns[0]
            input_summary_ready = True
            input_summary_count = len(analysis_df)
            input_summary_label = "mapped row(s) from uploaded file"
            input_summary_preview = analysis_df[preview_source].dropna().astype(str).head(3).tolist()

    if input_summary_ready:
        _C = "#255aa7"
        preview_text = ", ".join(input_summary_preview) + ("..." if input_summary_count > 3 else "")
        st.markdown(
            f"<div style='background:linear-gradient(135deg,{_C}12 0%,{_C}04 100%);"
            f"border-left:5px solid {_C};border-radius:12px;padding:1.25rem;"
            f"font-size:0.95rem;line-height:1.6;'>"
            f"<p style='font-weight:700;margin:0 0 0.4rem 0;font-size:1rem;"
            f"font-family:Poppins,sans-serif;letter-spacing:0.02em;'>"
            f"Input Summary</p>"
            f"<strong>{input_summary_count} {input_summary_label}</strong> ready to process<br>"
            f"<strong>Preview:</strong> {preview_text}"
            f"</div>",
            unsafe_allow_html=True,
        )

    return analysis_df, input_summary_ready, input_summary_count, input_summary_label, input_summary_preview
