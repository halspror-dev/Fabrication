# Local mesh checks for the v0.95 print files (nothing leaves this machine). Step 6 review: printing/review/.
# Usage: python3 stl_review.py STLDIR [LAYER_MM]   (needs: pip install trimesh shapely numpy)
# Make STLDIR first: cd drawing-scripts && python3 make_stl.py templates.py STLDIR
import sys, os, math
import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union

LAYER = float(sys.argv[2]) if len(sys.argv) > 2 else 0.20
TWO_LINES = 0.85                # narrower than this gets one extrusion line or none (0.4 nozzle, ~0.42 lines)
RHO = 1.37                      # PETG Matte g/cm3 (Bambu TDS, research/design-strength.md)
COMP = (0.0, 0.10, 0.15, 0.20)  # XY hole compensation per side (mm) to try on lobed holes


def sliced_height(h):
    """Bambu Studio keeps a layer if its centre is below the model top (research/accuracy.md, S5)."""
    n = 0
    while (n + 0.5) * LAYER < h - 1e-9:
        n += 1
    return n * LAYER


def section(m, z):
    s = m.section(plane_origin=(0, 0, z), plane_normal=(0, 0, 1))
    if s is None:
        return None
    p2, _ = s.to_2D(to_2D=np.eye(4))
    return unary_union([Polygon(p) for p in p2.polygons_full]) if p2.polygons_full else None


def holes(poly):
    """Closed holes in a layer (XY hole compensation only acts on these): (centre x, y, hole polygon)."""
    return [(Polygon(r).centroid.x, Polygon(r).centroid.y, Polygon(r))
            for g in getattr(poly, "geoms", [poly]) for r in g.interiors]


def necks(h):
    """Local minima of the hole's width across its long axis: the necks between the lobes of a scalloped hole."""
    x0, y0, x1, y1 = h.bounds
    along_y = (y1 - y0) >= (x1 - x0)
    a0, a1 = (y0, y1) if along_y else (x0, x1)
    w = []
    for t in np.arange(a0 + 0.3, a1 - 0.3, 0.01):
        ln = LineString([(x0 - 1, t), (x1 + 1, t)] if along_y else [(t, y0 - 1), (t, y1 + 1)])
        w.append(h.intersection(ln).length)
    return [w[i] for i in range(1, len(w) - 1) if w[i] < w[i - 1] and w[i] <= w[i + 1]]


def thin(poly, w):
    """The parts of a layer narrower than w (lost by an opening of w/2)."""
    t = poly.difference(poly.buffer(-w / 2, join_style=2).buffer(w / 2, join_style=2))
    return [g for g in getattr(t, "geoms", [t]) if g.area > 0.05]


for f in sorted(os.listdir(sys.argv[1])):
    if not f.endswith(".stl"):
        continue
    m = trimesh.load(os.path.join(sys.argv[1], f))
    lo, hi = m.bounds
    h = hi[2] - lo[2]
    print("== %s" % f)
    print("  watertight %s, winding %s, volume %s, bodies %d, euler %d, degenerate faces %d"
          % (m.is_watertight, m.is_winding_consistent, m.is_volume, len(m.split(only_watertight=False)), m.euler_number,
             int((m.area_faces < 1e-10).sum())))
    print("  size %.2f x %.2f x %.2f mm, %.2f cm3, solid mass %.1f g, sliced height at %.2f layers %.2f mm (%d layers)"
          % (*(hi - lo), m.volume / 1000, m.volume / 1000 * RHO, LAYER, sliced_height(h), round(sliced_height(h) / LAYER)))
    nz, zc = m.face_normals[:, 2], m.triangles_center[:, 2]
    up = zc > lo[2] + 0.01                                   # not the bed face
    over = up & (nz < -math.cos(math.radians(45)) + 1e-9) & (nz > -0.999)
    flat = up & (nz <= -0.999)
    print("  overhangs lower than 45 deg from the bed: %.1f mm2%s; flat ceilings (bridges): %.1f mm2%s"
          % (m.area_faces[over].sum(), (" at z %.1f-%.1f" % (zc[over].min(), zc[over].max())) if over.any() else "",
             m.area_faces[flat].sum(), (" at z %s" % sorted(set(np.round(zc[flat], 2).tolist()))) if flat.any() else ""))
    found, worst = {}, []
    for z in np.arange(lo[2] + LAYER / 2, hi[2], LAYER):
        p = section(m, z)
        if p is None:
            continue
        worst += [(z, g) for g in thin(p, TWO_LINES)]
        for x, y, hp in holes(p):
            found.setdefault((round(x, 1), round(y, 1)), (z, hp))
    if worst:
        b = unary_union([g for _, g in worst]).bounds
        print("  narrower than 2 lines (%.2f mm) in %d layers, z %.1f-%.1f, x %.1f-%.1f, y %.1f-%.1f"
              % (TWO_LINES, len(set(round(z, 2) for z, _ in worst)), min(z for z, _ in worst), max(z for z, _ in worst),
                 b[0], b[2], b[1], b[3]))
    for (x, y), (z, hp) in sorted(found.items()):
        inscribed = 2 * hp.exterior.distance(hp.centroid)
        eq = 2 * math.sqrt(hp.area / math.pi)
        x0, y0, x1, y1 = hp.bounds
        line = "  closed hole at (%.1f, %.1f): %.3f x %.3f, eq. dia %.3f" % (x, y, x1 - x0, y1 - y0, eq)
        nk = necks(hp) if min(x1 - x0, y1 - y0) > 4 and hp.area < 400 else []
        if nk:
            line += ", necks " + "; ".join("comp %+.2f: %s" % (c, "/".join("%.2f" % v for v in necks(hp.buffer(c, join_style=2, mitre_limit=10))))
                                           for c in COMP)
        elif hp.area < 400:
            line += ", narrowest %.3f" % inscribed
        print(line)
