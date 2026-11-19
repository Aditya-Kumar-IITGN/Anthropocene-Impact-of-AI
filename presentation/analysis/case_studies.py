"""Step 5 of O2: two case studies (Google Mesa, Arizona; Google-AdaniConneX Visakhapatnam, India).

Run from presentation_slides/:  /Users/aryan/miniforge3/envs/geo/bin/python analysis/case_studies.py
Outputs: figs/case_mesa.pdf, figs/case_vizag.pdf, printed numbers for the slides.

Reported facts (cited on the slides):
  Mesa supply: 53% Colorado River via the Central Arizona Project canal, 40% Salt and Verde rivers,
    7% groundwater (City of Mesa). The canal runs ~190 mi (≈306 km) from Lake Havasu to the
    Phoenix area (US Bureau of Reclamation). Google site approved to use up to 4 million US
    gallons a day (CNBC/NBC, June 2021, citing Bloomberg).
  Vizag: city receives ~410 million L/day against ~480 million L/day needed (The Federal,
    27 Oct 2026). 1 GW hub (Google, AdaniConneX, Airtel). Operational water use not disclosed in
    the environmental clearance (Mongabay India, 12 May 2026).
Our estimates use the same parameter ranges as water_use.py (de Vries-Gao 2026 + our load factor).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from style import *                                   # noqa: F401,F403

import pandas as pd
from water_params import SCENARIOS                     # same ranges as slide O2c

L_PER_GALLON = 3.78541
s = pd.read_csv("data/processed/sites_water.csv").set_index("name")

# ---------------------------------------------------------------- Mesa
m = s.loc["Google Mesa"]
mesa_lpd = 4e6 * L_PER_GALLON
print(f"Google Mesa: {m.current_mw:.0f} MW now, {m.planned_2030_mw:.0f} MW planned; "
      f"{m.bws_label}; months withdrawals > supply: {m.scarce_months:.0f}/12")
print(f"approved up to 4 M gal/day = {mesa_lpd / 1e6:.1f} million L/day = {mesa_lpd * 365 / 1e9:.1f} bn L/yr")

fig, ax = plt.subplots(figsize=(2.55, 0.95))
parts = [("Colorado River,\nvia ~300 km canal", 53, PHASE["ai"]),
         ("Salt and Verde\nrivers", 40, "#7FA7D9"),
         ("Ground-\nwater", 7, PHASE["ga"])]
left = 0
for label, v, c in parts:
    ax.barh(0, v, left=left, color=c, height=0.55)
    ax.text(left + v / 2, 0, f"{v}%", ha="center", va="center", color="white", fontsize=7.5,
            fontweight="bold")
    if v > 10:
        ax.text(left + v / 2, -0.52, label, ha="center", va="top", fontsize=6.2, color=INK,
                linespacing=0.95)
    else:
        ax.text(100, 0.42, label.replace("-\n", ""), ha="right", va="bottom", fontsize=6.2, color=INK)
    left += v
ax.set_xlim(0, 100); ax.set_ylim(-1.35, 0.75)
ax.set_axis_off()
ax.set_title("Where Mesa's water comes from", fontsize=7, loc="left", pad=2)
fig.savefig(f"{FIGS}/case_mesa.pdf")
plt.close(fig)

# ---------------------------------------------------------------- Visakhapatnam
supply, need, mw = 410, 480, 1000
indirect = {}
for sc, p in SCENARIOS.items():
    e_fac = mw * p["lf"] * 8760 * 1e3                    # kWh per year
    indirect[sc] = e_fac * p["wi"] / 365 / 1e6           # million L per day
print(f"\nVizag city: {supply} vs {need} million L/day -> gap {need - supply} ({(need - supply) / need:.0%} short)")
print(f"1 GW, air-cooled: indirect water at the power plants {indirect['low']:.0f}-{indirect['high']:.0f} million L/day"
      f" = {indirect['low'] / supply:.0%}-{indirect['high'] / supply:.0%} of the city's supply")

fig, ax = plt.subplots(figsize=(2.55, 1.25))
rows = [("City supply today", supply, supply, SLATE),
        ("City requirement", need, need, MUTED),
        ("1 GW hub: water at\npower plants (our range)", indirect["low"], indirect["high"], PHASE["ai"])]
for i, (label, lo, hi, c) in enumerate(rows):
    if lo == hi:
        ax.barh(i, hi, color=c, height=0.55)
        ax.text(hi + 8, i, f"{hi:.0f}", va="center", fontsize=7, color=c, fontweight="bold")
    else:
        ax.barh(i, hi, color=c, height=0.55, alpha=0.3)
        ax.barh(i, lo, color=c, height=0.55)
        ax.text(hi + 8, i, f"{lo:.0f}–{hi:.0f}", va="center", fontsize=7, color=c, fontweight="bold")
ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=6.4)
ax.invert_yaxis()
ax.set_xlim(0, 560); ax.set_xticks([0, 200, 400])
ax.tick_params(axis="y", length=0)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_xlabel("Million litres a day", fontsize=6.4)
fig.savefig(f"{FIGS}/case_vizag.pdf")
plt.close(fig)
print("wrote figs/case_mesa.pdf, figs/case_vizag.pdf")


# ---------------------------------------------------------------- locator map + Vizag basin check
# Points geocoded with Nominatim (OpenStreetMap), 10 Nov 2026. Mesa = the Epoch site geocode.
# Mark Wilmer Pumping Plant = the CAP intake on Lake Havasu. Polavaram = the village at the dam.
import geopandas as gpd
import numpy as np

GDB = ("data/raw/aqueduct/Aqueduct40_waterrisk_download_Y2023M07D05/GDB/"
       "Aq40_Y2023D07M05.gdb")
PTS = {
    "mesa":      (33.415, -111.831, "Google Mesa"),
    "cap":       (34.289, -114.104, "CAP intake,\nLake Havasu"),
    "phoenix":   (33.448, -112.074, "Phoenix"),
    "vizag_dc":  (17.906, 83.329, "Hub site\n(Tarluvada)"),
    "vizag":     (17.694, 83.292, "Visakhapatnam"),
    "polavaram": (17.247, 81.644, "Polavaram\nproject"),
}


def km(a, b):
    la1, lo1, la2, lo2 = map(np.radians, (PTS[a][0], PTS[a][1], PTS[b][0], PTS[b][1]))
    return 2 * 6371 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 +
                                        np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))


def basins(bbox):
    b = gpd.read_file(GDB, layer="baseline_annual", bbox=bbox,
                      columns=["bws_cat", "bws_label"]).to_crs("EPSG:4326")
    b["color"] = b.bws_cat.map(AQUEDUCT).fillna("#E6E6E6")
    return b


AZ, AP = (-115.3, 32.2, -110.6, 35.4), (80.9, 16.3, 84.2, 19.0)
b_az, b_ap = basins(AZ), basins(AP)

# Vizag basin check (was an ad hoc check; now reproducible here)
mon = gpd.read_file(GDB, layer="baseline_monthly", bbox=AP,
                    columns=[f"bws_{m:02d}_raw" for m in range(1, 13)]).to_crs("EPSG:4326")
pt = gpd.GeoDataFrame(geometry=gpd.points_from_xy([PTS["vizag_dc"][1]], [PTS["vizag_dc"][0]]), crs="EPSG:4326")
vb = gpd.sjoin(pt, b_ap, predicate="within").iloc[0]
vm = gpd.sjoin(pt, mon, predicate="within").iloc[0]
months = int((vm[[f"bws_{m:02d}_raw" for m in range(1, 13)]].astype(float) > 1).sum())
print(f"\nVizag hub basin: {vb.bws_label}; months withdrawals > supply: {months}/12")
print(f"straight-line distances: CAP intake -> Google Mesa {km('cap', 'mesa'):.0f} km; "
      f"Polavaram -> Vizag hub {km('polavaram', 'vizag_dc'):.0f} km")

fig, axes = plt.subplots(1, 2, figsize=(3.0, 1.75), gridspec_kw={"wspace": 0.08})
panels = [(axes[0], b_az, AZ, "mesa", "cap", "~300 km by canal", "Case 1 · Mesa, Arizona"),
          (axes[1], b_ap, AP, "vizag_dc", "polavaram", f"~{km('polavaram', 'vizag_dc'):.0f} km\n(straight line)",
           "Case 2 · Visakhapatnam")]
for ax, b, box, site, src, dist, title in panels:
    b.plot(ax=ax, color=b.color, linewidth=0.15, edgecolor="white", alpha=0.75)
    (y1, x1, _), (y2, x2, _) = PTS[site], PTS[src]
    ax.plot([x2, x1], [y2, y1], color=INK, lw=0.7, ls=(0, (2, 1.5)), zorder=3)
    box_kw = dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85)
    ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.2, dist, fontsize=5.4, ha="center", va="bottom", color=INK,
            linespacing=0.95, bbox=box_kw)
    ax.scatter([x1], [y1], marker="*", s=70, color=PHASE["ai"], edgecolor="white", linewidth=0.4, zorder=5)
    ax.scatter([x2], [y2], marker="^", s=22, color=INK, edgecolor="white", linewidth=0.3, zorder=5)
    ax.text(x1 + 0.1, y1 - 0.2, PTS[site][2], fontsize=5.8, va="top", ha="right", color=PHASE["ai"],
            fontweight="bold", linespacing=0.95, bbox=box_kw)
    ax.text(x2, y2 + 0.2, PTS[src][2], fontsize=5.4, va="bottom", ha="center", color=INK,
            linespacing=0.95, bbox=box_kw)
    ax.set_xlabel(""); ax.set_ylabel("")
    ax.set_xlim(box[0], box[2]); ax.set_ylim(box[1], box[3]); ax.set_aspect(1 / np.cos(np.radians(np.mean(box[1::2]))))
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color("#C9CDD2")
    ax.set_title(title, fontsize=6.6, loc="left", pad=2)
fig.savefig(f"{FIGS}/case_locator.pdf")
plt.close(fig)
print("wrote figs/case_locator.pdf")
