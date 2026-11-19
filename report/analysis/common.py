"""Shared paths and figure style for the report figures.

Every script in report/analysis/ does `from common import *`.
Run any script from anywhere:  /Users/aryan/miniforge3/envs/geo/bin/python -I report/analysis/<script>.py

Reads (never writes): presentation/data/processed/ (per-site results from the deck) and raw data
(Aqueduct, GHSL, Epoch, Ember, OWID, Epoch models). Raw data are looked for, in order: $EH627_RAW, then
data_raw/ next to report/ (the team package), then ../presentation_slides/data/raw and ../proposal/data/raw
(Aryan's original layout).
Writes: report/figs/*.pdf and report/data/*.csv only.

Figures are drawn at their printed size (one column = 3.3 in, full width = 6.85 in) and included
in LaTeX at width=\\linewidth, so 7 pt here is 7 pt on the page.
"""
import glob
import os

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.dirname(HERE)                                   # final_report/report
FINAL = os.path.dirname(REPORT)                                  # final_report
PROJECT = os.path.dirname(FINAL)                                 # eh_627/project
PROC = os.path.join(FINAL, "presentation", "data", "processed")  # deck results (read-only)
if os.environ.get("EH627_RAW"):                                   # 1. explicit override
    RAW = PROPOSAL_RAW = os.environ["EH627_RAW"]
elif os.path.isdir(os.path.join(FINAL, "data_raw")):              # 2. team package: one data_raw/ folder
    RAW = PROPOSAL_RAW = os.path.join(FINAL, "data_raw")
else:                                                             # 3. original layout on Aryan's machine
    RAW = os.path.join(PROJECT, "presentation_slides", "data", "raw")
    PROPOSAL_RAW = os.path.join(PROJECT, "proposal", "data", "raw")
GDB = os.path.join(RAW, "aqueduct", "Aqueduct40_waterrisk_download_Y2023M07D05", "GDB", "Aq40_Y2023D07M05.gdb")
_ghsl = glob.glob(os.path.join(RAW, "ghsl", "GHS_POP_E2025*_30ss*.tif"))
GHSL = _ghsl[0] if _ghsl else os.path.join(RAW, "ghsl", "GHS_POP_E2025_GLOBE_R2023A_4326_30ss_V1_0.tif")


def need(*paths):
    """Stop a script with a clear message if a large raw dataset is missing (see README_TEAM.md)."""
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        raise SystemExit("missing raw data (see README_TEAM.md, 'Large datasets'):\n  " + "\n  ".join(missing))


FIGS = os.path.join(REPORT, "figs")
DATA = os.path.join(REPORT, "data")

COL, FULL = 3.3, 6.85                                            # printed widths, inches

for f in glob.glob(os.path.join(HERE, "fonts", "lmsans*.otf")) + glob.glob(
        os.path.expanduser("~/Library/Caches/TectonicProject.Tectonic/bundles/data/*/lmsans*.otf")):
    font_manager.fontManager.addfont(f)

# Report chrome (main.tex): navy. Data colours: the deck's phase colours, kept for continuity.
NAVY, INK, MUTED, GRID = "#12305E", "#1A1A1A", "#6E6E6E", "#D9D9D9"
PHASE = {"ga": "#8C4A2F", "cloud": "#7E8A96", "ai": "#2E5EAA"}
RED = "#A8322D"
GOLD, GREEN, SKY, GREY = "#B88A1E", "#3C7A5A", "#7FA7D9", "#C5CAD1"   # reference-PDF style accents
EMBER_CSV = os.path.join(RAW, "ember", "release_generation_yearly_global.csv")
EPOCH_TIMELINES = os.path.join(RAW, "epoch", "data_center_timelines.csv")


def bar_axes(ax):
    """Horizontal-bar look used throughout: no y ticks, no left/top/right spines."""
    ax.tick_params(axis="y", length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
AQUEDUCT = {0: "#FFFF99", 1: "#FFE600", 2: "#FF9900", 3: "#FF1900", 4: "#990000", -1: "#808080"}
AQUEDUCT_LABEL = {0: "Low", 1: "Low–medium", 2: "Medium–high", 3: "High", 4: "Extremely high",
                  -1: "Arid, low use"}

plt.rcParams.update({
    "font.family": "Latin Modern Sans", "font.size": 7,
    "mathtext.fontset": "custom", "mathtext.rm": "Latin Modern Sans",
    "pdf.fonttype": 42, "text.color": INK, "axes.labelcolor": INK, "axes.titlesize": 7,
    "xtick.color": INK, "ytick.color": INK, "axes.edgecolor": MUTED, "axes.linewidth": 0.5,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
    "legend.fontsize": 6.3, "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "savefig.dpi": 300,
})


def clean(ax, left=True):
    ax.spines[["top", "right"]].set_visible(False)
    if not left:
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)


def save(fig, name):
    fig.savefig(os.path.join(FIGS, name))
    plt.close(fig)
    print("wrote figs/" + name)
