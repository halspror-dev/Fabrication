import ezdxf, math, sys
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
def load(p):
    doc = ezdxf.readfile(p); msp = doc.modelspace()
    assert doc.units == 1, "units not inches"
    rings = []
    for e in msp:
        if e.dxftype() == "CIRCLE":
            rings.append(Point(e.dxf.center.x, e.dxf.center.y).buffer(e.dxf.radius, 256))
        elif e.dxftype() == "LWPOLYLINE":
            rings.append(Polygon([p[:2] for p in e.get_points()]))
        else:
            raise SystemExit(f"unexpected entity {e.dxftype()} in {p}")
    rings.sort(key=lambda r: -r.area)
    outer = rings[0]
    for r in rings[1:]:
        assert outer.contains(r), "hole outside part"
        outer = outer.difference(r)
    return outer, [e.dxftype() for e in msp], [l.dxf.name for l in doc.layers]
for n in ["collar", "keeper", "frame", "trigger"]:
    g, ents, layers = load(f"out/{n}.dxf")
    print(n, "valid", g.is_valid, "area sq in", round(g.area, 3), "entities", ents, "layers", layers)
