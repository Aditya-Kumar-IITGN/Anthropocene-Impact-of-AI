# Review prompt: cross-validate the EH627 final presentation (read-only)

Paste everything below the line into a new Claude Code session started in
`/Users/aryan/Desktop/Academics/semester_7/eh_627/project/presentation_slides`.
For a hard guarantee, start it with `claude --permission-mode plan` (plan mode cannot edit files).

---

You are reviewing a university group presentation before it is submitted and presented. Your job is
to find **wrong reporting** and **fair, substantive criticisms**, not to polish wording.

## Strict read-only rules

- Do **not** create, edit, move or delete any file. Do not run any command that writes to disk:
  no `tectonic`, no `analysis/*.py` scripts (they overwrite figures and CSVs), no `pip`/`conda`, no git.
- You may read files, run `pdftotext`/`pdftoppm` with output to stdout or to `/tmp` only, and run
  short read-only Python (`/Users/aryan/miniforge3/envs/geo/bin/python -I -c "..."`) that loads CSVs
  and prints numbers without saving anything.
- You may use web search to check a cited source when a claim looks doubtful.
- Report findings in your reply only. Do not offer to fix them.

## Context

- Course: EH627 *Anthropocene: Human Impact on the Earth*, IIT Gandhinagar. Project: *The Regional
  Footprint of AI Data Centres: Energy, Water, Materials and Planetary Boundaries*. Group: Aryan,
  Aditya, Prerna. About 30 minutes; the professor's required structure is in `../outline.md`.
- **The deck to review:** `main_v1.pdf` (source: `main_v1.tex` + `sections_v1/*.tex`). Speaker notes:
  `notes_v1.pdf`. Ignore `main.pdf`/`sections/` (an older version kept for reference).
- **What was promised (the "report" to check coherence against):**
  - `references_aditya_work/EH627_Project_Plan.pdf` (the submitted plan; source of truth for the
    objectives, methods, expected results and deliverables)
  - `../preliminary_report/EH627_Preliminary_Report.tex` (almost the same text)
- **Where the numbers come from:** `data/claims.csv` (ledger: every slide number, its source, how it
  was obtained, verified flag), scripts in `analysis/`, outputs in `data/processed/`, raw data in
  `data/raw/`. Background and decisions: `context.md`, `O2_PLAN.md`.
- Key sources on disk: `references_aditya_work/` (de Vries-Gao 2026 *Patterns* paper,
  `Colliste2018eartharxiv_pes.pdf` = Earth3 technical notes), `data/raw/usgs/*.pdf`.

## What to check

1. **Wrong reporting (highest priority).** For each number on a slide, does it match `claims.csv`,
   the processed data or script logic, and the cited source? Look especially for: wrong units or
   magnitudes; a share computed on one denominator but described with another (sites vs MW, current
   vs planned, all data centres vs tracked AI sites); projections presented as observations; a
   correlation presented as causation; numbers from different years or geographies compared as if
   like-for-like; a claim stronger than its source supports; a source cited that does not contain
   the claim. Spot-check the riskiest items against the source itself.
2. **Coherence with the submitted plan.** Does the deck deliver what the plan promised (objectives
   O1–O4, methods 1–5, expected results, deliverables D1–D4)? Where it changed course (e.g. Epoch AI
   sites only instead of an all-data-centre layer; two news-based case studies instead of four
   clusters), is that stated honestly? Is anything claimed as done that was not done?
3. **Internal coherence.** Do slides contradict each other (e.g. a number on the summary slide vs
   the results slide, slide references like "(slide 24)" pointing to the right slide, the deliverables
   table vs what is actually shown, the "expected vs found" verdicts vs the evidence)? Does the story
   hold: problem → three phases since 1950 → "why did cloud growth leave energy flat but AI does not?"
   → results → "small globally, concentrated locally"?
4. **Method soundness.** Fair criticisms of the approach: e.g. Aqueduct annual stress includes
   power-plant withdrawals; the water-use model's load-factor assumption and US-derived grid water
   factors applied to India; comparing consumption with a withdrawal-based boundary (Earth3); the
   seven-group Gini proxy; growth rates from two published points; breakpoint test results. Say
   whether each limitation is already disclosed on the slide or in the notes, and whether the
   disclosure is adequate.
5. **Fit for the course.** Does it address the Anthropocene / planetary-boundaries framing the course
   expects, and the professor's outline sections?

## What not to do

- Do not report typography, colour, wording preferences or minor layout issues unless they change
  meaning.
- Do not invent problems to fill a list. If an area is sound, say so in one line.
- Do not treat a disclosed limitation as an error; judge whether the disclosure is enough.

## Output format

1. **Verdict** (3–5 sentences): is it fit to submit and present? The single most important fix, if any.
2. **Wrong or unsupported reporting:** a table with slide number (footer), the claim as written, what
   the source/data actually says, severity (high / medium / low), and how you checked.
3. **Coherence with the plan:** promised vs delivered, with gaps that are not disclosed.
4. **Internal inconsistencies.**
5. **Fair methodological criticisms** a professor might raise, each with "disclosed? yes/partly/no".
6. **Likely Q&A questions** (up to 8) with the honest short answer the data supports.

Keep it concise. Rank by severity. Cite file paths and slide numbers for everything.
