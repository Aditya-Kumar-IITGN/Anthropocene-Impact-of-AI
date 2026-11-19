"""O2 figures (column width), re-made from the deck's processed results for the printed report.

Run:  /Users/aryan/miniforge3/envs/geo/bin/python -I report/analysis/fig_o2.py
Inputs (read-only): presentation/data/processed/{water_stress_summary,water_use_summary,materials,ewaste_regions}.csv
                    Aqueduct 4.0 GDB (case locator only)
Outputs: report/figs/o2_count_vs_size.pdf, o2_water_use.pdf, o2_materials_ewaste.pdf, o2_case_locator.pdf

Nothing is recomputed here except the case-locator distances (same points and formula as
presentation/analysis/case_studies.py). Numbers are those in claims.csv rows O2b, O2c, O2d, Method5.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# ================================================================ count vs size
s = pd.read_csv(os.path.join(PROC, "water_stress_summary.csv"))
rows = [("Rosa-like: >= 1 month demand > supply", "Monthly scarcity\n(1+ month, Rosa-like)"),
        ("baseline: high or extremely high", "Baseline (annual)"),
        ("2030 BAU: high or extremely high", "2030, business as usual"),
        ("2050 BAU: high or extremely high", "2050, business as usual"),
        ("2050 PES: high or extremely high", "2050, pessimistic")]
weights = [("sites", "Sites", GREY), ("current MW", "Current MW", NAVY), ("planned 2030 MW", "Planned 2030 MW", SKY)]
fig, ax = plt.subplots(figsize=(COL, 2.4))
h = 0.27
for i, (key, _) in enumerate(rows):
    for k, (w, wl, c) in enumerate(weights):
        v = 100 * s.loc[(s.metric == key) & (s.weight == w), "share"].iloc[0]
        y = i + (k - 1) * h
        ax.barh(y, v, height=h * 0.92, color=c, label=wl if i == 0 else None)
        if w == "planned 2030 MW":
            ax.text(max(v, 25.6) + 1, y, f"{v:.0f}%", va="center", fontsize=6.6, color=NAVY, fontweight="bold")
ax.plot([25, 25], [-0.45, 0.45], color=RED, lw=0.8, ls=(0, (2, 1.5)), zorder=5)
ax.text(31, -0.27, "Rosa et al.: 25% of sites", fontsize=6, color=RED, va="center")
ax.set_yticks(range(len(rows)), [r[1] for r in rows])
ax.invert_yaxis()
ax.set_xlim(0, 70)
ax.set_xticks([0, 20, 40, 60], ["0", "20", "40", "60%"])
ax.set_xlabel("Share in high or extremely high water stress")
ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=3, frameon=False, handlelength=0.9,
          columnspacing=1.0, borderaxespad=0.1, title="Weighted by:", title_fontsize=6.3,
          alignment="left")
bar_axes(ax)
save(fig, "o2_count_vs_size.pdf")

# ================================================================ water-use ranges
g = pd.read_csv(os.path.join(PROC, "water_use_summary.csv")).set_index(["when", "scenario"])
items = [("Direct, today", "today", "direct_bnL"), ("Direct, 2030 plan", "2030", "direct_bnL"),
         ("Indirect, today", "today", "indirect_bnL"), ("Indirect, 2030 plan", "2030", "indirect_bnL")]
fig, ax = plt.subplots(figsize=(COL, 1.95))
for i, (label, when, col) in enumerate(items):
    lo, hi = g.loc[(when, "low"), col], g.loc[(when, "high"), col]
    c = NAVY if when == "today" else SKY
    ax.plot([lo, hi], [i, i], color=c, lw=6.5, solid_capstyle="butt")
    ax.text(hi * 1.1, i, f"{lo:,.0f}–{hi:,.0f}", va="center", fontsize=6.6, color=NAVY, fontweight="bold")
    if col == "direct_bnL":
        st = g.loc[(when, "high"), "direct_stressed_share"]
        ax.text(lo, i + 0.42, f"{st:.0%} of it in stressed basins", va="center", ha="left", fontsize=5.9,
                color=MUTED)
ax.plot([312.5, 764.6], [4.25, 4.25], color=GREY, lw=6.5, solid_capstyle="butt")   # de Vries-Gao (2026), all AI 2025
ax.text(764.6 * 1.1, 4.25, "312–765", va="center", fontsize=6.6, color=INK, fontweight="bold")
ax.set_yticks(list(range(4)) + [4.25], [it[0] for it in items] + ["All AI worldwide, 2025\n(de Vries-Gao 2026)"])
ax.set_xscale("log")
ax.set_xlim(20, 7000)
ax.set_xticks([100, 1000], ["100", "1,000"])
ax.minorticks_off()
ax.invert_yaxis()
ax.set_xlabel("Billion litres consumed a year (log scale), low–high range")
bar_axes(ax)
save(fig, "o2_water_use.pdf")

# ================================================================ minerals + e-waste
m = pd.read_csv(os.path.join(PROC, "materials.csv"))
ew = pd.read_csv(os.path.join(PROC, "ewaste_regions.csv"))
PROD_C = {"China": RED, "DR Congo": GOLD, "Chile": GREEN, "United States": NAVY}
fig, (a, b) = plt.subplots(2, 1, figsize=(COL, 3.05), gridspec_kw={"hspace": 0.62, "height_ratios": [6, 5]})
labels = [f"{r.item} ({'primary' if r.stage == 'primary production' else r.stage.replace(' production', '')})"
          for r in m.itertuples()]
vals = list(m.top_share_pct)
prods = list(m.top_producer)
labels.append("AI capacity (planned 2030 MW)")
vals.append(86.2)          # claims.csv O2d: US share of planned 2030 AI MW (water_stress inputs; Epoch AI)
prods.append("United States")
for i, (lab, v, p) in enumerate(zip(labels, vals, prods)):
    a.barh(i, 100, color="#EEEEEE", height=0.66)
    a.barh(i, v, color=PROD_C[p], height=0.66)
    a.text(v - 1.5, i, f"{p} {v:.0f}%", va="center", ha="right", fontsize=6.4, color="white", fontweight="bold")
a.axhline(len(labels) - 1.5, color=MUTED, lw=0.5, ls=(0, (2, 1.5)))
a.set_yticks(range(len(labels)), labels)
a.invert_yaxis()
a.set_xlim(0, 100)
a.set_xticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
a.set_title("(a) Largest producer's share of world supply, 2025 (USGS)", loc="left", pad=3)
bar_axes(a)
for i, r in enumerate(ew.itertuples()):
    col = r.generated_kg_per_capita * r.formally_collected_pct / 100
    b.barh(i, r.generated_kg_per_capita, color=GREY, height=0.66, label="Generated" if i == 0 else None)
    b.barh(i, col, color=NAVY, height=0.66, label="Formally collected" if i == 0 else None)
    b.text(r.generated_kg_per_capita + 0.4, i, f"{r.formally_collected_pct:g}% collected", va="center",
           fontsize=6.2, color=INK)
b.set_yticks(range(len(ew)), ew.region)
b.invert_yaxis()
b.set_xlim(0, 26)
b.set_xlabel("E-waste, kg per person, 2022")
b.set_title("(b) E-waste generated and formally collected (Global E-waste Monitor)", loc="left", pad=3)
b.legend(loc="lower right", frameon=False, handlelength=0.9)
bar_axes(b)
save(fig, "o2_materials_ewaste.pdf")

# ================================================================ case locator (same points as case_studies.py)
if not os.path.exists(GDB):
    raise SystemExit("skipped figs/o2_case_locator.pdf: Aqueduct GDB not found (see README_TEAM.md)")
PTS = {"mesa": (33.415, -111.831, "Google Mesa"), "cap": (34.289, -114.104, "CAP intake,\nLake Havasu"),
       "vizag_dc": (17.906, 83.329, "Hub site\n(Tarluvada)"), "polavaram": (17.247, 81.644, "Polavaram\nproject")}


def km(a_, b_):
    la1, lo1, la2, lo2 = map(np.radians, (PTS[a_][0], PTS[a_][1], PTS[b_][0], PTS[b_][1]))
    return 2 * 6371 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 +
                                        np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))


def basins(bbox):
    bb = gpd.read_file(GDB, layer="baseline_annual", bbox=bbox, columns=["bws_cat"]).to_crs("EPSG:4326")
    bb["color"] = bb.bws_cat.map(AQUEDUCT).fillna("#E6E6E6")
    return bb


AZ, AP = (-115.3, 32.2, -110.6, 35.4), (80.9, 16.3, 84.2, 19.0)
d_mesa, d_viz = km("cap", "mesa"), km("polavaram", "vizag_dc")
print(f"straight-line: CAP intake -> Google Mesa {d_mesa:.0f} km; Polavaram -> Vizag hub {d_viz:.0f} km")
fig, axes = plt.subplots(1, 2, figsize=(COL, 1.72), gridspec_kw={"wspace": 0.06})
panels = [(axes[0], basins(AZ), AZ, "mesa", "cap", "~300 km by canal\n(" + f"{d_mesa:.0f} km straight)",
           "(a) Mesa, Arizona", (0.95, 0.45)),
          (axes[1], basins(AP), AP, "vizag_dc", "polavaram", f"~{d_viz:.0f} km\n(straight line)",
           "(b) Visakhapatnam, India", (0.0, 0.2))]
box_kw = dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85)
for ax, bb, box, site, src, dist, title, (dx, dy) in panels:
    bb.plot(ax=ax, color=bb.color, linewidth=0.15, edgecolor="white", alpha=0.75)
    (y1, x1, _), (y2, x2, _) = PTS[site], PTS[src]
    ax.plot([x2, x1], [y2, y1], color=INK, lw=0.7, ls=(0, (2, 1.5)), zorder=3)
    ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, dist, fontsize=5.4, ha="center", va="bottom", color=INK,
            linespacing=0.95, bbox=box_kw)
    ax.scatter([x1], [y1], marker="*", s=70, color=NAVY, edgecolor="white", linewidth=0.4, zorder=5)
    ax.scatter([x2], [y2], marker="^", s=22, color=INK, edgecolor="white", linewidth=0.3, zorder=5)
    ax.text(x1 + 0.1, y1 - 0.2, PTS[site][2], fontsize=5.7, va="top", ha="right", color=NAVY,
            fontweight="bold", linespacing=0.95, bbox=box_kw)
    ax.text(x2, y2 + 0.2, PTS[src][2], fontsize=5.4, va="bottom", ha="center", color=INK, linespacing=0.95,
            bbox=box_kw)
    ax.set_xlim(box[0], box[2]); ax.set_ylim(box[1], box[3])
    ax.set_aspect(1 / np.cos(np.radians(np.mean(box[1::2]))))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(""); ax.set_ylabel("")
    for sp in ax.spines.values():
        sp.set_color("#C9CDD2")
    ax.set_title(title, fontsize=6.6, loc="left", pad=2)
save(fig, "o2_case_locator.pdf")
