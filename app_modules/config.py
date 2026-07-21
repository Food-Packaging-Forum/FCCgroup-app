"""UI and mapping configuration values for the app."""

from typing import Dict

MAPPING_FIELD_LABELS = {
    "cas": "CAS",
    "smiles": "SMILES",
    "name_columns": "Name columns",
    "formula": "Formula",
}

CAS_COLUMN_INPUT = "casId"
SMILES_COLUMN_INPUT = "SMILES"
CHEMICAL_NAMES_COLUMN_INPUT = "column_names"
FORMULA_COLUMN_INPUT = "formula"

CAS_COLUMN = "CAS RN"
SMILES_COLUMN = "SMILES"
CHEMICAL_NAMES_COLUMN = "Chemical names"
FORMULA_COLUMN = "Formula"
FOOD_CONTACT_CHEMICAL_COLUMN = "is Food Contact Chemical"
HAZARD_COLUMN = "Hazard"
TIER_OF_FCCPRIO_COLUMN = "Tier of FCCprio"
GROUPS_OF_CONCERN_COLUMN = "Priority groups"

DISPLAY_RESULT_COLUMNS = [
    CAS_COLUMN,
    SMILES_COLUMN,
    CHEMICAL_NAMES_COLUMN,
    FORMULA_COLUMN,
    FOOD_CONTACT_CHEMICAL_COLUMN,
    TIER_OF_FCCPRIO_COLUMN,
    HAZARD_COLUMN,
    GROUPS_OF_CONCERN_COLUMN,
]

RENAME_DICT = {
    CAS_COLUMN_INPUT: CAS_COLUMN, 
    SMILES_COLUMN_INPUT: SMILES_COLUMN, 
    CHEMICAL_NAMES_COLUMN_INPUT: CHEMICAL_NAMES_COLUMN, 
    FORMULA_COLUMN_INPUT: FORMULA_COLUMN,
}

def build_default_mapping_payload(input_type: str) -> Dict[str, object]:
    """Build default mapping payload for the selected manual input type."""
    return {
        "cas": input_type if input_type == CAS_COLUMN_INPUT else None,
        "smiles": input_type if input_type == SMILES_COLUMN_INPUT else None,
        "name_columns": [],
        "formula": None,
    }
