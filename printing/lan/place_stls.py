"""Copy ASCII STLs to fixed bed positions so the CLI keeps parts square and where we put them.
Run: python place_stls.py OUTDIR  (edit PARTS for the job; x y = front-left corner on the bed, mm)."""
import re, sys
from pathlib import Path

SRC = Path(r"C:\PrintLocal\v096")
PARTS = {  # 256 x 256 bed. These are set 1b as printed; y 8 breaks FRONT_MARGIN, so re-lay before reusing
    "handle-plate-v096-0.125in.stl": (25, 8),
    "collar-v096.stl": (25, 176),
    "trigger-0.125in.stl": (141, 8),  # unchanged from v0.95, copied into v096/
    "lever-v096-tight.stl": (139, 166),
    "lever-v096.stl": (170, 166),
    "lever-v096-loose.stl": (201, 166),
}
FRONT_MARGIN = 15  # mm from the bed's front edge; the load line runs at Y 0
OUT = Path(sys.argv[1])
if min(y for _, y in PARTS.values()) < FRONT_MARGIN:
    sys.exit(f"stopped: a part starts in front of Y {FRONT_MARGIN}, too close to the load line")
OUT.mkdir(parents=True, exist_ok=True)
VERT = re.compile(r"vertex\s+(\S+)\s+(\S+)\s+(\S+)")
for name, (x, y) in PARTS.items():
    text = (SRC / name).read_text(encoding="ascii")
    placed = VERT.sub(lambda m: f"vertex {float(m[1]) + x:.4f} {float(m[2]) + y:.4f} {m[3]}", text)
    (OUT / name).write_text(placed, encoding="ascii", newline="\n")
    print(name, "at", x, y)
