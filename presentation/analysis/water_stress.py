"""Step 2 of O2: join sites to Aqueduct 4.0 water stress, count vs size-weighted shares.

Run from presentation_slides/:  /Users/aryan/miniforge3/envs/geo/bin/python analysis/water_stress.py
Inputs:  data/processed/sites.csv (from geocode_sites.py), Aqueduct 4.0 geodatabase
Outputs: data/processed/sites_water.csv, data/processed/water_stress_summary.csv, printed summary

Metrics
  annual:  Aqueduct baseline water stress category bws_cat >= 3 (high, extremely high:
           withdrawals >= 40% of available supply). -1 = arid and low water use, reported apart.
  future:  {bau,pes}{30,50}_ws_x_c >= 3 (business as usual / pessimistic, 2030 / 2050).
  monthly: months a year with bws_raw > 1 (withdrawals exceed available supply). This is
           closest to the Rosa et al. (2026) test (demand > renewable supply in >= 1 month),
           but it is not the same model, so we call it "Rosa-like".
"""
import geopandas as gpd
import numpy as np
import pandas as pd

GDB = ("data/raw/aqueduct/Aqueduct40_waterrisk_download_Y2023M07D05/GDB/"
       "Aq40_Y2023D07M05.gdb")
OUT = "data/processed"

sites = pd.read_csv(f"{OUT}/sites.csv")
pts = gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites.lon, sites.lat), crs="EPSG:4326")

base = gpd.read_file(GDB, layer="baseline_annual",
                     columns=["string_id", "pfaf_id", "gid_0", "name_0", "name_1",
                              "bws_raw", "bws_cat", "bws_label"])
fut = gpd.read_file(GDB, layer="future_annual",
                    columns=["pfaf_id"] + [f"{s}{y}_ws_x_{t}" for s in ("bau", "pes")
                                           for y in (30, 50) for t in ("r", "c")])
months = [f"bws_{m:02d}_raw" for m in range(1, 13)]
mon = gpd.read_file(GDB, layer="baseline_monthly", columns=["pfaf_id"] + months)
for layer in (base, fut, mon):
    layer.to_crs("EPSG:4326", inplace=True)

j = gpd.sjoin(pts, base, how="left", predicate="within").drop(columns="index_right")
f = gpd.sjoin(pts[["name", "geometry"]], fut, how="left", predicate="within").drop(
    columns=["index_right", "geometry", "pfaf_id"])
m = gpd.sjoin(pts[["name", "geometry"]], mon, how="left", predicate="within")
m["scarce_months"] = (m[months] > 1).sum(axis=1)
m = m[["name", "scarce_months"]]

out = (pd.DataFrame(j.drop(columns="geometry"))
       .merge(f.drop_duplicates("name"), on="name", how="left")
       .merge(m.drop_duplicates("name"), on="name", how="left"))
out = out.drop_duplicates("name")
out.to_csv(f"{OUT}/sites_water.csv", index=False)

# ---------------------------------------------------------------- checks
unmatched = out[out.bws_cat.isna()]
iso = {"United States": "USA", "China": "CHN", "Malaysia": "MYS", "Norway": "NOR",
       "United Kingdom": "GBR", "Indonesia": "IDN", "Finland": "FIN", "Australia": "AUS",
       "Portugal": "PRT", "Iceland": "ISL", "Sweden": "SWE", "United Arab Emirates": "ARE"}
wrong_country = out[out.gid_0.notna() & (out.country.map(iso) != out.gid_0)]
print(f"sites: {len(out)}, not inside any basin: {len(unmatched)}, country mismatch: {len(wrong_country)}")
if len(unmatched):
    print(unmatched[["name", "lat", "lon"]].to_string())
if len(wrong_country):
    print(wrong_country[["name", "country", "gid_0", "name_0"]].to_string())

# ---------------------------------------------------------------- shares
def shares(mask, label):
    rows = []
    for wname, w in [("sites", np.ones(len(out))),
                     ("current MW", out.current_mw.fillna(0).to_numpy()),
                     ("planned 2030 MW", out.planned_2030_mw.fillna(out.current_mw).fillna(0).to_numpy())]:
        ok = mask.notna().to_numpy() & (w > 0)
        share = (w[ok] * mask[ok].astype(float)).sum() / w[ok].sum()
        rows.append({"metric": label, "weight": wname, "share": share, "n_sites": int(ok.sum()),
                     "total_weight": w[ok].sum()})
    return rows

def at_least_high(col):
    c = out[col]
    return (c >= 3).where(c.notna())

rows = []
rows += shares(at_least_high("bws_cat"), "baseline: high or extremely high")
rows += shares((out.bws_cat == -1).where(out.bws_cat.notna()), "baseline: arid and low water use")
for sc, yr in [("bau", 30), ("bau", 50), ("pes", 30), ("pes", 50)]:
    rows += shares(at_least_high(f"{sc}{yr}_ws_x_c"), f"20{yr} {sc.upper()}: high or extremely high")
rows += shares((out.scarce_months >= 1).where(out.scarce_months.notna()),
               "Rosa-like: >= 1 month demand > supply")
summary = pd.DataFrame(rows)
summary.to_csv(f"{OUT}/water_stress_summary.csv", index=False)

pd.set_option("display.width", 160)
print(summary.pivot(index="metric", columns="weight", values="share")
      .reindex(columns=["sites", "current MW", "planned 2030 MW"]).mul(100).round(1).to_string())
print("\nweights: current MW total", round(out.current_mw.fillna(0).sum()),
      "| planned 2030 MW total", round(out.planned_2030_mw.fillna(out.current_mw).fillna(0).sum()))
print("\nbaseline category counts:", out.bws_label.value_counts().to_dict())
