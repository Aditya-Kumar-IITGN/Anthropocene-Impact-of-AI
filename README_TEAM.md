# EH627 final report: team package

Preliminary draft of the final report, with everything needed to edit it and rebuild it.
Start with **`report/main.pdf`** (the current draft) and **`report/STATUS.md`** (what is done, and the TODOs for
each of us).

## What is in here

| Path | What it is |
|---|---|
| `report/main.pdf` | The current draft (title page + 11 pages) |
| `report/STATUS.md` | Status per section and **the TODO list for each of us** |
| `report/main.tex` | Preamble, title page (fill in names/roll numbers at the top), section order |
| `report/sections/*.tex` | One file per section: edit only your own to avoid clashes |
| `report/refs.bib` | Bibliography (cite with `\citep{key}` or `\citet{key}`) |
| `report/figs/`, `report/tables/` | Generated figures and table bodies: do not edit by hand |
| `report/analysis/*.py` | Scripts that make every figure and table |
| `report/data/` | Results of those scripts; `claims_report.csv` logs every new number with its source |
| `presentation/` | The deck we presented (`main_v1.pdf`, `notes_v1.pdf`), its LaTeX, `context.md` (full project history), `data/claims.csv` (every number in the deck and its source), `data/processed/` (per-site results) |
| `reference/` | Format reference PDF, project plan, preliminary report, professor's outline, course plan, key papers |
| `data_raw/` | Raw data, except the two large datasets (see below) |
| `CLAUDE.md` | LaTeX build playbook (Tectonic, build loop, error cookbook) |

## Three ways to work on it

1. **Text only (easiest).** Edit `report/sections/*.tex` and rebuild the PDF:
   `zsh report/build.sh pdf`. Needs only [Tectonic](https://tectonic-typesetting.github.io)
   (`brew install tectonic`); it downloads LaTeX packages by itself on the first build.
2. **Overleaf.** Upload the `report/` folder and compile `main.tex` (pdfLaTeX, with BibTeX). Not tested there,
   but it uses only standard packages.
3. **Rebuild figures and tables.** Needs Python with pandas, numpy, scipy, matplotlib, geopandas, rasterio and
   pillow, e.g. `conda create -n geo -c conda-forge python=3.11 geopandas rasterio scipy matplotlib pillow`.
   Then `PY=$(which python) zsh report/build.sh` (all) or `... build.sh tables` (tables + PDF).

## Large datasets (not in the zip, about 1 GB)

Without them, `build.sh` skips three steps and keeps the existing outputs: the atlas (`figs/d1_atlas.pdf`), the
D3 country table and Lorenz curve, and the case-locator map. Everything else rebuilds. To rebuild those too,
download and unzip into `data_raw/` so these paths exist:

- **WRI Aqueduct 4.0**, "Aqueduct 4.0 Current and Future Global Maps Data" (file
  `aqueduct-4-0-water-risk-data.zip`, wri.org/data) →
  `data_raw/aqueduct/Aqueduct40_waterrisk_download_Y2023M07D05/GDB/Aq40_Y2023D07M05.gdb`
- **GHSL GHS-POP R2023A**, epoch 2025, WGS84, 30 arc-second (file `GHS_POP_E2025_GLOBE_R2023A_4326_30ss_V1_0.zip`,
  JRC Global Human Settlement Layer download page) →
  `data_raw/ghsl/GHS_POP_E2025_GLOBE_R2023A_4326_30ss_V1_0.tif`

Or ask Aryan for a copy. A different location works too: `export EH627_RAW=/path/to/raw`.

## Rules we agreed on

- Every number comes from `presentation/data/claims.csv`, `report/data/claims_report.csv` or a cited source. If you
  add a number, add a row to `claims_report.csv` (source, how you got it, verified or not).
- Keep the honesty decisions: the verdicts in Section 6 (partly confirmed / partly supported / supported as a
  framework), D2 "Partly complete", the "Changes from the plan" paragraph and the corrections paragraph in Section 5.
- Red `[TODO ...]` notes show while `\drafttrue` is set in `main.tex`; set `\draftfalse` for the version we submit.
- After any change: build, check `Overfull boxes: 0`, and look at every page of the PDF.
