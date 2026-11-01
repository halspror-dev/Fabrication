"""v0.96 print and cut files: STLs in millimetres (lying in print orientation, no supports) and 1:1 inch DXFs.
Usage (from drawing-scripts/):  python3 v096_export.py OUTDIR
STLs: collar (plate + seat pads + stop post + upright flange, one piece), lever in 3 jaw sizes (nominal, tight +0.25 mm,
loose -0.25 mm) for the print test, handle plate, trigger, both sleeves and the pivot shim (the last four as v0.95).
DXFs: flat outlines of the collar plate, lever, handle plate and trigger (the pads, stop post and flange are printed
features on the collar: the metal version of those is not designed yet).
"""
import sys, os, math, json
import numpy as np
import manifold3d as m3d
import ezdxf
from shapely.geometry import Polygon, LineString
from shapely.geometry.polygon import orient
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v096 as V
import sleeves as SL

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
MM, g = 25.4, V.g


def xs(poly):
    poly = orient(poly, 1.0)
    return m3d.CrossSection([list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors])


def slab(poly, z0, z1):                  # plan-view outline, z0..z1
    return xs(poly).extrude(z1 - z0).translate((0, 0, z0))


def wall_xz(poly, y0, y1):               # side-view (x, z) outline, standing between y0 and y1
    return xs(poly).extrude(y1 - y0).transform([[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0]])


def write(name, m):
    m = m.scale((MM, MM, MM))
    m = m.translate(tuple(-np.array(m.bounding_box()[:3])))
    t = SL.tris(m)
    with open(os.path.join(OUT, name + ".stl"), "w") as f:
        f.write("solid %s\n" % name)
        for a, b, c in t:
            n = np.cross(b - a, c - a); n = n / (np.linalg.norm(n) or 1.0)
            f.write("facet normal %.6f %.6f %.6f\n outer loop\n" % tuple(n))
            for v in (a, b, c):
                f.write("  vertex %.4f %.4f %.4f\n" % tuple(v))
            f.write(" endloop\nendfacet\n")
        f.write("endsolid %s\n" % name)
    bb = m.bounding_box()
    print("%-28s %6.1f x %6.1f x %5.1f mm  %5.1f cm3  genus %d" % (name + ".stl", bb[3], bb[4], bb[5], m.volume() / 1000, m.genus()))


# collar: one printed piece, bottom face on the bed
collar = slab(V.collar, -V.CT, 0)
for p in V.pads:
    collar = collar + slab(p, -0.001, V.PAD_H)
collar = collar + slab(V.stop_post, -0.001, V.LT) + wall_xz(V.flange.buffer(0), V.FL_Y[0], V.FL_Y[1]).translate((0, 0, -0.001))
write("collar-v096", collar)
for tag, extra in (("", 0.0), ("-tight", 0.25 / MM), ("-loose", -0.25 / MM)):
    write("lever-v096" + tag, slab(V.lever_shape(extra)[0], 0, V.LT))
write("handle-plate-v096-0.125in", slab(V.frame, 0, 0.125))
write("trigger-0.125in", slab(g["trigger"], 0, 0.125))
W, nf = g["W"], g["GRIP_SLV"][0][2]
write("trigger-sleeve", SL.trigger_sleeve(g).transform([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, W]]))
write("grip-sleeve", SL.grip_sleeve(g).transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, nf]]))
write("shim-pivot", m3d.Manifold.cylinder(1 / 32, 0.25, 0.25, 96) - m3d.Manifold.cylinder(1, 0.1325, 0.1325, 96).translate((0, 0, -0.5)))

# DXFs (flat outlines, inches)
report = {}
for name, geom in (("collar-v096-plate", V.collar), ("lever-v096", V.lever_local), ("handle-plate-v096", V.frame), ("trigger", g["trigger"])):
    assert geom.geom_type == "Polygon", (name, geom.geom_type)
    minx, miny, maxx, maxy = geom.bounds
    geom = affinity.translate(geom, -minx, -miny)
    doc = ezdxf.new("R2010", setup=False); doc.units = ezdxf.units.IN; doc.header["$MEASUREMENT"] = 0
    msp = doc.modelspace(); circles = []
    for i, ring in enumerate([geom.exterior] + list(geom.interiors)):
        pts = list(ring.coords)[:-1]; c = Polygon(ring).centroid
        d = [math.hypot(x - c.x, y - c.y) for x, y in pts]
        if i > 0 and max(d) - min(d) < 1e-4:
            r = round(sum(d) / len(d) * 2 / 0.001) * 0.001 / 2
            msp.add_circle((c.x, c.y), r); circles.append(round(2 * r, 3))
        else:
            msp.add_lwpolyline(list(LineString(ring.coords).simplify(0.0003).coords)[:-1], close=True)
    doc.saveas(os.path.join(OUT, name + ".dxf"))
    report[name] = dict(width=round(maxx - minx, 3), height=round(maxy - miny, 3), area_sq_in=round(geom.area, 2), holes=sorted(circles))
print(json.dumps(report))
