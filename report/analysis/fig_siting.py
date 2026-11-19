"""Siting figure for Section 4.3 (why Visakhapatnam?): column width.

Run:  /Users/aryan/miniforge3/envs/geo/bin/python -I report/analysis/fig_siting.py
Inputs (read-only): presentation/data/processed/sites_water.csv (96 Epoch sites with their Aqueduct class)
                    presentation/analysis/water_params.py (same PUE/WUE/grid ranges as Section 3, method 3)
Outputs: report/figs/o2_siting.pdf, report/data/o2_siting_airwater.csv

(a) Where Visakhapatnam's basin class sits among the basins of the 96 tracked sites, weighted by planned 2030 MW.
    The hub is not in the Epoch data; its class (medium-high, 20-40%, 0 of 12 months over supply) is the deck's
    Aqueduct check at 17.906 N, 83.329 E (claims.csv row Case2).
(b) Water for a 1 GW hub with the Section 3 water model, for two cooling designs. Air cooling removes on-site
    (direct) water but, by Google's own figure, needs about 10% more energy on average, and about twice that on
    a hot day; we test +10% and +20%. Indirect water scales with the energy drawn. US-derived grid factors.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, os.path.join(FINAL, "presentation", "analysis"))
from water_params import SCENARIOS  # noqa: E402

# ------------------------------------------------------------------ (a) basin class of the tracked sites
s = pd.read_csv(os.path.join(PROC, "sites_water.csv"))
tot = s.planned_2030_mw.sum()
share = (s.groupby("bws_cat").planned_2030_mw.sum() / tot * 100).reindex([-1, 0, 1, 2, 3, 4])
lower = share.loc[[-1, 0, 1]].sum()
same = share.loc[2]
higher = share.loc[[3, 4]].sum()
print(f"planned MW in basins: lower than medium-high {lower:.1f}%, same {same:.1f}%, higher {higher:.1f}%")

# ------------------------------------------------------------------ (b) 1 GW hub, two cooling designs
MW, CITY_SUPPLY, CITY_NEED = 1000, 410, 480
rows = []
for sc, p in SCENARIOS.items():
    e_fac = MW * p["lf"] * 8760 * 1e3                       # kWh a year
    direct = e_fac / p["pue"] * p["wue"] / 365 / 1e6         # million L a day, if wet-cooled
    indirect = e_fac * p["wi"] / 365 / 1e6
    for pen in (0.10, 0.20):
        ind_air = indirect * (1 + pen)
        rows.append(dict(case=sc, energy_penalty_air=pen, direct_wet_ML_d=direct, indirect_wet_ML_d=indirect,
                         indirect_air_ML_d=ind_air, total_wet_ML_d=direct + indirect,
                         net_saving_air_ML_d=direct + indirect - ind_air,
                         direct_pct_city_supply=100 * direct / CITY_SUPPLY))
out = pd.DataFrame(rows).round(2)
out.to_csv(os.path.join(DATA, "o2_siting_airwater.csv"), index=False)
print(out.to_string())
lo, hi = SCENARIOS["low"], SCENARIOS["high"]
g = out.set_index(["case", "energy_penalty_air"])

fig, (a, b) = plt.subplots(2, 1, figsize=(COL, 3.45), gridspec_kw={"height_ratios": [1.0, 0.95], "hspace": 0.62})
# panel (a)
labels = [AQUEDUCT_LABEL[k] for k in share.index]
for i, k in enumerate(share.index):
    a.barh(i, share.loc[k], color=AQUEDUCT[k], edgecolor=MUTED, linewidth=0.3, height=0.72)
    a.text(share.loc[k] + 0.7, i, f"{share.loc[k]:.0f}%", va="center", fontsize=6.4, color=NAVY, fontweight="bold")
a.set_yticks(range(len(labels)), labels)
a.invert_yaxis()
a.set_xlim(0, 44)
a.set_xlabel("Share of planned 2030 MW of the 96 tracked sites (%)")
yv = list(share.index).index(2)
a.annotate("Visakhapatnam hub\n(Aqueduct check)", xy=(share.loc[2] + 5.2, yv), xytext=(36.5, yv - 0.78),
           fontsize=6.2, color=RED, ha="center", va="center", fontweight="bold",
           arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.7, shrinkA=0, shrinkB=1))
a.text(43.5, 4.15, f"basins less stressed: {lower:.0f}%\nsame class: {same:.0f}%\nmore stressed: {higher:.0f}%",
       fontsize=6.0, color=INK, ha="right", va="center", linespacing=1.25)
a.set_title("(a) Basin stress of the hub against the tracked sites", loc="left", fontsize=7, fontweight="bold")
bar_axes(a)
# panel (b)
items = [("Wet-cooled:\non-site cooling", g.loc[("low", 0.10), "direct_wet_ML_d"], g.loc[("high", 0.10), "direct_wet_ML_d"], SKY),
         ("Wet-cooled:\nat power plants", g.loc[("low", 0.10), "indirect_wet_ML_d"], g.loc[("high", 0.10), "indirect_wet_ML_d"], NAVY),
         ("Air-cooled, +10\u201320%\nenergy: at power plants", g.loc[("low", 0.10), "indirect_air_ML_d"],
          g.loc[("high", 0.20), "indirect_air_ML_d"], PHASE["ai"])]
for i, (lab, l, h, c) in enumerate(items):
    b.plot([l, h], [i, i], color=c, lw=6, solid_capstyle="butt")
    b.text(h + 3, i, f"{l:.0f}\u2013{h:.0f}", va="center", fontsize=6.6, color=NAVY, fontweight="bold")
b.plot([CITY_NEED - CITY_SUPPLY] * 2, [-0.55, 2.55], color=RED, lw=0.8, ls=(0, (2, 1.5)))
b.text(CITY_NEED - CITY_SUPPLY + 3, 2.75, "city shortfall today: 70", fontsize=6.0, color=RED, va="center")
b.set_yticks(range(len(items)), [i[0] for i in items])
b.invert_yaxis()
b.set_ylim(3.0, -0.6)
b.set_xlim(0, 150)
b.set_xlabel("Water consumed by a 1 GW hub (million litres a day)")
b.set_title("(b) What the cooling choice changes", loc="left", fontsize=7, fontweight="bold")
bar_axes(b)
save(fig, "o2_siting.pdf")
print("wrote figs/o2_siting.pdf and data/o2_siting_airwater.csv")
