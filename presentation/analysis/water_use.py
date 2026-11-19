"""Step 4 of O2: water-use range for the tracked AI data centres, today and planned 2030.

Run from presentation_slides/:  /Users/aryan/miniforge3/envs/geo/bin/python analysis/water_use.py
Needs data/processed/sites_water.csv (water_stress.py).
Outputs: data/processed/water_use.csv, water_use_summary.csv, figs/o2c_water_use.pdf

  E_fac    = facility MW × load factor × 8,760 h
  E_IT     = E_fac / PUE
  direct   = E_IT × WUE           (on-site cooling, consumed)
  indirect = E_fac × WI_grid      (water consumed generating the electricity)

Parameter ranges are from de Vries-Gao (2026, Patterns 7:101430), which compiles IEA, LBNL and
company figures. The load factor is OUR assumption (AI clusters run near-continuously); it is
stated on the slide.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from style import *                                   # noqa: F401,F403

import numpy as np
import pandas as pd

P = "data/processed"
L_PER_GALLON = 3.78541

from water_params import SCENARIOS          # parameter ranges + sources

s = pd.read_csv(f"{P}/sites_water.csv")
s["mw_now"] = s.current_mw.fillna(0)
s["mw_2030"] = s.planned_2030_mw.fillna(s.current_mw).fillna(0)
s["stressed"] = s.bws_cat >= 3

rows = []
for when, mw in [("today", "mw_now"), ("2030", "mw_2030")]:
    for sc, p in SCENARIOS.items():
        e_fac = s[mw] * p["lf"] * 8760 * 1e3                   # kWh
        e_it = e_fac / p["pue"]
        direct = e_it * p["wue"] / 1e9                         # billion L
        indirect = e_fac * p["wi"] / 1e9
        s[f"direct_{when}_{sc}"] = direct
        s[f"indirect_{when}_{sc}"] = indirect
        rows.append({"when": when, "scenario": sc, "mw": s[mw].sum(),
                     "e_fac_twh": e_fac.sum() / 1e9,
                     "direct_bnL": direct.sum(), "indirect_bnL": indirect.sum(),
                     "total_bnL": direct.sum() + indirect.sum(),
                     "direct_stressed_bnL": direct[s.stressed].sum(),
                     "direct_stressed_share": direct[s.stressed].sum() / direct.sum()})
summary = pd.DataFrame(rows)
summary.to_csv(f"{P}/water_use_summary.csv", index=False)
s.to_csv(f"{P}/water_use.csv", index=False)

# Check against the sites that report water use in Epoch (basis of the figure not stated)
t = pd.read_csv("data/raw/epoch/data_center_timelines.csv")
t["mgd"] = pd.to_numeric(t["Water use (MGD)"], errors="coerce")
t["mw"] = pd.to_numeric(t["Power (MW)"], errors="coerce")
rep = t[(t.mgd > 0) & (t.mw > 0)].sort_values("Date").groupby("Data center").tail(1).copy()
rep["L_per_kWh_fac_at_lf0.8"] = rep.mgd * 1e6 * L_PER_GALLON * 365 / (rep.mw * 0.8 * 8760 * 1e3)

pd.set_option("display.width", 160)
print(summary.round(2).to_string(index=False))
print("\nReported non-zero water use in Epoch (implied L per facility kWh at 80% load):")
print(rep[["Data center", "Date", "mw", "mgd", "L_per_kWh_fac_at_lf0.8"]].round(3).to_string(index=False))
lo, hi = [SCENARIOS[k]["wue"] / SCENARIOS[k]["pue"] for k in ("low", "high")]
print(f"our direct range per facility kWh: {lo:.2f}-{hi:.2f} L/kWh")


# ---------------------------------------------------------------- Fig O2c
g = summary.set_index(["when", "scenario"])
items = [("Direct, today", "today", "direct_bnL"),
         ("Direct, 2030 plan", "2030", "direct_bnL"),
         ("Indirect, today", "today", "indirect_bnL"),
         ("Indirect, 2030 plan", "2030", "indirect_bnL")]

fig, ax = plt.subplots(figsize=(3.05, 2.25))
for i, (label, when, col) in enumerate(items):
    lo_v, hi_v = g.loc[(when, "low"), col], g.loc[(when, "high"), col]
    c = SLATE if when == "today" else PHASE["ai"]
    ax.plot([lo_v, hi_v], [i, i], color=c, lw=7, solid_capstyle="butt", alpha=0.9)
    ax.text(hi_v * 1.08, i, f"{lo_v:,.0f}–{hi_v:,.0f}", va="center", fontsize=7.2, color=c,
            fontweight="bold")
    if col == "direct_bnL":
        st = g.loc[(when, "high"), "direct_stressed_share"]
        ax.text(lo_v, i + 0.38, f"{st:.0%} of it in stressed basins", va="center",
                ha="left", fontsize=6.2, color=MUTED)
# Benchmark: de Vries-Gao (2026), all AI systems worldwide, 2025, direct + indirect
ax.plot([312.5, 764.6], [4.2, 4.2], color="#B9BEC4", lw=7, solid_capstyle="butt")   # benchmark: grey, not gold
ax.text(764.6 * 1.08, 4.2, "312–765", va="center", fontsize=7.2, color=INK, fontweight="bold")
ax.set_yticks(list(range(4)) + [4.2],
              [it[0] for it in items] + ["All AI, 2025\n(de Vries-Gao)"], fontsize=7.2)
ax.set_xscale("log")
ax.set_xlim(20, 6000)
ax.set_xticks([10, 100, 1000], ["10", "100", "1,000"])
ax.minorticks_off()
ax.invert_yaxis()
ax.tick_params(axis="y", length=0)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_xlabel("Billion litres a year (log scale), low–high range", fontsize=7)
fig.savefig(f"{FIGS}/o2c_water_use.pdf")
print("wrote figs/o2c_water_use.pdf")
