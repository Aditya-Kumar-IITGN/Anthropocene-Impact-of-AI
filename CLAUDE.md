# LaTeX → PDF: a working playbook

**Who this is for:** Claude Code, starting a document project in a folder that has no
LaTeX setup yet. This is the toolchain that was actually used to build a 6-page,
two-column, figure-led academic report on this machine (macOS, Apple Silicon) — not a
generic tutorial. Everything below was run and verified.

**How to use it:** copy this file into the new project. Rename it `CLAUDE.md`, or leave
it as-is and read it before the first compile. Adapt paths — the *shape* of the workflow
is what transfers.

---

## 1. Toolchain

| Need | Tool | Path on this machine |
|---|---|---|
| LaTeX engine | **Tectonic 0.17** | `/opt/homebrew/bin/tectonic` |
| Figures | matplotlib in a conda env | `/Users/aryan/miniforge3/envs/mktg/bin/python` |
| Inspect PDFs | poppler (`pdftotext`, `pdftoppm`, `pdfinfo`) | `/opt/homebrew/bin/` |

Check what exists before assuming:

```bash
which tectonic pdflatex latexmk pdftotext pdftoppm pdfinfo
tectonic --version
```

### Why Tectonic, not MacTeX

- ~50 MB, one binary, `brew install tectonic`. MacTeX is ~5 GB.
- **Auto-downloads packages on demand.** You do not manage a TeX distribution. Write
  `\usepackage{tcolorbox}` and it fetches it on the next build. This is the single
  biggest reason it suits an agent workflow: no "package not found, go install it" loop.
- First build of a document is slow (10–60 s while it pulls packages), subsequent builds
  are ~1–3 s. Packages are cached in `~/Library/Caches/Tectonic`.
- Needs network on first use of a new package. Fully offline afterwards.

If neither Tectonic nor a TeX install is present, ask before installing (`brew install
tectonic`). The zero-install fallback is Overleaf: write the `.tex` + figures locally and
have the user paste them in. Slower loop, no local PDF to inspect — avoid if you can.

---

## 2. Quick start

```bash
mkdir -p report/figs report/data && cd report
# write main.tex (see §4)
tectonic -X compile --synctex --keep-logs main.tex
pdfinfo main.pdf | grep Pages
```

Output lands next to the source: `main.pdf`, `main.log`, `main.synctex.gz`.

Flags worth knowing:

| Flag | Effect |
|---|---|
| `-X compile` | The V2 interface. Use it. |
| `--keep-logs` | Writes `main.log`. **Always pass this** — the log is how you find overfull boxes. |
| `--synctex` | Enables click-from-PDF-to-source in VS Code. |
| `--outdir DIR` | Put build products elsewhere. |
| `--keep-intermediates` | Keeps `.aux`/`.bbl`. Needed only when debugging bibliography. |
| `--print` | Streams the raw TeX log to stdout. Useful when a build fails mysteriously. |

---

## 3. The build loop — and the part everyone skips

```bash
# 1. compile
tectonic -X compile --keep-logs main.tex

# 2. check for real problems
grep -c "Overfull" main.log          # want 0
grep -n "Underfull \\\\vbox" main.log  # usually ignorable
grep -in "warning\|undefined" main.log | head

# 3. page and word count
pdfinfo main.pdf | grep Pages
pdftotext -f 2 main.pdf - | wc -w    # -f 2 to skip a title page

# 4. LOOK AT IT
pdftoppm -png -r 92 -f 3 -l 3 main.pdf /tmp/pg   # renders page 3 -> /tmp/pg-3.png
```

**Step 4 is not optional.** Read the PNG with the Read tool. On this project, rendering
pages visually caught errors that `pdftotext` extraction could not:

- overlapping labels inside a matplotlib figure,
- a legend sitting on top of a data series,
- a float pushed to a page on its own, leaving a half-empty column,
- two figures whose captions contradicted each other.

Text extraction says the words are present. It cannot tell you the document looks wrong.
Render every page at least once before declaring it done. `-r 92` is enough to judge
layout; use `-r 150` to read small figure labels.

Render a range: `pdftoppm -png -r 92 -f 1 -l 6 main.pdf /tmp/pg` → `/tmp/pg-1.png` … `-6.png`.

---

## 4. Templates

### 4a. Standard report (start here unless space is tight)

