"""O2 figures: Fig O2a (sites over water stress) and Fig O2b (count vs size-weighted shares).

Run from presentation_slides/:  /Users/aryan/miniforge3/envs/geo/bin/python analysis/o2_figures.py
Needs data/processed/sites_water.csv and water_stress_summary.csv (water_stress.py).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from style import *                                   # noqa: F401,F403  (rcParams, colours)

import geopandas as gpd
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

GDB = ("data/raw/aqueduct/Aqueduct40_waterrisk_download_Y2023M07D05/GDB/"
       "Aq40_Y2023D07M05.gdb")
P = "data/processed"

sites = pd.read_csv(f"{P}/sites_water.csv")
sites["planned"] = sites.planned_2030_mw.fillna(sites.current_mw).fillna(0)
sites["current"] = sites.current_mw.fillna(0)
pts = gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites.lon, sites.lat), crs="EPSG:4326")


# ================================================================ Fig O2a: map
basins = gpd.read_file(GDB, layer="baseline_annual", columns=["bws_cat"]).to_crs("EPSG:4326")
basins["geometry"] = basins.geometry.simplify(0.03, preserve_topology=False)
basins = basins[~basins.geometry.is_empty]
basins["color"] = basins.bws_cat.map(AQUEDUCT).fillna("#E6E6E6")

def size(mw):                       # marker area in pt^2, proportional to MW
    return np.asarray(mw) * 0.045

def panel(ax, crs, bbox, sel):
    b = basins.cx[bbox[0]:bbox[2], bbox[1]:bbox[3]].to_crs(crs)
    b.plot(ax=ax, color=b.color, linewidth=0, rasterized=True, alpha=0.6)
    p = pts[sel].to_crs(crs)
    ax.scatter(p.geometry.x, p.geometry.y, s=size(p.planned), facecolor="none",
               edgecolor=INK, linewidth=0.5, zorder=3)
    ax.scatter(p.geometry.x, p.geometry.y, s=size(p.current), facecolor=INK,
               edgecolor="white", linewidth=0.3, alpha=0.85, zorder=4)
    ax.set_axis_off()
    return b

fig = plt.figure(figsize=(5.5, 1.9))
ax_us = fig.add_axes([0.0, 0.13, 0.6, 0.85])
ax_w = fig.add_axes([0.61, 0.25, 0.39, 0.66])

us = sites.country.eq("United States") & sites.lon.between(-125, -66)
b = panel(ax_us, "EPSG:5070", (-126, 23, -65, 51), us.to_numpy())
ax_us.set_xlim(-2.40e6, 2.30e6); ax_us.set_ylim(0.25e6, 3.20e6)          # contiguous US, Albers
ax_us.set_title("Contiguous United States", fontsize=7, loc="left", color=INK, pad=1)

b = panel(ax_w, "EPSG:8857", (-180, -58, 180, 84), np.ones(len(sites), bool))
ax_w.set_ylim(-6.2e6, 8.6e6)
ax_w.set_title("World", fontsize=7, loc="left", color=INK, pad=1)

handles = [Patch(facecolor=AQUEDUCT[k], label=AQUEDUCT_LABEL[k]) for k in (0, 1, 2, 3, 4, -1)]
handles += [Line2D([], [], ls="", marker="o", ms=4, mfc=INK, mec="white", label="Current MW"),
            Line2D([], [], ls="", marker="o", ms=6, mfc="none", mec=INK, mew=0.5, label="Planned 2030 MW")]
fig.legend(handles=handles, loc="lower center", ncol=8, frameon=False, fontsize=5.8,
           handlelength=1.1, columnspacing=0.9, bbox_to_anchor=(0.5, -0.01))
fig.text(0.62, 0.16, "Marker area by MW:", fontsize=5.5, color=MUTED, va="center")
for mw, x in [(100, 0.755), (500, 0.835), (2000, 0.94)]:
    r = np.sqrt(size(mw)) / 2 / 72 / 5.5                 # marker radius as a fraction of fig width
    fig.add_artist(Line2D([x], [0.16], ls="", marker="o", ms=np.sqrt(size(mw)),
                          mfc="none", mec=MUTED, mew=0.5, transform=fig.transFigure))
    fig.text(x + r + 0.006, 0.16, f"{mw:,}", fontsize=5.5, color=MUTED, ha="left", va="center")
fig.savefig(f"{FIGS}/o2a_sites_water_stress.pdf")
plt.close(fig)


# ================================================================ Fig O2b: count vs size
s = pd.read_csv(f"{P}/water_stress_summary.csv")
rows = [("Rosa-like: >= 1 month demand > supply", "Monthly scarcity\n(1+ month, Rosa-like)"),
        ("baseline: high or extremely high", "Baseline (annual)"),
        ("2030 BAU: high or extremely high", "2030, business as usual"),
        ("2050 BAU: high or extremely high", "2050, business as usual"),
        ("2050 PES: high or extremely high", "2050, pessimistic")]
weights = [("sites", "Share of sites", "#B9BEC4"),
           ("current MW", "Share of current MW", SLATE),
           ("planned 2030 MW", "Share of planned 2030 MW", PHASE["ai"])]

fig, ax = plt.subplots(figsize=(3.05, 2.3))
h = 0.26
for i, (key, label) in enumerate(rows):
    for k, (w, wl, c) in enumerate(weights):
        v = 100 * s.loc[(s.metric == key) & (s.weight == w), "share"].iloc[0]
        y = i + (k - 1) * h
        ax.barh(y, v, height=h * 0.92, color=c, label=wl if i == 0 else None)
        if w == "planned 2030 MW":
            ax.text(max(v, 25.6) + 1, y, f"{v:.0f}%", va="center", fontsize=7, color=c, fontweight="bold")
ax.plot([25, 25], [-0.45, 0.45], color=INK, lw=0.9, ls=(0, (2, 1.5)), zorder=5)   # reference, not data: no gold
ax.text(26.2, -0.27, "Rosa et al.: 25% of sites", fontsize=6.2, color=INK, va="center")
ax.set_yticks(range(len(rows)), [r[1] for r in rows], fontsize=7)
ax.invert_yaxis()
ax.set_xlim(0, 72)
ax.set_xticks([0, 20, 40, 60], ["0", "20", "40", "60%"])
ax.tick_params(axis="y", length=0)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_xlabel("In high or extremely high water stress", fontsize=7)
ax.legend(loc="lower left", bbox_to_anchor=(-0.42, 1.0), ncol=3, frameon=False, fontsize=6.4,
          handlelength=0.9, columnspacing=0.8, borderaxespad=0.1)
fig.savefig(f"{FIGS}/o2b_count_vs_size.pdf")
plt.close(fig)
print("wrote figs/o2a_sites_water_stress.pdf, figs/o2b_count_vs_size.pdf")
