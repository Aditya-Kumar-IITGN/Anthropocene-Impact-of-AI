# O2 · Materials, water and waste: work plan (Aryan)

The submitted plan commits O2 to: **water-stress exposure of capacity and nearby people, water
use, water sources (and distance to source), and the geography of critical minerals and
e-waste.** In the deck, this fills four slides (O2a–O2d) and parts of deliverables D1 (atlas)
and D3 (regional table).

Environment: `geo` conda env (geopandas, rasterio, geopy) for all O2 scripts. `mktg` stays untouched.

---

## Steps

| # | Step | Output | Feeds | Status |
|---|---|---|---|---|
| 1 | **Site table.** 96 Epoch AI data centres: current MW, plus planned MW by 2030 from `data_center_timelines.csv`. Geocode the 82 addresses (Nominatim, ≤1 request/s, cached); place the 14 without an address by hand from name/project; record precision (street / city) | `data/processed/sites.csv` | all | ✅ done: 96/96 geocoded, 0 state or country mismatches |
| 2 | **Water-stress join.** Point-in-basin join to Aqueduct 4.0: baseline `bws_cat`, future `bau30_ws_x_c`, `bau50_ws_x_c` (BAU; pessimistic as a sensitivity check). Share of **sites** vs share of **MW** (now, and planned 2030) in high or extremely high stress | `sites_water.csv`, Fig O2a (map), Fig O2b (bars) | slides O2a, O2b | ✅ done: on slides 20–21 |
| 3 | **People exposed.** GHSL population grid (GHS-POP, 1 km): people within 25 and 50 km of sites in high or extremely high stress basins | numbers on O2b | slide O2b, D3 | ✅ done: 21 M within 25 km, 48 M within 50 km |
| 4 | **Water-use range.** Per site: E_IT = IT MW × utilisation × 8,760 h. Direct = E_IT × WUE; indirect = E_IT × PUE × WI_grid (country). Low/high bounds from published ranges. Checks: the ≈10 sites with non-zero reported use in Epoch, and the global total from de Vries-Gao (2026) | `water_use.csv`, Fig O2c | slide O2c, D3 | ✅ done: slide 22 |
| 5 | **Water source and distance.** For the 4 case clusters (N. Virginia, Phoenix, Dublin, Johor) and the Epoch sites with reported use: source type (groundwater / municipal / reclaimed / desalinated) and distance to it, from utility, permit and company records | two case slides | slides 23–25 | ✅ done: two news-based case studies (Mesa, Visakhapatnam) instead of four clusters, by choice |
| 6 | **Minerals and e-waste.** USGS Mineral Commodity Summaries 2026: top-producer shares for Ga, Ge, rare earths, Cu (+ Co, high-purity quartz if available) vs where AI capacity sits. Global E-waste Monitor: generation vs formal collection by region | Fig O2d | slide O2d | ✅ done: slide 26 |

Order: 1 → 2 → 3 make the core result (today). 4 and 6 are independent. 5 is reading, not
code, and can run alongside.

## Metric definitions (state these on the slides)

- **High / extremely high baseline water stress:** Aqueduct `bws_cat` ≥ 3 (withdrawals ≥ 40% of
  available renewable supply). "Arid and low water use" (`bws_cat` = −1) is reported separately,
  not lumped in.
- **Rosa et al. (2026) is a different metric:** demand > renewable supply in ≥1 month a year,
  2001–2010 conditions: 2,315 of 9,347 sites (≈25%), ≈33% at 3 °C. We compare against it but do
  not call ours a size-weighted version of theirs.
- **Size weighting:** by current power (MW) where reported; planned 2030 MW for the forward
  view. Sites with neither are counted in the site share only.

## Data quality notes

- Epoch covers **AI-specific** sites (96, 83% of MW in the US), not all data centres. Our
  result is "AI capacity", which is the project's definition of AI anyway.
- Reported water use: 25 sites have a value, but most are 0 (probably closed-loop or air
  cooling, or not disclosed). It is a check, not a sample.
- Geocoding precision varies (some addresses are city-level). That is fine for basin
  joins (HydroBASINS level-6 basins are large), but distances to source must use case-study
  records, not geocodes.

## Decisions (defaults in bold)

1. Site universe: **Epoch AI sites only**, or also build an all-data-centre layer from
   OpenStreetMap/IM3 with footprint-calibrated MW (as written in the submitted plan; days of
   work, and Rosa et al. already give the site-count view)?
2. Future scenario: **BAU for 2030/2050, with pessimistic as a range**, or BAU only?

## Results so far (10 Nov)

| Share in high or extremely high stress | Sites | Current MW | Planned 2030 MW |
|---|---|---|---|
| Baseline (annual) | 36.5% | 34.4% | 38.6% |
| 2030 BAU | 37.5% | 36.7% | 45.4% |
| 2050 BAU | 36.5% | 36.2% | 39.8% |
| 2050 pessimistic | 50.0% | 51.5% | 61.8% |
| Rosa-like monthly (≥1 month withdrawals > supply) | 21.9% | 18.3% | 23.8% |

- 15.1 GW today → 50.3 GW planned by 2030. Capacity in stressed basins grows 3.7×, against 3.1× elsewhere.
- Planned MW in stressed basins is led by Texas (7.3 GW; Abilene, Shackelford, Goodnight, Helios),
  New Mexico (2.7 GW; Stargate), Indiana (2.3 GW; New Carlisle), Virginia (1.9 GW), Abu Dhabi
  (1.4 GW) and Ulanqab.
- Our Rosa-like site share (22%) is close to Rosa et al.'s 25%: a sanity check of the join.
- Caveat for Q&A: annual stress counts *all* withdrawals, including thermal power-plant cooling,
  which is why Indiana and western New York score "high".

## Review (10 Nov)

- All numbers reproduce from the scripts. Every claim in claims.csv is verified.
- Corrected: Mesa water deal (reported 2020, 1 M gal/day guaranteed, up to 4 M); Duff's vote was on a
  different data centre; Asia e-waste 6.4 kg/cap; Ga/Ge ban on US suspended to 27 Nov 2026; map caption
  ("many of", not "the largest"); gold removed from figures; methods slide 1 no longer mentions a footprint model.
- Slide 21 headline now 34% → 39–45%: the 2030 step is mostly two borderline Gulf Coast basins.
- Added: locator map (method 5), Vizag basin check inside case_studies.py, speaker notes (`notes.tex` → `notes.pdf`).
