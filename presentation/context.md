# Context: EH627 final presentation (hand-off, 10 Nov 2026)

Read this first in a new chat. It records what exists, how to build it, what was decided, and
what is still open. Details live in [TEMPLATE_PLAN.md](TEMPLATE_PLAN.md) (deck design),
[O2_PLAN.md](O2_PLAN.md) (Aryan's objective) and [data/claims.csv](data/claims.csv) (every
number on a slide and its source).

---

## 1. The project

- **Course:** EH627 *Anthropocene: Human Impact on the Earth*, IIT Gandhinagar (Earth Sciences).
  The project is worth 20 marks: 10 for the presentation, 10 for the report.
- **Title:** *The Regional Footprint of AI Data Centres: Energy, Water, Materials and Planetary Boundaries*.
- **Group:** Aryan (the user), Aditya, Prerna.
- **Source of truth for content:** the submitted plan,
  [references_aditya_work/EH627_Project_Plan.pdf](references_aditya_work/EH627_Project_Plan.pdf).
  [../preliminary_report/EH627_Preliminary_Report.tex](../preliminary_report/EH627_Preliminary_Report.tex)
  is almost the same text.
- **Framing:** three phases since 1950: Great Acceleration (1950–2010), cloud era (2010–2018),
  AI era (2019→). The question: *why did cloud growth leave energy use almost flat, while AI
  growth does not?* In this project, "AI" means data-centre infrastructure.
- **Objectives and owners:** O1 energy and carbon (**Aditya**), O2 materials, water and waste
  (**Aryan**), O3 economy, politics and society (**Prerna**), O4 synthesis (all).
- **Earlier work, now superseded:** the 27 Oct proposal deck in [../proposal/](../proposal/)
  used a pre-industrial / industrial / AI framing. Reusable pieces: its doubling-time code
  (`make_figures.py`, Epoch compute and OWID energy fits) and `build_pptx.py`.

## 2. Final presentation format (decided with the user)

