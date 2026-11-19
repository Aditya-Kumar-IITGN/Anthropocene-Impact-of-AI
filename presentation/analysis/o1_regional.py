"""O1 figure: where data-centre electricity is used (IEA 2024) and the carbon intensity of those grids (Ember 2024).

Run from presentation_slides/:  /Users/aryan/miniforge3/envs/geo/bin/python -I analysis/o1_regional.py
Inputs:  data/raw/ember/release_generation_yearly_global.csv (Ember yearly data, downloaded 12 Nov 2026 from
         files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv)
Output:  figs/o1_regional_carbon.pdf
Replaces Aditya's PNG, whose EU value (179 g/kWh) did not match Ember (EU 2024 = 212).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from style import *                                   # noqa: F401,F403

import pandas as pd

# IEA (2025) Energy and AI, executive summary: 415 TWh in 2024; US 45%, China 25%, Europe 15% (rest = remainder)
IEA = [("United States", 45), ("China", 25), ("Europe", 15), ("Rest of world", 15)]

e = pd.read_csv("data/raw/ember/release_generation_yearly_global.csv",
                usecols=["Area", "Year", "Electricity source", "Emissions intensity (gCO2e/kWh)"])
e = e[(e.Year == 2024) & (e["Electricity source"] == "Total generation")].set_index("Area")
gi = [("China", "China"), ("United States", "United States"), ("EU-27", "EU")]
vals = {lab: e.loc[area, "Emissions intensity (gCO2e/kWh)"] for lab, area in gi}
world = e.loc["World", "Emissions intensity (gCO2e/kWh)"]
print("Ember 2024 gCO2e/kWh:", {k: round(v) for k, v in vals.items()}, "world", round(world))

C = {"United States": PHASE["ai"], "China": "#B5442E", "Europe": "#3C7A5A", "EU-27": "#3C7A5A", "Rest of world": "#B9BEC4"}
fig, (a, b) = plt.subplots(1, 2, figsize=(5.5, 1.75), gridspec_kw={"wspace": 0.55})
for i, (lab, v) in enumerate(IEA):
    a.barh(i, v, color=C[lab], height=0.62)
    a.text(v + 1, i, f"{v}%", va="center", fontsize=7, color=INK, fontweight="bold")
a.set_yticks(range(len(IEA)), [l for l, _ in IEA], fontsize=7); a.invert_yaxis()
a.set_xlim(0, 55); a.set_xticks([0, 20, 40], ["0", "20", "40%"])
a.set_title("Share of data-centre electricity, 2024 (IEA)", fontsize=7, loc="left", pad=3)
for i, (lab, _) in enumerate(gi):
    v = vals[lab]
    b.barh(i, v, color=C[lab], height=0.62)
    b.text(v + 8, i, f"{v:.0f}", va="center", fontsize=7, color=INK, fontweight="bold")
b.axvline(world, color=INK, lw=0.7, ls=(0, (2, 1.5)))
b.text(world, -0.6, f"world {world:.0f}", fontsize=6.2, ha="center", va="bottom", color=INK)
b.set_yticks(range(len(gi)), [l for l, _ in gi], fontsize=7); b.invert_yaxis()
b.set_ylim(len(gi) - 0.5, -0.95)
b.set_xlim(0, 680); b.set_xticks([0, 200, 400, 600])
b.set_title("Grid carbon intensity, 2024 (gCO2e/kWh, Ember)", fontsize=7, loc="left", pad=3)
for ax in (a, b):
    ax.tick_params(axis="y", length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
fig.savefig(f"{FIGS}/o1_regional_carbon.pdf")
print("wrote figs/o1_regional_carbon.pdf")
