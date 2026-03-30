# FCC Chemical Grouping Tool

This web app helps you classify chemicals for food-contact assessment in three steps:

1. Identify whether each chemical appears in food-contact databases.
2. Add FCCprio prioritization tiers where available.
3. Group chemicals by structural patterns (for example, groups of concern).

It is designed for practical screening workflows: paste or upload a list of chemicals, run one analysis, then filter and export results.

## Quick Start

### 1) Install dependencies

```bash
cd "FCCgroup app"
pip install -r requirements.txt
```

### 2) (Optional) Prepare SMILES lookup data

If you want robust SMILES matching, run this once (or whenever the FCC database is updated):

```bash
python scripts/preprocess_smiles_lookup.py
```

This generates `assets/smiles_lookup.tsv`.

### 3) Run the app

```bash
streamlit run app.py
```

Open the URL shown in your terminal (usually `http://localhost:8501`).

## What You Do In The App

The interface follows a clear 3-step flow.

### Step 1: Add input data

Choose one input path:

- Manual Entry: paste one identifier per line.
- File Upload: upload Excel/CSV and map your columns.

You can work with either:

- CAS numbers (for example `50-00-0`)
- SMILES strings (for example `C=O`)

When to choose each:

- Use CAS when you already have CAS IDs and want direct lookup.
- Use SMILES when your source data is structure-based.

### Step 2: Start analysis

Click **Start Analysis**. The app runs:

1. FCC identification using FCCdb and FCCmigex references.
2. FCCprio tier enrichment (when available).
3. Structural grouping with SMARTS-based pattern detection.

You will see progress updates while this runs.

### Step 3: Explore and export results

The app shows:

- A summary dashboard.
- A detailed table with filters.
- Download buttons for CSV and Excel.

You can filter by FCC status, FCCprio tier, and groups of concern.

## Understanding The Output

### Summary cards

- Total Chemicals: number of rows analyzed.
- Valid SMILES: rows with usable structure representation.
- Food Contact: rows with food-contact status assigned.
- FCCprio Tier: rows with a tier available.
- With Groups: rows with at least one detected group of concern.

### Main result columns

- CAS RN: chemical identifier.
- SMILES: structure notation.
- Chemical names: available names from the matched data.
- Formula: molecular formula when available.
- is Food Contact Chemical: Yes/No based on database matching.
- Tier of FCCprio: priority tier when available.
- Groups of concern: structural groups detected by the pipeline.

Practical interpretation tip:
If a chemical is marked as food-contact, has a high-priority tier, and falls into groups of concern, it is a strong candidate for deeper review.

## Key Terms (Plain Language)

- CAS number: unique global ID for a chemical.
- SMILES: text representation of chemical structure.
- Canonical SMILES: standardized SMILES used for reliable matching.
- FCC: Food Contact Chemical.
- FCCdb: database of chemicals used in food-contact materials.
- FCCmigex: database of chemicals found migrating from food-contact materials.
- FCCprio: prioritization system with concern tiers.
- SMARTS pattern: rule used to detect structural motifs in molecules.
- Read-across: using similarity to other chemicals to support hazard assessment.

## Data Sources

This app integrates Food Packaging Forum resources:

- FCCdb
- FCCmigex
- FCCprio
- FCCgroup

References:

1. FCCdb paper
https://www.sciencedirect.com/science/article/pii/S0160412020321802

2. FCCmigex paper
https://doi.org/10.1080/10408398.2022.2067828

3. FCCprio dataset
https://doi.org/10.5281/zenodo.14881617

4. FCCgroup package (PyPI)
https://pypi.org/project/fccgroup/

## Troubleshooting

- No results shown:
Check identifier format and ensure your input column mapping is correct.

- Missing FCCprio tier:
Not every matched chemical has tier data.

- SMILES matching seems weak:
Run `python scripts/preprocess_smiles_lookup.py` to refresh the lookup table.

- Errors reading upload files:
Use `.xlsx`, `.xls`, or `.csv` and verify the selected header row.

## For Developers (Short Notes)

- Main app entry point: `app.py`.
- UI logic is split in `app_modules/` (input, processing, results, sidebar, workflow).
- Default analysis uses SMARTS grouping; additional methods can be enabled in the sidebar.
- Run from repository root so relative `assets/` paths resolve correctly.

## Citation

If you use this tool in research outputs, cite the tool name and the FCCdb/FCCmigex/FCCprio references above.