```latex
\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{microtype,amsmath,graphicx,xcolor,booktabs,siunitx}
\usepackage{caption,subcaption,fancyhdr,tcolorbox,enumitem}
\usepackage[hidelinks]{hyperref}
\tcbuselibrary{skins,breakable}

\definecolor{navy}{HTML}{12305E}
\captionsetup{font=small,labelfont=bf}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\footnotesize Course \textbar\ Institution}
\fancyhead[R]{\footnotesize Document title}
\fancyfoot[C]{\footnotesize\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\begin{document}
...
\end{document}
```

`microtype` is not cosmetic — it materially reduces overfull boxes. Always include it.

### 4b. Dense two-column academic (when there is a page limit)

This is the layout that shipped. `extarticle` unlocks 9pt, which `article` refuses.
Roughly **60% more content per page** than 4a, and it reads like a journal.

```latex
\documentclass[9pt,a4paper]{extarticle}
\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[a4paper,margin=0.70in]{geometry}
\usepackage{microtype,amsmath,graphicx,xcolor,booktabs,array}
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}
\usepackage{caption,fancyhdr,tcolorbox,enumitem,ragged2e}
\usepackage[hidelinks]{hyperref}
\usepackage[compact]{titlesec}
\usepackage{stfloats}          % allows floats at the BOTTOM of a two-column page
\setlength{\columnsep}{0.26in}
\titlespacing*{\section}{0pt}{6pt}{2.5pt}

% Let floats fill pages instead of forcing whitespace. Without these, two-column
% LaTeX strands half-empty pages around every wide figure.
\renewcommand{\topfraction}{0.94}
\renewcommand{\bottomfraction}{0.88}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.72}
\renewcommand{\dbltopfraction}{0.94}
\renewcommand{\dblfloatpagefraction}{0.72}
\setlength{\textfloatsep}{7pt plus 2pt minus 3pt}
\setlength{\intextsep}{7pt plus 2pt minus 3pt}
\setlength{\dbltextfloatsep}{8pt plus 2pt minus 3pt}

% Tight columns break badly without help:
\linespread{1.005}
\tolerance=1500
\emergencystretch=1.4em
\hyphenpenalty=90
\hyphenation{mar-ket-ing per-form-ance op-er-a-tion-al-ise}
```

Title page + full-width abstract, then two columns:

```latex
\begin{document}
\thispagestyle{empty}
\begin{center}\vspace*{2.1cm}
{\large\scshape Individual Summary}\\[2.3cm]
{\LARGE\bfseries Title Here}\\[14pt]
\vfill
{\large\bfseries Author Name}\\[4pt]
{\normalsize Roll number \quad\textbar\quad Programme}\\[16pt]
{\normalsize Institution}\\[6pt]
{\normalsize Submitted to: Instructor}
\vspace*{1.5cm}\end{center}

\twocolumn[{%                      % spans BOTH columns
\begin{center}{\LARGE\bfseries Title Here}\end{center}\vspace{4pt}
\begin{minipage}{\textwidth}\small\noindent\textbf{Abstract.}~...\end{minipage}
\vspace{9pt}
}]
\setcounter{page}{1}              % body starts at page 1
```

Callout boxes — cheap, and they make a document look considered:

```latex
\newtcolorbox{finding}[1]{colback=navy!4,colframe=navy,coltitle=white,
  fonttitle=\bfseries\scriptsize,title={#1},boxrule=0.6pt,arc=1.2pt,
  left=4.5pt,right=4.5pt,top=2.5pt,bottom=2.5pt,
  before skip=5pt,after skip=5pt,fontupper=\small}

\begin{finding}{Finding 1 — Measurement tracks data cost}
Market share is measured in 25.2\% of studies; CLV in 0.5\%.
\end{finding}
```

**Two-column float rules.** `figure`/`table` = one column wide. `figure*`/`table*` =
full width, and starred floats can only appear at the *top* of a page (or bottom, with
`stfloats`) — never mid-column, and never on the page where they are declared if that
page is already typeset. Declare a `figure*` one paragraph *earlier* than where you want
it to land.

---

## 5. Figures: matplotlib → vector PDF

Never `.png` in a LaTeX document. Save `.pdf` — vector, sharp at any zoom, smaller.

```python
import matplotlib
matplotlib.use("pdf")            # headless backend; must precede pyplot import
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica","Arial","DejaVu Sans"],
    "font.size": 7.2,            # sized for a 3.3in column, NOT the notebook default
    "axes.edgecolor": "#c3c2b7", "axes.linewidth": 0.6,
    "pdf.fonttype": 42,          # embed real fonts, not outlines — keeps text selectable
    "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})

fig, ax = plt.subplots(figsize=(3.3, 2.3))   # width == the LaTeX column width
...
ax.spines[["top","right"]].set_visible(False)
fig.tight_layout()
fig.savefig("figs/f1.pdf")
```

