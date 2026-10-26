#!/usr/bin/env python3
"""List the preview pages that changed since the last build, so only those get a visual review.

Usage: python3 pagediff.py NEW_DIR [OLD_DIR]
Compares every *.png in NEW_DIR with the same name in OLD_DIR (default: NEW_DIR/../last-review).
Prints CHANGED / NEW / same per page and a one-line summary. Then copy NEW_DIR's PNGs to OLD_DIR
once the review is done:  python3 pagediff.py NEW_DIR --accept
"""
import shutil, sys
from pathlib import Path
import numpy as np
from PIL import Image

new = Path(sys.argv[1])
accept = "--accept" in sys.argv
rest = [a for a in sys.argv[2:] if a != "--accept"]
old = Path(rest[0]) if rest else new.parent / "last-review"

if accept:
    old.mkdir(parents=True, exist_ok=True)
    for f in new.glob("*.png"):
        shutil.copy2(f, old / f.name)
    sys.exit(print(f"accepted {len(list(new.glob('*.png')))} pages into {old}"))

changed = []
for f in sorted(new.glob("*.png")):
    o = old / f.name
    if not o.exists():
        print(f"NEW      {f.name}"); changed.append(f.name); continue
    a, b = np.asarray(Image.open(f).convert("L"), int), np.asarray(Image.open(o).convert("L"), int)
    if a.shape != b.shape:
        print(f"CHANGED  {f.name}  (size {b.shape} -> {a.shape})"); changed.append(f.name); continue
    diff = np.abs(a - b) > 24                      # ignore antialiasing noise
    if diff.sum() >= 20:                           # builds are deterministic, so any real move counts
        ys, xs = np.nonzero(diff)
        print(f"CHANGED  {f.name}  {diff.mean():.2%} of pixels, box x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()}")
        changed.append(f.name)
    else:
        print(f"same     {f.name}")
print(f"{len(changed)} of {len(list(new.glob('*.png')))} pages need a look: {' '.join(changed) or 'none'}")
