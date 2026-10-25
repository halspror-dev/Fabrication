import sys, math
import numpy as np
import shapely
from shapely.geometry import box
from shapely import affinity

src = open(sys.argv[1]).read().split("\ndef draw(")[0]
src = src.replace("OUT = sys.argv[1]", "").replace("PNG = sys.argv[2]", "")
g = {}; exec(src, g)
collar, keeper, frame, trigger = g["collar"], g["keeper"], g["frame"], g["trigger"]
P, S = g["P"], g["S"]
trig = affinity.translate(trigger, *P)
tsc = affinity.translate(g["trig_scale"], *P)
gsc = g["grip_scale"]
HD = g["HDPE"]
TS = g["collar_holes"][0][1]   # thumbscrew y
T = 0.125

# ---------- mesh building: list of (tri[3x3], part_id, color) ----------
TRIS, PID, COL = [], [], []
def add_tri(a, b, c, pid, col):
    TRIS.append((a, b, c)); PID.append(pid); COL.append(col)

def extrude(poly, plane, t0, t1, pid, col, off=(0, 0, 0)):
    if poly.geom_type == "MultiPolygon":
        for pp in poly.geoms: extrude(pp, plane, t0, t1, pid, col, off)
        return
    poly = poly.simplify(0.004)
    def to3(u, v, t):
        p = (u, v, t) if plane == "xy" else (u, t, v)
        return (p[0] + off[0], p[1] + off[1], p[2] + off[2])
    for tr in shapely.constrained_delaunay_triangles(poly).geoms:
        c = list(tr.exterior.coords)[:3]
        add_tri(*[to3(u, v, t0) for u, v in c], pid, col)
        add_tri(*[to3(u, v, t1) for u, v in c], pid, col)
    for ring in [poly.exterior] + list(poly.interiors):
        cs = list(ring.coords)
        for (u1, v1), (u2, v2) in zip(cs, cs[1:]):
            a, b, c, d = to3(u1, v1, t0), to3(u2, v2, t0), to3(u2, v2, t1), to3(u1, v1, t1)
            add_tri(a, b, c, pid, col); add_tri(a, c, d, pid, col)

def revolve(profile, pid, col, n=72, axis="z", center=(0, 0, 0)):
    th = np.linspace(0, 2 * np.pi, n + 1)
    def pt(r, h, a):
        cx, cy, cz = center
        if axis == "z": return (cx + r * math.cos(a), cy + r * math.sin(a), cz + h)
        return (cx + r * math.cos(a), cy + h, cz + r * math.sin(a))  # axis y
    for (r1, h1), (r2, h2) in zip(profile, profile[1:]):
        for a, b in zip(th, th[1:]):
            p1, p2, p3, p4 = pt(r1, h1, a), pt(r1, h1, b), pt(r2, h2, b), pt(r2, h2, a)
            add_tri(p1, p2, p3, pid, col); add_tri(p1, p3, p4, pid, col)

COLORS = dict(collar=(0.55, 0.74, 0.92), keeper=(0.62, 0.84, 0.58), frame=(0.93, 0.78, 0.55),
              clip=(0.70, 0.70, 0.72), trigger=(0.45, 0.45, 0.48), can=(0.86, 0.86, 0.86), ring=(0.75, 0.75, 0.75), button=(0.98, 0.98, 0.98))
STEEL, DARK, NYLON, BLACKNY, ALUM = (0.66, 0.67, 0.70), (0.18, 0.18, 0.20), (0.95, 0.94, 0.88), (0.16, 0.16, 0.17), (0.82, 0.82, 0.85)
CT, TY0, TY1 = g["CT"], g["TY0"], g["TY1"]
CLIP_Y, SIDE_Z, SR = g["CLIP_Y"], g["SIDE_Z"], g["STOP_R"]
FY0, FY1 = 0.095, 0.22          # handle plate faces
UY1 = 0.345                     # clip upright leg, outer face (inner face = FY1)

