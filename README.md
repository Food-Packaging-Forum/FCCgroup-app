<h1 align="center">FCCgroup</h1>

<p align="center">
  <b>Identify, prioritize, and group Food Contact Chemicals (FCCs)</b><br>
  A Streamlit web app by the <a href="https://www.foodpackagingforum.org/">Food Packaging Forum</a>
</p>

<p align="center">
  <a href="https://doi.org/10.1021/acs.est.5c15186"><img alt="Paper: Environ. Sci. Technol. 10.1021/acs.est.5c15186" src="https://img.shields.io/badge/Paper-10.1021%2Facs.est.5c15186-b31b1b"></a>
  <a href="https://pypi.org/project/fccgroup/"><img alt="fccgroup on PyPI" src="https://img.shields.io/pypi/v/fccgroup?label=fccgroup"></a>
  <a href="LICENSE"><img alt="License: CC BY-SA 4.0" src="https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey"></a>
  <img alt="Python 3.11" src="https://img.shields.io/badge/Python-3.11-3776ab">
  <img alt="Built with Streamlit" src="https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b">
</p>

---

## What this app does

Paste or upload a list of chemicals, run one analysis, and get back
whether each chemical is a known food contact chemical, its FCCprio priority tier, its hazard
flags, and the structural priority groups it belongs to. Then filter the table and export it.

The analysis combines two things:

1. **Lookup enrichment** against a bundled extract of the Food Packaging Forum's FCC universe
   (`assets/FCCuniverse.xlsx`), which supplies FCC status, FCCprio tier, and hazard flags.
