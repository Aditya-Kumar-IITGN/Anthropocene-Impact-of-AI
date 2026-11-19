"""O1 figure (column width): where data-centre electricity is used (IEA 2024) and the carbon intensity of those grids
(Ember 2024). Re-make of presentation/analysis/o1_regional.py for the printed report.

Run:  /Users/aryan/miniforge3/envs/geo/bin/python -I report/analysis/fig_o1.py
Inputs (read-only): ../presentation_slides/data/raw/ember/release_generation_yearly_global.csv
                    (Ember yearly electricity data, downloaded 12 Nov 2026)
Output: report/figs/o1_regional_carbon.pdf

IEA shares are typed from IEA (2025) Energy and AI, executive summary (claims.csv row "S1/O1"): US 45%, China 25%,
Europe 15%; rest of world is the remainder. EU-27 stands in for the IEA's "Europe" (stated in the caption).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402

import pandas as pd  # noqa: E402

IEA = [("United States", 45), ("China", 25), ("Europe", 15), ("Rest of world", 15)]
e = pd.read_csv(EMBER_CSV, usecols=["Area", "Year", "Electricity source", "Emissions intensity (gCO2e/kWh)"])
e = e[(e.Year == 2024) & (e["Electricity source"] == "Total generation")].set_index("Area")
gi = [("China", "China"), ("United States", "United States"), ("EU-27", "EU")]
vals = {lab: e.loc[area, "Emissions intensity (gCO2e/kWh)"] for lab, area in gi}
world = e.loc["World", "Emissions intensity (gCO2e/kWh)"]
print("Ember 2024 gCO2e/kWh:", {k: round(v) for k, v in vals.items()}, "world", round(world),
      "| China/EU ratio", round(vals["China"] / vals["EU-27"], 2))

C = {"United States": NAVY, "China": RED, "Europe": GOLD, "EU-27": GOLD, "Rest of world": GREY}
fig, (a, b) = plt.subplots(2, 1, figsize=(COL, 2.45), gridspec_kw={"hspace": 0.75, "height_ratios": [4, 3]})
for i, (lab, v) in enumerate(IEA):
    a.barh(i, v, color=C[lab], height=0.66)
    a.text(v + 1, i, f"{v}%", va="center", fontsize=6.8, color=INK, fontweight="bold")
a.set_yticks(range(len(IEA)), [lab for lab, _ in IEA])
a.invert_yaxis()
a.set_xlim(0, 55)
a.set_xticks([0, 10, 20, 30, 40, 50], ["0", "10", "20", "30", "40", "50%"])
a.set_title("(a) Share of world data-centre electricity, 2024 (IEA; 415 TWh)", loc="left", pad=3)
for i, (lab, _) in enumerate(gi):
    v = vals[lab]
    b.barh(i, v, color=C[lab], height=0.66)
    b.text(v + 8, i, f"{v:.0f}", va="center", fontsize=6.8, color=INK, fontweight="bold")
b.axvline(world, color=INK, lw=0.6, ls=(0, (2, 1.5)))
b.text(world + 8, 2.0, f"world {world:.0f}", fontsize=6.2, ha="left", va="center", color=INK)
b.set_yticks(range(len(gi)), [lab for lab, _ in gi])
b.invert_yaxis()
b.set_xlim(0, 680)
b.set_xticks([0, 200, 400, 600])
b.set_title("(b) Grid carbon intensity, 2024 (gCO$_2$e per kWh; Ember)", loc="left", pad=3)
for ax in (a, b):
    bar_axes(ax)
save(fig, "o1_regional_carbon.pdf")
