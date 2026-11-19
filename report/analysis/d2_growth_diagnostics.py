"""Deliverable D2: fit diagnostics for the growth table (the deck's growth_table.py fits, re-run and checked).

Run:  /Users/aryan/miniforge3/envs/geo/bin/python -I report/analysis/d2_growth_diagnostics.py
Inputs (read-only): ../proposal/data/raw/owid_global_primary_energy.csv (Our World in Data),
                    ../proposal/data/raw/epoch_notable_ai_models.csv (Epoch AI, accessed 26 Oct 2026)
Outputs: report/data/d2_diagnostics.csv, report/data/d2_breaks.csv, report/figs/d2_diagnostics.pdf

For each OLS fit ln y = a + b t:
  r = e^b - 1, T2 = ln2 / b; R^2; residual SD; Durbin-Watson d and lag-1 residual autocorrelation (annual series);
  a Newey-West (HAC, Bartlett kernel) standard error for b, giving an autocorrelation-robust 95% interval on T2.
Breakpoints: continuous two-segment (hinge) fit, break year chosen by least SSE (as in growth_table.py), plus
the BIC change from one to two segments (break year counted as a parameter) and the growth rate on each side.
The data-centre rows of the growth table rest on two published values each: no fit, so no diagnostics.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

LN2 = np.log(2)

en = pd.read_csv(os.path.join(PROPOSAL_RAW, "owid_global_primary_energy.csv"))
en = en[en.entity == "World"].set_index("year").drop(columns=["entity", "code"]).sum(axis=1)
d = pd.read_csv(os.path.join(PROPOSAL_RAW, "epoch_notable_ai_models.csv"), low_memory=False)[
    ["Publication date", "Training compute (FLOP)"]].dropna()
d = d[d["Training compute (FLOP)"] > 0]
dt = pd.to_datetime(d["Publication date"], errors="coerce")
cx = (dt.dt.year + (dt.dt.day_of_year - 1) / 365.25).to_numpy()
cy = d["Training compute (FLOP)"].to_numpy()
ok = np.isfinite(cx)
cx, cy = cx[ok], cy[ok]


def nw_se(x, e, L):
    """Newey-West HAC standard error of the OLS slope (Bartlett weights, L lags)."""
    X = np.column_stack([np.ones_like(x), x])
    XtX_inv = np.linalg.inv(X.T @ X)
    u = X * e[:, None]
    S = u.T @ u
    for l in range(1, L + 1):
        g = u[l:].T @ u[:-l]
        S += (1 - l / (L + 1)) * (g + g.T)
    V = XtX_inv @ S @ XtX_inv
    return np.sqrt(V[1, 1])


def fit(name, period, x, y, annual=True):
    ly = np.log(y)
    res = stats.linregress(x, ly)
    e = ly - (res.intercept + res.slope * x)
    n = len(x)
    t = stats.t.ppf(0.975, n - 2)
    out = dict(series=name, period=period, n=n, r_pct=100 * (np.exp(res.slope) - 1), T2=LN2 / res.slope,
               T2_lo=LN2 / (res.slope + t * res.stderr), T2_hi=LN2 / (res.slope - t * res.stderr),
               r2=res.rvalue ** 2, resid_sd=e.std(ddof=2))
    if annual:
        out["dw"] = np.sum(np.diff(e) ** 2) / np.sum(e ** 2)
        out["rho1"] = np.corrcoef(e[:-1], e[1:])[0, 1]
        L = int(np.floor(4 * (n / 100) ** (2 / 9)))
        se = nw_se(x, e, L)
        out.update(nw_lags=L, T2_lo_hac=LN2 / (res.slope + t * se), T2_hi_hac=LN2 / (res.slope - t * se))
    else:  # one point per model: residual spread in orders of magnitude is the useful number
        out["resid_sd_log10"] = e.std(ddof=2) / np.log(10)
    return out, e


def hinge(x, ly, candidates):
    prof = []
    for c in candidates:
        X = np.column_stack([np.ones_like(x), x, np.clip(x - c, 0, None)])
        coef, *_ = np.linalg.lstsq(X, ly, rcond=None)
        prof.append((c, float(np.sum((ly - X @ coef) ** 2)), coef))
    best = min(prof, key=lambda p: p[1])
    X1 = np.column_stack([np.ones_like(x), x])
    c1, *_ = np.linalg.lstsq(X1, ly, rcond=None)
    sse1 = float(np.sum((ly - X1 @ c1) ** 2))
    n = len(x)
    dbic = (n * np.log(best[1] / n) + 4 * np.log(n)) - (n * np.log(sse1 / n) + 2 * np.log(n))
    return best, dbic, np.array([(p[0], p[1]) for p in prof])


rows, breaks, profiles = [], [], {}
e5010 = en.loc[1950:2010]
o, resid_ga = fit("World primary energy", "1950–2010", e5010.index.to_numpy(float), e5010.to_numpy())
rows.append(o)
e1019 = en.loc[2010:2019]
o, _ = fit("World primary energy", "2010–2019", e1019.index.to_numpy(float), e1019.to_numpy())
rows.append(o)
m = cx >= 2010
o, _ = fit("AI training compute", "2010–2026", cx[m], cy[m], annual=False)
rows.append(o)

for a0, a1 in [(1950, 2019), (1990, 2019)]:
    e = en.loc[a0:a1]
    x, ly = e.index.to_numpy(float), np.log(e.to_numpy())
    best, dbic, prof = hinge(x, ly, np.arange(a0 + 5, a1 - 4))
    b0, b1 = best[2][1], best[2][1] + best[2][2]
    breaks.append(dict(series="World primary energy", window=f"{a0}–{a1}", n=len(x), break_year=best[0],
                       r_before_pct=100 * (np.exp(b0) - 1), r_after_pct=100 * (np.exp(b1) - 1), delta_bic=dbic))
    profiles[f"World energy, {a0}–{a1}"] = prof
best, dbic, prof = hinge(cx, np.log(cy), np.arange(1990, 2016.01, 0.25))
b0, b1 = best[2][1], best[2][1] + best[2][2]
breaks.append(dict(series="AI training compute", window=f"{int(cx.min())}–{int(cx.max())}", n=len(cx),
                   break_year=best[0], r_before_pct=100 * (np.exp(b0) - 1), r_after_pct=100 * (np.exp(b1) - 1),
                   T2_before=LN2 / b0, T2_after=LN2 / b1, delta_bic=dbic))
profiles["AI compute, all models"] = prof

D = pd.DataFrame(rows); B = pd.DataFrame(breaks)
D.to_csv(os.path.join(DATA, "d2_diagnostics.csv"), index=False)
B.to_csv(os.path.join(DATA, "d2_breaks.csv"), index=False)
pd.set_option("display.width", 220)
print(D.round(3).to_string(index=False)); print(B.round(3).to_string(index=False))

# ------------------------------------------------------------------ figure: (a) residuals, (b) break profiles
fig, (a, b) = plt.subplots(2, 1, figsize=(COL, 3.25), gridspec_kw={"hspace": 0.62, "height_ratios": [1, 1]})
yrs = e5010.index.to_numpy()
a.axhline(0, color=MUTED, lw=0.5)
a.plot(yrs, 100 * resid_ga, color=PHASE["ga"], lw=0.9, marker="o", ms=1.8)
a.axvline(1973.5, color=MUTED, lw=0.5, ls=(0, (2, 1.5)))
a.text(1975.2, -27, "best single break\n(1950–2019): 1974", fontsize=6, color=MUTED, va="center")
a.set_ylabel("Residual (%)")
a.set_xlim(1948, 2012)
a.set_title("(a) World primary energy, 1950–2010: residuals from one growth rate", loc="left", fontsize=7)
clean(a)
styles = {"World energy, 1950–2019": (PHASE["ga"], "-"), "World energy, 1990–2019": (PHASE["ga"], (0, (2, 1.2))),
          "AI compute, all models": (PHASE["ai"], "-")}
for k, prof in profiles.items():
    c, ls = styles[k]
    rel = prof[:, 1] / prof[:, 1].min()
    b.plot(prof[:, 0], rel, color=c, ls=ls, lw=0.9, label=k)
    i = np.argmin(prof[:, 1])
    b.plot(prof[i, 0], 1, "o", color=c, ms=3)
b.set_ylim(0.95, 2.6)
b.set_xlim(1955, 2016)
b.set_ylabel("SSE / minimum SSE")
b.set_xlabel("Candidate break year")
b.set_title("(b) Two-segment fit: where does the break fall?", loc="left", fontsize=7)
b.legend(loc="upper left", frameon=False, handlelength=2.0)
clean(b)
save(fig, "d2_diagnostics.pdf")