# ---------- hardware catalog (nominal catalog dimensions, inches) ----------
# num: (name, source, qty per handle, where)
HW = {
    1: ("Shoulder bolt 1/4\" x 1/4\", 10-24", "Bolt Depot #14221", 1, "trigger pivot"),
    2: ("Nylon washer 1/4\" (0.265 x 0.625 x 0.060)", "Bolt Depot #15939", 1, "pivot, between trigger and handle"),
    3: ("Nylon-insert locknut 10-24", "Bolt Depot #2552", 6, "pivot, up-stop, 4 clip bolts"),
    4: ("Button-head screw 10-24 x 5/8\"", "Bolt Depot #4396", 3, "2 clip-to-collar, 1 up-stop"),
    5: ("Flat-head socket screw 10-24 x 5/8\" (82 deg)", "Bolt Depot #4467", 2, "clip-to-handle, flush on trigger side"),
    6: ("Nylon spacer 5 mm ID x 10 mm OD x 5 mm", "Bolt Depot #13775", 1, "up-stop, under the trigger tail"),
    7: ("#10 flat washer", "Bolt Depot #2946", 2, "up-stop nut, thumbscrew"),
    8: ("Spade thumbscrew 10-24 x 1/2\"", "Bolt Depot #24038", 1, "keeper lock"),
    9: ("Hex nut 10-24 (epoxied under collar)", "Bolt Depot #2560", 1, "keeper lock"),
    10: ("Screw post, barrel half, 3/16\" x 5/8\"", "MyBinding SO058ASP", 4, "scales (head on the outside)"),
    11: ("Screw post, screw half", "MyBinding SO058ASP", 4, "scales (head on the inside)"),
}
INST = []    # (pid, hw number, joint name, anchor point)


def hexagon(cx, cy, af, hole_d=None, rot=0.0):
    r = af / math.sqrt(3)
    h = shapely.geometry.Polygon([(cx + r * math.cos(rot + k * math.pi / 3), cy + r * math.sin(rot + k * math.pi / 3)) for k in range(6)])
    return h.difference(shapely.geometry.Point(cx, cy).buffer(hole_d / 2, 24)) if hole_d else h


def rev(axis, x, y, z, prof, pid, col, n=28):
    """Revolve a profile [(r, a)] about a y- or z-axis through (x, y, z); a is the absolute coordinate along the axis."""
    if axis == "y":
        revolve(prof, pid, col, n=n, axis="y", center=(x, 0, z))
    else:
        revolve(prof, pid, col, n=n, axis="z", center=(x, y, 0))


def hexprism(axis, x, y, z, a0, a1, af, pid, col, hole=0.19):
    if axis == "y":
        extrude(hexagon(x, z, af, hole), "xz", a0, a1, pid, col)
    else:
        extrude(hexagon(x, y, af, hole), "xy", a0, a1, pid, col)


def socket(axis, x, y, z, a, s, pid):   # dark hex socket drawn on a head face at axial coordinate a (s = +1/-1 outward)
    hexprism(axis, x, y, z, a, a + 0.006 * s if s > 0 else a, 0.125, pid, DARK, hole=None) if s > 0 else hexprism(axis, x, y, z, a - 0.006, a, 0.125, pid, DARK, hole=None)


def shank(axis, x, y, z, a0, a1, pid, r=0.095):
    lo, hi = min(a0, a1), max(a0, a1)
    rev(axis, x, y, z, [(0, lo), (r, lo), (r, hi), (0, hi)], pid, STEEL, n=20)


def hw_button(axis, x, y, z, a_face, s, pid):
    """Button-head socket screw: head bearing face at a_face, head grows in -s, shank grows in +s (0.625 long)."""
    prof = [(0, 0), (0.1875, 0), (0.18, 0.035), (0.15, 0.07), (0.10, 0.095), (0, 0.105)]
    rev(axis, x, y, z, [(r, a_face - s * h) for r, h in prof], pid, STEEL)
    socket(axis, x, y, z, a_face - s * 0.105, -s, pid)
    shank(axis, x, y, z, a_face, a_face + s * 0.625, pid)


