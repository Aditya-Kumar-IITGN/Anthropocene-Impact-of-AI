#!/bin/zsh
# Rebuild the report.  Usage (from anywhere):
#   zsh report/build.sh          figures + tables + PDF (figures whose large raw data are missing are skipped)
#   zsh report/build.sh tables   tables + PDF
#   zsh report/build.sh pdf      PDF only (needs Tectonic only)
# Python: set PY to your interpreter (needs pandas, numpy, scipy, matplotlib, geopandas, rasterio, pillow).
cd "$(dirname "$0")"
PY=${PY:-/Users/aryan/miniforge3/envs/geo/bin/python}
[[ -x "$PY" ]] || PY=$(command -v python3)
run() { echo "== $1"; $PY -I "analysis/$1" || echo "   (skipped or failed: $1)"; }
if [[ "$1" == "" ]]; then
  run d2_growth_diagnostics.py      # D2 diagnostics  -> data/d2_*.csv, figs/d2_diagnostics.pdf
  run d3_country_table.py           # D3 country table -> data/d3_*.csv, figs/o3_lorenz.pdf   (needs GHSL)
  run fig_o1.py                     # figs/o1_regional_carbon.pdf
  run fig_o2.py                     # figs/o2_*.pdf  (case locator needs Aqueduct)
  run fig_d1_atlas.py               # figs/d1_atlas.pdf   (needs GHSL + Aqueduct)
  run fig_siting.py                 # figs/o2_siting.pdf, data/o2_siting_airwater.csv (Section 4.3; uses presentation/data/processed)
fi
if [[ "$1" == "" || "$1" == "tables" ]]; then
  run make_tables.py                # tables/*.tex from the CSVs
fi
tectonic -X compile --synctex --keep-logs main.tex || exit 1
echo "Overfull boxes: $(grep -c Overfull main.log)   $(pdfinfo main.pdf 2>/dev/null | grep Pages)"
