"""Shared figure style: the deck's font (Latin Modern Sans, from Tectonic's cache) and colours.

Every figure script does `from style import *` and sizes figures to their slide slot:
16:9 text width ≈ 5.5 in; the content area under the title bar is ≈ 2.4 in tall.
"""
import glob
import os

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for f in glob.glob(os.path.expanduser(
        "~/Library/Caches/TectonicProject.Tectonic/bundles/data/*/lmsans*.otf")):
    font_manager.fontManager.addfont(f)

# Deck chrome (beamerthemegotham.sty)
SLATE, GOLD, INK, MUTED = "#2D3E50", "#FFCC00", "#191919", "#7A7A7A"
# Phases (main.tex)
PHASE = {"ga": "#8C4A2F", "cloud": "#7E8A96", "ai": "#2E5EAA"}
# WRI Aqueduct 4.0 water-stress palette, by bws_cat (-1 = arid and low water use)
AQUEDUCT = {0: "#FFFF99", 1: "#FFE600", 2: "#FF9900", 3: "#FF1900", 4: "#990000", -1: "#808080"}
AQUEDUCT_LABEL = {0: "Low", 1: "Low–medium", 2: "Medium–high", 3: "High", 4: "Extremely high",
                  -1: "Arid, low use"}

plt.rcParams.update({
    "font.family": "Latin Modern Sans", "font.size": 7,
    "mathtext.fontset": "custom", "mathtext.rm": "Latin Modern Sans",
    "pdf.fonttype": 42, "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": INK, "axes.edgecolor": MUTED, "axes.linewidth": 0.5,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "savefig.dpi": 300,
})

FIGS = os.path.join(os.path.dirname(__file__), "..", "figs")
