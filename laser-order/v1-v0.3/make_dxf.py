import sys, math, json
import ezdxf
from shapely.geometry import Polygon, LineString, Point
from shapely import affinity

SRC = sys.argv[1]; OUT = sys.argv[2]
code = open(SRC).read()
code = code[:code.index("# ---- Angle clip")]
code = code.replace("OUT = sys.argv[1]\nPNG = sys.argv[2]\n", "")
g = {}
exec(code, g)

# Trigger: add bend relief notches at both ends of the bend line (per build notes 4.4)
a, b = g["bend"]; nx, nz = g["nx"], g["nz"]
def relief(p):
    return LineString([p, (p[0] - nx * 0.0875, p[1] - nz * 0.0875)]).buffer(0.0625, 64)
trigger = g["trigger"].difference(relief(a)).difference(relief(b))

parts = {"collar": g["collar"], "keeper": g["keeper"], "frame": g["frame"], "trigger": trigger}
report = {}
for name, geom in parts.items():
    assert geom.geom_type == "Polygon", (name, geom.geom_type)
    minx, miny, maxx, maxy = geom.bounds
    geom = affinity.translate(geom, -minx, -miny)   # lower-left corner at 0,0
    doc = ezdxf.new("R2010", setup=False)
    doc.units = ezdxf.units.IN
    doc.header["$MEASUREMENT"] = 0
    msp = doc.modelspace()
    circles, polys = [], 0
    rings = [geom.exterior] + list(geom.interiors)
    for i, ring in enumerate(rings):
        pts = list(ring.coords)[:-1]
        c = Polygon(ring).centroid
        d = [math.hypot(x - c.x, y - c.y) for x, y in pts]
        if i > 0 and max(d) - min(d) < 1e-4:          # a plain round hole -> true circle
            r = sum(d) / len(d)
            r = round(r * 2 / 0.001) * 0.001 / 2     # snap to nearest 0.001" diameter
            msp.add_circle((c.x, c.y), r)
            circles.append(round(2 * r, 3))
        else:
            s = LineString(list(ring.coords)).simplify(0.0003)
            msp.add_lwpolyline(list(s.coords)[:-1], close=True)
            polys += 1
    doc.saveas(f"{OUT}/{name}.dxf")
    report[name] = dict(width=round(maxx - minx, 3), height=round(maxy - miny, 3),
                        circles=sorted(circles), closed_outlines=polys)
print(json.dumps(report, indent=1))
