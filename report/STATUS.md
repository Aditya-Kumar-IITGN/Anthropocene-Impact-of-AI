# EH627 final report: status (Final Submission Version)

`main.pdf` = title page + 11 pages (10 body + references), 0 overfull boxes. Draft mode is **off**
(`\draftfalse` in `main.tex`): all red `[TODO name: ...]` notes resolved and hidden. Submission-ready.

## Title page authors

- Aryan Solanki (23110049)
- Aditya Kumar (22110015)
- Prerna Sawane (22110235)
- Date: November 2026

## Per section

| Section | File | Drafted | Verified | Notes |
|---|---|---|---|---|
| Abstract | `0_abstract.tex` | yes | yes | numbers from claims; verified |
| 1 Statement of the problem | `1_problem.tex` | yes | yes | Masanet +550%/+6% verified against Science (194->205 TWh); includes "Terms" box |
| 2 Objectives | `2_objectives.tex` | yes | yes | |
| 3 Data and methods | `3_data_methods.tex` | yes | yes | "Changes from the plan" kept and updated |
| 4.1 O1 Energy and carbon | `4_1_o1_energy.tex` | yes | yes | Reviewed; numbers match claims and growth table |
| 4.2 O2 Water, materials, waste | `4_2_o2_water.tex` | yes | yes | MOFCOM suspension updated (Nov 2026 status) |
| 4.3 Siting logic: why Visakhapatnam? | `4_3_siting.tex` | yes | yes | Public record analyzed; Table 4 verified |
| 4.4 O3 Economy and society | `4_3_o3_society.tex` | yes | yes | GHSL populations cross-checked with UN WPP 2024 (<1% diff); DCW Q2 cited |
| 4.5 O4 Synthesis | `4_4_o4_synthesis.tex` | yes | yes | Matrix as presented with Q/D/N coding |
| 5 Deliverables | `5_deliverables.tex` | yes | yes | D2 stays "Partly complete" (honest assessment) |
| 6 Summary and conclusions | `6_conclusions.tex` | yes | yes | Verdicts as presented; limitations (10 items) |
| 7 Bibliography | `refs.bib` | yes | yes | The Federal headline, Google air cooling, and Mongabay updated |
| Author contributions | `8_contributions.tex` | yes | yes | Added author roles, deliverables, and research |

## What the report added beyond the deck

- **D1** atlas (`figs/d1_atlas.pdf`, `analysis/fig_d1_atlas.py`): capacity, baseline water stress and population on
  the same maps, US and world; the 4 sites entering high stress by 2030 (BAU) marked.
- **D2** fit diagnostics (`analysis/d2_growth_diagnostics.py`): HAC intervals, Durbin–Watson, R², break tests with
  ΔBIC (Table 3, Figure 1). Finding: the 1950–2010 energy fit is strongly autocorrelated (DW 0.15), so its honest
  interval is 25.6–35.7 yr, not 27.9–32.0.
- **D3** country table (`analysis/d3_country_table.py`, Table 5): LQ today and 2030, country Gini 0.936 / 0.940
  (deck's seven-group 0.927 was a lower bound, as expected), W per person, stressed share, people within 50 km,
  water. Population from the GHSL grid already on disk (no download), so it matches the exposure counts.
- All figures re-made at column width for print (`analysis/fig_o1.py`, `fig_o2.py`).
- Correction found: one of the "two Ulanqab sites" is Huawei Horinger (Hohhot); logged in `claims_report.csv`.
- **Siting logic of the Visakhapatnam hub** (Section 4.3; `analysis/fig_siting.py` -> `figs/o2_siting.pdf`,
  `data/o2_siting_airwater.csv`): why the site was chosen, whether water stress, distance to source and nearby people
  were tests, and which frameworks existed. Finding 4: water shaped the cooling design, not the choice of site; air
  cooling shifts water to power plants (net -7 to +4 M L/day for 1 GW). Finding boxes after it are renumbered 5 and 6.
- Correction found: the 1 GW hub is on three campuses (Tarluvada, Adavivaram, Rambilli), not at Tarluvada alone.
- The deck's "833 opposition groups" is the end-of-March count in Data Center Watch's later reporting; Q2 2026 is now
  cited (45 projects, about US$68 bn; 843 groups). Cited from press summaries: open the DCW report itself.
- Logo: the supplied PNG had a baked-in checkerboard; `iitgn_logo_clean.png` is used instead.

## Completed TODOs and Verification

**Aditya (O1)**
1. Reviewed §4.1: fits, rates and narrative verified against claims and Table 2.
2. Masanet et al. (2020) (+550% compute instances / +6% energy, 194 to 205 TWh) verified against Science full text.
3. LBNL series: kept published benchmark points and honesty decision (D2 "Partly complete").
4. Chip efficiency: clearly noted as not tested in text and Table 7.

**Aryan (O2)**
0. Section 4.3 citing, NITI Aayog framework (Oct 2026), and Bikash Koley (Google) air cooling trade-off statement cited.
1. MOFCOM gallium/germanium suspension status verified (Announcement 72 valid through 27 Nov 2026; unconfirmed press extension noted).
2. Exact headline/citation for The Federal (G. P. Venkateswarlu, 27 Oct 2026) and exact entries for Mongabay and Google updated in `refs.bib`.
3. Title-page names and roll numbers filled:
   - Aryan Solanki (23110049)
   - Aditya Kumar (22110015)
   - Prerna Sawane (22110235)

**Prerna (O3)**
1. Reviewed §4.3 (O3): location quotients, Lorenz curve, and Gini 0.940 verified.
2. GHSL country populations cross-checked against UN WPP 2024 (agree within <1% for world and major countries; logged in `claims_report.csv`).
3. Gini per internet user: kept under "Changes from the plan" as agreed.
4. Qualitative disputes framework (5 EJAtlas grievance tags) verified.
5. Data Center Watch Q2 2026 data (45 projects, ~$68 bn, 843 opposition groups) verified and cited.

**Final checks**
- Draft switch set to `\draftfalse` in `main.tex`; all red TODO notes removed.
- Full document recompiled with Tectonic: 12 pages (title page + 11 body pages), 0 overfull boxes.
- Visual inspection of all pages completed.
