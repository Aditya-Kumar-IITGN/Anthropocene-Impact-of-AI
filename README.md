# Anthropocene: Impact of AI

**EH627: Anthropocene Course Project — Final Report, Presentation, and Data**  
*Indian Institute of Technology Gandhinagar (IITGN)*  
*November 2026*

---

## Authors & Contributions

- **Aryan Solanki (23110049)**: Objective 2 lead (Water stress, material bottlenecks, semiconductor supply chains, e-waste flows), creation and coordination of the final report, literature and quantitative research.
- **Aditya Kumar (22110015)**: Objective 1 lead (Energy consumption trajectories, carbon intensity, historical acceleration, power grid coupling), creation and coordination of the presentation deck, literature research, finding sources and primary datasets.
- **Prerna Sawane (22110235)**: Objective 3 lead (Political economy, spatial concentration, regulatory frameworks, environmental justice and public opposition), proofreading, quality review, and editorial consistency across deliverables.

---

## Project Abstract

The rapid scaling of frontier Artificial Intelligence (AI) models and hyper-scale compute infrastructure represents an emerging planetary-scale shock across the energy–water–materials nexus. This project provides a critical, empirical, and systemic assessment of the physical footprint of global AI expansion:

1. **Energy and Carbon (O1)**: Evaluating historical growth rates, exponential compute scaling against decarbonization curves, and power grid constraints.
2. **Water, Materials, and Waste (O2)**: Mapping datacenter cooling withdrawals against high-stress hydrological basins (WRI Aqueduct 4.0), critical mineral bottlenecks (gallium, germanium, rare earths, MOFCOM export restrictions), and lifecycle e-waste flows.
3. **Siting Logic & Political Economy (O3)**: Deconstructing hyper-scale campus placement (including a deep dive into the 1 GW Visakhapatnam AI cluster across Tarluvada, Adavivaram, and Rambilli), spatial inequality (Gini > 0.93), community exposure (GHSL GHS-POP), and anti-datacenter citizen mobilization.
4. **Planetary Synthesis (O4)**: Synthesizing systemic feedbacks within the Anthropocene boundary framework.

---

## Repository Structure

```
├── report/                     # Final Report package
│   ├── main.pdf                # Submission-ready compiled PDF (12 pages, 0 overfull boxes)
│   ├── main.tex                # Root LaTeX document
│   ├── sections/               # Modular LaTeX section files (1_problem .. 8_contributions)
│   ├── analysis/               # Python scripts generating figures, tables, and diagnostics
│   ├── data/                   # Processed data, diagnostics, and claims_report.csv
│   ├── figs/                   # High-resolution vector figures (PDF)
│   ├── tables/                 # Auto-generated LaTeX tables
│   ├── refs.bib                # Complete bibliography
│   └── STATUS.md               # Deliverable tracking and verification log
├── presentation/               # Presentation package
│   ├── main_v1.pdf             # Presented deck (slides)
│   ├── notes_v1.pdf            # Speaker notes and annotations
│   ├── sections_v1/            # Beamer slide sources
│   ├── pics/                   # Visuals, maps, and infographics
│   └── data/                   # Deck data and claims.csv audit
├── reference/                  # Academic literature, technical notes, and course references
├── data_raw/                   # Primary datasets (Ember, OWID, Epoch, USGS)
├── CLAUDE.md                   # LaTeX build playbook (Tectonic instructions)
└── README.md                   # This overview
```

---

## How to Build the Report

The final report uses [Tectonic](https://tectonic-typesetting.github.io), a modern, self-contained TeX engine:

```bash
# Build the PDF
zsh report/build.sh pdf

# Or directly with tectonic
tectonic -X compile report/main.tex
```

---

## License & Attribution

This repository is maintained by the EH627 course project team at IIT Gandhinagar. All datasets are cited and attributed to their primary sources (Ember, OWID, Epoch AI, WRI, JRC, USGS, NITI Aayog).
