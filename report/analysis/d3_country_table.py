"""Deliverable D3: country table with location quotients, country-level Gini, water stress, exposure, water use.

Run:  /Users/aryan/miniforge3/envs/geo/bin/python -I report/analysis/d3_country_table.py
Inputs (read-only):
  presentation/data/processed/sites_water.csv, water_use.csv   (per-site results from the deck scripts)
  GHSL GHS-POP E2025 R2023A, 30 arc-second (~1 km) grid         (population; same file as the exposure counts)
  Aqueduct 4.0 baseline_annual polygons, field gid_0            (country outlines; GADM-based)
Outputs:
  report/data/country_population_ghsl.csv   (cache; delete it to recompute, ~2-4 min)
  report/data/d3_country_table.csv          (one row per country hosting a tracked AI site)
  report/data/d3_gini.csv                   (Gini variants)
  report/figs/o3_lorenz.pdf

Population source. Country population = sum of GHSL 2025 cells whose centres fall inside the union of the
country's Aqueduct polygons; world population = sum of the whole grid. This keeps the D3 denominators
consistent with the 25/50 km exposure counts (same grid). It is NOT UN WPP 2024; a cross-check against WPP
is a TODO (see STATUS.md). Coastal cells outside Aqueduct's polygons are lost, so country totals are, if
anything, slightly low.

Gini. Countries are sorted by MW per person; every country without a tracked site is pooled into one
zero-capacity group. Because all of those countries have exactly zero capacity, pooling them does not change
the country-level Gini: this is the exact country-level value for the Epoch sample.
  LQ_i = (C_i / C) / (P_i / P)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import rasterio  # noqa: E402
from rasterio.mask import mask as rmask  # noqa: E402
from rasterio.windows import Window, from_bounds  # noqa: E402
from shapely import union_all  # noqa: E402
need(GHSL)                                   # GDB is only needed if the population cache is deleted

R_EARTH = 6371.0
s = pd.read_csv(os.path.join(PROC, "sites_water.csv"))
w = pd.read_csv(os.path.join(PROC, "water_use.csv"))
assert (s.name.values == w.name.values).all()
s["mw_now"] = s.current_mw.fillna(0)
s["mw_2030"] = s.planned_2030_mw.fillna(s.current_mw).fillna(0)       # same rule as water_stress.py
s["stressed"] = s.bws_cat >= 3
for when in ("today", "2030"):
    for sc in ("low", "high"):
        s[f"water_{when}_{sc}"] = w[f"direct_{when}_{sc}"] + w[f"indirect_{when}_{sc}"]
iso = s.groupby("country").gid_0.agg(lambda x: sorted(set(x)))
assert all(len(v) == 1 for v in iso), iso               # every site's Aqueduct country matches Epoch's country
iso = iso.str[0]

# ------------------------------------------------------------------ population (GHSL), cached
cache = os.path.join(DATA, "country_population_ghsl.csv")
if os.path.exists(cache):
    pop = pd.read_csv(cache).set_index("iso3")
else:
    rows = []
    with rasterio.open(GHSL) as src:
        world = 0.0
        for r0 in range(0, src.height, 1200):
            a = src.read(1, window=Window(0, r0, src.width, min(1200, src.height - r0))).astype("float64")
            world += a[a > 0].sum()
        rows.append({"iso3": "WORLD", "population": world})
        polys = gpd.read_file(GDB, layer="baseline_annual", columns=["gid_0"],
                              where="gid_0 IN (%s)" % ",".join(f"'{c}'" for c in iso.values)).to_crs("EPSG:4326")
        for c, g in polys.groupby("gid_0"):
            parts = gpd.GeoSeries([union_all(g.geometry.values)], crs="EPSG:4326").explode(index_parts=False)
            total = 0.0
            for geom in parts:
                try:
                    a, _ = rmask(src, [geom], crop=True, filled=True, nodata=0, all_touched=False)
                except ValueError:                       # part smaller than a cell / outside the grid
                    continue
                a = a[0].astype("float64")
                total += a[a > 0].sum()
            rows.append({"iso3": c, "population": total})
            print(f"  {c}: {total / 1e6:,.1f} M")
    pop = pd.DataFrame(rows).set_index("iso3")
    pop["source"] = "GHSL GHS-POP E2025 R2023A 30ss, summed inside Aqueduct 4.0 gid_0 polygons"
    pop.to_csv(cache)
P_WORLD = pop.loc["WORLD", "population"]


# ------------------------------------------------------------------ people near sites, union per country
def cells_within(src, lat, lon, km):
    """Same function as presentation/analysis/population.py: raster cells whose centres lie within km."""
    dlat = km / 111.0 + 0.02
    dlon = km / (111.0 * np.cos(np.radians(lat))) + 0.02
    win = from_bounds(lon - dlon, lat - dlat, lon + dlon, lat + dlat, src.transform).round_offsets().round_lengths()
    data = src.read(1, window=win, boundless=True, fill_value=0).astype("float64")
    data[data < 0] = 0
    rows, cols = np.indices(data.shape)
    rows += int(win.row_off); cols += int(win.col_off)
    xs, ys = rasterio.transform.xy(src.transform, rows.ravel(), cols.ravel())
    xs, ys = np.radians(np.asarray(xs)), np.radians(np.asarray(ys))
    la, lo = np.radians(lat), np.radians(lon)
    d = 2 * R_EARTH * np.arcsin(np.sqrt(np.sin((ys - la) / 2) ** 2 +
                                        np.cos(la) * np.cos(ys) * np.sin((xs - lo) / 2) ** 2))
    keep = (d <= km) & (rows.ravel() >= 0) & (cols.ravel() >= 0)
    return rows.ravel()[keep] * src.width + cols.ravel()[keep], data.ravel()[keep]


def union_pop(parts):
    if not parts:
        return 0.0
    idx = np.concatenate([p[0] for p in parts]); v = np.concatenate([p[1] for p in parts])
    _, first = np.unique(idx, return_index=True)
    return float(v[first].sum())


near = {}
with rasterio.open(GHSL) as src:
    cells = {r.Index: cells_within(src, r.lat, r.lon, 50) for r in s.itertuples()}
for c, g in s.groupby("country"):
    near[c] = (union_pop([cells[i] for i in g.index]), union_pop([cells[i] for i in g.index if s.stressed[i]]))
check = union_pop([cells[i] for i in s.index if s.stressed[i]])
print(f"check: people within 50 km of stressed sites, all countries = {check / 1e6:.2f} M (deck: 47.88 M)")

# ------------------------------------------------------------------ the table
C_NOW, C_2030 = s.mw_now.sum(), s.mw_2030.sum()
t = []
for c, g in s.groupby("country"):
    p = pop.loc[iso[c], "population"]
    t.append({
        "country": c, "iso3": iso[c], "sites": len(g),
        "mw_now": g.mw_now.sum(), "mw_2030": g.mw_2030.sum(),
        "share_now_pct": 100 * g.mw_now.sum() / C_NOW, "share_2030_pct": 100 * g.mw_2030.sum() / C_2030,
        "population_m": p / 1e6, "pop_share_pct": 100 * p / P_WORLD,
        "w_per_person_now": g.mw_now.sum() * 1e6 / p, "w_per_person_2030": g.mw_2030.sum() * 1e6 / p,
        "lq_now": (g.mw_now.sum() / C_NOW) / (p / P_WORLD), "lq_2030": (g.mw_2030.sum() / C_2030) / (p / P_WORLD),
        "stressed_2030_pct": 100 * g.mw_2030[g.stressed].sum() / g.mw_2030.sum(),
        "people_50km_m": near[c][0] / 1e6, "people_50km_stressed_m": near[c][1] / 1e6,
        "water_2030_low_bnL": g.water_2030_low.sum(), "water_2030_high_bnL": g.water_2030_high.sum(),
    })
t = pd.DataFrame(t).sort_values("mw_2030", ascending=False)
t.to_csv(os.path.join(DATA, "d3_country_table.csv"), index=False)


# ------------------------------------------------------------------ Gini
def lorenz(cap, popn):
    """Lorenz points (pop share, cap share), groups sorted by capacity per person."""
    cap, popn = np.asarray(cap, float), np.asarray(popn, float)
    o = np.argsort(cap / popn)
    x = np.concatenate([[0], np.cumsum(popn[o]) / popn.sum()])
    y = np.concatenate([[0], np.cumsum(cap[o]) / cap.sum()])
    return x, y


def gini(cap, popn):
    x, y = lorenz(cap, popn)
    return 1 - np.sum((x[1:] - x[:-1]) * (y[1:] + y[:-1]))


rest = P_WORLD - t.population_m.sum() * 1e6
g_rows = []
for col, lab in (("mw_now", "current MW"), ("mw_2030", "planned 2030 MW")):
    cap = list(t[col]) + [0.0]
    popn = list(t.population_m * 1e6) + [rest]
    g_rows.append({"measure": lab, "grouping": f"countries ({len(t)} with sites + all others, zero)",
                   "gini": gini(cap, popn)})
    # only countries that host capacity (how unequal is it among hosts?)
    m = t[col] > 0
    g_rows.append({"measure": lab, "grouping": f"host countries only ({int(m.sum())})",
                   "gini": gini(t[col][m], t.population_m[m])})
g = pd.DataFrame(g_rows)
g.to_csv(os.path.join(DATA, "d3_gini.csv"), index=False)

pd.set_option("display.width", 220)
print(f"world population (GHSL 2025): {P_WORLD / 1e9:.3f} bn; countries with sites: {t.population_m.sum() / 1e3:.3f} bn")
print(t.round(3).to_string(index=False))
print(g.round(4).to_string(index=False))

# ------------------------------------------------------------------ Fig: Lorenz curve
fig, ax = plt.subplots(figsize=(COL, 2.35))
ax.plot([0, 1], [0, 1], color=MUTED, lw=0.6, ls=(0, (2, 1.5)))
for col, lab, c in (("mw_now", "Current MW", NAVY), ("mw_2030", "Planned 2030 MW", PHASE["ai"])):
    x, y = lorenz(list(t[col]) + [0.0], list(t.population_m * 1e6) + [rest])
    gv = g[(g.measure == ("current MW" if col == "mw_now" else "planned 2030 MW")) & g.grouping.str.startswith("countries")].gini.iloc[0]
    ax.plot(100 * x, 100 * y, color=c, lw=1.2 if col == "mw_now" else 1.0,
            ls="-" if col == "mw_now" else (0, (3, 1.2)), label=f"{lab} (Gini {gv:.3f})")
ax.set_xlim(0, 100); ax.set_ylim(0, 100)
ax.set_xticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
ax.set_yticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
ax.set_xlabel("Cumulative share of world population (countries by MW per person)")
ax.set_ylabel("Cumulative share of AI capacity")
ax.legend(loc="upper left", frameon=False, handlelength=2.2)
us = t[t.iso3 == "USA"].iloc[0]
ax.annotate(f"United States: {us.pop_share_pct:.1f}% of people,\n{us.share_now_pct:.1f}% of current MW",
            xy=(100 - us.pop_share_pct, 100 - us.share_now_pct), xytext=(42, 30), fontsize=6.2,
            arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED), color=INK)
ax.text(45, 4, f"{100 * rest / P_WORLD:.0f}% of people live in countries\nwith no tracked AI site",
        fontsize=6.2, color=MUTED, ha="center")
clean(ax)
save(fig, "o3_lorenz.pdf")
