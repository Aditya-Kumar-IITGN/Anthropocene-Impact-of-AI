"""Water-use parameter ranges shared by water_use.py and case_studies.py.

PUE, WUE and grid water intensity from de Vries-Gao (2026, Patterns 7:101430), which compiles
IEA, LBNL and company figures. The load factor is our assumption, stated on the slides.
"""
SCENARIOS = {
    #        load factor, PUE, WUE (L/kWh IT), WI_grid (L/kWh)
    "low":  dict(lf=0.7, pue=1.10, wue=0.56, wi=1.04),
    "high": dict(lf=0.9, pue=1.43, wue=1.04, wi=4.52),
}
SOURCES = {
    "pue": "1.10 Google; 1.43 IEA global average 2023",
    "wue": "0.56 IEA-implied 2023 (tech-company average 0.59); 1.04 Google",
    "wi": "1.04 IEA-implied 2023; 4.52 LBNL US 2023 (800 bn L / 176 TWh)",
    "lf": "assumption: average draw 70-90% of facility power",
}
