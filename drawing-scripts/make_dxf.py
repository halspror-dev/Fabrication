# Write the part outlines from templates.py as 1:1 inch DXFs (cut lines only).
# Usage: python3 make_dxf.py templates.py OUTDIR
import sys, math, json
import ezdxf
from shapely.geometry import Polygon, LineString
from shapely import affinity

src = open(sys.argv[1]).read().split("\ndef draw(")[0].replace("OUT = sys.argv[1]\nPNG = sys.argv[2]\n", "")
g = {}
exec(src, g)
report = {}
for name in ("collar", "keeper", "frame", "trigger", "trig_scale", "grip_scale"):
    geom = g[name]
    assert geom.geom_type == "Polygon", (name, geom.geom_type)
    minx, miny, maxx, maxy = geom.bounds
    geom = affinity.translate(geom, -minx, -miny)
    doc = ezdxf.new("R2010", setup=False)
    doc.units = ezdxf.units.IN
    doc.header["$MEASUREMENT"] = 0
    msp = doc.modelspace()
    circles = []
    for i, ring in enumerate([geom.exterior] + list(geom.interiors)):
        pts = list(ring.coords)[:-1]
        c = Polygon(ring).centroid
        d = [math.hypot(x - c.x, y - c.y) for x, y in pts]
        if i > 0 and max(d) - min(d) < 1e-4:          # round hole -> true circle
            r = round(sum(d) / len(d) * 2 / 0.001) * 0.001 / 2
            msp.add_circle((c.x, c.y), r)
            circles.append(round(2 * r, 3))
        else:
            msp.add_lwpolyline(list(LineString(ring.coords).simplify(0.0003).coords)[:-1], close=True)
    doc.saveas(f"{sys.argv[2]}/{name}.dxf")
    report[name] = dict(width=round(maxx - minx, 3), height=round(maxy - miny, 3), area_sq_in=round(geom.area, 2), holes=sorted(circles))
print(json.dumps(report, indent=1))
