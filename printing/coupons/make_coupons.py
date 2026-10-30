# Calibration coupons for the P2S plan (../PLAN.md, "Coupons"), written as STL files in mm, each already lying in its
# print orientation. C1-C3 and C6-C8 are plain shapes with no design sizes. C4 and C5 copy fit sizes from
# drawing-scripts/templates.py, so they are written only with --private, on BigGuy, into a folder that no cloud
# (OneDrive, Dropbox, Google Drive) syncs. Never upload them.
# Usage: python3 make_coupons.py OUTDIR [--private]      (needs: pip install manifold3d numpy shapely)
import sys, os
import numpy as np
import manifold3d as m3d

MM = 25.4
out = sys.argv[1]
private = "--private" in sys.argv[2:]
os.makedirs(out, exist_ok=True)


def write(name, m):
    """Set on the bed at the origin, binary STL."""
    m = m.translate(tuple(-np.array(m.bounding_box()[:3])))
    mesh = m.to_mesh()
    v, t = np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    n /= np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]
    rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v", "<f4", 9), ("attr", "<u2")])
    rec["n"], rec["v"] = n, np.hstack([a, b, c])
    path = os.path.join(out, name + ".stl")
    with open(path, "wb") as f:
        f.write(name.encode().ljust(80, b" ")[:80])
        f.write(np.uint32(len(t)).tobytes())
        f.write(rec.tobytes())
    bb = m.bounding_box()
    print("%s: %.2f x %.2f x %.2f mm, %.2f cm3, genus %d" % (path, bb[3], bb[4], bb[5], m.volume() / 1000, m.genus()))


def box(x, y, z):
    return m3d.Manifold.cube((x, y, z))


def cyl(h, d, n=128):
    return m3d.Manifold.cylinder(h, d / 2, d / 2, n)


def ramp(deg, h=10.0, w=8.0, top=8.0):
    """Block with a vertical back and a front face overhanging `deg` from vertical (0 = wall, 90 = flat ceiling)."""
    run = h * np.tan(np.radians(deg))
    return m3d.CrossSection([[(0, 0), (top, 0), (top + run, h), (0, h)]]).extrude(w).transform(
        [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]])


# C1 stringing: two 5 mm towers, 20 mm tall, 50 mm apart (centres), joined by a 0.6 mm base strip
write("C1-stringing-towers", box(60, 8, 0.6).translate((-5, -4, 0)) + cyl(20, 5) + cyl(20, 5).translate((50, 0, 0)))
# C2 elephant foot cube; C3 shrink bar (print two: one along X, one turned 90 degrees along Y)
write("C2-cube-25x25x10", box(25, 25, 10))
write("C3-shrink-bar-100x10x4", box(100, 10, 4))
# C6 overhang ramps, left to right 30, 40, 45, 50, 60, 70 degrees from vertical, 6 mm apart, one tick per ramp on a
# 0.6 mm base so the order can be read after printing
parts, x = [], 0.0
for i, deg in enumerate((30, 40, 45, 50, 60, 70)):
    r = ramp(deg)
    parts.append(r.translate((x, 0, 0.6)))
    for k in range(i + 1):
        parts.append(box(0.8, 2, 0.6).translate((x + 1 + 1.6 * k, -3, 0.6)))
    x += r.bounding_box()[3] + 6
write("C6-overhang-ramps", m3d.Manifold.batch_boolean([box(x - 6, 13, 0.6).translate((0, -4, 0))] + parts, m3d.OpType.Add))
# C7 strength bar; C8 solvent bar
write("C7-strength-bar-60x10x6", box(60, 10, 6))
write("C8-solvent-bar-60x10x3", box(60, 10, 3))

if private:
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient
    g = {}
    here = os.path.dirname(os.path.abspath(__file__))
    exec(open(os.path.join(here, "..", "..", "drawing-scripts", "templates.py")).read(), g)
    T = 0.125 * MM                     # laser-cut plate thickness, 3.175

    def plate(poly, thick):
        poly = orient(poly, 1.0)
        rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
        return m3d.CrossSection(rings).extrude(thick)

    # C4 fit plate, 70 x 45, notched corner at (0, 0) marks the layout (see the batch record's map).
    # Row y=8: pin holes DF, DF, DF+0.1, DF-0.1, clip hole PIN_D, screw hole D7. Slots run along Y, 15 mm long
    # overall: tab SLOT_W, keeper guide GSLOT, sleeve SLV_SLOT. Right: the frame's 4-lobe pivot hole (DF lobes at PIV).
    dfm = g["DF"] * MM
    c4 = Polygon([(3, 0), (70, 0), (70, 45), (0, 45), (0, 3)])
    for x, d in ((8, dfm), (18, dfm), (28, dfm + 0.1), (38, dfm - 0.1), (48, g["PIN_D"] * MM), (58, g["D7"] * MM)):
        c4 = c4.difference(g["hole"](x, 8, d))
    for x, w in ((10, g["SLOT_W"]), (22, g["GSLOT"]), (34, g["SLV_SLOT"])):
        w *= MM
        c4 = c4.difference(g["slot"](x, 20 + w / 2, x, 35 - w / 2, w))
    lobes = None
    for dz in g["PIV"]:
        h = g["hole"](55, 20 + dz * MM, dfm)
        lobes = h if lobes is None else lobes.union(h)
    write("C4-fit-plate-PRIVATE", plate(c4.difference(lobes), T))
    # C4h: 10 mm wide block with one horizontal pin hole (axis along X), to compare with the vertical ones
    write("C4h-horizontal-pin-hole-PRIVATE", box(10, 14, 14) - cyl(10, dfm).transform(
        [[0, 0, 1, 0], [0, 1, 0, 7], [1, 0, 0, 7]]))
    # C5 Z rounding: collar disc (print two: plain and Precise Z height), plate square, shim disc
    write("C5a-collar-disc-PRIVATE", cyl(g["CT"] * MM, 20))
    write("C5b-plate-square-PRIVATE", box(20, 20, T))
    write("C5c-shim-disc-PRIVATE", cyl(MM / 32, 20))