**Sizing.** Set `figsize` to the *final printed size* and never scale in LaTeX. Then the
figure's 7pt labels are 7pt on the page, matching the body text.

- one column of the 0.70in-margin two-column layout ≈ **3.3 in**
- full text width, same layout ≈ **6.83 in**
- single-column 1in-margin article ≈ **6.5 in**

Include at natural size:

```latex
\begin{figure}[t]\centering
  \includegraphics[width=\linewidth]{figs/f1.pdf}
  \caption{Caption that states the finding, not the chart type.}
  \label{fig:one}
\end{figure}
```

**Keep figures reproducible.** One `make_figures.py` that reads from `data/*.csv` and
writes every `figs/*.pdf`. When a number changes, rerun one script — do not hand-edit.

```bash
$PY make_figures.py && tectonic -X compile --keep-logs main.tex
```

**Propagate fixes across figures.** A real bug on this project: Figure 1 was corrected,
Figure 2 kept the old (now contradictory) labelling for another two rounds. If a
conceptual fix lands in one figure, grep the others for the same claim before moving on.

---

## 6. Tables

`booktabs` only — `\toprule`, `\midrule`, `\bottomrule`. No vertical rules, ever.
`siunitx`'s `S` column aligns on the decimal point:

```latex
\begin{table}[t]\centering
\caption{Measures by era (\% of 998 studies)}
\small
\begin{tabular}{lS[table-format=2.1]S[table-format=2.1]S[table-format=2.1]}
\toprule
Aspect & {1981--94} & {1995--2004} & {2005--14} \\
\midrule
Accounting       & 63.6 & 68.8 & 62.0 \\
Financial-market & 5.1  & 9.8  & 18.3 \\
\bottomrule
\end{tabular}
\end{table}
```

Header cells in an `S` column must be `{braced}` or siunitx tries to parse them as
numbers. For wrapping text columns, use the `P{2.2cm}` type defined in §4b.

---

## 7. Hitting a page limit

In order of what to try. The first three are free; the last two cost quality.

1. **Go two-column at 9pt** (§4b). Biggest single win, and it looks better.
2. **Fix the float parameters** (§4b). Default LaTeX strands enormous whitespace around
   figures. This alone recovered most of a page here.
3. `\usepackage[compact]{titlesec}` + `\setlist{nosep,leftmargin=1.1em}` +
   `\linespread{1.005}`. Tightens headings and lists without looking cramped.
4. Shrink figures, or merge two into one panel.
5. Cut words.

Do **not** shrink margins below ~0.6in or drop below 9pt — it reads as gaming the limit.

**Does the title page count?** Usually not, if the exemplars for that course put the
title on its own page. Check the provided examples rather than guessing; `\setcounter{page}{1}`
after the title page makes the intent explicit.

Measure, don't estimate:

```bash
pdfinfo main.pdf | grep Pages
pdftotext -f 2 main.pdf - | wc -w    # words, excluding a page-1 title page
```

`texcount` is not installed here; the `pdftotext | wc -w` route counts what is actually
on the page, which is the number that matters anyway.

---

## 8. Bibliography

**Verified on this machine:**

- ✅ `natbib` + `bibtex` — works out of the box. Tectonic bundles bibtex and reruns
  passes automatically.
- ❌ `biblatex` + `biber` — **fails**: `error: No such file or directory`. Tectonic shells
  out to an external `biber` binary, which is not installed. `brew install biber` would
  fix it; do not reach for biblatex unless you need it.

Working pattern:

```latex
\usepackage{natbib}
...
Cited \citep{katsikeas2016}.
\bibliographystyle{apalike}   % or plainnat, unsrtnat
\bibliography{refs}
```

For a document with under ~15 references, a manual `thebibliography` environment is
often less trouble than a `.bib` file:

```latex
\begin{thebibliography}{9}
\bibitem{kat16} Katsikeas, C., Morgan, N., Leonidou, L., \& Hult, G. (2016).
Assessing Performance Outcomes in Marketing. \textit{Journal of Marketing}, 80(2), 1--20.
\end{thebibliography}
```

---

## 9. Error cookbook

