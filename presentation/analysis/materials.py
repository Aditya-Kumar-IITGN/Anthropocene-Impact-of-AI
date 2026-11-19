"""Step 6 of O2: where the materials come from, where AI capacity is, where e-waste is handled.

Run from presentation_slides/:  /Users/aryan/miniforge3/envs/geo/bin/python analysis/materials.py
Inputs:  data/processed/materials.csv (USGS MCS 2026), ewaste_regions.csv (Global E-waste
         Monitor 2024), sites_water.csv (for the AI-capacity share)
Output:  figs/o2d_materials_ewaste.pdf
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from style import *                                   # noqa: F401,F403

import pandas as pd

P = "data/processed"
m = pd.read_csv(f"{P}/materials.csv")
e = pd.read_csv(f"{P}/ewaste_regions.csv")
s = pd.read_csv(f"{P}/sites_water.csv")
mw2030 = s.planned_2030_mw.fillna(s.current_mw).fillna(0)
us_share = 100 * mw2030[s.country == "United States"].sum() / mw2030.sum()
print(f"US share of planned 2030 AI MW: {us_share:.1f}%")

PRODUCER = {"China": "#B5442E", "DR Congo": "#6B4C9A", "Chile": "#3C7A5A", "United States": PHASE["ai"]}

fig, (a, b) = plt.subplots(1, 2, figsize=(5.5, 2.0), gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.75})

# ---- (a) top producer share of each material, vs the AI capacity it serves
labels = [f"{r.item} ({r.stage.replace(' production', '')})" for r in m.itertuples()]
labels.append("AI capacity (planned 2030 MW)")
vals = list(m.top_share_pct) + [us_share]
who = list(m.top_producer) + ["United States"]
y = range(len(vals))
a.barh(y, [100] * len(vals), color="#EEEEEE", height=0.62)
a.barh(y, vals, color=[PRODUCER[w] for w in who], height=0.62)
for i, (v, w) in enumerate(zip(vals, who)):
    inside = v > 40
    a.text(v - 2 if inside else v + 2, i, f"{w} {v:.0f}%", va="center",
           ha="right" if inside else "left", fontsize=6.2, fontweight="bold",
           color="white" if inside else PRODUCER[w])
a.axhline(len(vals) - 1.5, color=MUTED, lw=0.5, ls=(0, (2, 2)))
a.set_yticks(list(y), labels, fontsize=6.4)
a.invert_yaxis()
a.set_xlim(0, 100); a.set_xticks([])
a.tick_params(axis="y", length=0)
a.spines[["top", "right", "bottom", "left"]].set_visible(False)
a.set_title("Largest producer's share of world supply, 2025", fontsize=6.8, loc="left", pad=3)

# ---- (b) e-waste generated vs formally collected, by region
e = e.sort_values("generated_kg_per_capita")
yy = range(len(e))
collected = e.generated_kg_per_capita * e.formally_collected_pct / 100
b.barh(yy, e.generated_kg_per_capita, color="#C9CDD2", height=0.62, label="Generated")
b.barh(yy, collected, color=SLATE, height=0.62, label="Formally collected")
for i, r in enumerate(e.itertuples()):
    b.text(r.generated_kg_per_capita + 0.4, i, f"{r.formally_collected_pct:g}% collected",
           va="center", fontsize=6, color=INK)
b.set_yticks(list(yy), e.region, fontsize=6.4)
b.set_xlim(0, 27); b.set_xticks([0, 10, 20])
b.tick_params(axis="y", length=0)
b.spines[["top", "right", "left"]].set_visible(False)
b.set_xlabel("kg per person, 2022", fontsize=6.4)
b.set_title("E-waste generated vs formally collected", fontsize=6.8, loc="left", pad=3)
b.legend(loc="lower right", frameon=False, fontsize=5.8, handlelength=0.9, borderaxespad=0)

fig.savefig(f"{FIGS}/o2d_materials_ewaste.pdf")
print("wrote figs/o2d_materials_ewaste.pdf")
