"""Deliverable D1: one atlas figure set. Capacity, water stress and population on the same maps (full text width).

Run:  /Users/aryan/miniforge3/envs/geo/bin/python -I report/analysis/fig_d1_atlas.py      (~1-2 min)
Inputs (read-only):
  presentation/data/processed/sites_water.csv        96 Epoch AI sites, geocoded, joined to Aqueduct (deck step 2)
  Aqueduct 4.0 GDB, layer baseline_annual             basin polygons and baseline water-stress category
  GHSL GHS-POP E2025 R2023A 30ss                      population grid (same file as the exposure counts)
Output: report/figs/d1_atlas.pdf

Panels: (a) contiguous US and (b) world over Aqueduct baseline water stress; (c) contiguous US and (d) world over
population density. Markers are the same in every panel: filled dot = current facility MW, open ring = planned
end-2030 MW (area proportional to MW). In (a)-(b), a thick navy ring marks the 4 sites whose basin is below "high"
today but high or extremely high under Aqueduct's 2030 business-as-usual projection (bau30_ws_x_c >= 3); in (c)-(d)
markers are red if the site's basin is in high or extremely high baseline stress, navy otherwise.
Population density = GHSL people per cell, block-averaged, divided by cell area (km^2), then reprojected.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import rasterio  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, LogNorm  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from rasterio.enums import Resampling  # noqa: E402
from rasterio.transform import from_bounds as tfb  # noqa: E402
from rasterio.warp import reproject  # noqa: E402
from rasterio.windows import from_bounds  # noqa: E402
need(GDB, GHSL)

W, H = FULL, 4.70
US_CRS, W_CRS = "EPSG:5070", "EPSG:8857"                       # Albers equal-area (US), Equal Earth (world)
US_X, US_Y = (-2.40e6, 2.30e6), (0.25e6, 3.20e6)
W_X, W_Y = (-17.3e6, 17.3e6), (-6.2e6, 8.6e6)
K = 0.032                                                        # marker area (pt^2) per MW


def size(mw):
    return np.asarray(mw, float) * K


s = pd.read_csv(os.path.join(PROC, "sites_water.csv"))
s["now"] = s.current_mw.fillna(0)
s["plan"] = s.planned_2030_mw.fillna(s.current_mw).fillna(0)
s["stressed"] = s.bws_cat >= 3
s["enters"] = (s.bws_cat < 3) & (s.bau30_ws_x_c >= 3)
print("sites entering high stress by 2030 BAU:", s.loc[s.enters, "name"].tolist())
pts = gpd.GeoDataFrame(s, geometry=gpd.points_from_xy(s.lon, s.lat), crs="EPSG:4326")

basins = gpd.read_file(GDB, layer="baseline_annual", columns=["bws_cat"]).to_crs("EPSG:4326")
basins["geometry"] = basins.geometry.simplify(0.03, preserve_topology=False)
basins = basins[~basins.geometry.is_empty]
basins["color"] = basins.bws_cat.map(AQUEDUCT).fillna("#E6E6E6")
b_us = basins.cx[-130:-60, 20:55].to_crs(US_CRS)
b_w = basins.to_crs(W_CRS)


def density(bounds, factor):
    """GHSL block-averaged to `factor` x coarser cells, as people per km^2, with its lon/lat transform."""
    with rasterio.open(GHSL) as src:
        win = from_bounds(*bounds, src.transform).round_offsets().round_lengths()
        shape = (int(win.height // factor), int(win.width // factor))
        a = src.read(1, window=win, out_shape=shape, resampling=Resampling.average, masked=True).filled(0)
        a = np.clip(a.astype("float64"), 0, None)
        tr = tfb(*bounds, shape[1], shape[0])
    lat = bounds[3] - (np.arange(shape[0]) + 0.5) * (bounds[3] - bounds[1]) / shape[0]
    cell_km2 = (30 / 3600 * 111.32) ** 2 * np.cos(np.radians(lat))
    return a / cell_km2[:, None], tr


def to_crs(arr, tr, crs, xlim, ylim, res):
    nx, ny = int((xlim[1] - xlim[0]) / res), int((ylim[1] - ylim[0]) / res)
    dst = np.zeros((ny, nx), "float64")
    reproject(arr, dst, src_transform=tr, src_crs="EPSG:4326", dst_transform=tfb(xlim[0], ylim[0], xlim[1], ylim[1],
              nx, ny), dst_crs=crs, resampling=Resampling.average)
    return np.ma.masked_less(dst, 5)


d_us, t_us = density((-128.0, 20.0, -62.0, 53.0), 4)
d_w, t_w = density((-180.0, -60.0, 180.0, 84.0), 20)
p_us = to_crs(d_us, t_us, US_CRS, US_X, US_Y, 4000)
p_w = to_crs(d_w, t_w, W_CRS, W_X, W_Y, 25000)
POP_CMAP = LinearSegmentedColormap.from_list("pop", ["#E9E9EC", "#9A9AA6", "#3A3A48"])
POP_NORM = LogNorm(vmin=5, vmax=3000)


def markers(ax, p, mode):
    if mode == "stress":
        ring_c = np.where(p.enters, NAVY, INK)
        ring_w = np.where(p.enters, 1.15, 0.45)
        dot_c = INK
    else:
        ring_c = np.where(p.stressed, RED, NAVY)
        ring_w = 0.55
        dot_c = np.where(p.stressed, RED, NAVY)
    ax.scatter(p.geometry.x, p.geometry.y, s=size(p.plan), facecolor="none", edgecolor=ring_c, linewidth=ring_w,
               zorder=3)
    ax.scatter(p.geometry.x, p.geometry.y, s=size(p.now), facecolor=dot_c, edgecolor="white", linewidth=0.25,
               alpha=0.9, zorder=4)


def panel(rect, title, crs, xlim, ylim, mode):
    ax = fig.add_axes(rect)
    b = b_us if crs == US_CRS else b_w
    if mode == "stress":
        b.plot(ax=ax, color=b.color, linewidth=0, alpha=0.65, rasterized=True)
    else:
        b.plot(ax=ax, color="#F6F6F6", linewidth=0, rasterized=True)
        img = p_us if crs == US_CRS else p_w
        ax.imshow(img, extent=(xlim[0], xlim[1], ylim[0], ylim[1]), origin="upper", cmap=POP_CMAP, norm=POP_NORM,
                  interpolation="nearest", zorder=2, rasterized=True)
    sel = (s.country.eq("United States") & s.lon.between(-125, -66)) if crs == US_CRS else np.ones(len(s), bool)
    markers(ax, pts[np.asarray(sel)].to_crs(crs), mode)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_axis_off()
    ax.set_title(title, loc="left", fontsize=7, pad=1.5, color=INK)
    return ax


fig = plt.figure(figsize=(W, H))
UW = 3.45                                     # US panel width (in); height follows the Albers extent
UH = UW * (US_Y[1] - US_Y[0]) / (US_X[1] - US_X[0])
WW = 3.22
WH = WW * (W_Y[1] - W_Y[0]) / (W_X[1] - W_X[0])
top1, top2 = H - 0.14, H - 0.14 - UH - 0.25
ax_a = panel([0, (top1 - UH) / H, UW / W, UH / H], "(a) Contiguous United States: water stress", US_CRS, US_X, US_Y,
             "stress")
ax_b = panel([(W - WW) / W, (top1 - WH) / H, WW / W, WH / H], "(b) World: water stress", W_CRS, W_X, W_Y, "stress")
ax_c = panel([0, (top2 - UH) / H, UW / W, UH / H], "(c) Contiguous United States: population", US_CRS, US_X, US_Y,
             "pop")
ax_d = panel([(W - WW) / W, (top2 - WH) / H, WW / W, WH / H], "(d) World: population", W_CRS, W_X, W_Y, "pop")


# a few labels for places named in the text
def label(ax, crs, lon, lat, text, dx, dy, ha="left"):
    p = gpd.GeoSeries(gpd.points_from_xy([lon], [lat]), crs="EPSG:4326").to_crs(crs).iloc[0]
    ax.annotate(text, (p.x, p.y), xytext=(dx, dy), textcoords="offset points", fontsize=5.6, ha=ha, va="center",
                color=INK, arrowprops=dict(arrowstyle="-", lw=0.4, color=INK, shrinkA=0, shrinkB=2), zorder=6,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))


label(ax_a, US_CRS, -111.83, 33.415, "Google Mesa", -6, -16, ha="right")
label(ax_a, US_CRS, -91.6, 32.5, "Meta Hyperion", 16, -14)
label(ax_b, W_CRS, 112.0, 41.0, "Inner Mongolia", 4, 18, ha="center")
label(ax_b, W_CRS, 54.4, 24.4, "Abu Dhabi", -10, -12, ha="right")
label(ax_b, W_CRS, 103.7, 1.5, "Johor", -12, -9, ha="right")

# ---- legends: stress row (under panel b), population row (under panel d)
xl = (W - WW) / W
stress_h = [Patch(facecolor=AQUEDUCT[k], alpha=0.8, label=AQUEDUCT_LABEL[k]) for k in (0, 1, 2, 3, 4, -1)]
fig.legend(handles=stress_h, loc="upper left", bbox_to_anchor=(xl, (top1 - WH - 0.06) / H), ncol=3, frameon=False,
           fontsize=6, handlelength=1.0, columnspacing=0.9, labelspacing=0.35,
           title="Baseline water stress (withdrawals / renewable supply)", title_fontsize=6, alignment="left")
mk = dict(ls="", marker="o")
mark_h = [Line2D([], [], ms=4.0, mfc=INK, mec="white", **mk, label="Current MW (dot)"),
          Line2D([], [], ms=6.5, mfc="none", mec=INK, mew=0.45, **mk, label="Planned 2030 MW (ring)"),
          Line2D([], [], ms=6.5, mfc="none", mec=NAVY, mew=1.15, **mk, label="Basin high by 2030 (BAU)")]
fig.legend(handles=mark_h, loc="upper left", bbox_to_anchor=(xl, (top1 - WH - 0.55) / H), ncol=3, frameon=False,
           fontsize=6, handlelength=1.0, columnspacing=0.8, handletextpad=0.3)
pop_h = [Line2D([], [], ms=4.5, mfc=RED, mec="white", **mk, label="Site in high or extremely high stress"),
         Line2D([], [], ms=4.5, mfc=NAVY, mec="white", **mk, label="Site in lower stress")]
fig.legend(handles=pop_h, loc="upper left", bbox_to_anchor=(xl, (top2 - WH - 0.04) / H), ncol=2, frameon=False,
           fontsize=6, handlelength=0.8, columnspacing=0.9, handletextpad=0.3)
size_h = [Line2D([], [], ms=np.sqrt(size(v)), mfc="none", mec=MUTED, mew=0.5, **mk, label=f"{v:,} MW")
          for v in (100, 500, 2000)]
fig.legend(handles=size_h, loc="upper left", bbox_to_anchor=(xl, (top2 - WH - 0.20) / H), ncol=3, frameon=False,
           fontsize=6, handlelength=1.6, columnspacing=1.2, handletextpad=0.3,
           title="Marker area, all panels", title_fontsize=6, alignment="left")
cax = fig.add_axes([xl + 0.01, 0.15 / H, 0.55 * WW / W, 0.065 / H])
cb = fig.colorbar(plt.cm.ScalarMappable(norm=POP_NORM, cmap=POP_CMAP), cax=cax, orientation="horizontal")
cb.set_ticks([10, 100, 1000], labels=["10", "100", "1,000"])
cb.ax.tick_params(labelsize=6, length=2, width=0.4)
cb.outline.set_linewidth(0.4)
cb.set_label("Population density, people per km$^2$ (GHSL 2025)", fontsize=6, labelpad=2)
save(fig, "d1_atlas.pdf")
