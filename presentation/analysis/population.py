"""Step 3 of O2: people living within 25 and 50 km of AI data centres in water-stressed basins.

Run from presentation_slides/:  /Users/aryan/miniforge3/envs/geo/bin/python analysis/population.py
Inputs:  data/processed/sites_water.csv; GHSL GHS-POP 2025 epoch, 30 arc-second (~1 km), WGS84
Output:  data/processed/population_exposure.csv (per site) and a printed summary

People near several sites are counted once (the union of all circles), so the totals are not
the sum of the per-site numbers.
"""
import glob

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds

P = "data/processed"
TIF = glob.glob("data/raw/ghsl/**/GHS_POP_E2025*_30ss*.tif", recursive=True)[0]
R_EARTH = 6371.0


def cells_within(src, lat, lon, km):
    """Flat raster indices and population of cells whose centres lie within km of (lat, lon)."""
    dlat = km / 111.0 + 0.02
    dlon = km / (111.0 * np.cos(np.radians(lat))) + 0.02
    win = from_bounds(lon - dlon, lat - dlat, lon + dlon, lat + dlat, src.transform).round_offsets().round_lengths()
    data = src.read(1, window=win, boundless=True, fill_value=0).astype("float64")
    data[data < 0] = 0                                           # nodata
    rows, cols = np.indices(data.shape)
    rows += int(win.row_off); cols += int(win.col_off)
    xs, ys = rasterio.transform.xy(src.transform, rows.ravel(), cols.ravel())
    xs, ys = np.radians(np.asarray(xs)), np.radians(np.asarray(ys))
    la, lo = np.radians(lat), np.radians(lon)
    d = 2 * R_EARTH * np.arcsin(np.sqrt(np.sin((ys - la) / 2) ** 2 +
                                        np.cos(la) * np.cos(ys) * np.sin((xs - lo) / 2) ** 2))
    keep = (d <= km) & (rows.ravel() >= 0) & (cols.ravel() >= 0)
    return (rows.ravel()[keep] * src.width + cols.ravel()[keep]), data.ravel()[keep]


s = pd.read_csv(f"{P}/sites_water.csv")
s["stressed"] = s.bws_cat >= 3
out, totals = [], {}
with rasterio.open(TIF) as src:
    for km in (25, 50):
        groups = {"stressed": [], "all": []}
        for r in s.itertuples():
            idx, pop = cells_within(src, r.lat, r.lon, km)
            out.append({"name": r.name, "km": km, "population": pop.sum(), "stressed": r.stressed})
            groups["all"].append((idx, pop))
            if r.stressed:
                groups["stressed"].append((idx, pop))
        for g, parts in groups.items():
            idx = np.concatenate([p[0] for p in parts]); pop = np.concatenate([p[1] for p in parts])
            _, first = np.unique(idx, return_index=True)
            totals[(g, km)] = pop[first].sum()

per_site = pd.DataFrame(out)
per_site.to_csv(f"{P}/population_exposure.csv", index=False)
print(f"GHSL file: {TIF}")
for (g, km), v in sorted(totals.items()):
    print(f"{g:9s} sites, within {km} km: {v / 1e6:6.2f} million people (union, counted once)")
top = (per_site[(per_site.km == 50) & per_site.stressed]
       .sort_values("population", ascending=False).head(8))
print("\nlargest populations within 50 km of stressed sites:")
print(top.assign(million=lambda d: (d.population / 1e6).round(2))[["name", "million"]].to_string(index=False))
