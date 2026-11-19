"""Deliverable D2: one standardised growth table across the three phases.

Run from presentation_slides/:  /Users/aryan/miniforge3/envs/geo/bin/python -I analysis/growth_table.py
Inputs:  ../proposal/data/raw/owid_global_primary_energy.csv (Our World in Data; Smil 2017 + Energy Institute)
         ../proposal/data/raw/epoch_notable_ai_models.csv (Epoch AI, accessed 26 Oct 2026)
         published endpoints (LBNL 2024, Masanet et al. 2020 via LBNL summary, IEA 2025)
Output:  data/processed/growth_table.csv and a printed table

  r  = e^b - 1 (annual growth),  T2 = ln 2 / b (doubling time), from OLS of ln(y) on year where an
       annual series exists (95% CI from the slope's t-interval); otherwise from two published values
       (no interval possible).
  Breakpoints: continuous two-segment (hinge) fit of ln(y) on year; the year with least SSE.
"""
import numpy as np
import pandas as pd
from scipy import stats

RAW = "../proposal/data/raw"
LN2 = np.log(2)
rows = []


def add(phase, series, period, b, lo=np.nan, hi=np.nan, n=2, method="two published values", projected=False, source=""):
    rows.append(dict(phase=phase, series=series, period=period, method=method, n=n, projected=projected,
                     r_pct=100 * (np.exp(b) - 1), r_lo=100 * (np.exp(lo) - 1), r_hi=100 * (np.exp(hi) - 1),
                     T2=LN2 / b, T2_lo=LN2 / hi if hi > 0 else np.nan, T2_hi=LN2 / lo if lo > 0 else np.nan,
                     source=source))


def ols(x, y):
    res = stats.linregress(x, np.log(y))
    t = stats.t.ppf(0.975, len(x) - 2)
    return res.slope, res.slope - t * res.stderr, res.slope + t * res.stderr, len(x)


def ends(y0, v0, y1, v1):
    return np.log(v1 / v0) / (y1 - y0)


def hinge(x, y, candidates):
    best = None
    for c in candidates:
        X = np.column_stack([np.ones_like(x), x, np.clip(x - c, 0, None)])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        sse = float(np.sum((y - X @ coef) ** 2))
        if best is None or sse < best[1]:
            best = (c, sse, coef)
    return best


# ---- Great Acceleration: world primary energy, annual
en = pd.read_csv(f"{RAW}/owid_global_primary_energy.csv")
en = en[en.entity == "World"].set_index("year").drop(columns=["entity", "code"]).sum(axis=1)
e = en.loc[1950:2010]
b, lo, hi, n = ols(e.index.to_numpy(float), e.to_numpy())
add("Great Acceleration", "World primary energy", "1950–2010", b, lo, hi, n, "OLS, annual",
    source="Our World in Data (Smil 2017; Energy Institute)")
e2 = en.loc[2010:2019]
b, lo, hi, n = ols(e2.index.to_numpy(float), e2.to_numpy())
add("Cloud era", "World primary energy (reference)", "2010–2019", b, lo, hi, n, "OLS, annual",
    source="Our World in Data")

# ---- Cloud era: data-centre electricity
add("Cloud era", "Data-centre electricity, world", "2010–2018", ends(2010, 1.0, 2018, 1.06),
    source="Masanet et al. (2020): +6% (LBNL summary)")
add("Cloud era", "Data-centre electricity, US", "2014–2018", np.log(1.07),
    source="Shehabi et al. (2024): ~7%/yr as stated")

# ---- AI era
add("AI era", "Data-centre electricity, US", "2018–2023", np.log(1.18),
    source="Shehabi et al. (2024): ~18%/yr as stated")
add("AI era", "Data-centre electricity, world (projected)", "2024–2030", ends(2024, 415, 2030, 945), projected=True,
    source="IEA (2025) base case: 415 -> 945 TWh")
d = pd.read_csv(f"{RAW}/epoch_notable_ai_models.csv", low_memory=False)[["Publication date", "Training compute (FLOP)"]].dropna()
d = d[d["Training compute (FLOP)"] > 0]
dt = pd.to_datetime(d["Publication date"], errors="coerce")
x = (dt.dt.year + (dt.dt.day_of_year - 1) / 365.25).to_numpy()
y = d["Training compute (FLOP)"].to_numpy()
m = (x >= 2010) & np.isfinite(x)
b, lo, hi, n = ols(x[m], y[m])
add("AI era", "AI training compute, notable models", "2010–2026", b, lo, hi, n, "OLS, per model",
    source="Epoch AI Notable AI Models")

t = pd.DataFrame(rows)
t.to_csv("data/processed/growth_table.csv", index=False)
pd.set_option("display.width", 200)
print(t[["phase", "series", "period", "method", "n", "r_pct", "r_lo", "r_hi", "T2", "T2_lo", "T2_hi"]].round(2).to_string(index=False))

# ---- breakpoint tests on the two long annual series
ex = en.loc[1900:2019]
bp = hinge(ex.index.to_numpy(float), np.log(ex.to_numpy()), np.arange(1920, 2011))
pre = 100 * (np.exp(bp[2][1]) - 1); post = 100 * (np.exp(bp[2][1] + bp[2][2]) - 1)
print(f"\nworld energy 1900-2019: breakpoint {bp[0]:.0f}; growth {pre:.2f}%/yr before, {post:.2f}%/yr after")
ex = en.loc[1950:2019]
bp = hinge(ex.index.to_numpy(float), np.log(ex.to_numpy()), np.arange(1960, 2016))
pre = 100 * (np.exp(bp[2][1]) - 1); post = 100 * (np.exp(bp[2][1] + bp[2][2]) - 1)
print(f"world energy 1950-2019: breakpoint {bp[0]:.0f}; growth {pre:.2f}%/yr before, {post:.2f}%/yr after")
mm = np.isfinite(x)
bp = hinge(x[mm], np.log10(y[mm]), np.arange(1990, 2016.01, 0.25))
pre = bp[2][1]; post = bp[2][1] + bp[2][2]
print(f"AI training compute: breakpoint {bp[0]:.2f}; doubling {np.log10(2)/pre:.2f} yr before, {np.log10(2)/post:.2f} yr after")
print("years in OWID world series:", en.index.min(), "-", en.index.max(), "n 1950-2010 =", len(en.loc[1950:2010]))

# ---- window sensitivity of the world-energy breakpoint (reported on slide 18)
for a0, a1 in [(1950, 2019), (1990, 2019), (1965, 2019), (1900, 2019)]:
    e = en.loc[a0:a1]
    bp = hinge(e.index.to_numpy(float), np.log(e.to_numpy()), np.arange(a0 + 5, a1 - 4))
    print(f"world energy {a0}-{a1}: best single break {bp[0]:.0f}")
print("years before 1965 in the OWID series:", [y for y in en.index if 1900 <= y < 1965])
