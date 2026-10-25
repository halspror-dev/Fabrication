# Write the printed sleeves as STL files (millimeters), each standing on its open side so it prints without supports,
# and the 4 plates at their real thickness (collar 0.090, the rest 0.125), lying flat, for the plastic test build.
# Usage: python3 make_stl.py templates.py OUTDIR      (needs: pip install manifold3d numpy)
import sys, os
import numpy as np
import manifold3d as m3d
from shapely.geometry.polygon import orient
import sleeves as SL

src = open(sys.argv[1]).read().split("\ndef draw(")[0].replace("OUT = sys.argv[1]\nPNG = sys.argv[2]\n", "")
g = {}
exec(src, g)
os.makedirs(sys.argv[2], exist_ok=True)
MM = 25.4


def write(name, m):
    """Inches -> mm, set on the bed at the origin, ASCII STL."""
    m = m.scale((MM, MM, MM))
    m = m.translate(tuple(-np.array(m.bounding_box()[:3])))
    t = SL.tris(m)
    path = os.path.join(sys.argv[2], name + ".stl")
    with open(path, "w") as f:
        f.write("solid %s\n" % name)
        for a, b, c in t:
            nrm = np.cross(b - a, c - a)
            nrm = nrm / (np.linalg.norm(nrm) or 1.0)
            f.write("facet normal %.6f %.6f %.6f\n outer loop\n" % tuple(nrm))
            for v in (a, b, c):
                f.write("  vertex %.4f %.4f %.4f\n" % tuple(v))
            f.write(" endloop\nendfacet\n")
        f.write("endsolid %s\n" % name)
    bb = m.bounding_box()
    print("%s: %.1f x %.1f x %.1f mm, %.1f cm3, genus %d" % (path, bb[3], bb[4], bb[5], m.volume() / 1000, m.genus()))


def plate(poly, thick):
    poly = orient(poly, 1.0)          # outline counterclockwise, holes clockwise
    rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
    return m3d.CrossSection(rings).extrude(thick)


# local (s, n, y) -> print (x, y, z): trigger sleeve open back (n = -W) on the bed, grip sleeve open front (n = front) on the bed
W, nf = g["W"], g["GRIP_SLV"][0][2]
write("trigger-sleeve", SL.trigger_sleeve(g).transform([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, W]]))
write("grip-sleeve", SL.grip_sleeve(g).transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, nf]]))
for name, thick in (("collar", g["CT"]), ("keeper", 0.125), ("frame", 0.125), ("trigger", 0.125)):
    write("%s-%.3fin" % (name, thick), plate(g[name], thick))