def hw_flat(axis, x, y, z, a_top, s, pid):
    """82 deg flat-head socket screw: top of head flush at a_top, cone and shank grow in +s, 0.625 overall."""
    rev(axis, x, y, z, [(0, a_top), (0.196, a_top), (0.095, a_top + s * 0.105), (0, a_top + s * 0.105)], pid, STEEL)
    socket(axis, x, y, z, a_top, -s, pid)
    shank(axis, x, y, z, a_top + s * 0.105, a_top + s * 0.625, pid)


def hw_shoulder(axis, x, y, z, a_face, s, pid):
    """Socket shoulder screw: head (0.375 x 0.188) behind a_face, 0.25 shoulder, 0.375 of 10-24 thread."""
    rev(axis, x, y, z, [(0, a_face - s * 0.188), (0.17, a_face - s * 0.188), (0.1875, a_face - s * 0.17), (0.1875, a_face), (0, a_face)], pid, STEEL)
    socket(axis, x, y, z, a_face - s * 0.188, -s, pid)
    rev(axis, x, y, z, [(0, a_face), (0.125, a_face), (0.125, a_face + s * 0.25), (0, a_face + s * 0.25)], pid, STEEL)
    shank(axis, x, y, z, a_face + s * 0.25, a_face + s * 0.625, pid)


def hw_locknut(axis, x, y, z, a_face, s, pid):
    hexprism(axis, x, y, z, *sorted((a_face, a_face + s * 0.17)), 0.375, pid, STEEL)
    rev(axis, x, y, z, [(0.098, a_face + s * 0.17), (0.17, a_face + s * 0.17), (0.15, a_face + s * 0.236), (0.098, a_face + s * 0.236)], pid, STEEL)
    rev(axis, x, y, z, [(0.06, a_face + s * 0.232), (0.098, a_face + s * 0.232), (0.098, a_face + s * 0.236), (0.06, a_face + s * 0.236)], pid, NYLON)


def hw_hexnut(axis, x, y, z, a_face, s, pid):
    hexprism(axis, x, y, z, *sorted((a_face, a_face + s * 0.125)), 0.375, pid, STEEL)


def hw_washer(axis, x, y, z, a_face, s, pid, idr, odr, t, col):
    rev(axis, x, y, z, [(idr, a_face), (odr, a_face), (odr, a_face + s * t), (idr, a_face + s * t), (idr, a_face)], pid, col)


def hw_post_barrel(axis, x, y, z, a_face, s, pid):
    """Screw-post barrel half: 7/16 head behind a_face, 3/16 barrel 0.625 long in +s."""
    rev(axis, x, y, z, [(0, a_face - s * 0.06), (0.21, a_face - s * 0.06), (0.219, a_face - s * 0.03), (0.219, a_face), (0, a_face)], pid, ALUM)
    rev(axis, x, y, z, [(0, a_face), (0.094, a_face), (0.094, a_face + s * 0.625), (0, a_face + s * 0.625)], pid, ALUM)


def hw_post_screw(axis, x, y, z, a_face, s, pid):
    """Screw-post screw half: slotted 7/16 head behind a_face, short screw in +s."""
    rev(axis, x, y, z, [(0, a_face - s * 0.06), (0.21, a_face - s * 0.06), (0.219, a_face - s * 0.03), (0.219, a_face), (0, a_face)], pid, ALUM)
    shank(axis, x, y, z, a_face, a_face + s * 0.25, pid, r=0.07)


def hw_spacer(axis, x, y, z, a_face, s, pid):
    rev(axis, x, y, z, [(0.098, a_face), (SR, a_face), (SR, a_face + s * 0.197), (0.098, a_face + s * 0.197), (0.098, a_face)], pid, BLACKNY)


def hw_thumb(x, y, z_face, pid):
    """Spade thumbscrew, axis z: washer face at z_face, spade head above, 1/2\" of thread below (head size approximate)."""
    rev("z", x, y, 0, [(0, z_face), (0.16, z_face), (0.16, z_face + 0.06), (0, z_face + 0.06)], pid, STEEL)
    spade = shapely.geometry.Polygon([(-0.12, 0.06), (0.12, 0.06), (0.265, 0.22), (0.265, 0.36), (0.20, 0.44), (-0.20, 0.44), (-0.265, 0.36), (-0.265, 0.22)])
    spade = affinity.translate(spade, x, z_face).buffer(0.02, join_style=1)
    extrude(spade, "xz", y - 0.045, y + 0.045, pid, STEEL)
    shank("z", x, y, 0, z_face, z_face - 0.5, pid)


