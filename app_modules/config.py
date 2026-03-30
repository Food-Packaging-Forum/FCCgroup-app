"""UI and mapping configuration values for the app."""

from typing import Dict

MAPPING_FIELD_LABELS = {
    "cas": "CAS",
    "smiles": "SMILES",
    "name_columns": "Name columns",
    "formula": "Formula",
}

DISPLAY_RESULT_COLUMNS = [
    "CAS RN",
    "SMILES",
    "Chemical names",
    "Formula",
    "is Food Contact Chemical",
    "Tier of FCCprio",
    "Groups of concern",
]


def build_default_mapping_payload(input_type: str) -> Dict[str, object]:
    """Build default mapping payload for the selected manual input type."""
    return {
        "cas": input_type if input_type == "casId" else None,
        "smiles": input_type if input_type == "SMILES" else None,
        "name_columns": [],
        "formula": None,
    }
