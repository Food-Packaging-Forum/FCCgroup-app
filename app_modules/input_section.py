"""Input and column-mapping UI section."""

from typing import List, Tuple

import pandas as pd
import streamlit as st

from app_modules.config import MAPPING_FIELD_LABELS, build_default_mapping_payload
from app_modules.styles import apply_mode_button_styles


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
        placeholder_text = "50-00-0\n67-56-1\n107-21-1\n..."
        help_text = "Enter one CAS ID per line."
        tips_html = """
        <div class="info-box">
            <strong>💡 Manual Entry Tips</strong>
            <ul style="margin: 0.5rem 0; padding-left: 1.2rem;">
                <li>One CAS per line</li>
                <li>Format: <code>123-45-6</code></li>
                <li>Best for quick ad hoc runs</li>
            </ul>
        </div>
        """
    else:
        placeholder_text = "CCO\nCC(=O)O\nc1ccccc1\n..."
        help_text = "Enter one SMILES string per line."
        tips_html = """
        <div class="info-box">
            <strong>💡 Manual Entry Tips</strong>
            <ul style="margin: 0.5rem 0; padding-left: 1.2rem;">
                <li>One SMILES per line</li>
                <li>Use standard SMILES notation</li>
                <li>Best for quick ad hoc runs</li>
            </ul>
        </div>
        """

    cas_input = st.text_area(
        input_label,
        value=st.session_state.cas_input_text,
        height=220,
        placeholder=placeholder_text,
        help=help_text,
        label_visibility="collapsed",
    )
    st.session_state.cas_input_text = cas_input

    manual_col1, manual_col2 = st.columns([1, 2])
    with manual_col1:
        if st.button("📝 Try Sample Data", use_container_width=True, key="sample_data_button"):
            if st.session_state.input_type == "casId":
                st.session_state.cas_input_text = "50-00-0\n67-56-1\n107-21-1\n108-95-2\n110-82-7\n111-46-6"
            else:
                st.session_state.cas_input_text = "C=O\nCO\nOCCO\nc1ccccc1O\nCCCCC\nCC(C)=O"
            st.rerun()
    with manual_col2:
        st.markdown(tips_html, unsafe_allow_html=True)

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
    )

    if uploaded_file is None:
        return

    try:
        row_col = st.number_input("Row number containing headers:", min_value=1, max_value=11, value=1, step=1, key="header_row_input")
        if uploaded_file.name.endswith(".csv"):
            df_upload = pd.read_csv(uploaded_file, header=row_col - 1)
        else:
            sheet_name = st.selectbox("Sheet name:", options=pd.ExcelFile(uploaded_file).sheet_names, key="sheet_selector")
            df_upload = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=row_col - 1)

        st.session_state.uploaded_df = df_upload
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
        <div class="process-step">
            <h3>Step 1: Add Input Data</h3>
            <p>Choose one input path before running the analysis</p>
        </div>
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
        st.markdown(
            f"""
            <div class="success-box">
                <strong>✅ Input Summary</strong><br>
                📊 <strong>{input_summary_count}</strong> {input_summary_label} ready to process<br>
                🔍 Preview: {', '.join(input_summary_preview)}{'...' if input_summary_count > 3 else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

    return analysis_df, input_summary_ready, input_summary_count, input_summary_label, input_summary_preview