def build(explode=0.0, show_can=True, show_trigger=True, show_hw=True):
    """explode = 0 assembled, 1 fully exploded (parts pulled apart along their bolt lines)."""
    TRIS.clear(); PID.clear(); COL.clear(); INST.clear()
    e = explode
    def O(dx=0.0, dy=0.0, dz=0.0):
        return (dx * e, dy * e, dz * e)
    OFF = dict(collar=O(dz=-0.9), keeper=O(dz=0.45), clip=O(dy=0.75, dz=0.75), trigger=O(dy=-1.35),
               tsc_out=O(dy=-1.95), tsc_in=O(dy=-0.75), gsc_in=O(dy=-0.55), gsc_out=O(dy=0.55))
    if show_can and e == 0:
        revolve([(0, -3.6), (1.28, -3.6), (1.28, -0.95), (1.15, -0.85), (1.0, -0.65), (0.75, -0.35), (0.6, -0.15), (0.53, -0.13), (0, -0.13)], 1, COLORS["can"])
        revolve([(0, 0), (0.64, 0), (0.64, 0.14), (0, 0.14)], 2, COLORS["ring"])
        revolve([(0, 0.14), (0.33, 0.14), (0.33, 0.765), (0, 0.765)], 3, COLORS["button"], n=48)
    extrude(collar, "xy", -CT, 0, 10, COLORS["collar"], off=OFF["collar"])
    extrude(keeper, "xy", 0, 0.125, 11, COLORS["keeper"], off=OFF["keeper"])
    extrude(frame, "xz", FY0, FY1, 12, COLORS["frame"])
    extrude(gsc, "xz", FY1, FY1 + HD, 18, (0.16, 0.16, 0.17), off=OFF["gsc_out"])
    extrude(gsc, "xz", FY0 - HD, FY0, 19, (0.16, 0.16, 0.17), off=OFF["gsc_in"])
    D7 = g["D7"]; H = g["hole"]
    flat = box(-1.80, FY1, -0.70, 0.97).difference(H(-0.95, CLIP_Y, D7)).difference(H(-1.45, CLIP_Y, D7))
    upr = box(-1.80, 0.0, -0.70, 0.75).difference(H(-1.05, SIDE_Z, D7)).difference(H(-1.50, SIDE_Z, D7))
    flat = flat.difference(box(-1.81, FY1 - 0.01, -0.69, UY1))  # corner belongs to the upright leg
    extrude(flat, "xy", 0, 0.125, 13, COLORS["clip"], off=OFF["clip"])
    extrude(upr, "xz", FY1, UY1, 13, COLORS["clip"], off=OFF["clip"])
    if show_trigger:
        extrude(trig, "xz", TY0, TY1, 14, COLORS["trigger"], off=OFF["trigger"])
        extrude(tsc, "xz", TY1, TY1 + HD, 16, (0.16, 0.16, 0.17), off=OFF["tsc_in"])
        extrude(tsc, "xz", TY0 - HD, TY0, 17, (0.16, 0.16, 0.17), off=OFF["tsc_out"])
    if not show_hw:
        return
    pid = [100]
    def add(num, joint, anchor, fn, off=(0, 0, 0)):
        p = pid[0]; pid[0] += 1
        ox, oy, oz = off
        fn(p, ox, oy, oz)
        INST.append((p, num, joint, (anchor[0] + ox, anchor[1] + oy, anchor[2] + oz)))
    px, pz = P
    sx, sz = S
    if show_trigger:
        # pivot: head on the trigger side, shoulder through trigger + nylon washer, bears on the handle plate; locknut on the clip side
        add(1, "pivot", (px, FY0 - 0.25 - 0.188, pz), lambda p, ox, oy, oz: hw_shoulder("y", px + ox, 0, pz + oz, FY0 - 0.25 + oy, 1, p), O(dy=-2.3))
        add(2, "pivot", (px, TY1 + 0.03, pz + 0.30), lambda p, ox, oy, oz: hw_washer("y", px + ox, 0, pz + oz, TY1 + oy, 1, p, 0.1325, 0.3125, 0.060, NYLON), O(dy=-0.65))
    add(3, "pivot", (px, FY1 + 0.236, pz), lambda p, ox, oy, oz: hw_locknut("y", px + ox, 0, pz + oz, FY1 + oy, 1, p), O(dy=0.75))
    # up-stop: button screw from the trigger side through the spacer and the handle plate, washer + locknut on the clip side
    add(4, "up-stop", (sx, FY0 - 0.197 - 0.105, sz), lambda p, ox, oy, oz: hw_button("y", sx + ox, 0, sz + oz, FY0 - 0.197 + oy, 1, p), O(dy=-2.3))
    add(6, "up-stop", (sx, FY0 - 0.1, sz + SR), lambda p, ox, oy, oz: hw_spacer("y", sx + ox, 0, sz + oz, FY0 - 0.197 + oy, 1, p), O(dy=-0.7))
    add(7, "up-stop", (sx, FY1 + 0.03, sz + 0.25), lambda p, ox, oy, oz: hw_washer("y", sx + ox, 0, sz + oz, FY1 + oy, 1, p, 0.1095, 0.25, 0.049, STEEL), O(dy=0.45))
    add(3, "up-stop", (sx, FY1 + 0.049 + 0.236, sz), lambda p, ox, oy, oz: hw_locknut("y", sx + ox, 0, sz + oz, FY1 + 0.049 + oy, 1, p), O(dy=0.85))
    # keeper thumbscrew: washer on the keeper, nut epoxied under the collar
    add(8, "keeper lock", (0, TS, 0.125 + 0.049 + 0.44), lambda p, ox, oy, oz: hw_thumb(ox, TS + oy, 0.125 + 0.049 + oz, p), O(dz=1.25))
    add(7, "keeper lock", (0.25, TS, 0.15), lambda p, ox, oy, oz: hw_washer("z", ox, TS + oy, 0, 0.125 + oz, 1, p, 0.1095, 0.25, 0.049, STEEL), O(dz=0.8))
    add(9, "keeper lock", (0, TS, -CT - 0.125), lambda p, ox, oy, oz: hw_hexnut("z", ox, TS + oy, 0, -CT + oz, -1, p), O(dz=-1.45))
    # angle clip to collar: button heads on the flat leg, locknuts under the collar
    for x in (-0.95, -1.45):
        add(4, "clip to collar", (x, CLIP_Y, 0.23), lambda p, ox, oy, oz, x=x: hw_button("z", x + ox, CLIP_Y + oy, 0, 0.125 + oz, -1, p), O(dy=0.75, dz=1.45))
        add(3, "clip to collar", (x, CLIP_Y, -CT - 0.236), lambda p, ox, oy, oz, x=x: hw_locknut("z", x + ox, CLIP_Y + oy, 0, -CT + oz, -1, p), O(dz=-1.55))
    # angle clip to handle plate: flat heads countersunk flush on the trigger side, locknuts on the clip side
    for x in (-1.05, -1.50):
        add(5, "clip to handle", (x, FY0, SIDE_Z), lambda p, ox, oy, oz, x=x: hw_flat("y", x + ox, 0, SIDE_Z + oz, FY0 + oy, 1, p), O(dy=-0.75))
        add(3, "clip to handle", (x, UY1 + 0.236, SIDE_Z), lambda p, ox, oy, oz, x=x: hw_locknut("y", x + ox, 0, SIDE_Z + oz, UY1 + oy, 1, p), O(dy=1.45, dz=0.75))
    # scales: barrel half from outside, screw half from inside
    if show_trigger:
        for hx, hz in g["SCALE_HOLES"]:
            x, z = hx + px, hz + pz
            add(10, "trigger scales", (x, TY0 - HD - 0.06, z), lambda p, ox, oy, oz, x=x, z=z: hw_post_barrel("y", x + ox, 0, z + oz, TY0 - HD + oy, 1, p), O(dy=-2.55))
            add(11, "trigger scales", (x, TY1 + HD + 0.06, z), lambda p, ox, oy, oz, x=x, z=z: hw_post_screw("y", x + ox, 0, z + oz, TY1 + HD + oy, -1, p), O(dy=-0.25))
    for x, z in g["GRIP_HOLES"]:
        add(10, "grip scales", (x, FY1 + HD + 0.06, z), lambda p, ox, oy, oz, x=x, z=z: hw_post_barrel("y", x + ox, 0, z + oz, FY1 + HD + oy, -1, p), O(dy=1.1))
        add(11, "grip scales", (x, FY0 - HD - 0.06, z), lambda p, ox, oy, oz, x=x, z=z: hw_post_screw("y", x + ox, 0, z + oz, FY0 - HD + oy, 1, p), O(dy=-1.1))