- About **30 minutes** in total; date in mid/late November, exact date not recorded.
- **PDF** output (no .pptx). **16:9.**
- Visual style: **Gotham** ([latextemplates.com/pdfs/gotham-beamer.pdf](https://latextemplates.com/pdfs/gotham-beamer.pdf)),
  rebuilt on metropolis. Section **divider slides kept** (the user likes the breaks).
  Results also gets light sub-dividers per objective.
- Structure follows the professor's outline ([../outline.md](../outline.md)): Statement and
  problem · Objectives · Data and methods · Results · Expected deliverables · Summary and
  conclusions · Bibliography.
- Names only on the title slide (no roll numbers, no presenter assignment).

## 3. Folder map

```
presentation_slides/
├── context.md                 # this file
├── TEMPLATE_PLAN.md           # deck design, slide types, how-to (§9)
├── O2_PLAN.md                 # Aryan's objective: steps, results, status
├── beamerthemegotham.sty      # theme: metropolis + Gotham colours, footer, dividers, blocks
├── main.tex                   # preamble, helper macros, title, overview, closing; \input sections
├── sections/1_problem.tex … 7_bibliography.tex   # one file per outline section
├── analysis/                  # all scripts (run from presentation_slides/)
│   ├── style.py               # shared figure style: LM Sans font, deck colours, Aqueduct palette
│   ├── geocode_sites.py       # O2 step 1: Epoch sites -> lat/lon (Nominatim, cached)
│   ├── water_stress.py        # O2 step 2: join to Aqueduct 4.0; count vs MW shares
│   ├── o2_figures.py          # Fig O2a map, Fig O2b bars
│   ├── population.py          # O2 step 3: GHSL people within 25/50 km (union)
│   ├── water_params.py        # shared WUE/PUE/grid-water ranges + sources
│   ├── water_use.py           # O2 step 4: direct/indirect water range, Fig O2c
│   ├── case_studies.py        # O2 step 5: Mesa + Vizag numbers and figures
│   └── materials.py           # O2 step 6: minerals and e-waste, Fig O2d
├── data/
│   ├── raw/                   # epoch/ (Aditya's CSVs, copied), aqueduct/, ghsl/, usgs/
│   ├── processed/             # sites.csv, sites_water.csv, water_use*.csv, population_exposure.csv,
│   │                          # materials.csv, ewaste_regions.csv, geocode_cache.csv
│   └── claims.csv             # ledger: every slide number + source + verified flag
├── figs/                      # generated PDFs only (o2a, o2b, o2c, o2d, case_mesa, case_vizag)
├── pics/                      # photos supplied by the user (see §7 caveat)
└── references_aditya_work/    # Aditya's material, read-only (Epoch dataset, de Vries-Gao paper, plan PDF)
```

## 3b. Two versions of the deck (since 12 Nov)

- **v0 (previous):** `main.tex` + `sections/` → `main.pdf`, `notes.tex` → `notes.pdf`. Left as it was
  before Aditya's material: O1/O3 placeholders, empty tables.
- **v1 (current):** `main_v1.tex` + `sections_v1/` → `main_v1.pdf`, `notes_v1.tex` → `notes_v1.pdf`.
  Adds Aditya's material from `Anthropocene_aditya_slides.pptx` (figures extracted to `pics/aditya/`,
  headlines cropped: `*_crop.png`). Edit **v1** from now on; figures, data and the theme are shared.
  v1 is **final** (`\draftfalse`, no to-dos or † left). Verification on 12 Nov corrected Aditya's EU grid
  intensity (179 → 212 g/kWh; slide 19 figure now ours, `analysis/o1_regional.py`, Ember CSV in
  `data/raw/ember/`) and dropped the unverifiable "833 opposition groups". All in claims.csv.

## 4. Build

```bash
cd /Users/aryan/Desktop/Academics/semester_7/eh_627/project/presentation_slides
GEO=/Users/aryan/miniforge3/envs/geo/bin/python     # geopandas, rasterio, geopy (made for O2)
$GEO -I analysis/geocode_sites.py   # only if sites change (uses cache)
$GEO -I analysis/water_stress.py
$GEO -I analysis/o2_figures.py
$GEO -I analysis/population.py
$GEO -I analysis/water_use.py
$GEO -I analysis/case_studies.py
$GEO -I analysis/materials.py
tectonic -X compile --keep-logs main.tex
grep -c Overfull main.log                      # must be 0
tectonic -X compile --keep-logs notes.tex      # speaker notes -> notes.pdf (\note{} blocks in the frames)
tectonic -X compile --keep-logs main_v1.tex    # v1 deck (current); notes_v1.tex for its notes
pdftoppm -png -r 110 main.pdf /tmp/s           # then LOOK at every slide
```

- **Two Python envs:** `geo` (made for O2) and `mktg` (`/Users/aryan/miniforge3/envs/mktg`,
  used by the proposal; it now has python-pptx). Do not install into `mktg`.
- **Tectonic** is at `/opt/homebrew/bin/tectonic`. The first build of a new package downloads it.
- **Draft mode:** `\drafttrue` in `main.tex` shows red to-do notes and † marks on unverified
  numbers. **Set `\draftfalse` for the final PDF.**

## 5. Theme and LaTeX gotchas (all hit and fixed)

- A frame whose body **starts with `{...}`** loses that content: Beamer reads it as a subtitle.
  Write `\begin{frame}{Title}{}`.
- **Latin Modern Sans lacks ≈, ₂, ≥, ∝**, both in LaTeX and in matplotlib. In LaTeX use
  `$\approx$`, `CO\textsubscript{2}`, `$T_2$`. In figures use plain words or `~`, `1+`.
- Fonts: the deck uses LM Sans (metropolis's fallback under Tectonic). `style.py` loads the same
  font for matplotlib from `~/Library/Caches/TectonicProject.Tectonic/bundles/data/*/lmsans*.otf`.
- Colours: chrome is slate `#2D3E50`, gold `#FFCC00` and track `#D6C6B7`. Data colours are
  `phaseGA #8C4A2F`, `phaseCloud #7E8A96` and `phaseAI #2E5EAA`. Never use gold for data.
- Helpers in `main.tex`: `\chk{}` (unverified †), `\todo{}`, `\figslot[w]{h}{label}` (placeholder),
  `\bignum[colour]{num}{caption}`, `\src{}` (source line), `\nodivider` (no divider before a section).
- Blocks (`\begin{block}{Our comment}`) are styled with a slate title and a light tint (theme).
- The **footer slide number = PDF page − 1** (the title slide is unnumbered).
- Shell safety: `rm` on a `$VAR` path is blocked by the harness; use literal paths or `"${VAR:?}"`.

## 6. Deck status, v1 (43 PDF pages; footer numbers from 18 on are +1 vs the rows below)

| Footer # | Slide | Status |
|---|---|---|
| 0–1 | Title, Overview | done |
| 2–6 | §1 Statement and problem | done; slide 4 PB picture (SRC); slide 5 now has Aditya's capacity map + IEA 45/25/15% split; Masanet "+6%" on slide 6 |
| 7–9 | §2 Objectives | done |
| 10–14 | §3 Data and methods | done; datasets table lists only sources actually used; methods 2 = Gini per person (7 groups); methods 4 says breakpoints not tested |
| 15–20 | §4 O1 (Aditya) | slide 18 = our D2 growth table (`analysis/growth_table.py`: three phases, CIs where annual data, breakpoints: compute 2011, world energy 1974); rest from his pptx: US growth 7 → 18 %/yr (T₂ 10.2 → 4.2 yr), AI servers <2 → >40 TWh, PUE 1.54 flat, IEA shares × Ember grid intensity |
| 20–28 | §4 O2 (Aryan) | done, with speaker notes |
| 29–31 | §4 O3 | done from Aditya's pptx: Lorenz (Gini proxy 0.927, 7 groups), Data Center Watch 833 / 75+ / $130 bn + grievance tags |
| 32–33 | §4 O4 | evidence-coded matrix (Q/D/N, Aditya's), with our O1/O2 numbers upgraded to Q |
| 35–36 | §5 Deliverables | D2 Complete (slide 18); D1, D3, D4 "In the report" with what the report adds (one atlas; country table with LQ + country Gini; the write-up) |
| 36–38 | §6 Conclusions | expected vs found filled: partly confirmed / partly supported / supported as a framework |
| 39–40 | Bibliography | complete except exact titles for Google, Mongabay, The Federal |
| 41 | Closing line | done |

Not carried over from Aditya's pptx: his "water-stress chart verification" slide (it re-checks our
slide 21, which already shows the same numbers).

**Speaker notes (v1, 12 Nov):** every content slide has a note (32 pages in `notes_v1.pdf`), written for a
reader with surface-level knowledge: a two-page primer on the title and overview slides, then per slide
"In one line / On the slide / Why it matters / Say / If asked" (macros `\NoteKey` etc. in `main_v1.tex`).
About 30–40 minutes to read end to end. No presenter names in the notes.

**Review prompt:** `REVIEW_PROMPT.md` (read-only cross-validation by a fresh session; run with
`claude --permission-mode plan`).

## 7. O2 (Aryan): results, all on slides 21–28 (footer numbers in the table below are pre-shift: add 1)

Data: Epoch AI "AI data centers" (96 sites; 15.1 GW today, 50.3 GW planned by end-2030 from the
timelines file), geocoded 96/96, with 0 country or state mismatches after a fix (the first run's
fallback geocoded about a dozen sites to "USA"; queries are now restricted by country code).

| Slide | Headline | Key numbers |
|---|---|---|
| 20 | The AI build-out is heading into dry basins | map: markers = all 96 sites (dot = current MW, ring = planned 2030 MW); background = Aqueduct baseline stress |
| 21 | By size, 34% of AI capacity is in stressed basins today, 39–45% by 2030 | high or extremely high: sites 36.5%, current MW 34.4%, planned MW 38.6% (baseline), 45.4% (2030 BAU), 61.8% (2050 pessimistic). Stressed capacity grows 3.7× vs 3.1× elsewhere. Rosa-like monthly test 21.9% of sites (Rosa et al. 25%). **21 M people within 25 km of stressed sites, 48 M within 50 km** |
| 22 | Most of the water is used at power plants, not on site | today 143–624 bn L/yr; 2030 plan 478–2,082; indirect 67–86%; direct in stressed basins 16–30 → 61–111 bn L/yr; reported sites 0.001–7 L/kWh. Parameters from de Vries-Gao (2026); load factor 70–90% is **our assumption** |
| 23 | Two case studies (pictures) | see caveat below |
| 24 | Case 1 · Google Mesa | 183 → 237 MW; extremely high stress, withdrawals > supply 12/12 months; deal reported 2020 (Bloomberg): 1 M gal/day guaranteed, up to 4 M (15 M L); Duff's lone no-vote (2021) was on a *different*, Facebook-linked data centre; Mesa water 53% Colorado River via CAP canal (~300 km to Phoenix), 40% Salt/Verde, 7% groundwater; Lower Basin cuts 1.25 MAF/yr 2027–28 (Reclamation, 21 Aug 2026) |
| 25 | Case 2 · Visakhapatnam | 1 GW, ~US$15 bn, foundation stone 28 Apr 2026; city 410 vs 480 M L/day; clearance does not disclose operational water; state says supply from Polavaram pipelines; Google/AdaniConneX say air cooling; "We cannot drink data". Our comment: basin medium–high (20–40%); air cooling still means ~17–98 M L/day at the power plants (4–24% of city supply; US-derived grid factors) |
| 26 | Minerals are mined in one place, used in another, discarded in a third | USGS MCS 2026: China 99% Ga, 69% rare earths (mine), 48% Cu refining; DRC 74% cobalt; Chile 23% Cu mine; US 86% of planned AI MW. E-waste collection Europe 42.8% → Africa 0.7% (Asia 6.4 kg/cap). Ga/Ge ban on US suspended until 27 Nov 2026 |
| 27 | Against a global boundary AI's water barely registers; in a basin it does | Earth3 (Collste et al. 2018, p. 27): freshwater withdrawals safe < 3,000, high-risk > 4,000 km³/yr; 2030 plan 0.5–2.1 km³ = <0.1% (consumption vs a withdrawal limit, stated); vs Mesa 12/12 months and Vizag 4–24% |

Decisions: **Epoch AI sites only** (no OSM footprint layer); **BAU 2030/2050 + pessimistic as a
range**; **two news-based case studies instead of four clusters** (the user wants fewer, more
thorough items, all cited); Vizag is not on the map because it is not in the Epoch data.

Caveats to remember:
- `pics/google_mesa_az.png` is **not Mesa** (wind turbines and grassland; it looks like Google's
  Eemshaven site in the Netherlands). `pics/vishakhapatnam_image.png` is a social-media
  graphic over a Google office photo. Slide 23 captions both honestly. Swap in a real Mesa
  photo if one turns up.
- The 2030 step (39% → 45%) is mostly **two Gulf Coast sites** (Meta Hyperion, Amazon Ridgeland)
  whose basins sit just under 40% at baseline and cross it in 2030 BAU (they fall back by 2050:
  why 2050 BAU < 2030 BAU). Two Ulanqab sites go from "arid, low use" to "extremely high". Said
  on the slide and in the notes.
- Aqueduct's annual stress counts all withdrawals, including power-plant cooling (why Indiana and
  western NY score "high"): a likely Q&A point.
- **Before presenting:** check whether MOFCOM extended the 27 Nov 2026 suspension (slide 26).
- All claims in claims.csv are now verified (10 Nov review: Rosa full text, GEM 2024 PDF, CAP,
  City of Mesa, Reclamation, MOFCOM, NBC/Bloomberg).

## 8. Open items

1. **O2:** done. Optional: red outline on stressed sites in the map; a real Mesa photo; exact
   titles/URLs for the Google, Mongabay and The Federal references; D1/D3 status cells (shared table).
2. **O1 (Aditya) and O3 (Prerna):** their results slides are placeholders. The O1 growth fits can
   reuse `../proposal/make_figures.py` (Epoch compute, OWID energy; LBNL 58→176 TWh 2014–2023;
   Masanet 194→205 TWh 2010–2018; IEA 415→945 TWh 2024–2030).
3. **Shared:** O4 matrix, deliverables status, expected-vs-found table, bibliography, verify
   the § 1 † numbers, then `\draftfalse`.

## 9. How the user likes to work

- Concise answers; recommend, don't survey. Fewer items, done thoroughly and cited, rather than breadth.
- Every number on a slide must come from a primary source or our own scripts, logged in
  `claims.csv`; say plainly when something is unverified or an assumption.
- Render and look at every changed slide before calling it done; 0 overfull boxes.

## 10. Review fixes (12 Nov, after external review)

Applied in v1: efficiency verdict → "Partly supported" (PUE flat from 2014, jump in 2018 matches AI servers); breakpoint
wording now window-dependent (1974 over 1950–2019, 2011 over 1990–2019; 1950 untestable); Earth3 slide's third number
is now Vizag "15% short" (power-plant water is regional, not basin evidence); D2 → "Partly complete"; e-waste described
as "very uneven collection", not displacement (minerals headline changed); "Changes from the plan" line on slide 11;
slide 4 "7 today"; slide 6 AI-era box 76 → 176 TWh (2018–23); slide 12 LQ "(in the report)"; slide 23 "planned sites
included"; Aditya's figures relabelled "facility power" (Epoch MW are facility power). Not changed: slide 17 keeps
"≈60 TWh" (LBNL text says "about 60"; 58 is not in the report); slide 6 GA box keeps the Steffen et al. framing.
