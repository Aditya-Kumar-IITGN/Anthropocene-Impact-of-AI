"""Remove the baked-in grey checkerboard (fake transparency) from iitgn_logo.png -> iitgn_logo_clean.png.

Run: /Users/aryan/miniforge3/envs/geo/bin/python -I report/analysis/clean_logo.py
Pixels that are near-grey (channel spread < 14) and light (mean > 222) become white; the blue, red and dark text of
the emblem are untouched. The original file is not modified.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = np.array(Image.open(os.path.join(HERE, "iitgn_logo.png")).convert("RGB")).astype(int)
grey = (a.max(2) - a.min(2) < 14) & (a.mean(2) > 222)
a[grey] = 255
Image.fromarray(a.astype("uint8")).save(os.path.join(HERE, "iitgn_logo_clean.png"))
print(f"whitened {grey.sum():,} of {grey.size:,} pixels -> iitgn_logo_clean.png")