# ---------- rasterizer ----------
def render(elev, azim, W=1400, H=1400, fit_ids=None, margin=0.06):
    tr = np.array(TRIS, float)          # (n,3,3)
    pid = np.array(PID); col = np.array(COL, float)
    el, az = math.radians(elev), math.radians(azim)
    view = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])  # toward camera
    right = np.cross([0, 0, 1], view); right /= np.linalg.norm(right)
    up = np.cross(view, right)
    pts = tr.reshape(-1, 3)
    u = pts @ right; v = pts @ up; d = pts @ view
    sel = np.isin(np.repeat(pid, 3), fit_ids) if fit_ids is not None else np.ones(len(u), bool)
    umin, umax, vmin, vmax = u[sel].min(), u[sel].max(), v[sel].min(), v[sel].max()
    s = min(W, H) * (1 - 2 * margin) / max(umax - umin, vmax - vmin)
    cu, cv = (umin + umax) / 2, (vmin + vmax) / 2
    X = (u - cu) * s + W / 2; Y = H / 2 - (v - cv) * s
    X = X.reshape(-1, 3); Y = Y.reshape(-1, 3); D = d.reshape(-1, 3)
    # normals + shading
    nrm = np.cross(tr[:, 1] - tr[:, 0], tr[:, 2] - tr[:, 0])
    ln = np.linalg.norm(nrm, axis=1); ok = ln > 1e-12
    nrm[ok] /= ln[ok][:, None]
    nrm[(nrm @ view) < 0] *= -1
    light = view + 0.45 * up + 0.2 * right; light /= np.linalg.norm(light)
    shade = 0.62 + 0.38 * np.clip(nrm @ light, 0, 1)
    zbuf = np.full((H, W), -np.inf); img = np.ones((H, W, 3)); idb = np.full((H, W), -1)
    nbuf = np.zeros((H, W, 3))
    for i in np.where(ok)[0]:
        x0, x1 = int(max(0, math.floor(X[i].min()))), int(min(W - 1, math.ceil(X[i].max())))
        y0, y1 = int(max(0, math.floor(Y[i].min()))), int(min(H - 1, math.ceil(Y[i].max())))
        if x1 < x0 or y1 < y0: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax_, bx, cx), (ay, by, cy) = X[i], Y[i]
        den = (by - cy) * (ax_ - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12: continue
        w1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        w2 = ((cy - ay) * (xs - cx) + (ax_ - cx) * (ys - cy)) / den
        w3 = 1 - w1 - w2
        inside = (w1 >= -1e-6) & (w2 >= -1e-6) & (w3 >= -1e-6)
        if not inside.any(): continue
        z = w1 * D[i, 0] + w2 * D[i, 1] + w3 * D[i, 2]
        zb = zbuf[y0:y1 + 1, x0:x1 + 1]
        m = inside & (z > zb)
        zb[m] = z[m]
        img[y0:y1 + 1, x0:x1 + 1][m] = col[i] * shade[i]
        idb[y0:y1 + 1, x0:x1 + 1][m] = pid[i]
        nbuf[y0:y1 + 1, x0:x1 + 1][m] = nrm[i]
    # outlines: part change, crease, or depth jump
    edge = np.zeros((H, W), bool)
    for dy_, dx_ in ((0, 1), (1, 0)):
        a = slice(0, H - dy_), slice(0, W - dx_)
        b = slice(dy_, H), slice(dx_, W)
        e1 = idb[a] != idb[b]
        e2 = (np.sum(nbuf[a] * nbuf[b], axis=2) < 0.9) & (idb[a] >= 0) & (idb[b] >= 0)
        za, zb_ = zbuf[a], zbuf[b]
        with np.errstate(invalid='ignore'):
            e3 = (idb[a] == idb[b]) & (idb[a] >= 0) & (np.abs(za - zb_) > 0.35)
        ee = e1 | e2 | e3
        edge[a] |= ee
    # thicken slightly
    th = edge.copy(); th[1:] |= edge[:-1]; th[:, 1:] |= edge[:, :-1]
    img[th] = img[th] * 0.25
    global LAST_IDB
    LAST_IDB = idb
    return img, (s, cu, cv, right, up, W, H)

def project(p, info):
    s, cu, cv, right, up, W, H = info
    p = np.array(p)
    return ((p @ right - cu) * s + W / 2, H / 2 - (p @ up - cv) * s)

if __name__ == "__main__":
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    out = sys.argv[2]
    def panel(fig, rect, img, info, cap, labels, balloons=True, min_px=200):
        ax = fig.add_axes(rect); ax.imshow(img, interpolation="lanczos"); ax.axis("off")
        ax.set_title(cap, fontsize=8, weight="bold", loc="left")
        for p3, txt, (dx, dy) in labels:
            x, y = project(p3, info)
            ax.annotate(txt, (x, y), (x + dx, y + dy), fontsize=6.5,
                        arrowprops=dict(arrowstyle="-", lw=0.5), bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5))
        shown = []
        if balloons:
            idb = LAST_IDB
            Hh, Ww = idb.shape
            used = []
            for p, num, joint, anchor in INST:
                ys, xs = np.nonzero(idb == p)
                if len(xs) < min_px:
                    continue
                cx, cy = xs.mean(), ys.mean()
                k = np.argmin((xs - cx) ** 2 + (ys - cy) ** 2)      # a visible pixel of the part nearest its centroid
                cx, cy = xs[k], ys[k]
                dx, dy = cx - Ww / 2, cy - Hh / 2
                n = math.hypot(dx, dy) or 1.0
                bx, by = cx + 95 * dx / n, cy + 95 * dy / n
                for _ in range(12):                                   # nudge off other balloons
                    if all(math.hypot(bx - ux, by - uy) > 46 for ux, uy in used):
                        break
                    bx, by = bx - 30 * dy / n, by + 30 * dx / n
                bx, by = min(max(bx, 25), Ww - 25), min(max(by, 25), Hh - 25)
                used.append((bx, by))
                ax.annotate(str(num), (cx, cy), (bx, by), fontsize=6, weight="bold", ha="center", va="center",
                            arrowprops=dict(arrowstyle="-", lw=0.5, color="#c0392b"),
                            bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec="#c0392b", lw=0.7))
                shown.append(p)
        return shown

    def legend(fig, y_top, title="HARDWARE (balloon numbers)"):
        fig.text(0.06, y_top, title, fontsize=8, weight="bold")
        rows = ["%-3s %-46s %-22s %4s  %s" % ("#", "part", "buy", "qty", "where")]
        for k, (name, src, q, where) in HW.items():
            rows.append("%-3d %-46s %-22s %4d  %s" % (k, name, src, q, where))
        fig.text(0.06, y_top - 0.008, "\n".join(rows), fontsize=5.6, family="monospace", va="top", linespacing=1.45)

    with PdfPages(out) as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.06, 0.965, "3D VIEWS: assembled on a can", fontsize=11, weight="bold")
        fig.text(0.06, 0.95, "Blue = collar, green = keeper, tan = handle plate, light gray = angle clip, dark gray = trigger, near-black = HDPE scales.\n"
                 "Hardware: steel = stainless bolts and nuts, white = nylon washer, black = nylon spacer, silver = aluminum screw posts.\n"
                 "Red balloons = hardware number (list at the bottom, and the exploded views on the next pages).", fontsize=7, va="top")
        build()
        img, info = render(12, -75)
        panel(fig, [0.03, 0.52, 0.94, 0.37], img, info, "From the front-right (trigger side)", [
            ((0.95, -0.4, -0.06), "COLLAR", (150, 170)),
            ((0.6, -1.9, 0.125), "KEEPER", (260, 60)),
            ((-1.0, -0.06, 1.2), "TRIGGER", (-200, -200)),
            ((-4.7, -0.1, -3.4), "GRIP", (-220, 40))], min_px=200)
        build()
        img, info = render(22, 125)
        panel(fig, [0.03, 0.15, 0.94, 0.37], img, info, "From the back-left (angle clip side)", [
            ((-1.25, 0.97, 0.06), "ANGLE CLIP", (-330, 120)),
            ((-3.0, 0.22, 0.0), "HANDLE plate", (300, 120))], min_px=200)
        legend(fig, 0.135)
        pdf.savefig(fig); fig.savefig(out.replace(".pdf", "-p1.png"), dpi=110)

        for pg, (el, az, side) in enumerate(((16, -38, "trigger side"), (18, 142, "angle clip side"))):
            fig = plt.figure(figsize=(8.5, 11))
            fig.text(0.06, 0.965, "EXPLODED VIEW, %s: every bolt, nut, washer and spacer (can hidden)" % side, fontsize=11, weight="bold")
            fig.text(0.06, 0.95, "Each part is pulled straight out along its own bolt line, so it lines up with the hole it goes in. The handle plate stays put.\n"
                     "Trigger-side parts come out toward you on page 3, clip-side parts on page 4. Red balloon = hardware number in the list below.", fontsize=7, va="top")
            build(explode=1.0, show_can=False)
            img, info = render(el, az, W=1600, H=1600, margin=0.03)
            panel(fig, [0.02, 0.24, 0.96, 0.69], img, info, "", [], min_px=400)
            legend(fig, 0.225)
            pdf.savefig(fig); fig.savefig(out.replace(".pdf", "-p%d.png" % (3 + pg)), dpi=110)

        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.06, 0.965, "ANGLE CLIP CLOSE-UP (can and trigger hidden)", fontsize=11, weight="bold")
        fig.text(0.06, 0.95, "The clip is a 1-1/10\" piece of 3/4\" x 3/4\" x 1/8\" aluminum ANGLE.\n"
                 "FLAT leg on the collar: 2 button-head screws (4) go DOWN through it and the collar, locknuts (3) underneath.\n"
                 "UPRIGHT leg against the handle plate: 2 flat-head screws (5) come from the TRIGGER side, countersunk flush in the handle plate,\n"
                 "locknuts (3) on the clip side. Flush heads are needed: the trigger swings 0.06\" from that face and would hit any head or nut.", fontsize=7, va="top")
        build(show_can=False, show_trigger=False)
        ids = [13] + [p for p, n, j, a in INST if j.startswith("clip")]
        img, info = render(28, 115, fit_ids=ids, margin=0.10)
        panel(fig, [0.03, 0.47, 0.94, 0.40], img, info, "Assembled", [
            ((-1.0, 0.85, 0.125), "FLAT leg", (-450, 230)),
            ((-1.25, 0.345, 0.65), "UPRIGHT leg", (-520, -260)),
            ((0.4, 0.4, -0.06), "COLLAR", (-150, 260))])
        build(explode=0.6, show_can=False, show_trigger=False)
        ids = [13] + [p for p, n, j, a in INST if j.startswith("clip")]
        img, info = render(28, 115, fit_ids=ids, margin=0.10)
        panel(fig, [0.03, 0.05, 0.94, 0.40], img, info, "Pulled apart along the bolt lines", [])
        pdf.savefig(fig); fig.savefig(out.replace(".pdf", "-p2.png"), dpi=110)
    print("ok")
