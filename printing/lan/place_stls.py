"""Copy ASCII STLs to fixed bed positions so the CLI keeps parts square and where we put them.
Run: python place_stls.py OUTDIR  (edit PARTS for the job; x y = front-left corner on the bed, mm)."""
import re, sys
from pathlib import Path

SRC = Path(r"C:\PrintLocal\v096")
PARTS = {  # 256 x 256 bed; block spans x 20-234, y 46-210, so it sits centred where the glue is
    "handle-plate-v096-0.125in.stl": (20, 46),
    "collar-v096.stl": (146, 46),
    "lever-v096-tight.stl": (140, 134),
    "lever-v096.stl": (174, 134),
    "lever-v096-loose.stl": (208, 134),
}
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
VERT = re.compile(r"vertex\s+(\S+)\s+(\S+)\s+(\S+)")
for name, (x, y) in PARTS.items():
    text = (SRC / name).read_text(encoding="ascii")
    placed = VERT.sub(lambda m: f"vertex {float(m[1]) + x:.4f} {float(m[2]) + y:.4f} {m[3]}", text)
    (OUT / name).write_text(placed, encoding="ascii", newline="\n")
    print(name, "at", x, y)
