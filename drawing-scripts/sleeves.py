# v0.95 printed sleeves as real solids, built from the sections in templates.py (TRIG_SLV, GRIP_SLV).
# Used by render3d.py (3D views + check3d) and make_stl.py (print files). Needs: pip install manifold3d
import math
import numpy as np
import manifold3d as m3d
from shapely import affinity
from shapely.geometry.polygon import orient

ARC = 24   # points on each half-round


def _hull_loft(sections):
    """Union of the convex hulls of each pair of neighboring sections (each section = 3D points of one convex outline)."""
    parts = [m3d.Manifold.hull_points(np.vstack([a, b])) for a, b in zip(sections, sections[1:])]
    return m3d.Manifold.batch_boolean(parts, m3d.OpType.Add)


def _d(s, n_flat, n_round, R, toward):
    """D-shaped section at s in local (s, n, y): flat side at n_flat, half-round of radius R whose tip is at n_round."""
    c = n_round - toward * R
    pts = [(s, n_flat, -R), (s, n_flat, R)]
    for k in range(ARC + 1):
        a = -math.pi / 2 + math.pi * k / ARC
        pts.append((s, c + toward * R * math.cos(a), R * math.sin(a)))
    return np.array(pts)


def _holes(m, holes, d):
    for s, n in holes:
        m = m - m3d.Manifold.cylinder(2.0, d / 2, d / 2, 32).translate((s, n, -1.0))
    return m


def trigger_sleeve(g):
    """Trigger sleeve in local coords: s down the bar front edge, n forward of it, y across (0 = plate middle)."""
    R, W, L = g["SLV_R"], g["W"], g["L"]
    m = _hull_loft([_d(s, -W, f, R, 1) for s, f in g["TRIG_SLV"]])
    m = m - m3d.Manifold.cube((L - g["TS0"] + 1.0, W + 1.0, g["SLV_SLOT"])).translate((g["TS0"] - 1.0, -W - 1.0, -g["SLV_SLOT"] / 2))
    return _holes(m, [(g["TS0"] + t, -W / 2) for t in (0.60, g["TS_LEN"] - 0.60)], g["D7"])


def grip_sleeve(g):
    """Grip sleeve in local coords: s down the grip centerline, n forward, y across. The plate's own outline is the slot."""
    R = g["SLV_R"]
    m = _hull_loft([_d(s, f, b, R, -1) for s, b, f in g["GRIP_SLV"]])
    G0, gu, gn = g["G0"], (g["gux"], g["guz"]), (g["gnx"], g["gnz"])
    # frame outline (x, z) -> local (s, n): rows of the inverse of [gu gn]
    plate = affinity.translate(g["plate_out"], -G0[0], -G0[1])
    plate = affinity.affine_transform(plate, [gu[0], gu[1], gn[0], gn[1], 0, 0]).buffer(0.003, join_style=2)
    plate = orient(plate, 1.0)                             # counterclockwise, or manifold reads it as empty
    slot = m3d.CrossSection([list(plate.exterior.coords)[:-1]]).extrude(g["SLV_SLOT"]).translate((0, 0, -g["SLV_SLOT"] / 2))
    return _holes(m - slot, [(t, 0.0) for t in (0.60, g["GL"] - 0.60)], g["D7"])


def _xform(m, o, u, n, ymid):
    """local (s, n, y) -> world (x, y, z), mirroring y if needed so the solid keeps its handedness (sleeves are symmetric in y)."""
    sy = 1.0 if (u[0] * n[1] - n[0] * u[1]) < 0 else -1.0
    return m.transform([[u[0], n[0], 0, o[0]], [0, 0, sy, ymid], [u[1], n[1], 0, o[1]]])


def world_trigger_sleeve(g):
    F0, P = g["F0"], g["P"]
    return _xform(trigger_sleeve(g), (F0[0] + P[0], F0[1] + P[1]), (g["ux"], g["uz"]), (g["nx"], g["nz"]), (g["TY0"] + g["TY1"]) / 2)


def world_grip_sleeve(g):
    return _xform(grip_sleeve(g), g["G0"], (g["gux"], g["guz"]), (g["gnx"], g["gnz"]), (g["FY0"] + g["FY1"]) / 2)


def tris(m):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    return v[np.asarray(mesh.tri_verts)]