2. **Structural grouping** via the [`fccgroup`](https://pypi.org/project/fccgroup/) Python
   package, which assigns priority groups from SMARTS substructure patterns (and, in admin
   mode, from curated lists and identifier regex rules).

The app is a thin UI over `fccgroup`; the chemistry lives in that package.

## Using the app

The app has two pages, switched with the buttons under the title: **🔬 Analysis** (the
three-step workflow) and **📖 How to use** (in-app explanation of each step, the
data sources, and common use cases).

### Step 1: Add input data

Two input modes:

**Manual Entry** lets you pick `CAS` or `SMILES` and paste one identifier per line.
Duplicates are removed automatically. **📝 Try Sample Data** fills in a working example for either type.

**File Upload** accepts `.xlsx`, `.xls`, and `.csv`. Choose the header row and (for Excel)
the sheet, preview the first rows, then map your columns:

| Mapping field | Notes |
|---|---|
| CAS | Required by the LISTS method |
| SMILES | Required by the SMARTS method |
| Name columns | One or more; required by the REGEX method |
| Formula | Optional metadata |

Only mapped columns are carried into the analysis. An **Input Summary** box confirms how
many rows are ready and previews the first few.

> Input is capped at **1,000 rows** per analysis for performance reasons.

### Step 2: Analyze chemicals

**🚀 Start Analysis** stays disabled until you have valid input and at least one grouping
method. The run reports three stages (initializing → processing rows → finalizing) and
reuses a cached grouper when the input, mapping, and methods are unchanged.

### Step 3: Explore results

**Summary dashboard** with five cards: Total Chemicals, Valid SMILES, Food Contact,
FCCprio Tier, and With Priority Groups (each as *matched / total*).

**Results table** columns:

| Column | Meaning |
|---|---|
| `CAS RN` | CAS Registry Number |
| `SMILES` | Structure notation as supplied or resolved |
| `Chemical names` | Names carried through from the input mapping |
| `Formula` | Molecular formula, when mapped |
| `is Food Contact Chemical` | Shown as tags: `FCCdb`, `FCCmigex`, both, or `Not an FCC` |
| `Tier of FCCprio` | `Tier 1` (highest priority) … `Tier 4`, or `NA` |
| `Hazard` | Comma-separated hazard flags, or `NA` |
| `Priority groups` | Structural groups detected by the grouping methods |

Hazard flags come from the FCC universe extract and cover CLP-style classifications
(`Carc. 1`, `Carc. 2`, `Muta. 1`, `Muta. 2`, `Repr. 1`, `Repr. 2`, `STOT-RE`) and
persistence / mobility / bioaccumulation / endocrine descriptors (`persistent`, `mobile`,
`bioaccumulative`, `endocrine disrupting`, plus their `potentially …` variants).

**Filters** (four selectors above the table):

- **Food Contact Chemical**: filter by FCC status.
- **Tier of FCCprio**: filter by tier.
- **Hazard**: selecting several flags requires *all* of them to be present.
- **Priority groups**: selecting several groups reveals an **OR / AND** toggle, matching
  *any* selected group or requiring *all* of them.

**Export**: choose the scope, then download:

- *Displayed results only*: exactly the rows and columns in the table, filters applied.
- *Whole dataset*: every analyzed chemical with all available columns, identifiers first,
  then the enrichment columns.

CSV and Excel are both available; **🔄 Clear Data** resets the session.

## How enrichment resolves a chemical

1. If a CAS column is present, look it up in the lookup table by normalized CAS, which sets
   FCC status, FCCprio tier, and hazard.
2. For rows still unresolved, canonicalize the SMILES with RDKit and look it up by canonical
   SMILES.
3. Anything still unmatched is reported as `Not an FCC`, with empty tier and hazard.

`Not an FCC` therefore means *not present in the bundled FCC universe extract*; it is not a
statement that the chemical is absent from food contact materials in general.

## Data sources

This app integrates Food Packaging Forum resources:

| Resource | What it is | Reference |
|---|---|---|
| **FCCdb** | Chemicals intentionally used in food contact materials | [Groh et al., *Environ. Int.*](https://www.sciencedirect.com/science/article/pii/S0160412020321802) |
| **FCCmigex** | Chemicals measured migrating from food contact articles | [Geueke et al., *Crit. Rev. Food Sci. Nutr.*](https://doi.org/10.1080/10408398.2022.2067828) |
| **FCCprio** | Prioritization tiers for FCCs | [Dataset on Zenodo](https://doi.org/10.5281/zenodo.14881617) · [Publication](https://doi.org/10.1021/acs.est.5c15186) |
| **FCCgroup** | Grouping engine used by this app | [PyPI](https://pypi.org/project/fccgroup/) · [Publication](https://doi.org/10.1021/acs.est.5c15186) |

## Glossary

- **CAS number**: unique global identifier for a chemical substance.
- **SMILES**: text representation of a molecular structure.
- **Canonical SMILES**: standardized SMILES used for reliable matching.
- **CX SMILES**: extended SMILES encoding enhanced stereochemistry, mixtures, and variable
  attachment points; expanded during preprocessing.
- **FCC**: Food Contact Chemical.
- **SMARTS pattern**: substructure query used to detect a structural motif.
- **Read-across**: inferring a property for one chemical from structurally similar ones.

## Troubleshooting

| Symptom | Fix |
|---|---|
| **Start Analysis** is disabled | You have no valid input, or (admin mode) no grouping method selected. |
| No FCC status / tier / hazard at all | `assets/smiles_lookup.tsv` is missing. Run `python scripts/preprocess_smiles_lookup.py`. |
| Missing tier for a matched chemical | Expected: only 1,222 of 15,159 entries carry an FCCprio tier. |
| SMILES matching seems weak | Regenerate the lookup table, and check that your SMILES parse in RDKit. |
| Error reading an uploaded file | Use `.xlsx`, `.xls`, or `.csv`, and verify the selected header row and sheet. |
| Assets or logo fail to load | Launch `streamlit run app.py` from the repository root. |

## For developers

### Developer quick start

```bash
# from the repository root
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown in your terminal (usually `http://localhost:8501`).

> **Run from the repository root.** All asset paths are relative (`assets/…`, `static/…`),
> so launching from elsewhere will break data loading and the logo.

#### Docker

```bash
docker build -t fccgroup-app .
docker run -p 8501:8501 fccgroup-app
```

#### Optional environment variables

Copy `.env.example` and set what you need:

| Variable | Effect |
|---|---|
| `IS_FCCGROUP_ADMIN` | `true` unlocks the **Grouping Configuration** panel (SMARTS / LISTS / REGEX selection). Regular users always run SMARTS only. |
| `COMPTOX_API_KEY` | Reserved for CompTox lookups in the underlying library. |

#### Regenerating the SMILES lookup table

`assets/smiles_lookup.tsv` is a generated file. It expands every SMILES in
`assets/FCCuniverse.xlsx` into all canonical forms (including CX SMILES enumeration) so
SMILES input can be matched reliably. Regenerate it whenever the FCC universe file changes:

```bash
python scripts/preprocess_smiles_lookup.py
```

If the file is missing, enrichment is skipped rather than crashing, but the FCC status,
tier, and hazard columns will come back empty.

#### Entry point

[`app.py`](app.py) holds the page config, the admin-only grouping
configuration panel, and the three-step orchestration.

| Module | Purpose |
|---|---|
| [`app_modules/input_section.py`](app_modules/input_section.py) | Step 1 UI: manual entry, file upload, column mapping, input summary |
| [`app_modules/processing.py`](app_modules/processing.py) | `run_grouping_pipeline()`: grouper caching, MultiIndex flattening, CAS/SMILES enrichment |
| [`app_modules/results_section.py`](app_modules/results_section.py) | Step 3 UI: summary cards, filters, table, export |
| [`app_modules/config.py`](app_modules/config.py) | Column-name constants, display order, default mapping payload |
| [`app_modules/state.py`](app_modules/state.py) | `initialize_session_state()`: every session-state key and default |
| [`app_modules/styles.py`](app_modules/styles.py) | Global CSS, page header and nav, footer, feedback buttons |
| [`app_modules/workflow.py`](app_modules/workflow.py) | The **How to use** page |
| [`scripts/preprocess_smiles_lookup.py`](scripts/preprocess_smiles_lookup.py) | Builds `assets/smiles_lookup.tsv` from `assets/FCCuniverse.xlsx` |

Conventions worth knowing:

- The grouper expects the CAS column to be named `casId` and the structure column `SMILES`
  (see `CAS_COLUMN_INPUT` / `SMILES_COLUMN_INPUT` in `config.py`); human-readable display
  names are applied afterwards via `RENAME_DICT`.
- Always canonicalize SMILES with `Chem.MolToSmiles(mol, canonical=True)` before comparing.
- `ChemicalGrouper` is cached with `@st.cache_resource` (it is not serializable); dataframes
  such as the lookup table use `@st.cache_data`. Cache invalidation goes through the
  content-aware `dataframe_signature()` and `mapping_signature()` helpers.
- `_flatten_results_columns()` turns `fccgroup`'s MultiIndex output into flat column names;
  duplicates get ` (2)`, ` (3)` suffixes.
- There are no automated tests or linters configured in this repository.

Bug reports and feature requests go through the
[issue templates](https://github.com/Food-Packaging-Forum/FCCgroup-app/issues/new/choose),
also reachable from the buttons in the app footer.

## Citation

If you use this tool in research outputs, please cite the accompanying paper:

> Wiesinger, H., Parkinson, L. V., Geueke, B., Anguera Sempere, A., Boucher, J., Cabane, E.,
> Scheringer, M., Muncke, M. (2026). Prioritizing and Grouping Food Contact Chemicals –
> From Chaos to Clarity. *Environmental Science & Technology*.
> DOI: [10.1021/acs.est.5c15186](https://doi.org/10.1021/acs.est.5c15186)

To cite the software itself:

<details>
<summary>BibTeX</summary>

```bibtex
@software{fccgroup_app,
  title     = {FCCgroup},
  author    = {Anguera Sempere, Albert and Wiesinger, Helene},
  publisher = {Food Packaging Forum Foundation},
  year      = {2026},
  license   = {CC-BY-SA-4.0},
  url       = {https://github.com/Food-Packaging-Forum/FCCgroup-app}
}
```

</details>

Machine-readable metadata lives in [`CITATION.cff`](CITATION.cff), which GitHub's *Cite this
repository* button reads directly.

Please also cite the underlying FCCdb, FCCmigex, and FCCprio references listed under
[Data sources](#data-sources) when you rely on those datasets.

## License

Licensed under [CC BY-SA 4.0](LICENSE).
© 2026 Food Packaging Forum, Albert Anguera Sempere, Helene Wiesinger.

This software is provided "as is", without warranties of any kind. See [`LICENSE`](LICENSE)
for the full disclaimer.