| Symptom | Cause | Fix |
|---|---|---|
| `Overfull \hbox (12pt too wide)` | Unbreakable long word/URL/table | Add to `\hyphenation{}`, raise `\emergencystretch`, or `\small` the table. Chase these to zero. |
| Figure lands pages away from its text | Float queue backed up | Fix float fractions (§4b); use `[t]` not `[h]`; `\usepackage{stfloats}` for bottom placement in two columns. |
| Half-empty page before a figure | `\floatpagefraction` too high | Set it to `0.72`. |
| `figure*` never appears | Starred floats are top-of-page only | Declare it one paragraph earlier, or add `stfloats`. |
| `Undefined control sequence` | Missing package | Add the `\usepackage`; Tectonic downloads it automatically. |
| `File 'x.sty' not found` | No network on first use | Reconnect and rebuild; cached thereafter. |
| Figure text tiny or huge | `figsize` ≠ printed size, or scaled by `width=` | Set `figsize` to final inches, include at `width=\linewidth`. |
| Table headers mangled in `S` columns | siunitx parsing text as a number | Brace them: `{1981--94}`. |
| Build hangs on first run | Downloading packages | Wait. It is one-time. |
| Numbers in text disagree with figures | Hand-typed twice | Single source of truth in `data/*.csv`; script both. See §10. |

Bad boxes are noisy in the log; suppress them in the editor, not in your checking:
`"latex-workshop.message.badbox.show": false`.

---

## 10. Verifying numbers against a source

If the document makes factual or numeric claims drawn from a source PDF, **write a script
that checks them.** On this project that found two errors that three careful human-style
read-throughs had missed.

```bash
pdftotext -layout source_paper.pdf source.txt   # -layout preserves table columns
python data/verify_tex.py source.txt main.tex   # parse both, compare cell by cell
```

The verifier regexes the numbers out of the extracted source text and out of `main.tex`,
then diffs them and prints a pass/fail count. Final state here: **107 checks, 0 failures.**
It is maybe 60 lines of Python and it is the difference between "I checked it" and
"it is checked".

Complementary and cheap: type the same table from two different pages of the source into
two different files and assert they agree.

---

## 11. VS Code integration

`.vscode/settings.json` — build on save, preview in a tab, SyncTeX both ways:

```json
{
  "latex-workshop.latex.tools": [
    { "name": "tectonic",
      "command": "/opt/homebrew/bin/tectonic",
      "args": ["-X", "compile", "--synctex", "--keep-logs", "%DOC%.tex"],
      "env": {} }
  ],
  "latex-workshop.latex.recipes": [ { "name": "Tectonic", "tools": ["tectonic"] } ],
  "latex-workshop.latex.outDir": "%DIR%",
  "latex-workshop.latex.autoBuild.run": "onSave",
  "latex-workshop.view.pdf.viewer": "tab",
  "latex-workshop.synctex.afterBuild.enabled": true,
  "latex-workshop.message.badbox.show": false,
  "latex-workshop.latex.clean.subfolder.enabled": true,

  "python.defaultInterpreterPath": "/Users/aryan/miniforge3/envs/mktg/bin/python"
}
```

Requires the **LaTeX Workshop** extension. Note `%DOC%.tex` — LaTeX Workshop's `%DOC%`
strips the extension, and Tectonic wants it back.

---

## 12. Suggested layout

```
project/
├── .vscode/settings.json
├── report/
│   ├── main.tex
│   ├── make_figures.py       # writes every figs/*.pdf
│   ├── figs/*.pdf            # generated — never hand-edited
│   └── data/
│       ├── table.csv         # single source of truth for every number
│       ├── parse_*.py        # source PDF -> csv
│       ├── validate.py       # internal consistency
│       └── verify_tex.py     # csv/source vs main.tex
└── source_material/*.pdf
```

---

## 13. Ship checklist

```bash
cd report
$PY make_figures.py                          # figures current?
tectonic -X compile --keep-logs main.tex
grep -c "Overfull" main.log                  # 0
pdfinfo main.pdf | grep Pages                # within limit
pdftotext -f 2 main.pdf - | wc -w            # word count
python data/verify_tex.py ../source.txt main.tex   # numeric claims
pdftoppm -png -r 92 -f 1 -l 6 main.pdf /tmp/pg     # then READ every page
cp main.pdf Final_Name_Rollnumber.pdf        # name it what the brief asks for
```

Rendering and reading every page is the last step and the one that catches what the
compiler cannot. Do it even when the build is clean.
